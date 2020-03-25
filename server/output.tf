output "wg_server_ip" {
  value = aws_instance.wg_server.public_ip
}

output "wg_sg_id" {
  value = aws_security_group.sg_wg_server.id
}