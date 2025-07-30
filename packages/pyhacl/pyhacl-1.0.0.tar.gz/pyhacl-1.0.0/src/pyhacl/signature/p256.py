R"""
Bindings for ECDSA secp256r1.

.. danger::

    The nonce **MUST** be unique per invocation with the same key,
    **MUST NOT** be communicated, **MUST NOT** be predicable, and
    **MUST** be uniformally distributed. Failure to meet those
    requirements makes it trivial to find the key.

    :rfc:`6979` gives guidance to safely generate nonces for ECDSA,
    section 3.3 describes how to use :class:`pyhacl.drbg.DRBGRandom`.

.. note::

    ECDSA signatures are often serialiazed using the following ASN.1
    structure::

        Dss-Sig-Value  ::=  SEQUENCE  {
          r       INTEGER,
          s       INTEGER  }

    HACL\* has no utility to encode or decode this structure, it instead
    uses the raw 32 bytes ``r`` and ``s`` integers.
"""

from cython.cimports.libc.stdint import uint8_t

from cython.cimports.pyhacl.signature import p256
from pyhacl import HACLError


def validate_private_key(private_key: bytes) -> bool:
    """
    Determine if the key is between 0 and the order of the curve.

    :returns: ``True`` when the key is valid; ``False`` otherwise.
    :raises ValueError: When the key is not a 32-bytes point.

    It uses ``Hacl_P256_validate_private_key``.
    """
    if len(private_key) != 32:
        e = "private key must be a raw key 32 bytes long"
        raise ValueError(e)
    return p256.Hacl_P256_validate_private_key(
        private_key,
    )


def validate_public_key(public_key: bytes) -> bool:
    R"""
    Determine if the public key is valid. See the documentation in
    HACL\* for details.

    :returns: ``True`` when the key is valid; ``False`` otherwise.
    :raises ValueError: When the key is not two concatenated 32-bytes
        points (64 bytes ``x || y``).

    It uses ``Hacl_P256_validate_public_key``.
    """
    if len(public_key) != 64:
        e = "public key must be a raw key 64 bytes long"
        raise ValueError(e)
    return p256.Hacl_P256_validate_public_key(
        public_key,
    )


def sign_without_hash(message: bytes, private_key: bytes, nonce: bytes) -> bytes:
    """
    Sign the message.

    ECDSA is slow on long inputs so it is assumed that the message
    is somewhat short. The other ``sign_`` functions are preferred if
    the input is long.

    .. warning::

        This function is only working on messages that are precisely 32
        bytes long, see `#1 <https://codeberg.org/drlazor8/pyhacl/issues/1>`__.

    :param message: The short message to be signed.
    :param private_key: The private key that'll sign the message.
    :param nonce: A unique, secret, unpredicable and uniformly
        distributed 32-bytes random value. See :rfc:`6979` for guidance.

    :returns: A 64-bytes signature that is the concatenation of 32-bytes
        ``R`` and 32-bytes ``S``.

    :raises ValueError: When the key or nonce has incorrect length.
    :raises HACLError: When the underlying C function failed to produce
        a signature, e.g. because the private key was invalid.

    Binding for ``Hacl_P256_ecdsa_sign_p256_without_hash``.
    """
    if len(message) != 32:
        e = "message must be 32 bytes long, see issue #1"
        raise ValueError(e)
    if len(private_key) != 32:
        e = "private key must be a raw key 32 bytes long"
        raise ValueError(e)
    if len(nonce) != 32:
        e = "nonce must be 32 bytes long"
        raise ValueError(e)
    signature: uint8_t[64]
    ok: bool = p256.Hacl_P256_ecdsa_sign_p256_without_hash(
        signature,  # noqa: F821
        len(message),
        message,
        private_key,
        nonce,
    )
    if not ok:
        e = "signature failed"
        raise HACLError(e)
    return signature[:64]  # noqa: F821


def sign_sha256(message: bytes, private_key: bytes, nonce: bytes) -> bytes:
    """
    Hash ``message`` using SHA-256 and sign the digest.

    :param message: The message (of any length) to be signed.
    :param private_key: The private key that'll sign the digest.
    :param nonce: A unique, secret, unpredicable and uniformly
        distributed 32-bytes random value. See :rfc:`6979` for guidance.

    :returns: A 64-bytes signature that is the concatenation of 32-bytes
        ``R`` and 32-bytes ``S``.

    :raises ValueError: When the key or nonce has incorrect length.
    :raises HACLError: When the underlying C function failed to produce
        a signature, e.g. because the private key was invalid.

    Binding for ``Hacl_P256_ecdsa_sign_p256_sha2``.
    """
    if len(private_key) != 32:
        e = "private key must be a raw key 32 bytes long"
        raise ValueError(e)
    if len(nonce) != 32:
        e = "nonce must be 32 bytes long"
        raise ValueError(e)
    signature: uint8_t[64]
    ok: bool = p256.Hacl_P256_ecdsa_sign_p256_sha2(
        signature,  # noqa: F821
        len(message),
        message,
        private_key,
        nonce,
    )
    if not ok:
        e = "signature failed"
        raise HACLError(e)
    return signature[:64]  # noqa: F821


sign_sha2 = sign_sha256


def sign_sha384(message: bytes, private_key: bytes, nonce: bytes) -> bytes:
    """
    Hash ``message`` using SHA-384 and sign the digest.

    :param message: The message (of any length) to be signed.
    :param private_key: The private key that'll sign the digest.
    :param nonce: A unique, secret, unpredicable and uniformly
        distributed 32-bytes random value. See :rfc:`6979` for guidance.

    :returns: A 64-bytes signature that is the concatenation of 32-bytes
        ``R`` and 32-bytes ``S``.

    :raises ValueError: When the key or nonce has incorrect length.
    :raises HACLError: When the underlying C function failed to produce
        a signature, e.g. because the private key was invalid.

    Binding for ``Hacl_P256_ecdsa_sign_p256_sha384``.
    """
    if len(private_key) != 32:
        e = "private key must be a raw key 32 bytes long"
        raise ValueError(e)
    if len(nonce) != 32:
        e = "nonce must be 32 bytes long"
        raise ValueError(e)
    signature: uint8_t[64]
    ok: bool = p256.Hacl_P256_ecdsa_sign_p256_sha384(
        signature,  # noqa: F821
        len(message),
        message,
        private_key,
        nonce,
    )
    if not ok:
        e = "signature failed"
        raise HACLError(e)
    return signature[:64]  # noqa: F821


def sign_sha512(message: bytes, private_key: bytes, nonce: bytes) -> bytes:
    """
    Hash ``message`` using SHA-512 and sign the digest.

    :param message: The message (of any length) to be signed.
    :param private_key: The private key that'll sign the digest.
    :param nonce: A unique, secret, unpredicable and uniformly
        distributed 32-bytes random value. See :rfc:`6979` for guidance.

    :returns: A 64-bytes signature that is the concatenation of 32-bytes
        ``R`` and 32-bytes ``S``.

    :raises ValueError: When the key or nonce has incorrect length.
    :raises HACLError: When the underlying C function failed to produce
        a signature, e.g. because the private key was invalid.

    Binding for ``Hacl_P256_ecdsa_sign_p256_sha512``.
    """
    if len(private_key) != 32:
        e = "private key must be a raw key 32 bytes long"
        raise ValueError(e)
    if len(nonce) != 32:
        e = "nonce must be 32 bytes long"
        raise ValueError(e)
    signature: uint8_t[64]
    ok: bool = p256.Hacl_P256_ecdsa_sign_p256_sha512(
        signature,  # noqa: F821
        len(message),
        message,
        private_key,
        nonce,
    )
    if not ok:
        e = "signature failed"
        raise HACLError(e)
    return signature[:64]  # noqa: F821


def verif_without_hash(message: bytes, public_key: bytes, signature: bytes) -> bool:
    """
    Verify that the signature matches the message.

    .. warning::

        This function is only working on messages that are precisely 32
        bytes long, see `#1 <https://codeberg.org/drlazor8/pyhacl/issues/1>`__.

    :param message: The message that is signed.
    :param public_key: The public key counter part of the private key
        that was used to generate the signature.
    :param signature: The signature of the message as the 64-bytes
        concatenation of 32-bytes ``R`` and 32-bytes ``S``.

    :returns: ``True`` when the signature matches; ``False`` otherwise.

    :raises ValueError: When the key or signature has incorrect length.

    Binding for ``Hacl_P256_ecdsa_verif_p256_without_hash``.
    """
    if len(message) != 32:
        e = "message must be 32 bytes long"
        raise ValueError(e)
    if len(public_key) != 64:
        e = "public key must be a raw key 64 bytes long"
        raise ValueError(e)
    if len(signature) != 64:
        e = "signature must be 64 bytes long"
        raise ValueError(e)
    signarure_r: uint8_t[32] = signature[:32]
    signature_s: uint8_t[32] = signature[32:]
    return p256.Hacl_P256_ecdsa_verif_without_hash(
        len(message),
        message,
        public_key,
        signarure_r,
        signature_s,
    )


def verif_sha256(message: bytes, public_key: bytes, signature: bytes) -> bool:
    """
    Verify that the signature matches the SHA-256 digest of the message.

    :param message: The message (of any length) that is signed.
    :param public_key: The public key counter part of the private key
        that was used to generate the signature.
    :param signature: The signature of the message as the 64-bytes
        concatenation of 32-bytes ``R`` and 32-bytes ``S``.

    :returns: ``True`` when the signature matches; ``False`` otherwise.

    :raises ValueError: When the key or signature has incorrect length.

    Binding for ``Hacl_P256_ecdsa_verif_p256_sha2``.
    """
    if len(public_key) != 64:
        e = "public key must be a raw key 64 bytes long"
        raise ValueError(e)
    if len(signature) != 64:
        e = "signature must be 64 bytes long"
        raise ValueError(e)
    signarure_r: uint8_t[32] = signature[:32]
    signature_s: uint8_t[32] = signature[32:]
    return p256.Hacl_P256_ecdsa_verif_p256_sha2(
        len(message),
        message,
        public_key,
        signarure_r,
        signature_s,
    )


verif_sha2 = verif_sha256


def verif_sha384(message: bytes, public_key: bytes, signature: bytes) -> bool:
    """
    Verify that the signature matches the SHA-384 digest of the message.

    :param message: The message (of any length) that is signed.
    :param public_key: The public key counter part of the private key
        that was used to generate the signature.
    :param signature: The signature of the message as the 64-bytes
        concatenation of 32-bytes ``R`` and 32-bytes ``S``.

    :returns: ``True`` when the signature matches; ``False`` otherwise.

    :raises ValueError: When the key or signature has incorrect length.

    Binding for ``Hacl_P256_ecdsa_verif_p256_sha384``.
    """
    if len(public_key) != 64:
        e = "public key must be a raw key 64 bytes long"
        raise ValueError(e)
    if len(signature) != 64:
        e = "signature must be 64 bytes long"
        raise ValueError(e)
    signarure_r: uint8_t[32] = signature[:32]
    signature_s: uint8_t[32] = signature[32:]
    return p256.Hacl_P256_ecdsa_verif_p256_sha384(
        len(message),
        message,
        public_key,
        signarure_r,
        signature_s,
    )


def verif_sha512(message: bytes, public_key: bytes, signature: bytes) -> bool:
    """
    Verify that the signature matches the SHA-512 digest of the message.

    :param message: The message (of any length) that is signed.
    :param public_key: The public key counter part of the private key
        that was used to generate the signature.
    :param signature: The signature of the message as the 64-bytes
        concatenation of 32-bytes ``R`` and 32-bytes ``S``.

    :returns: ``True`` when the signature matches; ``False`` otherwise.

    :raises ValueError: When the key or signature has incorrect length.

    Binding for ``Hacl_P256_ecdsa_verif_p256_sha512``.
    """
    if len(public_key) != 64:
        e = "public key must be a raw key 64 bytes long"
        raise ValueError(e)
    if len(signature) != 64:
        e = "signature must be 64 bytes long"
        raise ValueError(e)
    signarure_r: uint8_t[32] = signature[:32]
    signature_s: uint8_t[32] = signature[32:]
    return p256.Hacl_P256_ecdsa_verif_p256_sha512(
        len(message),
        message,
        public_key,
        signarure_r,
        signature_s,
    )
