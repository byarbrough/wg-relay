/***********************************************
Module for wireguard server to serve as a relay
************************************************/

# ssh key for accessing the server
resource "aws_key_pair" "wg_server_key_pair" {
  key_name_prefix = "wg-server-"
  public_key      = var.public_key_pair
  tags = {
    Project = "wg-relay"
  }
}




# security group for the server
resource "aws_security_group" "sg_wg_server" {
  name        = "WG Relay Server"
  description = "Security group for SSH and wireguard traffic"

  # ssh from whitelisted hosts
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "TCP"
    cidr_blocks = [var.allowed_ssh_ips] # TODO: figure out escaping for tfvars so can be true list
  }

  # allow anything out
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Project = "wg-relay"
  }
}


# the server itself
resource "aws_instance" "wg_server" {
  ami                         = var.wg_server_ami
  instance_type               = var.wg_server_size
  key_name                    = aws_key_pair.wg_server_key_pair.key_name
  monitoring                  = true
  associate_public_ip_address = true
  security_groups             = [aws_security_group.sg_wg_server.id]
  tags = {
    Name    = "Wireguard Relay Server"
    Project = "wg-relay"
  }
}