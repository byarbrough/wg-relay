variable "public_key_pair" {
  type = string
}

variable "availability_zone" {
  type = string
}

variable "allowed_ssh_ips" {
  # whitelist of CIDR block for ssh
  type = list(string)
}

variable "wg_server_size" {
  type    = string
  default = "t3.micro"
}

variable "wg_server_ami" {
  type    = string
  default = "ami-01cd5988241256cd8" # ubuntu-eoan-19.10-amd64-minimal-20200317
}

variable "private_key_path" {
  type = string
}