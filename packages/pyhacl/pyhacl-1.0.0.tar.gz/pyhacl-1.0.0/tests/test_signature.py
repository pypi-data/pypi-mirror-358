import unittest

from parameterized import parameterized

from pyhacl import hashlib
from pyhacl.signature import ed25519, p256

from .ecdsa_test_vectors import p256_test_vector
from .eddsa_test_vectors import ed25519_test_vectors


class TestSignatureED25519(unittest.TestCase):
    @parameterized.expand(ed25519_test_vectors)
    def test_sign_ed25519(
        self,
        _name,
        private_key,
        public_key,
        message,
        expected_signature
    ):
        signature = ed25519.sign(private_key, message)
        self.assertEqual(signature, expected_signature)
        self.assertTrue(
            ed25519.verify(public_key, message, signature)
        )


class TestSignatureP256(unittest.TestCase):
    def test_sign_p256_key_valid(self):
        self.assertTrue(p256.validate_private_key(p256_test_vector.private_key))
        self.assertTrue(p256.validate_public_key(p256_test_vector.public_key.xy))

    @parameterized.expand(('sha2', 'sha256', 'sha384', 'sha512'))
    def test_sign_p256(self, name):
        sign_func = getattr(p256, f'sign_{name}')
        verif_func = getattr(p256, f'verif_{name}')

        for data in ('sample', 'test'):
            with self.subTest(data=data):
                expected_signature = getattr(p256_test_vector, f'{name}_{data}')
                signature = sign_func(
                    data.encode(),
                    p256_test_vector.private_key,
                    expected_signature.nonce,
                )
                self.assertEqual(signature, expected_signature.rs)
                self.assertTrue(
                    verif_func(
                        data.encode(),
                        p256_test_vector.public_key.xy,
                        signature,
                    ),
                    "the signature must match (verif must returns True)",
                )
                self.assertFalse(
                    verif_func(
                        (data + ' ').encode(),
                        p256_test_vector.public_key.xy,
                        signature,
                    ),
                    "the signature must not match (verif must returns False)",
                )

    def test_sign_p256_without_hash(self):
        for data in ('sample', 'test'):
            with self.subTest(data=data):
                expected_signature = getattr(p256_test_vector, f'sha256_{data}')
                good_sha = hashlib.sha256.oneshot(data.encode())
                bad_sha = hashlib.sha256.oneshot((data + ' ').encode())
                signature = p256.sign_without_hash(
                    good_sha,
                    p256_test_vector.private_key,
                    expected_signature.nonce,
                )
                self.assertEqual(signature, expected_signature.rs)
                self.assertTrue(
                    p256.verif_without_hash(
                        good_sha,
                        p256_test_vector.public_key.xy,
                        signature,
                    ),
                    "the signature must match (verif must returns True)",
                )
                self.assertFalse(
                    p256.verif_without_hash(
                        bad_sha,
                        p256_test_vector.public_key.xy,
                        signature,
                    ),
                    "the signature must not match (verif must returns False)",
                )
