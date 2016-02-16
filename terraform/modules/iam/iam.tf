// file: modules/iam/iam.tf

resource "aws_iam_role" "lambda_function" {
  name = "${var.name}"
  assume_role_policy = "${file("${path.module}/role.json")}"
}

resource "aws_iam_role_policy" "dns_binder" {
  name = "${var.name}"
  role = "${aws_iam_role.lambda_function.id}"
  policy = "${file("${path.module}/iam.json")}"
}