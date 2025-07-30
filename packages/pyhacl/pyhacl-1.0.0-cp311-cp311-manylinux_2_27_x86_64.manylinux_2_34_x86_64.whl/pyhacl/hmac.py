# noqa: A005
"""
Bindings for HMAC.

.. danger::

    When comparing the signature to an externally supplied digest during
    a verification routine, it is mandatory to use a **constant-time
    comparison function** such as :func:`secrets.compare_digest()` from
    python's standard library. Not doing so makes it vulnerable to
    `timing attacks <https://en.wikipedia.org/wiki/Timing_attack>`_.
"""

from cython.cimports.libc.stdint import uint8_t

from cython.cimports.pyhacl import hmac


def hmac_sha256(key: bytes, message: bytes) -> bytes:
    """
    Return the HMAC-SHA-2-256 MAC of ``message`` using ``key``.

    The key can be any length and will be hashed if it is longer and
    padded if it is shorter than 64 bytes.

    :return: A 32 bytes signature.

    Binding for ``Hacl_HMAC_compute_sha2_256``.
    """
    dst: uint8_t[32]
    hmac.Hacl_HMAC_compute_sha2_256(dst, key, len(key), message, len(message))  # noqa: F821
    return dst[:32]  # noqa: F821


def hmac_sha384(key: bytes, message: bytes) -> bytes:
    """
    Return the HMAC-SHA-2-384 MAC of ``message`` using ``key``.

    The key can be any length and will be hashed if it is longer and
    padded if it is shorter than 128 bytes.

    :return: A 48 bytes signature.

    Binding for ``Hacl_HMAC_compute_sha2_384``.
    """
    dst: uint8_t[48]
    hmac.Hacl_HMAC_compute_sha2_384(dst, key, len(key), message, len(message))  # noqa: F821
    return dst[:48]  # noqa: F821


def hmac_sha512(key: bytes, message: bytes) -> bytes:
    """
    Return the HMAC-SHA-2-256 MAC of ``message`` using ``key``.

    The key can be any length and will be hashed if it is longer and
    padded if it is shorter than 128 bytes.

    :return: A 64 bytes signature.

    Binding for ``Hacl_HMAC_compute_sha2_512``.
    """
    dst: uint8_t[64]
    hmac.Hacl_HMAC_compute_sha2_512(dst, key, len(key), message, len(message))  # noqa: F821
    return dst[:64]  # noqa: F821
