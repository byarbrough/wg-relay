variable public_key_pair {
  type = string
}

variable wg_server_ami {
	type = string
}

variable wg_server_size {
	type = string
	default = "t3.small"
}