output "wg_server_ip" {
  value = aws_eip.wg_eip.public_ip
}
