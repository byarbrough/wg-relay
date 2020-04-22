"""
Test the wg.confs module
"""
from ipaddress import ip_network
from ipaddress import ip_address
from src.wg import confs
import pytest


def test_get_cidr():
    """Test confs.get_cidr()"""

    net = ip_network('192.168.0.0/30')
    assert confs.get_cidr(net) == 30

    net = ip_network('10.13.0.0/24')
    assert confs.get_cidr(net) == 24

    net = ip_network('172.14.0.0/16')
    assert confs.get_cidr(net) == 16

    net = '192.168.1.0/24'
    assert confs.get_cidr(net) == 24

    # bad IP address
    with pytest.raises(ValueError):
        confs.get_cidr('192.168.0.0/48')


def test_new_relay():
    """Test conf.new_relay()"""

    net = ip_network('172.20.0.0/16')
    public_ip = ip_address('65.73.48.2')
    listen_port = 7532
    relay_private_key = 'ICCdVYBjzJn+flYk3v8+o+LUkfeinO/hLK9G6AIg7UU='

    relay = confs.init_wgrelay(net, public_ip, listen_port, relay_private_key)

    expected = \
        '''[Interface]
Address = 172.20.0.1/16
ListenPort = 7532
PrivateKey = ICCdVYBjzJn+flYk3v8+o+LUkfeinO/hLK9G6AIg7UU=
'''
    assert confs.new_relay(relay) == expected


def test_relay_class():
    """Test the creation of a confs Relay object"""
    net = ip_network('10.13.0.0/24')
    public_ip = ip_address('1.2.3.4')
    listen_port = 51820
    wg_private_key = 'yNEoiTM24mAaJ6jyRbUCfScazt1lJAhTUb5wdR1R1Vc='

    wgr = confs.init_wgrelay(net, public_ip, listen_port, wg_private_key)

    assert wgr.wg_ip == ip_address('10.13.0.1')
    assert wgr.wg_subnet == net
    assert wgr.wg_cidr == 24
    assert wgr.public_ip == public_ip
    assert wgr.listen_port == listen_port
    assert wgr.wg_private_key == wg_private_key
    assert wgr.wg_public_key == 'jCWSoP7TYPcgTKS2GJ3P9c1YKDcEGFwLiS0yo/HRJmI='
