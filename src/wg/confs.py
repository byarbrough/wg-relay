"""
Module for generating WireGuard interface configuration files
"""
from ipaddress import IPv4Network


def get_cidr(network):
    """Helper function to convert netmask to CIDR"""

    # convert to IPv4Network if not already
    network = IPv4Network(network)
    netmask = str(network.netmask)
    # add up the bits
    return sum(bin(int(x)).count('1') for x in netmask.split('.'))


def new_relay(relay_ip, cidr, relay_listen_port, relay_private_key):
    """Return conf for relay"""

    new_relay_fmt = \
        '''[Interface]
Address = {RELAY_IP}/{CIDR}
ListenPort = {RELAY_LISTEN_PORT}
PrivateKey = {RELAY_PRIVATE_KEY}
'''
    return new_relay_fmt.format(RELAY_IP=relay_ip,
                                CIDR=cidr,
                                RELAY_LISTEN_PORT=relay_listen_port,
                                RELAY_PRIVATE_KEY=relay_private_key)
