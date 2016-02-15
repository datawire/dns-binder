// file: modules/sns/outputs.tf

output "scaling_notifications_role_arn" {
  value = "${aws_sns_topic.scaling_notifications.arn}"
}

output "scaling_notifications_role_id" {
  value = "${aws_sns_topic.scaling_notifications.id}"
}