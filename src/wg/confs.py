"""
Module for generating WireGuard interface configuration files
"""
from ipaddress import IPv4Network
from ipaddress import IPv4Address
from ipaddress import ip_network
from .keys import get_pubkey


def get_cidr(network):
    """Helper function to convert netmask to CIDR"""

    # convert to IPv4Network if not already
    network = IPv4Network(network)
    netmask = str(network.netmask)
    # add up the bits
    return sum(bin(int(x)).count('1') for x in netmask.split('.'))


def new_relay(relay):
    """Return conf for relay"""

    new_relay_fmt = \
        '''[Interface]
Address = {RELAY_IP}/{CIDR}
ListenPort = {RELAY_LISTEN_PORT}
PrivateKey = {RELAY_PRIVATE_KEY}
'''
    return new_relay_fmt.format(RELAY_IP=relay.wg_ip,
                                CIDR=relay.wg_cidr,
                                RELAY_LISTEN_PORT=relay.listen_port,
                                RELAY_PRIVATE_KEY=relay.wg_private_key)


def new_peer(peer_ip, peer_priv_key, relay):
    """Create a new peer configuration"""

    # layout for text
    relay_peer_fmt = \
        '''[Peer]
PublicKey = {PEER_PUB_KEY}
AllowedIPs = {PEER_IP}/32

'''

    new_peer_fmt = \
        '''[Interface]
Address = {PEER_IP}/{CIDR}
PrivateKey = {PEER_PRIVATE_KEY}

[Peer]
PublicKey = {RELAY_PUBLIC_KEY}
AllowedIPs = {SUBNET}
Endpoint = {RELAY_PUBLIC_IP}:{RELAY_LISTEN_PORT}
PersistentKeepalive=23
'''

    # format the new peer
    new_peer = new_peer_fmt.format(PEER_IP=peer_ip,
                                   CIDR=relay.wg_cidr,
                                   PEER_PRIVATE_KEY=peer_priv_key,
                                   RELAY_PUBLIC_KEY=relay.wg_public_key,
                                   SUBNET=relay.wg_subnet,
                                   RELAY_PUBLIC_IP=relay.public_ip,
                                   RELAY_LISTEN_PORT=relay.listen_port)

    # format the addition to relay configuration
    relay_peer = relay_peer_fmt.format(PEER_PUB_KEY=get_pubkey(peer_priv_key),
                                       PEER_IP=peer_ip)

    return (new_peer, relay_peer)


class WgRelay(object):
    """WireGuard Relay Object"""

    wg_ip = IPv4Address
    wg_subnet = IPv4Network
    wg_cidr = 0
    public_ip = IPv4Network
    listen_port = 0
    wg_private_key = ''
    wg_public_key = ''

    def __init__(self, wg_subnet, public_ip, listen_port, wg_private_key):
        """Initialize the class"""
        self.wg_ip = next(wg_subnet.hosts())  # first host on subnet
        self.wg_subnet = ip_network(wg_subnet)
        self.wg_cidr = get_cidr(wg_subnet)
        self.public_ip = public_ip
        self.listen_port = listen_port
        self.wg_private_key = wg_private_key
        self.wg_public_key = get_pubkey(wg_private_key)


def init_wgrelay(wg_subnet, public_ip, listen_port, wg_private_key):
    """Create a relay"""
    wgr = WgRelay(wg_subnet, public_ip, listen_port, wg_private_key)
    return wgr
