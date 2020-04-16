provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

module "wg_relay" {
  source            = "./relay"
  public_key_pair   = var.public_key_pair
  allowed_ssh_ips   = var.allowed_ssh_ips
  allowed_wg_ips    = var.allowed_wg_ips
  wg_port           = var.wg_port
  availability_zone = var.availability_zone
  private_key_path  = var.private_key_path
}