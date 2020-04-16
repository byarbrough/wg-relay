variable aws_profile {
  type = string
}

variable aws_region {
  type    = string
  default = "us-east-1"
}


#### wg_relay module ####

variable "allowed_ssh_ips" {
  # whitelist of CIDR block for ssh
  type    = list(string)
  default = ["0.0.0.0/0"]
}

variable "allowed_wg_ips" {
  # whitelist of CIDR block for wg peer
  type    = list(string)
  default = ["0.0.0.0/0"]
}

variable "availability_zone" {
  type    = string
  default = "us-east-1a"
}

variable "public_key_pair" {
  type = string
}

variable "private_key_path" {
  type = string
}

variable "wg_port" {
  type    = number
  default = 51820
}
