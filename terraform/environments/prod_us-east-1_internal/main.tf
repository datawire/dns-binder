// file: environments/dev_us-east-1_dwc/main.tf

module "iam" {
  source = "../../modules/iam"
}

module "sns" {
  source = "../../modules/sns"
  name = "${var.environment}-${var.label}-scaling-notifications"
}