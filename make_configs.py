"""
Create the wireguard server and configuration files
"""
from re import search
import sys


def is_ip(ip):
    """ Use regular expression to verify that argument is an IP"""
    ip_regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\.(
        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\.(
        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\.(
        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''

    return search(ip_regex, ip)


# verify arguments
if len(sys.argv) != 2:
    raise TypeError('Eaxctly 1 argument required: server public IP address')

if not is_ip(sys.argv[1]):
    raise ValueError('Expected valid ip address, got', sys.argv[1])


# gloabl variables
SERVER_ADDRESS = sys.argv[1] 	# Public facing IP of wireguard server
SERVER_PORT = 51820				# UDP port hosting wireguard on server
SUBNET = '10.37.0'				# Base address of CIDR 24 subnet


# Format of start of server's wg0.conf
server_new_conf = \
    '''[Peer]
    Address = {SUBNET}.1/24
    ListenPort = {SERVER_PORT}
    PrivateKey = {server_private_key}

    '''

# Format of info to append to server's wg0.conf
server_new_peer = \
    '''[Peer]
    PublicKey = {peer_public_key}
    AllowedIPs = {peer_ip}/32

    '''

# Format of info for peer's wg0.conf
peer_new_conf = \
    '''[Interface]
    Address = {peer_ip}/24
    PrivateKey = {peer_private_key}

    [Peer]
    PublicKey = {server_public_key}
    AllowedIPs = {SUBNET}.0/24
    Endpoint = {SERVER_ADDRESS}:{SERVER_PORT}
    PersistentKeepalive=23
    '''
