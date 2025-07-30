R"""
Python (Cython) bindings for `HACL`_ *A High Assurance Cryptographic Library*.

.. _HACL: https://hacl-star.github.io/
"""


class HACLError(Exception):
    """
    Error class used when any underlying C function returned an error
    code. The message in ``args[0]`` indicates what went wrong.
    """
