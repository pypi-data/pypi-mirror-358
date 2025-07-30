"""A demo script to show the capabilities of pyhacl."""


# fmt: off

import os
import sys

from .aead import chacha_poly1305
from .diffie_hellman import curve25519
from .drbg import DRBGRandom, SpecHashDefinitions
from .hashlib import sha224, sha256, sha384, sha512
from .signature import ed25519, p256


def main() -> None:
    """Run the demo script."""
    data = b"Hello world!"

    print("pyhacl demo over the data", data)

    # Hashlib
    sha = sha256.oneshot(data)
    print(
        "\nHash"
        "\nsha224", sha224.oneshot(data).hex(),
        "\nsha256", sha.hex(),
        "\nsha384", sha384.oneshot(data).hex(),
        "\nsha512", sha512.oneshot(data).hex(),
    )

    # AEAD
    key32 = os.urandom(32)
    nonce12 = b'\x01' * 12
    cipher, tag = chacha_poly1305.encrypt(
        data, sha, key32, nonce12
    )
    text = chacha_poly1305.decrypt(
        cipher, sha, key32, nonce12, tag
    )
    print(
      "\nAEAD"
      "\nchapoly"
      "\n\trandom key", key32.hex(),
      "\n\tnonce", nonce12.hex(),
      "\n\tcipher", cipher.hex(),
      "\n\ttag", tag.hex(),
      "\n\tdecrypted back", text,
    )

    # Signature
    p256_priv = bytes.fromhex(
        '3813E9CC1168AED230DCA65AF0F0BF3EAF2D48A3495777A0D865D4CE1E0094E0')
    assert p256.validate_private_key(p256_priv)
    p256_pub = bytes.fromhex(
        '7BD9F4AA8801613D81C73B9480347D0A6AB4AF7EB1B04EB634151477EB651ED6'
        'CBBC6251D01C0CD52E5FDC1B44C9AC544059FAC6398EE1DA4F4382E356A4D9C9')
    assert p256.validate_public_key(p256_pub)

    nonce32 = b'\x01' * 32
    p256_signature = p256.sign_sha256(data, p256_priv, nonce32)
    print(
        "\nSignature"
        "\np256"
        "\n\tpriv", p256_priv.hex(),
        "\n\tpub", p256_pub.hex(),
        "\n\tnonce", nonce32.hex(),
        "\n\tsigned sha256", p256_signature.hex()
    )
    assert p256.verif_sha256(data, p256_pub, p256_signature)
    print("\tsignature validates")

    ed25519_priv = bytes.fromhex(
        '9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60')
    ed25519_pub = bytes.fromhex(
        'd75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
    ed25519_signature = ed25519.sign(ed25519_priv, data)
    print(
        "ed25519"
        "\n\tpriv", ed25519_priv.hex(),
        "\n\tpub", ed25519_pub.hex(),
        "\n\tsignature", ed25519_signature.hex(),
    )
    assert ed25519.verify(ed25519_pub, data, ed25519_signature)
    print("\tsignature validates")

    # Diffie-Hellman
    alice_priv = os.urandom(32)
    alice_pub = curve25519.secret_to_public(alice_priv)
    bob_priv = os.urandom(32)
    bob_pub = curve25519.secret_to_public(bob_priv)
    alice_shared = curve25519.ecdh(alice_priv, bob_pub)
    bob_shared = curve25519.ecdh(bob_priv, alice_pub)
    print(
        "\nDiffie-Hellman",
        "\nx25519"
        "\n\talice priv", alice_priv.hex(),
        "\n\talice pub", alice_pub.hex(),
        "\n\tbob priv", bob_priv.hex(),
        "\n\tbob pub", bob_pub.hex(),
        "\n\talice shared", alice_shared.hex(),
        "\n\tbob shared  ", bob_shared.hex(),
    )

    # DRBG
    rng = DRBGRandom(SpecHashDefinitions.SHA2_256, key32, nonce12, data)
    print(
        "\nDRBG HMAC"
        "\nsha256"
        "\n\tentropy", key32.hex(),
        "\n\tnonce", nonce12.hex(),
        "\n\tpersonalization string", data,
        "\n\trandom 32 bytes #1", rng.generate(32).hex(),
        "\n\trandom 32 bytes #2", rng.generate(32).hex(),
        "\n\trandom 32 bytes #3", rng.generate(32).hex(),
    )


sys.exit(main())
