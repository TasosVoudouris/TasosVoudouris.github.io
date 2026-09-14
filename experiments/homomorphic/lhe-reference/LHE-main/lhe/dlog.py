from mclbn256 import Fr, G1, G2, GT
from typing import Union, Optional

def dlog(base: Union[Fr, G1, G2, GT], power: GT, unsigned=False) -> Optional[Fr]:
    """
    Discrete logarithm on any group, either Fr, G1, G2, or GT.

    Can work with up to 20-bits before giving up.  The example below
    tests 16-bit exponents of each type (for efficiency).

    This helper may be replaced with Pollard's Kangaroo method for
    a big boost (~2x) in performance.  That optimization is unimplemented.
    Alternatively, we may use a lookup table.

    >>> x = Fr()
    >>> a = Fr() % (2 ** 16)
    >>> dlog(x, x ** a) == a
    True

    >>> x = G1().randomize()
    >>> a = Fr() % (2 ** 16)
    >>> y = x * a
    >>> dlog(x, y) == a
    True

    >>> x = G2().randomize()
    >>> a = Fr() % (2 ** 16)
    >>> y = x * a
    >>> dlog(x, y) == a
    True

    >>> x = G1().randomize() @ G2().randomize()
    >>> a = Fr() % (2 ** 16)
    >>> y = x ** a
    >>> dlog(x, y) == a
    True
    """
    domain = range(pow(2, 20)) if unsigned else \
        [e for i in range(pow(2, 20)) for e in (i, -i)]
    try:
        for exponent in map(Fr, domain):
            if base ** exponent == power:
                return exponent
    except TypeError:
        for exponent in map(Fr, domain):
            if base * exponent == power:
                return exponent
    # raise ValueError("No such exponent.")
    return None