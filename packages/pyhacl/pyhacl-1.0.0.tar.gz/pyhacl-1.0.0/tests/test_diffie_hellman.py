import unittest

from pyhacl.diffie_hellman import curve25519


class TestDiffieHellman(unittest.TestCase):
    def test_diffie_hellman_x25519(self):
        # test vectors from rfc7748
        alice_sk = bytes.fromhex(
            '77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a')
        alice_pk = curve25519.secret_to_public(alice_sk)
        self.assertEqual(alice_pk, bytes.fromhex(
            '8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a'))

        bob_sk = bytes.fromhex(
            '5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb')
        bob_pk = curve25519.secret_to_public(bob_sk)
        self.assertEqual(bob_pk, bytes.fromhex(
            'de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f'))

        shared1 = curve25519.ecdh(alice_sk, bob_pk)
        shared2 = curve25519.ecdh(bob_sk, alice_pk)
        self.assertEqual(shared1, bytes.fromhex(
            '4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742'))
        self.assertEqual(shared2, bytes.fromhex(
            '4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742'))
        self.assertEqual(shared1, shared2)

    def test_diffie_hellman_x25519_nullbyte(self):
        alice_sk = b"abcdefghijklmnopqrstuvwxyz\x0012345"
        alice_pk = curve25519.secret_to_public(alice_sk)

        bob_sk = b"\x0012345abcdefghijklmnopqrstuvwxyz"
        bob_pk = curve25519.secret_to_public(bob_sk)

        shared1 = curve25519.ecdh(alice_sk, bob_pk)
        shared2 = curve25519.ecdh(bob_sk, alice_pk)

        self.assertEqual(shared1, shared2)
