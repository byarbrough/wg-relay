/***********************************************
Module for wg_relay server
************************************************/

# ssh key for accessing the relay
resource "aws_key_pair" "wg_relay_key_pair" {
  key_name_prefix = "wg-server-"
  public_key      = var.public_key_pair

  tags = {
    Project = "wg-relay"
  }
}


# the next serveral resources are for networking
resource "aws_vpc" "wg_vpc" {
  cidr_block = var.vpc_subnet

  tags = {
    Project = "wg-relay"
  }
}


resource "aws_subnet" "wg_subnet" {
  vpc_id            = aws_vpc.wg_vpc.id
  cidr_block        = var.vpc_subnet
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
resource "aws_security_group" "sg_wg_relay" {
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
    from_port   = var.wg_port
    to_port     = var.wg_port
    protocol    = "UDP"
    cidr_blocks = var.allowed_wg_ips
  }

  # allow dns out
  egress {
    from_port   = 53
    to_port     = 53
    protocol    = "UDP"
    cidr_blocks = ["8.8.8.8/32", "1.1.1.1/32"]
  }

  # allow http out
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # allow https out
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = "wg-relay"
  }
}


# elastic ip address
resource "aws_eip" "wg_eip" {
  vpc = true

  tags = {
    Project = "wg-relay"
  }
}


# the server itself
resource "aws_instance" "wg_relay" {
  ami                         = var.wg_relay_ami
  instance_type               = var.wg_relay_size
  availability_zone           = var.availability_zone
  key_name                    = aws_key_pair.wg_relay_key_pair.key_name
  monitoring                  = true
  associate_public_ip_address = true
  subnet_id                   = aws_subnet.wg_subnet.id
  vpc_security_group_ids      = [aws_security_group.sg_wg_relay.id]

  # generate wireguard key files
  provisioner "local-exec" {
    # use eip that will be associated after creation
    command = "python3 ../src/make_configs.py ${aws_eip.wg_eip.public_ip}"
  }

  # execute ansible playbooks
  provisioner "local-exec" {
    # use current public ip becuase eip is not associated yet
    command = <<EOC
              "ansible-playbook -u ubuntu -i '${self.public_ip},' \
              --private-key ${var.private_key_path} \
              playbooks/wg_relay.yml"
              EOC
  }

  tags = {
    Name    = "Wireguard Relay Server"
    Project = "wg-relay"
  }
}


# associate the elastic ip with the ec2 instance
resource "aws_eip_association" "wg_relay_eip" {
  instance_id   = aws_instance.wg_relay.id
  allocation_id = aws_eip.wg_eip.id
}
