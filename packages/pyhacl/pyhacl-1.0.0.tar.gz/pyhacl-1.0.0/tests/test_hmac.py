import unittest

from parameterized import parameterized

from pyhacl import hmac

from .hmac_test_vectors import case5, hmac_test_vectors


class TestHMAC(unittest.TestCase):
    @parameterized.expand(hmac_test_vectors)
    def test_hmac_sha2(self, _name, key, data, _sha224, sha256, sha384, sha512):
        with self.subTest(name='sha256'):
            self.assertEqual(hmac.hmac_sha256(key, data), sha256)
        with self.subTest(name='sha384'):
            self.assertEqual(hmac.hmac_sha384(key, data), sha384)
        with self.subTest(name='sha512'):
            self.assertEqual(hmac.hmac_sha512(key, data), sha512)

    def test_hmac_sha2_vector_5(self):
        # https://datatracker.ietf.org/doc/html/rfc4231#section-4.6
        # Test with a truncation of output to 128 bits.

        with self.subTest(name='sha256'):
            self.assertEqual(hmac.hmac_sha256(
                case5.key, case5.data)[:16],
                case5.hmac_sha_256,
            )
        with self.subTest(name='sha384'):
            self.assertEqual(hmac.hmac_sha384(
                case5.key, case5.data)[:16],
                case5.hmac_sha_384,
            )
        with self.subTest(name='sha512'):
            self.assertEqual(hmac.hmac_sha512(
                case5.key, case5.data)[:16],
                case5.hmac_sha_512,
            )
