// file: environments/test_us-east-1/variables.tf

variable "environment" {
  description = "the operational environment of the active deployment"
}

variable "dns_config_format" {
  description = "the format string that the dns-binder lambda can process"
}

variable "image_id" {
  description = "the AMI ID used for instances in the test auto scaling group"
}

variable "instance_type" {
  description = "the EC2 instance type to use for test auto scaling group instances"
}

variable "label" {
  description = "A special label to apply to the deployed infrastructure"
}

variable "sns_topic_arn" {
  description = "the ARN of the SNS topic where lifecycle notifications should be delivered"
}