"""
Test the wg.keys module
"""
from src.wg import keys
import pytest


def test_genkey():
    """ Test keys.genkey()"""

    assert not (keys.genkey() is None)


def test_get_pubkey():
    """ Test keys.get_pubkey()"""

    with pytest.raises(TypeError):
        keys.get_pubkey()

    (privatekey, pubkey) = keys.genkey()
    assert pubkey == keys.get_pubkey(privatekey)
