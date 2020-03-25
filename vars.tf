variable aws_region {
  type    = string
  default = "us-east-1"
}

variable aws_profile {
  type = string
}

# server module
variable "public_key_pair" {
  type = string
}

variable "allowed_ssh_ips" {
  # whitelist of CIDR block for ssh
  type = list(string)
}

variable "availability_zone" {
  type    = string
  default = "us-east-1a"
}