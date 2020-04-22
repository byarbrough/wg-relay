"""
Test the wg.confs module
"""
from ipaddress import ip_network
from src.wg import confs


def test_get_cidr():
    """ Test confs.get_cidr()"""

    net = ip_network('192.168.0.0/30')
    assert confs.get_cidr(net) == 30
