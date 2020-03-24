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