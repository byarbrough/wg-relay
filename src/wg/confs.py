"""
Module for generating WireGuard interface configuration files
"""
from ipaddress import IPv4Network


def get_cidr(network):
	"""Helper function to convert netmask to CIDR"""
	netmask = str(network.netmask)
	return sum(bin(int(x)).count('1') for x in netmask.split('.'))
