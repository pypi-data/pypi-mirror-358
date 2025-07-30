"""
Bindings for the portable (any platform that is 32-bits or higher)
implementation of chacha-poly1305.

.. danger::

    The nonce **MUST** be unique per invocation with the same key and
    **MUST NOT** be predicable. Failure to meet those two requirements
    makes it trivial to find the key.

    The nonce **CANNOT** be random, as there is not enough entropy in 12
    bytes to guarantee uniqueness. It **CANNOT** be a counter as it
    would be predicable.

    :rfc:`7539` gives guidance to safely generate nonces for
    chacha-poly1305. :class:`pyhacl.drbg.DRBGRandom` can be used too,
    albeit slow.
"""

from typing import NamedTuple

import cython
from cython.cimports.libc.stdint import uint8_t, uint32_t
from cython.cimports.libc.stdlib import free, malloc

from cython.cimports.pyhacl.aead import chacha_poly1305
from pyhacl import HACLError


class _EncryptReturn(NamedTuple):
    """The return type of :func:`encrypt`."""

    output: bytes
    tag: bytes


def encrypt(input_: bytes, data: bytes, key: bytes, nonce: bytes) -> _EncryptReturn:
    """
    Encrypt ``input_`` and produce an authenticated tag over ``data``.

    :param input_: The plain text to be enciphered.
    :param data: The associated data for which an authenticated tag is
        computed.
    :param key: The 32 bytes private key.
    :param nonce: A unique and unpredictable 12 bytes nonce. See
        :rfc:`7538` for guidance.

    :returns: a 2-items named tuple with:

        output (bytes, index 0)
            The encrypted output of same length as the input.

        tag (bytes, index 1)
            The 16 bytes authenticated tag.

    :raises ValueError: When the key or nonce has incorrect length.

    Binding for ``Hacl_AEAD_Chacha20Poly1305_encrypt``.
    """
    if len(key) != 32:
        e = "key must be 32 bytes long"
        raise ValueError(e)
    if len(nonce) != 12:
        e = "nonce must be 12 bytes long"
        raise ValueError(e)
    output: cython.pointer(uint8_t) = cython.cast(
        cython.pointer(uint8_t), malloc(len(input_))
    )
    if output is cython.NULL:
        raise MemoryError
    tag: uint8_t[16]
    chacha_poly1305.Hacl_AEAD_Chacha20Poly1305_encrypt(
        output,
        tag,  # noqa: F821
        input_,
        len(input_),
        data,
        len(data),
        key,
        nonce,
    )
    cipher: bytes = output[: len(input_)]
    free(output)
    return (cipher, tag[:16])  # noqa: F821


def decrypt(input_: bytes, data: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
    """
    Decrypt ``input_`` and verify ``tag``.

    :param input_: The encrypted text to be decrypted.
    :param data: The associated data over which a tag is computed and
        compared against ``tag``.
    :param key: The 32 bytes private key.
    :param nonce: The 12 bytes nonce used by the other side.
    :param tag: The 16 bytes tag computed by the other side that is
        verified.

    :returns: The decrypted text.

    :raises ValueError: When the key or nonce or tag has incorrect
        length.
    :raises HACLError: When the underlying C function returned an error.

    Binding for ``Hacl_AEAD_Chacha20Poly1305_decrypt``.
    """
    if len(key) != 32:
        e = "key must be 32 bytes long"
        raise ValueError(e)
    if len(nonce) != 12:
        e = "nonce must be 12 bytes long"
        raise ValueError(e)
    if len(tag) != 16:
        e = "tag must be 16 bytes long"
        raise ValueError(e)
    output: cython.pointer(uint8_t) = cython.cast(
        cython.pointer(uint8_t), malloc(len(input_))
    )
    if output is cython.NULL:
        raise MemoryError
    ko: uint32_t = chacha_poly1305.Hacl_AEAD_Chacha20Poly1305_decrypt(
        output,
        input_,
        len(input_),
        data,
        len(data),
        key,
        nonce,
        tag,
    )
    if ko:
        e = "decryption failed"
        raise HACLError(e)
    plain: bytes = output[: len(input_)]
    free(output)
    return plain
