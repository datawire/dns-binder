// file: environments/test_us-east-1/main.tf

resource "aws_launch_configuration" "test" {
  associate_public_ip_address = true
  enable_monitoring = false
  image_id = "${var.image_id}"
  instance_type = "${var.instance_type}"
  lifecycle {
    create_before_destroy = true
  }
  name_prefix = "dnsbinder-test-"
}

resource "aws_autoscaling_group" "test" {
  force_delete = true
  health_check_grace_period = 30
  health_check_type = "EC2"
  launch_configuration = "${aws_launch_configuration.test.id}"
  lifecycle {
    create_before_destroy = true
  }
  max_size = 1
  min_size = 1
  name = "dnsbinder-test"
  tag {
    key = "DnsConfig"
    value = "${var.dns_config_format}"
    propagate_at_launch = true
  }
  vpc_zone_identifier = ["subnet-e14b96b9"]
}

resource "aws_autoscaling_lifecycle_hook" "launch" {
  name = "${aws_autoscaling_group.test.name}-launching"
  autoscaling_group_name = "${aws_autoscaling_group.test.name}"
  heartbeat_timeout = 60
  lifecycle_transition = "autoscaling:EC2_INSTANCE_LAUNCHING"
  notification_target_arn = "${var.sns_topic_arn}"
  role_arn = "${aws_iam_role.asg_publish_to_sns.arn}"
}

resource "aws_autoscaling_lifecycle_hook" "terminate" {
  name = "${aws_autoscaling_group.test.name}-terminating"
  autoscaling_group_name = "${aws_autoscaling_group.test.name}"
  heartbeat_timeout = 60
  lifecycle_transition = "autoscaling:EC2_INSTANCE_TERMINATING"
  notification_target_arn = "${var.sns_topic_arn}"
  role_arn = "${aws_iam_role.asg_publish_to_sns.arn}"}