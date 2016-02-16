// file: environments/dev_us-east-1_dwc/main.tf

resource "terraform_remote_state" "prod" {
  backend = "s3"
  config = {
    bucket = "d6e-terraform-state"
    key = "prod_us-east-1_internal/dns-binder"
    region = "us-east-1"
    encrypt = 1
  }
}

resource "aws_sns_topic" "dns_binder" {
  name = "${var.environment}-${var.label}-dns-binder"}

module "iam" {
  source = "../../modules/iam"
  name = "dns-binder"
}