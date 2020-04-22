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

    relay_ip = ip_address('10.37.0.1')
    cidr = 24
    relay_listen_port = 51820
    relay_private_key = 'ICCdVYBjzJn+flYk3v8+o+LUkfeinO/hLK9G6AIg7UU='
    expected = \
        '''[Interface]
Address = 10.37.0.1/24
ListenPort = 51820
PrivateKey = ICCdVYBjzJn+flYk3v8+o+LUkfeinO/hLK9G6AIg7UU=
'''
    assert confs.new_relay(relay_ip, cidr,
                           relay_listen_port,
                           relay_private_key) == expected
