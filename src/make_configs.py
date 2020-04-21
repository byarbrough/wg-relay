"""
Create the wireguard server and configuration files
"""
from pathlib import Path
from wg import keys
from ipaddress import ip_address
from ipaddress import ip_network
import argparse


# parse args
parser = argparse.ArgumentParser(
    description='Generate WireGuard interface config files')
parser.add_argument('relay_public_ip', type=str,
                    help='The public IP of the wg relay server')
parser.add_argument('relay_listen_port', type=int,
                    help='UDP port listening on WireGuard relay')
parser.add_argument('--wg_subnet', type=str, default='10.37.0.0/24',
                    help='The CIDR notation of wg VPN subnet')

args = parser.parse_args()
relay_listen_port = args.relay_listen_port

# verify relay_public_ip is valid
try:
    relay_public_ip = ip_address(args.relay_public_ip)
except ValueError:
    raise

# verify subnet is valid
try:
    wg_subnet = ip_network(args.wg_subnet, strict=True)
except ValueError:
    raise


# Generate a new private and pulic key for the relay
(RELAY_PRIVATE_KEY, RELAY_PUBLIC_KEY) = keys.genkey()


NUM_PEERS = 2  # Number of peers (and conf files generated) max 253
PEER_CONF_DIR = Path('../peer/config')  # Path to store peer conf files
PEER_CONF_DIR.mkdir(exist_ok=True)
SERVER_CONF_DIR = Path('../infrastructure/playbooks/files/')
SERVER_CONF_DIR.mkdir(exist_ok=True)

# Format of start of server's wg0.conf
server_new_conf = \
    '''[Interface]
    Address = {SUBNET}.1/24
    ListenPort = {RELAY_LISTEN_PORT}
    PrivateKey = {RELAY_PRIVATE_KEY}

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
    PublicKey = {RELAY_PUBLIC_KEY}
    AllowedIPs = {SUBNET}.0/24
    Endpoint = {RELAY_PUBLIC_IP}:{RELAY_LISTEN_PORT}
    PersistentKeepalive=23
    '''


# Continually append new information to buffer
server_conf_buffer = \
    server_new_conf.format(SUBNET=wg_subnet,
                           RELAY_LISTEN_PORT=relay_listen_port,
                           RELAY_PRIVATE_KEY=RELAY_PRIVATE_KEY)

# Server is 'x.x.x.1' so peers get 'x.x.x.2' to 'x.x.x.NUM_PEERS'
for i in range(2, NUM_PEERS + 2):
    # IP of new peer being provisioned
    peer_ip = f'{wg_subnet}.{str(i)}'
    # Generate new keys with wireguard
    (peer_private_key, peer_public_key) = keys.genkey()

    # Append new peer to server conf buffer
    server_conf_buffer += \
        server_new_peer.format(peer_public_key=peer_public_key,
                               peer_ip=peer_ip)

    peer_new_conf_buffer = \
        peer_new_conf.format(peer_ip=peer_ip,
                             peer_private_key=peer_private_key,
                             RELAY_PUBLIC_KEY=RELAY_PUBLIC_KEY,
                             SUBNET=wg_subnet,
                             RELAY_PUBLIC_IP=relay_public_ip,
                             RELAY_LISTEN_PORT=relay_listen_port)

    # New conf file generated for each peer and placed in same directory
    (PEER_CONF_DIR / f"wg_{peer_ip.replace('.', '-')}.conf")\
        .write_text(peer_new_conf_buffer)

# Write full server conf buffer to single file
(SERVER_CONF_DIR / "wg0.conf").write_text(server_conf_buffer)
