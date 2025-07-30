import pathlib
import unittest

from parameterized import parameterized

from pyhacl.drbg import DRBGRandom, SpecHashDefinitions

drbgtestvectors_dir = pathlib.Path(__file__).parent.joinpath('drbgtestvectors')


str2bool = {'False': False, 'True': True}.__getitem__


def read_rsp_line(file, assert_name, type_=bytes.fromhex, *, strip=False):
    line = file.readline().removesuffix('\n')
    if strip:
        line = line.removeprefix('[').removesuffix(']')
    name, value = line.split(' = ')
    assert name == assert_name, (name, assert_name)  # noqa: S101
    return name, type_(value)


def read_rsp_config(file):
    return dict([
        read_rsp_line(file, 'PredictionResistance', str2bool, strip=True),
        read_rsp_line(file, 'EntropyInputLen', int, strip=True),
        read_rsp_line(file, 'NonceLen', int, strip=True),
        read_rsp_line(file, 'PersonalizationStringLen', int, strip=True),
        read_rsp_line(file, 'AdditionalInputLen', int, strip=True),
        read_rsp_line(file, 'ReturnedBitsLen', int, strip=True),
    ])


def read_no_reseed_rsp_chunk(file):
    return dict([
        read_rsp_line(file, 'COUNT', int),
        read_rsp_line(file, 'EntropyInput'),
        read_rsp_line(file, 'Nonce'),
        read_rsp_line(file, 'PersonalizationString'),
        ('AdditionalInput', read_rsp_line(file, 'AdditionalInput')[1]),
        ('AdditionalInput_', read_rsp_line(file, 'AdditionalInput')[1]),
        read_rsp_line(file, 'ReturnedBits'),
    ])


def read_reseed_rsp_chunk(file):
    return dict([
        read_rsp_line(file, 'COUNT', int),
        read_rsp_line(file, 'EntropyInput'),
        read_rsp_line(file, 'Nonce'),
        read_rsp_line(file, 'PersonalizationString'),
        read_rsp_line(file, 'EntropyInputReseed'),
        read_rsp_line(file, 'AdditionalInputReseed'),
        ('AdditionalInput', read_rsp_line(file, 'AdditionalInput')[1]),
        ('AdditionalInput_', read_rsp_line(file, 'AdditionalInput')[1]),
        read_rsp_line(file, 'ReturnedBits'),
    ])


class TestDRBG(unittest.TestCase):
    def _assert_lengths(self, chunk, lengths):
        for name, value in chunk.items():
            alias = name.removesuffix('_').removesuffix('Reseed')
            if bit_length := lengths.get(alias):
                self.assertEqual(len(value), bit_length // 8, f"{name=}")

    @parameterized.expand(('256', '384', '512'))
    def test_drbg_no_reseed_sha2(self, sha):
        digestmod = SpecHashDefinitions[f'SHA2_{sha}']

        path = drbgtestvectors_dir.joinpath('HMAC_DRBG_no_reseed.rsp')
        with path.open() as file:
            # move to the first SHA-{sha} section
            for line in file:
                if line == f'[SHA-{sha}]\n':
                    break
            else:
                raise ValueError

            for case in range(16):
                with self.subTest(case=case):
                    if case:
                        self.assertEqual(file.readline(), f'[SHA-{sha}]\n')
                    config = read_rsp_config(file)
                    self.assertEqual(file.readline(), '\n')
                    for count in range(15):
                        with self.subTest(count=count):
                            chunk = read_no_reseed_rsp_chunk(file)
                            self.assertEqual(file.readline(), '\n')
                            self.assertEqual(chunk['COUNT'], count)
                            self._assert_lengths(chunk, config)

                            r = DRBGRandom(
                                digestmod,
                                chunk['EntropyInput'],
                                chunk['Nonce'],
                                chunk['PersonalizationString'],
                            )
                            r.generate(
                                config['ReturnedBitsLen'] // 8,
                                chunk['AdditionalInput'],
                            ).hex()
                            randbytes = r.generate(
                                config['ReturnedBitsLen'] // 8,
                                chunk['AdditionalInput_'],
                            )
                            self.assertEqual(randbytes, chunk['ReturnedBits'])

    @parameterized.expand(('256', '384', '512'))
    def test_drbg_pr_false_sha2(self, sha):
        digestmod = SpecHashDefinitions[f'SHA2_{sha}']

        path = drbgtestvectors_dir.joinpath('HMAC_DRBG_pr_false.rsp')
        with path.open() as file:
            # move to the first SHA-{sha} section
            for line in file:
                if line == f'[SHA-{sha}]\n':
                    break
            else:
                raise ValueError

            for case in range(16):
                with self.subTest(case=case):
                    if case:
                        self.assertEqual(file.readline(), f'[SHA-{sha}]\n')
                    config = read_rsp_config(file)
                    self.assertEqual(file.readline(), '\n')
                    for count in range(15):
                        with self.subTest(count=count):
                            chunk = read_reseed_rsp_chunk(file)
                            self.assertEqual(file.readline(), '\n')
                            self.assertEqual(chunk['COUNT'], count)
                            self._assert_lengths(chunk, config)

                            r = DRBGRandom(
                                digestmod,
                                chunk['EntropyInput'],
                                chunk['Nonce'],
                                chunk['PersonalizationString'],
                            )
                            r.reseed(
                                chunk['EntropyInputReseed'],
                                chunk['AdditionalInputReseed'],
                            )
                            r.generate(
                                config['ReturnedBitsLen'] // 8,
                                chunk['AdditionalInput'],
                            )
                            randbytes = r.generate(
                                config['ReturnedBitsLen'] // 8,
                                chunk['AdditionalInput_'],
                            )
                            self.assertEqual(randbytes, chunk['ReturnedBits'])
