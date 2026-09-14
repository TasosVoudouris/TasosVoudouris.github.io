from __future__ import annotations
from typing import NamedTuple, Union, Optional, Tuple
from mclbn256 import Fr, G1, G2, GT


def add_G1(ct1: CTG1, ct2: CTG1) -> CTG1:
    """Homomorphically add two G1 ciphertexts in level 1."""
    return CTG1(
        ct1.g1r + ct2.g1r,
        ct1.g1m_pr + ct2.g1m_pr
    )


def add_G2(ct1: CTG2, ct2: CTG2) -> CTG2:
    """Homomorphically add two G2 ciphertexts in level 1."""
    return CTG2(
        ct1.g2r + ct2.g2r,
        ct1.g2m_pr + ct2.g2m_pr
    )


def add_GT(ct1: CTGT, ct2: CTGT) -> CTGT:
    """Homomorphically add two GT ciphertexts in level 2."""
    return CTGT(
        ct1.z_r1_r2 * ct2.z_r1_r2,  # multiply because the m's we want to add are up in powers of z1
        ct1.z_m2_s2_r2__r1 * ct2.z_m2_s2_r2__r1,
        ct1.z_m1_s1_r1__r2 * ct2.z_m1_s1_r1__r2,
        ct1.z_m1_s1_r1__m2_s2_r2 * ct2.z_m1_s1_r1__m2_s2_r2
    )


def multiply_G1_G2(ct1: CTG1, ct2: CTG2) -> CTGT:
    """
    Homomorphically multiply two complementary level-1 ciphertexts
    and return a level-2 ciphertext of their product.
    """
    return CTGT(
        ct1.g1r @ ct2.g2r,  # z1 ** (r1 * r2)
        ct1.g1r @ ct2.g2m_pr,  # z1 ** (r1 * (m2 + (r2 * s2))) = z1 ** ((m2 + (s2 * r2)) * r1)
        ct1.g1m_pr @ ct2.g2r,  # z1 ** ((m1 + (s1 * r1)) * r2)
        ct1.g1m_pr @ ct2.g2m_pr  # e((g1 * m1) + (p1 * r1), (g2 * m2) + (p2 * r2))
                                 # = e((g1 * m1) + (g1 * s1 * r1), (g2 * m2) + (g2 * s2 * r2))
                                 # = e((g1 * m1) + (g1 * (s1 * r1)), (g2 * m2) + (g2 * (s2 * r2)))
                                 # = e(g1 * (m1 + (s1 * r1))), g2 * (m2 + (s2 * r2)))
                                 # = e(g1 * (m1 + (s1 * r1))), g2) ** (m2 + (s2 * r2))
                                 # = e(g1, g2) ** (m1 + (s1 * r1)) ** (m2 + (s2 * r2))
                                 # = z1 ** ((m1 + (s1 * r1)) * (m2 + (s2 * r2)))
                                 # = z1 ** (
                                 #     (m2 * r1 * s1) +
                                 #     (m1 * r2 * s2) +
                                 #     (r1 * r2 * s1 * s2) +
                                 #     (m1 * m2)
                                 #   )
                                 # = z1 ** (m2 * r1 * s1)
                                 # * z1 ** (m1 * r2 * s2)
                                 # * z1 ** (r1 * r2 * s1 * s2)
                                 # * z1 ** (m1 * m2)
        # dec: m1m2 = (r1r2)(s1s2) + r1(m2+s2r2)(-s1) + r2(m1+s1r1)(-s2) + (m1+s1r1)(m2+s2r2)
    )


class CTG1(NamedTuple):
    """Ciphertext in strictly `G1 x G1` only."""
    g1r: G1
    g1m_pr: G1

    def __add__(self: CTG1, other: CTG1) -> CTG1:
        return add_G1(self, other)

    def __mul__(self: CTG1, other: Union[CTG2, Fr, int]) -> CTG1 | CTGT:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CTG1(
                    self.g1r * other,
                    self.g1m_pr * other
                )
        else:
            return multiply_G1_G2(self, other)

    def __rmul__(self: CTG1, other: Union[Fr, int]) -> CTG1:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CTG1(
                self.g1r * other,
                self.g1m_pr * other
            )

    def __neg__(self: CTG1) -> CTG1:
        return self * -1


class CTG2(NamedTuple):
    """Ciphertext in strictly `G2 x G2` only."""
    g2r: G2
    g2m_pr: G2

    def __add__(self: CTG2, other: CTG2) -> CTG2:
        return add_G2(self, other)

    def __mul__(self: CTG2, other: Union[CTG1, Fr, int]) -> CTG2 | CTGT:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CTG2(
                    self.g2r * other,
                    self.g2m_pr * other
                )
        else:
            return multiply_G1_G2(other, self)

    def __rmul__(self: CTG2, other: Union[Fr, int]) -> CTG2:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CTG2(
                self.g2r * other,
                self.g2m_pr * other
            )

    def __neg__(self: CTG2) -> CTG2:
        return self * -1


class CTGT(NamedTuple):
    """Level-2 ciphertext in $\textsf{GT}^{4}$."""
    z_r1_r2: GT
    z_m2_s2_r2__r1: GT
    z_m1_s1_r1__r2: GT
    z_m1_s1_r1__m2_s2_r2: GT

    def __add__(self: CTGT, other: CTGT) -> CTGT:
        return add_GT(self, other)

    # def __mul__(self: CTG1, other: Fr):
    #     return multiply_constant_GT_Fr(self, other)
    def __mul__(self: CTG1, other: Union[Fr, int]) -> Optional[CTGT]:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CTGT(
                self.z_r1_r2 ** other,
                self.z_m2_s2_r2__r1 ** other,
                self.z_m1_s1_r1__r2 ** other,
                self.z_m1_s1_r1__m2_s2_r2 ** other
            )

    def __rmul__(self: CTGT, other: Union[Fr, int]) -> Optional[CTGT]:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CTGT(
                self.z_r1_r2 ** other,
                self.z_m2_s2_r2__r1 ** other,
                self.z_m1_s1_r1__r2 ** other,
                self.z_m1_s1_r1__m2_s2_r2 ** other
            )

    def __neg__(self: CTGT) -> CTGT:
        return self * -1


class CT1(NamedTuple):
    """All-purpose (dual) level-1 ciphertext making use of both G1 and G2."""
    ctg1: CTG1
    ctg2: CTG2

    def __add__(self: CT1, other: CT1) -> CT1:
        return CT1(
            self.ctg1 + other.ctg1,
            self.ctg2 + other.ctg2
        )

    def __mul__(self: CT1, other: Union[CT1, Fr, int]) -> CT1 | CT2:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CT1(
                self.ctg1 * other,
                self.ctg2 * other
            )
        else:
            ct = multiply_G1_G2(other.ctg1, self.ctg2)
            return CT2(
                ct or multiply_G1_G2(self.ctg1, other.ctg2)
            )
            # `or` just in case first product is corrupted

    def __rmul__(self: CT1, other: Union[Fr, int]) -> CT1:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CT1(
                self.ctg1 * other,
                self.ctg2 * other
            )

    def __neg__(self: CT1) -> CT1:
        return CT1(
            -self.ctg1,
            -self.ctg2
        )


class CT2(NamedTuple):
    """Level-2 ciphertext (wrapper around GT^4)."""
    ctgt: CTGT

    def __add__(self: CT2, other: CT2) -> CT2:
        return CT2(self.ctgt + other.ctgt)

    def __mul__(self: CT2, other: Union[Fr, int]) -> CT2:
        if type(other) == int:
            other = Fr(other)
        if type(other) == Fr:
            if int(other) == 1:
                return self
            return CT2(
                self.ctgt * other
            )
        raise TypeError("Cannot perform constant multiplication with these operands.")

    def __rmul__(self: CT1, other: Union[Fr, int]) -> CT1:
        return self.__mul__(other)


class KPG1(NamedTuple):
    """Keypair for G1-based encryption."""
    sk: Fr  # secret scalar
    pk: G1  # public point (in Group 1)


class KPG2(NamedTuple):
    """Keypair for G2-based encryption."""
    sk: Fr  # secret scalar
    pk: G2  # public point (in Group 2)


class SK(NamedTuple):
    """Dual secret key for decryption"""
    s1: Fr  # secret scalar
    s2: Fr


class PK(NamedTuple):
    """Dual public key for encryption (either 'dumb' group-agnostic, or optimal)"""
    p1: G1  # public point (in Group 1)
    p2: G2  # public point (in Group 2)
#   z2: GT# = g1 @ p2
#   z3: GT# = p1 @ g2
#   z4: GT# = p1 @ p2


g1 = G1().hash("Fixed public point in Group 1")
g2 = G2().hash("Fixed public point in Group 2")
z1 = g1 @ g2  # z a.k.a. z1 is the pairing of the two generators
#               and is also a generator in its own right, for GT.
