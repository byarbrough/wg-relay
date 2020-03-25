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


resource "aws_vpc" "wg_vpc" {
  cidr_block = "10.0.0.0/24"

  tags = {
    Project = "wg-relay"
  }
}


resource "aws_subnet" "wg_subnet" {
  vpc_id            = aws_vpc.wg_vpc.id
  cidr_block        = "10.0.0.0/24"
  availability_zone = var.availability_zone

  tags = {
    Project = "wg-relay"
  }
}


resource "aws_internet_gateway" "wg_gw" {
  vpc_id = aws_vpc.wg_vpc.id

  tags = {
    Project = "wg-relay"
  }
}


resource "aws_route_table" "wg_route_table" {
  vpc_id = aws_vpc.wg_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.wg_gw.id
  }

  tags = {
    Project = "wg-relay"
  }
}

resource "aws_main_route_table_association" "wg_a" {
  vpc_id         = aws_vpc.wg_vpc.id
  route_table_id = aws_route_table.wg_route_table.id
}


# security group for the server
resource "aws_security_group" "sg_wg_server" {
  name        = "WG Relay Server"
  description = "Security group for SSH and wireguard traffic"
  vpc_id      = aws_vpc.wg_vpc.id

  # ssh from whitelisted hosts
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "TCP"
    cidr_blocks = var.allowed_ssh_ips
  }

  # allow wg in
  ingress {
    from_port   = 0
    to_port     = var.wg_port
    protocol    = "UDP"
    cidr_blocks = var.allowed_wg_ips
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
  availability_zone           = var.availability_zone
  key_name                    = aws_key_pair.wg_server_key_pair.key_name
  monitoring                  = true
  associate_public_ip_address = true
  subnet_id                   = aws_subnet.wg_subnet.id
  vpc_security_group_ids      = [aws_security_group.sg_wg_server.id]

  # execute ansible playbooks from the same machine running this terraform
  provisioner "local-exec" {
    command = "ansible-playbook -u ubuntu -i '${self.public_ip},' --private-key ${var.private_key_path} playbooks/wg_server.yml"
  }

  tags = {
    Name    = "Wireguard Relay Server"
    Project = "wg-relay"
  }
}


resource "aws_eip" "wg_eip" {
  vpc                       = true
  instance                  = aws_instance.wg_server.id
  associate_with_private_ip = aws_instance.wg_server.private_ip
  depends_on                = [aws_internet_gateway.wg_gw]
}
