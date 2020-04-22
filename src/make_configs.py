"""
Create the wireguard server and configuration files
"""
from pathlib import Path
from wg import confs
from wg import keys
from ipaddress import ip_address
from ipaddress import ip_network
from itertools import islice
import argparse


PEER_CONF_DIR = Path('../peer/config')  # Path to store peer conf files
PEER_CONF_DIR.mkdir(exist_ok=True)
SERVER_CONF_DIR = Path('../infrastructure/playbooks/files/')
SERVER_CONF_DIR.mkdir(exist_ok=True)


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
wgr_listen_port = args.relay_listen_port

# verify relay_public_ip is valid
try:
    wgr_public_ip = ip_address(args.relay_public_ip)
except ValueError:
    raise

# verify subnet is valid and create iterator
try:
    wg_subnet = ip_network(args.subnet, strict=True)
    # hosts() returns iterator, then slice the first peers
    wg_peers = islice(wg_subnet.hosts(), args.peers)
except ValueError:
    raise


# Generate a new private and pulic key for the relay
(wgr_priv_key, wgr_pub_key) = keys.genkey()

# create the relay object
wgr = confs.init_wgrelay(wg_subnet, wgr_public_ip,
                         wgr_listen_port, wgr_priv_key)

# Continually append new information to buffer
server_conf_buffer = confs.new_relay(wgr)

# Server is 'x.x.x.1' so peers get 'x.x.x.2' to 'x.x.x.NUM_PEERS'
for peer_ip in wg_peers:

    # Generate new keys with wireguard
    (peer_priv_key, peer_pub_key) = keys.genkey()

    # generate confs
    (new_peer, relay_peer) = confs.new_peer(peer_ip, peer_priv_key, wgr)

    # Append new peer to server conf buffer
    server_conf_buffer += relay_peer

    # New conf file generated for each peer and placed in same directory
    (PEER_CONF_DIR / f"wg_{peer_ip.replace('.', '-')}.conf")\
        .write_text(new_peer)

# Write full server conf buffer to single file
(SERVER_CONF_DIR / "wg0.conf").write_text(server_conf_buffer)
