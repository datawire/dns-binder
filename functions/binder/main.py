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

import csv
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

autoscaling = boto3.client('autoscaling')
route53 = boto3.client('route53')


def handle(event, context):
    logger.info("%s - %s", event, context)

    # asg_msg = json.loads(event['Records'][0]['Sns']['Message'])
    # asg_name = asg_msg['AutoScalingGroupName']
    # event_type = asg_msg['Event']
    # instance = asg_msg['EC2InstanceId']
    #
    # group = get_auto_scaling_group(asg_msg)
    # config_idx = next(index for (index, d) in enumerate(group['Tags']) if d["key"] == "DnsConfig")
    # config = parse_dns_binder_tag(group['Tags'][config_idx])
    #
    # if event_type == "autoscaling:EC2_INSTANCE_LAUNCH":
    #     pass
    # elif event_type == "autoscaling:EC2_INSTANCE_TERMINATE":
    #     pass
    # else:
    #     logger.info("unsupported autoscaling event (type: %s)", event_type)
    #
    # return event


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

    return location[0:1] + short_qualifier[qualifier] + index


def create_subdomain(prefix, short_region_id, instance_id, domain):
    return prefix + "-" + short_region_id + "-" + instance_id + "." + domain


def parse_dns_binder_tag(value):

    """Parse the value of the 'DnsBinder' tag.

    The format of the value of the tag is <key>=<value>[;<key>=<value>]...

    Supported keys are:

    'z'  - The hosted zone ID that should be updated.
    'pr' - The prefix to append onto the ID.

    :param value:
    :return:
    """

    return dict(csv.reader([item], delimiter='=', quotechar="'").next()
                for item in csv.reader([value], delimiter=';', quotechar="'").next())


def get_auto_scaling_group(group_name):
    response = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[group_name], MaxRecords=1)
    return response['AutoScalingGroups'][0]


def bind(instance_id, aws_dns_name):
    pass


def unbind(instance_id):
    pass


def id_to_subdomain(instance_id):
    return str(instance_id).replace("i-", "disco-")
