import unittest

from pyhacl.aead import chacha_poly1305


class TestAEAD(unittest.TestCase):
    def test_aead_chacha_poly1305(self):
        plain1 = b'Hello world!'
        adata = b'additionnal'
        key = b'a' * 32
        nonce = (0).to_bytes(12, 'big')

        cipher, tag = chacha_poly1305.encrypt(plain1, adata, key, nonce)
        plain2 = chacha_poly1305.decrypt(cipher, adata, key, nonce, tag)

        self.assertEqual(plain1, plain2)

    def test_aead_chacha_poly1305_nullbyte(self):
        plain1 = b'Hello\0world!'
        adata = b'addi\0tionnal'
        key = b'a' * 32
        nonce = (0).to_bytes(12, 'big')

        cipher, tag = chacha_poly1305.encrypt(plain1, adata, key, nonce)
        plain2 = chacha_poly1305.decrypt(cipher, adata, key, nonce, tag)

        self.assertEqual(plain1, plain2)
