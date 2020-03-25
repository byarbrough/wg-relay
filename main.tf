provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

module "wg_server" {
  source            = "./server"
  public_key_pair   = var.public_key_pair
  allowed_ssh_ips   = var.allowed_ssh_ips
  availability_zone = var.availability_zone
}