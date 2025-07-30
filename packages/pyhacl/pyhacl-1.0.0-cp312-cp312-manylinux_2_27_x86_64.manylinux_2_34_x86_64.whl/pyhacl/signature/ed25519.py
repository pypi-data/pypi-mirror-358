"""Bindings for EdDSA."""

from cython.cimports.libc.stdint import uint8_t

from cython.cimports.pyhacl.signature import ed25519


def secret_to_public(private_key: bytes) -> bytes:
    """
    Calculate a public point from a private key.

    :raises ValueError: When the key has an incorrect length.

    Uses ``Hacl_Ed25519_secret_to_public``.
    """
    if len(private_key) != 32:
        e = "private key must be 32 bytes long"
        raise ValueError(e)
    public_key: uint8_t[32]
    ed25519.Hacl_Ed25519_secret_to_public(public_key, private_key)  # noqa: F821
    return public_key[:32]  # noqa: F821


def sign(private_key: bytes, message: bytes) -> bytes:
    """
    Sign the message.

    :param message: The message (of any length) to be signed.
    :param private_key: The private key that'll sign the message.

    :returns: The 64 bytes signature.

    :raises ValueError: When the key has incorrect length.

    Binding for ``Hacl_Ed25519_sign``.
    """
    if len(private_key) != 32:
        e = "private key must be 32 bytes long"
        raise ValueError(e)
    signature: uint8_t[64]
    ed25519.Hacl_Ed25519_sign(signature, private_key, len(message), message)  # noqa: F821
    return signature[:64]  # noqa: F821


def verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """
    Verify that the signature matches the message.

    :param public_key: The 32-bytes public key used to verify the
        signature.
    :param message: The message for which ``signature`` was computed.
    :param signature: The 64-bytes signature to verify.

    :returns: ``True`` when the signature matches, ``False`` otherwise.

    :raises ValueError: When the key or signature has incorrect length.

    Binding for ``Hacl_Ed25519_verify``.
    """
    if len(public_key) != 32:
        e = "public key must be 32 bytes long"
        raise ValueError(e)
    if len(signature) != 64:
        e = "signature must be 64 bytes long"
        raise ValueError(e)
    return ed25519.Hacl_Ed25519_verify(public_key, len(message), message, signature)
