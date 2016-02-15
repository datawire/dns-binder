# DNS Binder

An AWS Lambda function that performs DNS binding by listening for auto scaling lifecycle SNS notifications and updating 
Route 53 DNS records as necessary.

## Theory of Operation

The DNS Binder listens to incoming autoscaling lifecycle events and either adds or removes Route53 CName DNS records
based on the event type.

## License