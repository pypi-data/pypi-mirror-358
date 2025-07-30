from libcpp cimport bool
from libc.stdint cimport uint8_t, uint32_t
from cython.cimports.pyhacl.streaming_types import Spec_Hash_Definitions_hash_alg

cdef extern from "Hacl_HMAC_DRBG.h":
    #ctypedef Spec_Hash_Definitions_hash_alg Hacl_HMAC_DRBG_supported_alg

    uint32_t Hacl_HMAC_DRBG_reseed_interval;

    cdef struct Hacl_HMAC_DRBG_state_s:
        uint8_t *k
        uint8_t *v
        uint32_t *reseed_counter
    ctypedef Hacl_HMAC_DRBG_state_s Hacl_HMAC_DRBG_state

    Hacl_HMAC_DRBG_state Hacl_HMAC_DRBG_create_in(Spec_Hash_Definitions_hash_alg a)
    void Hacl_HMAC_DRBG_instantiate(
        Spec_Hash_Definitions_hash_alg a,
        Hacl_HMAC_DRBG_state st,
        uint32_t entropy_input_len,
        uint8_t *entropy_input,
        uint32_t nonce_len,
        uint8_t *nonce,
        uint32_t personalization_string_len,
        uint8_t *personalization_string,
    )
    void Hacl_HMAC_DRBG_reseed(
        Spec_Hash_Definitions_hash_alg a,
        Hacl_HMAC_DRBG_state st,
        uint32_t entropy_input_len,
        uint8_t *entropy_input,
        uint32_t additional_input_input_len,
        uint8_t *additional_input_input,
    )
    bool Hacl_HMAC_DRBG_generate(
        Spec_Hash_Definitions_hash_alg a,
        uint8_t *output,
        Hacl_HMAC_DRBG_state st,
        uint32_t n,
        uint32_t additional_input_len,
        uint8_t *additional_input,
    )
    void Hacl_HMAC_DRBG_free(Spec_Hash_Definitions_hash_alg uu___, Hacl_HMAC_DRBG_state s)
    uint32_t Hacl_HMAC_DRBG_min_length(Spec_Hash_Definitions_hash_alg a)
