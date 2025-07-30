R"""Bindings for the secure hash algorithms of HACL\*."""

from __future__ import annotations

from .sha2 import sha224, sha256, sha384, sha512

_hashes = {
    Hash.name: Hash
    for Hash in (
        sha224,
        sha256,
        sha384,
        sha512,
    )
}

algorithms_available = list(_hashes)
__all__ = [*algorithms_available, 'new', 'algorithms_available']  # noqa: PLE0604


def new(name: str, data: bytes = b'') -> sha224 | sha256 | sha384 | sha512:
    """Instantiate a new hash object, using its canonical name."""
    if Hash := _hashes.get(name):  # noqa: N806
        return Hash(data)
    e = f'unsupported hash type {name}'
    raise ValueError(e)
