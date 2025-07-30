from libc.stdint cimport uint8_t, uint32_t

cdef extern from "Hacl_HMAC.h":
    void Hacl_HMAC_compute_sha2_256(uint8_t *dst, uint8_t *key, uint32_t key_len, uint8_t *data, uint32_t data_len)
    void Hacl_HMAC_compute_sha2_384(uint8_t *dst, uint8_t *key, uint32_t key_len, uint8_t *data, uint32_t data_len)
    void Hacl_HMAC_compute_sha2_512(uint8_t *dst, uint8_t *key, uint32_t key_len, uint8_t *data, uint32_t data_len)
