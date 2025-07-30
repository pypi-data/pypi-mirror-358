R"""Bindings for the Deterministic Random Bit Generator algorithm of HACL\*."""

import enum

import cython
from cython.cimports.libc.stdint import uint8_t
from cython.cimports.libc.stdlib import free, malloc

from cython.cimports.pyhacl import drbg

from . import HACLError


class SpecHashDefinitions(enum.IntEnum):
    """Available hash algorithms."""

    SHA2_256 = 1
    SHA2_384 = 2
    SHA2_512 = 3

def get_reseed_interval() -> int:
    """
    Get the global call count limit of :meth:`DRBGRandom.generate`
    before new bytes must be seeded.
    """
    return drbg.Hacl_HMAC_DRBG_reseed_interval


def set_reseed_interval(value: int) -> None:
    """
    Set the global call count limit of :meth:`DRBGRandom.generate`
    before new bytes must be seeded.
    """
    drbg.Hacl_HMAC_DRBG_reseed_interval = value


@cython.cclass
class DRBGRandom:
    """
    >>> DRBGRandom(
    >>>     digestmod: SpecHashDefinitions,
    >>>     entropy: bytes,
    >>>     nonce: bytes,
    >>>     personalization_string: bytes,
    >>> )

    A deterministric :abbr:`CSPRNG (Cryptographic Secure Pseudo Random
    Number Generator)` built upon ``HMAC_DRBG`` as described in
    `NIST SP 800-90A`_.

    It takes a (short) raw entropy and stretches it in (long) random
    bytes that are evenly distributed and are not predictable to anyone
    who lacks the initial raw entropy.

    :param digestmod: The hash for the underlying HMAC.
    :type digestmod: SpecHashDefinitions
    :param bytes entropy: Random bytes coming from another CSPRNG such
        as :func:`os.urandom`, or collected from hardware noise. Each
        ``digestmod`` comes with a minimum required entropy, see
        :meth:`min_length`.
    :param bytes nonce: Non-secret bytes used to allow initializing a
        new different :class:`DRBGRandom` with a same ``entropy``, or
        Can be empty.
    :param bytes personalization_string: A human-readable bytes used to
        identify this instanciation. Its purpose it to allow reusing a
        same ``entropy`` but in various settings. Similar to the *label*
        in :rfc:`5869` (HKDF). Can be empty.

    The entropy, nonce and personalization string form together the
    initial state over which random bytes are generated.

    :raises ValueError: When not enough entropy is provided.

    See also :func:`os.urandom` and :mod:`secrets`, both found in the
    python standard library. They use the operating system random number
    generator which is suited for cryptography, is much faster, but is
    not deterministic. They can be used in situations where a
    deterministic algorithm is not necessary.

    .. _NIST SP 800-90A: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-90Ar1.pdf
    """  # noqa: D400, D415

    _digestmod: drbg.Spec_Hash_Definitions_hash_alg
    _state: drbg.Hacl_HMAC_DRBG_state

    def __cinit__(
        self,
        digestmod: SpecHashDefinitions,
        entropy: bytes,
        nonce: bytes,
        personalization_string: bytes,
    ):
        SpecHashDefinitions(digestmod)
        self._digestmod = int(digestmod)
        self._state = drbg.Hacl_HMAC_DRBG_create_in(self._digestmod)

    def __dealloc__(self):
        drbg.Hacl_HMAC_DRBG_free(self._digestmod, self._state)

    def __init__(
        self,
        digestmod: SpecHashDefinitions,
        entropy: bytes,
        nonce: bytes,
        personalization_string: bytes,
    ):
        """Create a new state."""
        SpecHashDefinitions(digestmod)
        if len(entropy) < self.min_length(digestmod):
            e = "not enough entropy"
            raise ValueError(e)
        drbg.Hacl_HMAC_DRBG_instantiate(
            self._digestmod,
            self._state,
            len(entropy),
            entropy,
            len(nonce),
            nonce,
            len(personalization_string),
            personalization_string,
        )

    def reseed(self, entropy: bytes, additional_input: bytes = b'') -> None:
        """
        Feed new entropy inside the internal state.

        :param entropy: Random bytes coming from another CSPRNG such
            as :func:`os.urandom`, or collected from hardware noise.

        Binding for ``Hacl_HMAC_DRBG_reseed``.
        """
        drbg.Hacl_HMAC_DRBG_reseed(
            self._digestmod,
            self._state,
            len(entropy),
            entropy,
            len(additional_input),
            additional_input,
        )

    def generate(self, length: int, additional_input: bytes = b'') -> bytes:
        """
        Generate output.

        :param length: How many bytes to generate.
        :param additional_input: Optional entropy that'll be consumed
            at next :meth:`reseed`.

        :raises HACLError: When the entropy has been exhausted and that
            it is unsafe to generate new bytes. Call :meth:`reseed` to
            feed more entropy.

        Binding for ``Hacl_HMAC_DRBG_generate``.
        """
        output: cython.pointer(uint8_t) = cython.cast(
            cython.pointer(uint8_t), malloc(length)
        )
        if output is cython.NULL:
            raise MemoryError
        ok: bool = drbg.Hacl_HMAC_DRBG_generate(
            self._digestmod,
            output,
            self._state,
            length,
            len(additional_input),
            additional_input,
        )
        if not ok:
            e = "entropy exhausted, call reseed()"
            raise HACLError(e)
        output_b: bytes = output[:length]
        free(output)
        return output_b

    @staticmethod
    def min_length(digestmod: SpecHashDefinitions) -> int:
        """
        Get the minimum entropy required for a given hash algorithm.

        All SHA2 algorithms requires 32 bytes of entropy.

        Binding for ``Hacl_HMAC_DRBG_free``.
        """
        SpecHashDefinitions(digestmod)
        return drbg.Hacl_HMAC_DRBG_min_length(digestmod)
