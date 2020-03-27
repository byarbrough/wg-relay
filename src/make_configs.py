"""
Create the wireguard server and configuration files
"""
from pathlib import Path
from subprocess import check_output
from re import search
import sys


def is_ip(ip):
    """ Use regular expression to verify that argument is an IP"""
    ip_regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\.(
        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\.(
        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\\.(
        25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''

    return search(ip_regex, ip)


def wg_genkey():
    """ Use wg genkey to create new public and private key"""

    # Private key first
    private_key_bytes = check_output(['wg', 'genkey'])
    # Use generated private key to generate associated public key
    public_key_bytes = check_output(['wg', 'pubkey'], input=private_key_bytes)

    # Convert bytes to string and strip newline
    private_key = private_key_bytes.decode('utf-8').strip('\n')
    public_key = public_key_bytes.decode('utf-8').strip('\n')

    return (private_key, public_key)


# verify arguments
if len(sys.argv) != 2:
    raise TypeError('Eaxctly 1 argument required: server public IP address')

if not is_ip(sys.argv[1]):
    raise ValueError('Expected valid ip address, got', sys.argv[1])


# gloabl variables
SERVER_PUBLIC_IP = sys.argv[1]  # Public facing IP of wireguard server
SERVER_PORT = 51820             # UDP port hosting wireguard on server
SUBNET = '10.37.0'              # Base address of CIDR 24 subnet
# For new servers, generate new keys. For existing servers, change this
(SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY) = wg_genkey()


NUM_PEERS = 1  # Number of peers (and conf files generated) max 253
PEER_CONF_DIR = Path('../peer/config')  # Path to store peer conf files
SERVER_CONF_PATH = Path('../infrastructure/playbooks/files/wg0.conf')

# Format of start of server's wg0.conf
server_new_conf = \
    '''[Interface]
    Address = {SUBNET}.1/24
    ListenPort = {SERVER_PORT}
    PrivateKey = {SERVER_PRIVATE_KEY}

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
    Endpoint = {SERVER_PUBLIC_IP}:{SERVER_PORT}
    PersistentKeepalive=23
    '''


# Continually append new information to buffer
server_conf_buffer = \
    server_new_conf.format(SUBNET=SUBNET,
                           SERVER_PORT=SERVER_PORT,
                           SERVER_PRIVATE_KEY=SERVER_PRIVATE_KEY)

# Server is 'x.x.x.1' so peers get 'x.x.x.2' to 'x.x.x.NUM_PEERS'
for i in range(2, NUM_PEERS + 2):
    # IP of new peer being provisioned
    peer_ip = f'{SUBNET}.{str(i)}'
    # Generate new keys with wireguard
    (peer_private_key, peer_public_key) = wg_genkey()

    # Append new peer to server conf buffer
    server_conf_buffer += \
        server_new_peer.format(peer_public_key=peer_public_key,
                               peer_ip=peer_ip)

    peer_new_conf_buffer = \
        peer_new_conf.format(peer_ip=peer_ip,
                             peer_private_key=peer_private_key,
                             server_public_key=SERVER_PUBLIC_KEY,
                             SUBNET=SUBNET,
                             SERVER_PUBLIC_IP=SERVER_PUBLIC_IP,
                             SERVER_PORT=SERVER_PORT)

    # New conf file generated for each peer and placed in same directory
    (PEER_CONF_DIR / f"wg_{peer_ip.replace('.', '-')}.conf")\
        .write_text(peer_new_conf_buffer)

# Write full server conf buffer to single file
SERVER_CONF_PATH.write_text(server_conf_buffer)
