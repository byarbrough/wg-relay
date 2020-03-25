/***********************************************
Module for wireguard server to serve as a relay
************************************************/

# ssh key for accessing the server
resource "aws_key_pair" "wg_server_key_pair" {
  key_name_prefix = "wg-server-"
  public_key      = var.public_key_pair
}

# the server itself
resource "aws_instance" "wg_server" {
  ami                         = "ami-0682ababa71304573"  # ubuntu-eoan-19.10-amd64-minimal-20191
  instance_type               = var.wg_server_size
  key_name                    = aws_key_pair.wg_server_key_pair.key_name
  monitoring                  = true
  associate_public_ip_address = true
  tags = {
    Name    = "Wireguard Relay Server"
    Project = "wg-relay"
  }
}