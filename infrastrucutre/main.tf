provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

module "wg_server" {
  source = "./server"
}