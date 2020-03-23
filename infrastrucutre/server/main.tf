/***********************************************
Module for wireguard server to serve as a relay
************************************************/

resource "aws_key_pair" "wg_server_key_pair" {
  key_name_prefix = "wg-server-"
  public_key      = var.public_key_pair
}