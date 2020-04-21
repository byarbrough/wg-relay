"""
Create the wireguard server and configuration files
"""
from pathlib import Path
from wg import keys
from ipaddress import ip_address
from ipaddress import ip_network
from itertools import islice
import argparse


# parse args
parser = argparse.ArgumentParser(
    description='Generate WireGuard interface config files')
parser.add_argument('relay_public_ip', type=str,
                    help='The public IP of the wg relay server')
parser.add_argument('relay_listen_port', type=int,
                    help='UDP port listening on WireGuard relay')
parser.add_argument('--subnet', type=str, default='10.37.0.0/24',
                    help='The CIDR notation of wg VPN subnet')
parser.add_argument('--peers', type=int, default='254',
                    help='Number of peer files to generate and add to relay')

args = parser.parse_args()
RELAY_LISTEN_PORT = args.relay_listen_port

# verify relay_public_ip is valid
try:
    RELAY_PUBLIC_IP = ip_address(args.relay_public_ip)
except ValueError:
    raise

# verify subnet is valid and create iterator
try:
    WG_SUBNET = ip_network(args.subnet, strict=True)
    # hosts() returns iterator, then slice the first peers
    wg_peers = islice(WG_SUBNET.hosts(), args.peers)
except ValueError:
    raise


# Generate a new private and pulic key for the relay
(RELAY_PRIVATE_KEY, RELAY_PUBLIC_KEY) = keys.genkey()


PEER_CONF_DIR = Path('../peer/config')  # Path to store peer conf files
PEER_CONF_DIR.mkdir(exist_ok=True)
SERVER_CONF_DIR = Path('../infrastructure/playbooks/files/')
SERVER_CONF_DIR.mkdir(exist_ok=True)

# Format of start of server's wg0.conf
server_new_conf = \
    '''[Interface]
    Address = {relay_ip}/24
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
    AllowedIPs = {SUBNET}
    Endpoint = {RELAY_PUBLIC_IP}:{RELAY_LISTEN_PORT}
    PersistentKeepalive=23
    '''


# Continually append new information to buffer
server_conf_buffer = \
    server_new_conf.format(relay_ip=str(next(wg_peers)),
                           RELAY_LISTEN_PORT=RELAY_LISTEN_PORT,
                           RELAY_PRIVATE_KEY=RELAY_PRIVATE_KEY)

# Server is 'x.x.x.1' so peers get 'x.x.x.2' to 'x.x.x.NUM_PEERS'
for peer in wg_peers:
    # convert from IPv4Address to string
    peer = str(peer)
    # Generate new keys with wireguard
    (peer_private_key, peer_public_key) = keys.genkey()

    # Append new peer to server conf buffer
    server_conf_buffer += \
        server_new_peer.format(peer_public_key=peer_public_key,
                               peer_ip=peer)

    peer_new_conf_buffer = \
        peer_new_conf.format(peer_ip=peer,
                             peer_private_key=peer_private_key,
                             RELAY_PUBLIC_KEY=RELAY_PUBLIC_KEY,
                             SUBNET=WG_SUBNET,
                             RELAY_PUBLIC_IP=RELAY_PUBLIC_IP,
                             RELAY_LISTEN_PORT=RELAY_LISTEN_PORT)

    # New conf file generated for each peer and placed in same directory
    (PEER_CONF_DIR / f"wg_{peer.replace('.', '-')}.conf")\
        .write_text(peer_new_conf_buffer)

# Write full server conf buffer to single file
(SERVER_CONF_DIR / "wg0.conf").write_text(server_conf_buffer)
