import pathlib
import unittest
import hashlib as pyhashlib

from parameterized import parameterized

from pyhacl.hashlib import sha224, sha256, sha384, sha512

shabytetestvectors_dir = pathlib.Path(__file__).parent.joinpath('shabytetestvectors')


class TestHashlib(unittest.TestCase):
    @parameterized.expand(
        [
            (f'SHA{Hash.name[3:]}{suite}', Hash)
            for Hash in [sha224, sha256, sha384, sha512]
            for suite in ('Short', 'Long')
        ]
    )
    def test_hashlib(self, name, Hash):  # noqa: N803
        with shabytetestvectors_dir.joinpath(f'{name}Msg.rsp').open() as file:
            header_lineno = 7
            for _ in range(header_lineno):
                file.readline()

            rl = iter(file.readline, '')
            for lineno, (Len, Msg, MD, _) in enumerate(zip(rl, rl, rl, rl)):  # noqa: N806
                with self.subTest(lineno=lineno * 4 + header_lineno + 1):
                    Len = int(Len.removeprefix('Len = ').strip()) // 8  # noqa: N806, PLW2901
                    Msg = bytes.fromhex(Msg.removeprefix('Msg = ').strip())  # noqa: N806, PLW2901
                    MD = MD.removeprefix('MD = ').strip()  # noqa: N806, PLW2901
                    if Len == 0 and Msg == b'\0':
                        Msg = b''  # noqa: N806, PLW2901
                    self.assertEqual(len(Msg), Len)  # safety check

                    sha = Hash()
                    for chunkno in range(0, Len, 256):
                        sha.update(Msg[chunkno : chunkno + 256])
                    self.assertEqual(sha.digest(), bytes.fromhex(MD))
                    self.assertEqual(sha.hexdigest(), MD)
                    self.assertEqual(Hash.oneshot(Msg), bytes.fromhex(MD))
                    self.assertEqual(Hash.hexoneshot(Msg), MD)

    @parameterized.expand([
        ('sha224', sha224, pyhashlib.sha224),
        ('sha256', sha256, pyhashlib.sha256),
        ('sha384', sha384, pyhashlib.sha384),
        ('sha512', sha512, pyhashlib.sha512),
    ])
    def test_hashlib_nullbyte(self, _name, hacl_hash, py_hash):
        data = b"some\0data"
        expected_digest = py_hash(data).digest()
        self.assertEqual(hacl_hash.oneshot(data), expected_digest)
        self.assertEqual(hacl_hash(data).digest(), expected_digest)
        h = hacl_hash()
        h.update(data[:4])
        h.update(data[4:])
        self.assertEqual(h.digest(), expected_digest)
