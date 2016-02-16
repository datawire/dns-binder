# Datawire DNS Binder

An AWS Lambda function that performs DNS binding by listening for auto scaling lifecycle SNS notifications and updating Route 53 DNS records as necessary.

## Theory of Operation

The DNS Binder listens to incoming autoscaling lifecycle events and either adds or removes Route 53 DNS records based on the event type.

## How to use

Add a tag named DnsConfig to the auto scaling group. The tag should be configured to propogate at launch to any launched EC2 instances. The DnsConfig tag values must follow the format of <key>=<value>[;<key>=<value> ...]. The following options are supported:

| Option |   Description   | Expected Value                                                           |
|--------|-----------------|------------------------------------------------------------------------- |
|   z    | Hosted Zone ID  | The Route 53 Hosted Zone ID for the domain that will be modified.        |
|   f    | Format          | The "format" of the resulting ID. See the formatting table for variables | 

### Formatting Rules

Formatting rules are specified by surrounding the rule in { } braces. 

| Rule | Description                      |
|------|----------------------------------|
|  id  | instance-id (the i- is stripped) |
|  re  | region ID                        |
|  sr  | short-region ID                  |

The format of a short region ID is:

`<first two chars of region ID><short region qualifier (see below)><number>`

The short region qualifier is mapped as such:

| Full Qualifier | Short Qualifier |
|----------------|-----------------|
| north          | n               |
| northeast      | ne              |
| northwest      | nw              |
| east           | e               |
| west           | w               |
| south          | s               |
| southeast      | se              |
| southwest      | sw              |
| central        | c               |

Examples:

1. `us-east-1` -> `use1`
2. `ap-northeast-2` -> `apne2`

### Examples

Given an EC2 instance with a Public Dns name and DnsConfig entry similar to below:

| Property        | Value                                    |
|-----------------|------------------------------------------|
| Instance ID     | i-407ae6d8                               |
| Public DNS Name | ec2-52-88-89-200.compute-1.amazonaws.com |
| tag:DnsConfig   | z=Z34ILYZ77N8APC;f=foobar-{sr}-{id};t=c  |

DnsConfig would generate a CName record like that did this `foobar-usw2-407ae6d8.example.com -> ec2-52-88-89-200.compute-1.amazonaws.com`

The "usw2" part indicates the region and is used to ensure globally unique record names since instance ID's are not gauranteed to be unique across regions. The value of that middle part changes based on the region the instance is located in.

## License

Datawire DNS Binder is open-source software licensed under **Apache 2.0**. Please see [LICENSE](LICENSE) for further details.