"""
Bindings for x25519.

.. hint::

    curve25519 has been designed so all points on the curve have the
    desired security properties. This makes picking a point (i.e.
    generating a private key) using ``secrets.token_bytes(32)`` (or
    ``os.urandom(32)``) easy, safe and recommended.
"""

from cython.cimports.libc.stdint import uint8_t

from cython.cimports.pyhacl.diffie_hellman import curve25519
from pyhacl import HACLError


def scalarmult(private_key: bytes, public_key: bytes) -> bytes:
    """
    Compute the scalar multiple of a point. It returns the resulting
    point encoded in 32 bytes.

    :raises ValueError: When any key has an incorrect length.

    Uses ``Hacl_Curve25519_51_scalarmult``.
    """
    if len(private_key) != 32:
        e = "private_key must be 32 bytes long"
        raise ValueError(e)
    if len(public_key) != 32:
        e = "public_key must be 32 bytes long"
        raise ValueError(e)
    point: uint8_t[32]
    curve25519.Hacl_Curve25519_51_scalarmult(
        point,  # noqa: F821
        private_key,
        public_key,
    )
    return point[:32]  # noqa: F821


def secret_to_public(private_key: bytes) -> bytes:
    """
    Calculate a public point from a private key.

    :raises ValueError: When the key has an incorrect length.

    Uses ``Hacl_Curve25519_51_secret_to_public``.
    """
    if len(private_key) != 32:
        e = "private must be 32 bytes long"
        raise ValueError(e)
    public_key: uint8_t[32]
    curve25519.Hacl_Curve25519_51_secret_to_public(public_key, private_key)  # noqa: F821
    return public_key[:32]  # noqa: F821


def ecdh(private_key: bytes, public_key: bytes) -> bytes:
    """
    Given our 32-bytes private key, and the 32-bytes public key of a
    peer, compute and return a third 32-bytes key. The peer is also
    capable of computing this same secret key given our public key and
    their private key.

    :param private_key: Our private key, as a 32 bytes point.
    :param public_key: Their public key, as a 32 bytes point.

    :raises ValueError: When any key has an incorrect length.

    Uses ``Hacl_Curve25519_51_ecdh``.
    """
    if len(private_key) != 32:
        e = "private_key must be 32 bytes long"
        raise ValueError(e)
    if len(public_key) != 32:
        e = "public_key must be 32 bytes long"
        raise ValueError(e)
    shared_key: uint8_t[32]
    ok: bool = curve25519.Hacl_Curve25519_51_ecdh(
        shared_key,  # noqa: F821
        private_key,
        public_key,
    )
    if not ok:
        e = "creation of a shared key failed"
        raise HACLError(e)
    return shared_key[:32]  # noqa: F821
