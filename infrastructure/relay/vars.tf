#### wg_relay ####

variable "allowed_ssh_ips" {
  # whitelist of CIDR block for ssh
  type = list(string)
}

variable "allowed_wg_ips" {
  # whitelist of CIDR block for wg peer
  type = list(string)
}

variable "availability_zone" {
  type = string
}

variable "private_key_path" {
  type = string
}

variable "public_key_pair" {
  type = string
}

variable "vpc_subnet" {
  type    = string
  default = "10.0.0.0/24"
}

variable "wg_port" {
  type = number
}

variable "wg_relay_ami" {
  type    = string
  default = "ami-01cd5988241256cd8" # ubuntu-eoan-19.10-amd64-minimal-20200317
}

variable "wg_relay_size" {
  type    = string
  default = "t3.micro"
}
