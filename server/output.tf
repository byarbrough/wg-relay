output "wg_server_ip" {
  value = aws_instance.wg_server.public_ip
}