"""
Test the wg.keys module
"""
from src.wg import keys
import pytest


def test_genkey():
    """ Test keys.genkey()"""

    # key formats
    (prikey, pubkey) = keys.genkey()
    assert prikey.endswith('=')
    assert pubkey.endswith('=')
    assert len(prikey) == 44
    assert len(pubkey) == 44

    # private key and public key correspond
    (prikey, pubkey) = keys.genkey()
    assert pubkey == keys.get_pubkey(prikey)


def test_get_pubkey():
    """ Test keys.get_pubkey()"""

    assert (keys.get_pubkey('ED7uksvEWsxPPLJMtXOKkPxiQPAyvwCC6qk9iNGGo2c=') ==
            'XEcj0j+6cpNMOqYIElNpa2y5FnMAU/Kd3RKl9k9jBgo=')

    assert (keys.get_pubkey('0E3nMgLKffidthZ+/EF8YGXEnp6zXhioNcEfJgEuOE4=') ==
            '2tijhAeR+PU/Db7HF/+FimiQ/k/rkBnGGtcmLKf3mBI=')


def test_durable_get_pubkey():
    """ Test bad inputs for keys.get_pubkey()"""

    # empty
    with pytest.raises(TypeError):
        keys.get_pubkey()

    # bad input
    with pytest.raises(TypeError):
        keys.get_pubkey('dQw4w9WgXcQ')

    with pytest.raises(TypeError):
        keys.get_pubkey('");#')
