"""
Module for interacting with WireGuard keys
"""
from subprocess import check_output


def genkey():
    """ Use wg genkey to create new public and private key"""

    # Private key first
    private_key_bytes = check_output(['wg', 'genkey'])
    # Use generated private key to generate associated public key
    public_key_bytes = check_output(['wg', 'pubkey'], input=private_key_bytes)

    # Convert bytes to string and strip newline
    private_key = private_key_bytes.decode('utf-8').strip('\n')
    public_key = public_key_bytes.decode('utf-8').strip('\n')

    return (private_key, public_key)
