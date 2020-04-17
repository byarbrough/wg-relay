"""
Module for interacting with WireGuard keys
"""
from subprocess import check_output
from subprocess import CalledProcessError


def genkey():
    """ Use wg genkey to create new public and private key """

    # Private key first
    private_key_bytes = check_output(['wg', 'genkey'])
    # Use generated private key to generate associated public key
    public_key_bytes = check_output(['wg', 'pubkey'], input=private_key_bytes)

    # Convert bytes to string and strip newline
    private_key = private_key_bytes.decode('utf-8').strip('\n')
    public_key = public_key_bytes.decode('utf-8').strip('\n')

    return (private_key, public_key)


def get_pubkey(private_key):
    """ Retun the wg public key corresponding to input wg private key """

    try:
        priv_key_bytes = private_key.encode('utf-8')
        publ_key_bytes = check_output(['wg', 'pubkey'], input=priv_key_bytes)
        publ_key = publ_key_bytes.decode('utf-8').strip('\n')
    except CalledProcessError:
        raise TypeError('WireGuard public key imporperly formatted.')

    return publ_key
