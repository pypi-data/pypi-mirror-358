from libcpp cimport bool
from libc.stdint cimport uint8_t

cdef extern from "Hacl_Curve25519_51.h":
    void Hacl_Curve25519_51_scalarmult(uint8_t *out, uint8_t *priv, uint8_t *pub)
    void Hacl_Curve25519_51_secret_to_public(uint8_t *pub, uint8_t *priv)
    bool Hacl_Curve25519_51_ecdh(uint8_t *out, uint8_t *priv, uint8_t *pub)
