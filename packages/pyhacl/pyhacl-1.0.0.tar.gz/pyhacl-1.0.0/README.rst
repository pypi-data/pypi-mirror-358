pyhacl
======

Cython bindings for `HACL*`_ the *High Assurance Cryptographic Library*.

Disclaimer
----------

There is this recurring blog post `Cryptographic Right Answsers`_ that
gets published every once in a while by various security experts and
security firms. Out of the many recommendations is the general advice
that people should stick with major libraries: NaCL, OpenSSL, or
whatever is available in the standard library of each programming
langage.

Altough HACL* itself is becoming a major library, this binding is
**not**. Following the above expert recommendations, you should **not**
use pyhacl. At least not until it has been formally reviewed.

Please instead use PyCA's `PyNaCl`_ or `cryptography`_ which are the
official python bindings for NaCL and OpenSSL respectively.

Contributions welcome
---------------------

We limited this binding to the portable C functions of HACL*, please get
in touch with us by email or via codeberg if you need anything that's
available in HACL* but that's missing from pyhacl.

.. _HACL*: https://hacl-star.github.io/index.html
.. _Cryptographic Right Answsers: https://www.latacora.com/blog/2018/04/03/cryptographic-right-answers/
.. _cryptography: https://cryptography.io/en/latest/
.. _PyNaCl: https://pynacl.readthedocs.io/en/latest/
