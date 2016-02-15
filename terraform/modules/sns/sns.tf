// file: modules/sns/sns.tf

resource "aws_sns_topic" "scaling_notifications" {
  name = "${var.name}"
}