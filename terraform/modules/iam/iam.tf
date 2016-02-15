// file: modules/iam/iam.tf

resource "aws_iam_role" "lambda_function" {
  name = "lambda_function"
  assume_role_policy = "${file("${path.module}/role.json")}"
}

resource "aws_iam_role_policy" "cloudwatchlogs_full_access" {
  name = "cloudwatchlogs_full_access"
  role = "${aws_iam_role.lambda_function.id}"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}