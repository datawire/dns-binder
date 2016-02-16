output "dns_binder_role_arn" {
  value = "${module.iam.lambda_function_role_arn}"
}

output "dns_binder_topic_arn" {
  value = "${aws_sns_topic.dns_binder.arn}"
}