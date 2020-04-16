#### wg_relay ####

output "wg_relay_ip" {
  value = aws_eip.wg_eip.public_ip
}
