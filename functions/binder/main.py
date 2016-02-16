# Copyright 2015, 2016 Datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import boto3
import csv
import logging
import json
import pprint
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)

autoscaling = boto3.client('autoscaling')
ec2 = boto3.client('ec2')
route53 = boto3.client('route53')


def handle(event, context):
    logger.debug("%s", pprint.pformat(event))

    msg = json.loads(event['Records'][0]['Sns']['Message'])

    group_name = msg['AutoScalingGroupName']

    instance_id = msg['EC2InstanceId']
    instance = get_ec2_instance(instance_id)
    instance_tags = tag_list_to_dict(instance.get('Tags', []))
    instance_az = instance['Placement']['AvailabilityZone']

    life_hook = msg['LifecycleHookName']
    life_token = msg['LifecycleActionToken']
    life_transition = msg['LifecycleTransition']

    if 'DnsConfig' not in instance_tags:
        logger.error("DnsConfig tag not present on registered auto scaling group (group: %s)", group_name)
        autoscaling.complete_lifecycle_action(
            AutoScalingGroupName=group_name,
            LifecycleActionToken=life_token,
            LifecycleActionResult='ABANDON',
            LifecycleHookName=life_hook,
        )
        return event

    dns_config = parse_dns_config_tag(instance_tags['DnsConfig'])
    hosted_zone = route53.get_hosted_zone(Id=dns_config['z'])['HostedZone']
    hosted_zone_id = hosted_zone['Id'].replace('/hostedzone/', '')
    domain_name = hosted_zone['Name']
    record_name = create_custom_name(dns_config, instance_id, instance_az) + "." + domain_name

    if life_transition == "autoscaling:EC2_INSTANCE_LAUNCHING":
        record_target = instance['PublicDnsName']
        bind(hosted_zone_id, record_name, record_target)
    elif life_transition == "autoscaling:EC2_INSTANCE_TERMINATING":
        # Query the bound DNS name from Route53 rather than relying on the EC2 instance public DNS address because if
        # the lifecycle times out before the lambda is called then the instance will be terminated and the DNS record
        # will be lost which leads to stale DNS records.
        record_target = get_record_target(hosted_zone_id, record_name, 'CNAME')
        unbind(hosted_zone_id, record_name, record_target)
    else:
        logger.warn("Unsupported auto scaling lifecycle transition (type: %s)", life_transition)

    autoscaling.complete_lifecycle_action(
        AutoScalingGroupName=group_name,
        LifecycleActionToken=life_token,
        LifecycleActionResult='CONTINUE',
        LifecycleHookName=life_hook,
    )


def get_ec2_instance(instance_id):

    """Retrieves an EC2 instance by the specified instance identifier.

    :param instance_id: The instance ID to query for.
    :return: The EC2 instance.
    :raises: ValueError if the EC2 instance is not found.
    """

    result = ec2.describe_instances(InstanceIds=[instance_id])
    if len(result['Reservations']) >= 1 and len(result['Reservations'][0]['Instances']) == 1:
        return result['Reservations'][0]['Instances'][0]
    else:
        raise ValueError("Unable to find EC2 instance by ID (id: {})".format(instance_id))


def create_custom_name(dns_config, instance_id, availability_zone):
    region = parse_region_from_zone(availability_zone)

    patterns = {
        '{id}': instance_id.replace('i-', ''),
        '{re}': region,
        '{sr}': create_short_region_id(region)
    }

    name_format = dns_config['f']
    regex = re.compile("(%s)" % "|".join(map(re.escape, patterns.keys())))
    return regex.sub(lambda mo: patterns[mo.string[mo.start():mo.end()]], name_format)


def tag_list_to_dict(tag_list):
    result = {}
    for item in tag_list:
        result[item['Key']] = item['Value']

    return result


def parse_region_from_zone(zone):
    logger.debug("Parsing region ID from zone ID (zone: %s)", zone)
    return str(zone).lower().rstrip("abcdefghijklmnopqrstuvwxyz")


def create_short_region_id(region):
    (location, qualifier, index) = region.split('-')
    short_qualifier = {
        "central": "c",
        "north": "n",
        "northeast": "ne",
        "northwest": "nw",
        "east": "e",
        "south": "s",
        "southeast": "se",
        "southwest": "sw",
        "west": "w",
    }

    return location[0:2] + short_qualifier[qualifier] + index


def parse_dns_config_tag(value):
    logger.debug("Parsing DnsConfig tag (value: %s)", value)
    return dict(csv.reader([item], delimiter='=', quotechar="'").next()
                for item in csv.reader([value], delimiter=';', quotechar="'").next())


def get_record_target(zone_id, name, record_type):
    logger.debug("Querying DNS record set (zone: %s, type: %s, name: %s)", zone_id, record_type, name)
    resp = route53.list_resource_record_sets(
        HostedZoneId=zone_id,
        StartRecordName=name,
        StartRecordType=record_type
    )

    record_sets = resp.get('ResourceRecordSets', [])
    if len(record_sets) >= 1:
        target = record_sets[0]['ResourceRecords'][0]['Value']
        logger.debug("Retrieved DNS record set target (zone: %s, type: %s, name: %s, target: %s)",
                     zone_id, record_type, name, target)
        return target
    else:
        raise ValueError('DNS record set not found (zone: {}, type: {}, name: {})'.format(zone_id, record_type, name))


def bind(zone_id, dns_name, target):
    logger.info('Binding DNS record (zone: %s, route: %s -> %s)', zone_id, dns_name, target)
    route53.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': dns_name,
                        'Type': 'CNAME',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': target}]
                    }
                }
            ]
        }
    )


def unbind(zone_id, dns_name, target):
    logger.info('Unbinding DNS record (zone: %s, route: %s -> %s)', zone_id, dns_name, target)
    route53.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'DELETE',
                    'ResourceRecordSet': {
                        'Name': dns_name,
                        'Type': 'CNAME',
                        'TTL': 300,
                        'ResourceRecords': [{'Value': target}]
                    }
                }
            ]
        }
    )
