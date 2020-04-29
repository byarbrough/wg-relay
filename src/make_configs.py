"""
Create the wireguard server and configuration files
"""
from datetime import datetime
from pathlib import Path
from wg import confs
from wg import keys
from ipaddress import ip_address
from ipaddress import ip_network
from itertools import islice
import argparse


def main():
    """Generate configuration files for WireGuard Relay and peers"""

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
                        help='Num. peer files to generate and add to relay')
    parser.add_argument('--wgrdir', type=str, default='./config/relay',
                        help='Where to place wg relay conf file')
    parser.add_argument('--peerdir', type=str, default='./config/peer',
                        help='Where to place wg peer conf files')

    # process args and make availale
    args = parser.parse_args()
    wgr_listen_port = args.relay_listen_port
    wgrdir = Path(args.wgrdir)
    peerdir = Path(args.peerdir)

    # check for or create directories for files
    wgrdir.mkdir(parents=True, exist_ok=True)
    peerdir.mkdir(parents=True, exist_ok=True)

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
    (wgr_priv_key, _) = keys.genkey()

    # create the relay object
    wgr = confs.init_wgrelay(wg_subnet, wgr_public_ip,
                             wgr_listen_port, wgr_priv_key)

    # Continually append new information to buffer
    wgr_conf_buffer = confs.new_relay(wgr)

    # Server is 'x.x.x.1' so peers get 'x.x.x.2' to 'x.x.x.NUM_PEERS'
    for peer_ip in wg_peers:

        # Generate new keys with wireguard
        (peer_priv_key, peer_pub_key) = keys.genkey()

        # generate confs
        (new_peer, relay_peer) = confs.new_peer(peer_ip, peer_priv_key, wgr)

        # Append new peer to relay conf buffer
        wgr_conf_buffer += relay_peer

        # New conf file generated for each peer and placed in same directory
        # Replace . in ip with - because random . in filenames are bad
        peerfile = (peerdir / f"wg_{str(peer_ip).replace('.', '-')}.conf")
        # tag the top of the file with datetime
        peerfile.write_text('# Auto generated ' + str(datetime.now()) + '\n')
        # restrict file read/write permissions to this user
        peerfile.chmod(0o600)
        # append the contents of new_peer to file
        with open(peerfile, 'a') as pf:
            pf.write(new_peer)

    # Write full relay conf buffer to single file
    wgrfile = (wgrdir / "wg0.conf")
    # tag the top of the file with datetime
    wgrfile.write_text('# Auto generated ' + str(datetime.now()) + '\n')
    # restric file read/write permissions to this user
    wgrfile.chmod(0o600)
    with open(wgrfile, 'a') as wgrf:
        wgrf.write(wgr_conf_buffer)


if __name__ == "__main__":
    main()
