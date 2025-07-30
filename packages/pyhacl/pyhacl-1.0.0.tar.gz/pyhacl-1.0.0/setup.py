import os
import platform

from Cython.Build import cythonize
from setuptools import Extension, find_namespace_packages, setup

with open('README.rst', encoding='utf-8') as file:
    long_description = file.read()

_build = 'msvc' if platform.system() == 'Windows' else 'gcc'
hacl_src_dir = f'hacl-star/dist/{_build}-compatible'
hacl_include_dirs = [
    hacl_src_dir,
    hacl_src_dir + '/internal',
    'hacl-star/dist/karamel/include',
    'hacl-star/dist/karamel/include/krml',
    'hacl-star/dist/karamel/include/krml/internal',
    'hacl-star/dist/karamel/krmllib/dist/minimal',
]

setup(
    name='pyhacl',
    version='1.0.0',
    description="Python binding to the HACL* library",
    long_description=long_description,
    author='Julien Castiaux',
    author_email='julien.castiaux@mailfence.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Security :: Cryptography',
    ],
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    license='Apache-2.0',
    package_data={
        'pyhacl': [
            'hacl_star',
        ],
    },
    install_requires=[
        'cython>=3.1',
    ],
    extras_require={
        'dev': [
            'build',
            'parameterized',
            'sphinx',
            'furo',
        ]
    },
    python_requires='>=3.10',
    project_urls={
        "Download": "https://pypi.org/project/pyhacl/",
        "Repository": "https://codeberg.org/drlazor8/pyhacl",
        "Documentation": "https://pyhacl.readthedocs.io/en/latest/",
    },
    ext_modules=cythonize(
        [
            Extension(
                name='pyhacl.aead.chacha_poly1305',
                sources=[
                    'src/pyhacl/aead/chacha_poly1305.py',
                    f'{hacl_src_dir}/Hacl_AEAD_Chacha20Poly1305.c',
                    f'{hacl_src_dir}/Hacl_Chacha20.c',
                    f'{hacl_src_dir}/Hacl_MAC_Poly1305.c',
                ],
                include_dirs=hacl_include_dirs,
            ),
            Extension(
                name='pyhacl.hashlib.sha2',
                sources=[
                    'src/pyhacl/hashlib/sha2.py',
                    f'{hacl_src_dir}/Hacl_Hash_SHA2.c',
                ],
                include_dirs=hacl_include_dirs,
            ),
            Extension(
                name='pyhacl.diffie_hellman.curve25519',
                sources=[
                    'src/pyhacl/diffie_hellman/curve25519.py',
                    f'{hacl_src_dir}/Hacl_Curve25519_51.c',
                ],
                include_dirs=hacl_include_dirs,
            ),
            Extension(
                name='pyhacl.signature.ed25519',
                sources=[
                    'src/pyhacl/signature/ed25519.py',
                    f'{hacl_src_dir}/Hacl_Ed25519.c',
                    f'{hacl_src_dir}/Hacl_Hash_SHA2.c',
                    f'{hacl_src_dir}/Hacl_Curve25519_51.c',
                ],
                include_dirs=hacl_include_dirs,
            ),
            Extension(
                name='pyhacl.signature.p256',
                sources=[
                    'src/pyhacl/signature/p256.py',
                    f'{hacl_src_dir}/Hacl_P256.c',
                    f'{hacl_src_dir}/Hacl_Hash_SHA2.c',
                ],
                include_dirs=hacl_include_dirs,
            ),
            Extension(
                name='pyhacl.hmac',
                sources=[
                    'src/pyhacl/hmac.py',
                    f'{hacl_src_dir}/Hacl_Hash_Blake2b.c',
                    f'{hacl_src_dir}/Hacl_Hash_Blake2s.c',
                    f'{hacl_src_dir}/Hacl_Hash_MD5.c',
                    f'{hacl_src_dir}/Hacl_Hash_SHA1.c',
                    f'{hacl_src_dir}/Hacl_Hash_SHA2.c',
                    f'{hacl_src_dir}/Hacl_Hash_SHA3.c',
                    f'{hacl_src_dir}/Hacl_HMAC.c',
                    f'{hacl_src_dir}/Lib_Memzero0.c',
                ],
                include_dirs=hacl_include_dirs,
            ),
            Extension(
                name='pyhacl.drbg',
                sources=[
                    'src/pyhacl/drbg.py',
                    f'{hacl_src_dir}/Hacl_HMAC_DRBG.c',
                    f'{hacl_src_dir}/Hacl_Hash_Blake2b.c',
                    f'{hacl_src_dir}/Hacl_Hash_Blake2s.c',
                    f'{hacl_src_dir}/Hacl_Hash_MD5.c',
                    f'{hacl_src_dir}/Hacl_Hash_SHA1.c',
                    f'{hacl_src_dir}/Hacl_Hash_SHA2.c',
                    f'{hacl_src_dir}/Hacl_Hash_SHA3.c',
                    f'{hacl_src_dir}/Hacl_HMAC.c',
                    f'{hacl_src_dir}/Lib_Memzero0.c',
                ],
                include_dirs=hacl_include_dirs,
            ),
        ],
        annotate=True,
        language_level='3',
        nthreads=os.cpu_count(),
    ),
)
