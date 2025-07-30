"""Bindings for SHA-2."""

import cython
from cython.cimports.libc.stdint import uint8_t
from cython.cimports.libc.string import memcpy

from cython.cimports.pyhacl.hashlib import sha2


@cython.cclass
class sha224:  # noqa: N801
    """
    Binding for SHA-224, as a ``haslib.Hash``-like interface, or as a
    :meth:`oneshot` function.
    """

    name = 'sha224'  #: The canonical name of this hash
    block_size = 64  #: The internal block size of the hash algorithm in bytes.
    digest_size = 28  #: The size of the resulting hash in bytes.

    _state: cython.pointer(sha2.Hacl_Hash_SHA2_state_t_224)

    def __cinit__(self):
        self._state = sha2.Hacl_Hash_SHA2_malloc_224()
        if not self._state:
            raise MemoryError

    def __dealloc__(self):
        sha2.Hacl_Hash_SHA2_free_224(self._state)
        self._state = cython.NULL

    def __init__(self, data: bytes = b''):
        """
        Create a new hash object seeded with ``data``.

        Uses ``Hacl_Hash_SHA2_malloc_224`` upon allocation, and
        ``Hacl_Hash_SHA2_free_224`` upon de-allocation.
        """
        super().__init__()
        if data:
            self.update(data)

    def update(self, data: bytes) -> None:
        """
        Feed the hash object with ``data``.

        Uses ``Hacl_Hash_SHA2_update_224``.
        """
        sha2.Hacl_Hash_SHA2_update_224(self._state, data, len(data))

    def digest(self) -> bytes:
        """
        Produce a 28-bytes hash value out of the current state of the
        hash object.

        Uses ``Hacl_Hash_SHA2_digest_224``.
        """
        output: uint8_t[28]
        sha2.Hacl_Hash_SHA2_digest_224(self._state, output)  # noqa: F821
        return output[:28]  # noqa: F821

    def hexdigest(self) -> str:
        """Shortcut for ``digest(data).hex()``."""
        return self.digest().hex()

    def copy(self):  # noqa: ANN201
        """
        Create a copy of the current hash object, so the two can be
        feeded with different data.
        """
        copy: sha224 = type(self)()
        copy._state[0].block_state[0] = self._state[0].block_state[0]  # noqa: SLF001
        memcpy(
            cython.cast(cython.p_void, copy._state[0].buf),  # noqa: SLF001
            cython.cast(cython.p_void, self._state[0].buf),
            64,
        )
        copy._state[0].total_len = self._state[0].total_len  # noqa: SLF001
        return copy

    @classmethod
    def oneshot(cls, data: bytes) -> bytes:
        """
        Produce a 28-bytes hash value out of the provided data.

        Using this function is faster then using :meth:`update` and then
        :meth:`digest` when the entire data is available right away, and
        that it is not necessary to keep the state machine around once
        it has been digested.

        Binding for ``Hacl_Hash_SHA2_hash_224``.
        """
        output: cython.char[28]
        sha2.Hacl_Hash_SHA2_hash_224(
            cython.cast(cython.pointer(uint8_t), output),  # noqa: F821
            data,
            len(data),
        )
        return output[:28]  # noqa: F821

    @classmethod
    def hexoneshot(cls, data: bytes) -> str:
        """Shortcut for ``oneshot(data).hex()``."""
        return cls.oneshot(data).hex()


@cython.cclass
class sha256:  # noqa: N801
    """
    Binding for SHA-256, as a ``haslib.Hash``-like interface, or as a
    :meth:`oneshot` function.
    """

    name = 'sha256'  #: The canonical name of this hash
    block_size = 64  #: The internal block size of the hash algorithm in bytes.
    digest_size = 32  #: The size of the resulting hash in bytes.

    _state: cython.pointer(sha2.Hacl_Hash_SHA2_state_t_256)

    def __cinit__(self):
        self._state = sha2.Hacl_Hash_SHA2_malloc_256()
        if not self._state:
            raise MemoryError

    def __dealloc__(self):
        sha2.Hacl_Hash_SHA2_free_256(self._state)
        self._state = cython.NULL

    def __init__(self, data: bytes = b''):
        """
        Create a new hash object seeded with ``data``.

        Uses ``Hacl_Hash_SHA2_malloc_256`` upon allocation, and
        ``Hacl_Hash_SHA2_free_256`` upon de-allocation.
        """
        super().__init__()
        if data:
            self.update(data)

    def update(self, data: bytes) -> None:
        """
        Feed the hash object with ``data``.

        Uses ``Hacl_Hash_SHA2_update_256``.
        """
        sha2.Hacl_Hash_SHA2_update_256(self._state, data, len(data))

    def digest(self) -> bytes:
        """
        Produce a 32-bytes hash value out of the current state of the
        hash object.

        Uses ``Hacl_Hash_SHA2_digest_256``.
        """
        output: uint8_t[32]
        sha2.Hacl_Hash_SHA2_digest_256(self._state, output)  # noqa: F821
        return output[:32]  # noqa: F821

    def hexdigest(self) -> str:
        """Shortcut for ``digest(data).hex()``."""
        return self.digest().hex()

    def copy(self):  # noqa: ANN201
        """
        Create a copy of the current hash object, so the two can be
        feeded with different data.
        """
        copy: sha256 = type(self)()
        copy._state[0].block_state[0] = self._state[0].block_state[0]  # noqa: SLF001
        memcpy(
            cython.cast(cython.p_void, copy._state[0].buf),  # noqa: SLF001
            cython.cast(cython.p_void, self._state[0].buf),
            64,
        )
        copy._state[0].total_len = self._state[0].total_len  # noqa: SLF001
        return copy

    @classmethod
    def oneshot(cls, data: bytes) -> bytes:
        """
        Produce a 32-bytes hash value out of the provided data.

        Using this function is faster then using :meth:`update` and then
        :meth:`digest` when the entire data is available right away, and
        that it is not necessary to keep the state machine around once
        it has been digested.

        Binding for ``Hacl_Hash_SHA2_hash_256``.
        """
        output: cython.char[32]
        sha2.Hacl_Hash_SHA2_hash_256(
            cython.cast(cython.pointer(uint8_t), output),  # noqa: F821
            data,
            len(data),
        )
        return output[:32]  # noqa: F821

    @classmethod
    def hexoneshot(cls, data: bytes) -> str:
        """Shortcut for ``oneshot(data).hex()``."""
        return cls.oneshot(data).hex()


@cython.cclass
class sha384:  # noqa: N801
    """
    Binding for SHA-384, as a ``haslib.Hash``-like interface, or as a
    :meth:`oneshot` function.
    """

    name = 'sha384'  #: The canonical name of this hash
    block_size = 128  #: The internal block size of the hash algorithm in bytes.
    digest_size = 48  #: The size of the resulting hash in bytes.

    _state: cython.pointer(sha2.Hacl_Hash_SHA2_state_t_384)

    def __cinit__(self):
        self._state = sha2.Hacl_Hash_SHA2_malloc_384()
        if not self._state:
            raise MemoryError

    def __dealloc__(self):
        sha2.Hacl_Hash_SHA2_free_384(self._state)
        self._state = cython.NULL

    def __init__(self, data: bytes = b''):
        """
        Create a new hash object seeded with ``data``.

        Uses ``Hacl_Hash_SHA2_malloc_384`` upon allocation, and
        ``Hacl_Hash_SHA2_free_384`` upon de-allocation.
        """
        super().__init__()
        if data:
            self.update(data)

    def update(self, data: bytes) -> None:
        """
        Feed the hash object with ``data``.

        Uses ``Hacl_Hash_SHA2_update_384``.
        """
        sha2.Hacl_Hash_SHA2_update_384(self._state, data, len(data))

    def digest(self) -> bytes:
        """
        Produce a 48-bytes hash value out of the current state of the
        hash object.

        Uses ``Hacl_Hash_SHA2_digest_384``.
        """
        output: uint8_t[48]
        sha2.Hacl_Hash_SHA2_digest_384(self._state, output)  # noqa: F821
        return output[:48]  # noqa: F821

    def hexdigest(self) -> str:
        """Shortcut for ``digest(data).hex()``."""
        return self.digest().hex()

    def copy(self):  # noqa: ANN201
        """
        Create a copy of the current hash object, so the two can be
        feeded with different data.
        """
        copy: sha384 = type(self)()
        copy._state[0].block_state[0] = self._state[0].block_state[0]  # noqa: SLF001
        memcpy(
            cython.cast(cython.p_void, copy._state[0].buf),  # noqa: SLF001
            cython.cast(cython.p_void, self._state[0].buf),
            128,
        )
        copy._state[0].total_len = self._state[0].total_len  # noqa: SLF001
        return copy

    @classmethod
    def oneshot(cls, data: bytes) -> bytes:
        """
        Produce a 48-bytes hash value out of the provided data.

        Using this function is faster then using :meth:`update` and then
        :meth:`digest` when the entire data is available right away, and
        that it is not necessary to keep the state machine around once
        it has been digested.

        Binding for ``Hacl_Hash_SHA2_hash_384``.
        """
        output: cython.char[48]
        sha2.Hacl_Hash_SHA2_hash_384(
            cython.cast(cython.pointer(uint8_t), output),  # noqa: F821
            data,
            len(data),
        )
        return output[:48]  # noqa: F821

    @classmethod
    def hexoneshot(cls, data: bytes) -> str:
        """Shortcut for ``oneshot(data).hex()``."""
        return cls.oneshot(data).hex()


@cython.cclass
class sha512:  # noqa: N801
    """
    Binding for SHA-512, as a ``haslib.Hash``-like interface, or as a
    :meth:`oneshot` function.
    """

    name = 'sha512'  #: The canonical name of this hash
    block_size = 128  #: The internal block size of the hash algorithm in bytes.
    digest_size = 64  #: The size of the resulting hash in bytes.

    _state: cython.pointer(sha2.Hacl_Hash_SHA2_state_t_512)

    def __cinit__(self):
        self._state = sha2.Hacl_Hash_SHA2_malloc_512()
        if not self._state:
            raise MemoryError

    def __dealloc__(self):
        sha2.Hacl_Hash_SHA2_free_512(self._state)
        self._state = cython.NULL

    def __init__(self, data: bytes = b''):
        """
        Create a new hash object seeded with ``data``.

        Uses ``Hacl_Hash_SHA2_malloc_512`` upon allocation, and
        ``Hacl_Hash_SHA2_free_512`` upon de-allocation.
        """
        super().__init__()
        if data:
            self.update(data)

    def update(self, data: bytes) -> None:
        """
        Feed the hash object with ``data``.

        Uses ``Hacl_Hash_SHA2_update_512``.
        """
        sha2.Hacl_Hash_SHA2_update_512(self._state, data, len(data))

    def digest(self) -> bytes:
        """
        Produce a 64-bytes hash value out of the current state of the
        hash object.

        Uses ``Hacl_Hash_SHA2_digest_512``.
        """
        output: uint8_t[64]
        sha2.Hacl_Hash_SHA2_digest_512(self._state, output)  # noqa: F821
        return output[:64]  # noqa: F821

    def hexdigest(self) -> str:
        """Shortcut for ``digest(data).hex()``."""
        return self.digest().hex()

    def copy(self):  # noqa: ANN201
        """
        Create a copy of the current hash object, so the two can be
        feeded with different data.
        """
        copy: sha512 = type(self)()
        copy._state[0].block_state[0] = self._state[0].block_state[0]  # noqa: SLF001
        memcpy(
            cython.cast(cython.p_void, copy._state[0].buf),  # noqa: SLF001
            cython.cast(cython.p_void, self._state[0].buf),
            128,
        )
        copy._state[0].total_len = self._state[0].total_len  # noqa: SLF001
        return copy

    @classmethod
    def oneshot(cls, data: bytes) -> bytes:
        """
        Produce a 64-bytes hash value out of the provided data.

        Using this function is faster then using :meth:`update` and then
        :meth:`digest` when the entire data is available right away, and
        that it is not necessary to keep the state machine around once
        it has been digested.

        Binding for ``Hacl_Hash_SHA2_hash_512``.
        """
        output: cython.char[64]
        sha2.Hacl_Hash_SHA2_hash_512(
            cython.cast(cython.pointer(uint8_t), output),  # noqa: F821
            data,
            len(data),
        )
        return output[:64]  # noqa: F821

    @classmethod
    def hexoneshot(cls, data: bytes) -> str:
        """Shortcut for ``oneshot(data).hex()``."""
        return cls.oneshot(data).hex()
