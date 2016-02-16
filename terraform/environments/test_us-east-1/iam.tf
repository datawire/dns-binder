resource "aws_iam_role" "asg_publish_to_sns" {
  name = "asg_publish_to_sns"
  assume_role_policy = "${file("role.json")}"
}

resource "template_file" "asg_publish_to_sns" {
  template = "${file("iam.json")}"
  vars {
    topic_arn = "${var.sns_topic_arn}"
  }
}

resource "aws_iam_role_policy" "asg_publish_to_sns" {
  name = "asg_publish_to_sns"
  role = "${aws_iam_role.asg_publish_to_sns.id}"
  policy = "${template_file.asg_publish_to_sns.rendered}"
}