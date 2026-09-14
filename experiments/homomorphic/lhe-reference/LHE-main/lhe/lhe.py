# pylint: disable=C0103# to allow capital letters in method signatures
"""
Python homomorphic encryption library supporting up
to three multiplications and unlimited additions.
"""
from algebra import *
from dlog import dlog

def keygen_G1() -> Tuple[Fr, G1]:
    """Generate a G1 keypair."""
    s = Fr()
    p = g1 * s
    return KPG1(s, p)


def keygen_G2() -> KPG2:
    """Generate a G2 keypair."""
    s = Fr()
    p = g2 * s
    return KPG2(s, p)


def keygen() -> Tuple[SK, PK]:
    """Generate a dual keypair."""
    s1, p1 = keygen_G1()
    s2, p2 = keygen_G2()
    return SK(s1, s2), PK(p1, p2)


def encrypt_G1(p: G1, m: int) -> CTG1:
    """Encrypt a plaintext to be a G1 ciphertext."""
    r = Fr()
    return CTG1(
        g1 * r,
        (g1 * Fr(m)) + (p * r)
    )


def encrypt_G2(p: G2, m: int) -> CTG2:
    """Encrypt a plaintext to be a G2 ciphertext."""
    r = Fr()
    return CTG2(
        g2 * r,
        (g2 * Fr(m)) + (p * r)
    )


def encrypt_GT(p1: G1, p2: G2, m: int) -> CTGT:
    """
    Encrypt a plaintext to be a GT ciphertext.

    Each such ciphertext is made of the components
    z1 ** (-t + r + s)
    z1 ** (r * s2)
    z1 ** (s * s1)
    z1 ** (m + (t * s1 * s2))
    from which (given the secrets, s1 and s2) you can compute
    z1 ** s and z1 ** r, then subtract from the first to get
    z1 ** -t which can then yield z1 ** (-t * s1 * s2), the
    inverse of everything in z1 ** (m + (t * s1 * s2)) except
    z1 ** m.  m is finally extracted by a d.log. computation.
    """
    r = Fr()  # random scalar
    s = Fr()  # random scalar
    t = Fr()  # random scalar
    # z1  = g1 @ g2     # z1 := e(g1, g2); constant/static global/public scalar
    z1_s2 = g1 @ p2     # e(g1, p2) = e(g1, g2 * s2) = e(g1, g2) ** s2 = z1 ** s2
    z1_s1 = p1 @ g2     # e(p1, g2) = e(g1 * s1, g2) = e(g1, g2) ** s1 = z1 ** s1
    z1_s1_s2 = p1 @ p2  # e(p1, p2) = e(g1 * s1, g2 * s2) = e(g1, g2) ** s1 ** s2 = z1 ** s1 ** s2
    return CTGT(
        z1 ** (r + s - t),             # z1 ** (r + s - t)
        z1_s2 ** r,                    # z1 ** (r * s2)
        z1_s1 ** s,                    # z1 ** (s * s1)
        z1_s1_s2 ** t * (z1 ** Fr(m))  # z1 ** (m + (t * s1 * s2))
    )



def encrypt(pk: PK, m: int) -> CT1:
    """Encrypt a plaintext to be a dual ('dumb') ciphertext."""
    ct1 = encrypt_G1(pk.p1, m)
    ct2 = encrypt_G2(pk.p2, m)
    return CT1(ct1, ct2)




def encrypt_lvl_1(pk: PK, m: int) -> CT1:
    """Encrypt a plaintext to be a dual ('dumb') ciphertext."""
    ct1 = encrypt_G1(pk.p1, m)
    ct2 = encrypt_G2(pk.p2, m)
    return CT1(ct1, ct2)



def encrypt_lvl_2(pk: PK, m: int) -> CT2:
    """Encrypt a level-2 ciphertext."""
    ct = encrypt_GT(pk.p1, pk.p2, m)
    return CT2(ct)





def decrypt_G1(s1: Fr, ct: CTG1) -> Optional[int]:
    """
    Decrypt a G1 ciphertext to a plaintext.

    >>> sk, pk = keygen_G1()
    >>> ct = encrypt_G1(pk, 737)
    >>> print(decrypt_G1(sk, ct))
    737
    """
    g1m = ct.g1m_pr - (ct.g1r * s1)  # remember, p = g^s
    return dlog(g1, g1m)


def decrypt_G2(s2: Fr, ct: CTG2) -> Optional[int]:
    """
    Decrypt a G2 ciphertext to a plaintext.

    >>> sk, pk = keygen_G2()
    >>> ct = encrypt_G2(pk, 747)
    >>> int(decrypt_G2(sk, ct))
    747
    """
    g2m = ct.g2m_pr - (ct.g2r * s2)  # remember, p = g^s
    return dlog(g2, g2m)


def decrypt_GT(s1: Fr, s2: Fr, ct: CTGT):
    """
    Decrypt a level-2 ciphertext.

    >>> sk1, pk1 = keygen_G1()
    >>> sk2, pk2 = keygen_G2()

    >>> ct11 = encrypt_G1(pk1, 1)
    >>> ct12 = encrypt_G1(pk1, 2)
    >>> ct21 = encrypt_G2(pk2, 200)
    >>> ct22 = encrypt_G2(pk2, 22)

    >>> ct1 = ct11 + ct12
    >>> ct2 = ct21 + ct22

    >>> ct3 = ct1 * ct2

    >>> pt = decrypt_GT(sk1, sk2, ct3)
    >>> int(pt)
    666

    >>> sk, pk = keygen()

    >>> ct_1 = encrypt_lvl_1(pk, 1)
    >>> ct_2 = encrypt_lvl_1(pk, 2)
    >>> ct_200 = encrypt_lvl_1(pk, 200)
    >>> ct_22 = encrypt_lvl_1(pk, 22)

    >>> ct_3 = ct_1 + ct_2
    >>> ct_222 = ct_200 + ct_22

    >>> ct_666 = ct_3 * ct_222

    >>> pt = decrypt(sk, ct_666)
    >>> int(pt)
    666

    The goal is to unmask the last ciphertext component and get z1 ** (m1 * m2).

    Note that that component,
    z1 ** ((m1 + (s1 * r1)) * (m2 + (s2 * r2))),
    expands to equal
     = z1 ** (m2 * r1 * s1)
     * z1 ** (m1 * r2 * s2)
     * z1 ** (r1 * r2 * s1 * s2)
     * z1 ** (m1 * m2)
     for whose terms we already have the ingredients to construct.

    The z1 ** (r1 * r2 * s1 * s2) specifically cancels the last negative term
    in the ct.z_m2_s2_r2__r1 by ct.z_m1_s1_r1__r2 product.

    We have z1 to the power of,
    (m2 + r1 s1)(m1 + r2 s2) = (m1 m2) + (m1 r1 s1) + (m2 r2 s2) + (r1 r2 s1 s2).

    And z1 to the power of,
    (r1 r2)(s1 s2) + r1 (m1 + r2 s2)(-s1) + r2 (m2 + r1 s1)(-s2) = -(m1 r1 s1) + -(m2 r2 s2) + -(r1 r2 s2 s1).

    Thus, we may decrypt by add these exponents (by multiplying powers) to get m1*m2
    which can be extracted by a discrete log.
    """
    z1_m1_m2 = \
        (ct.z_r1_r2 ** (s1 * s2)) * \
        (ct.z_m2_s2_r2__r1 ** (-s1)) * \
        (ct.z_m1_s1_r1__r2 ** (-s2)) * \
        ct.z_m1_s1_r1__m2_s2_r2
    return dlog(z1, z1_m1_m2)


def decrypt(sk: SK, ct: Union[CT1, CT2, CTG1, CTG2, CTGT]) -> Fr:
    """
    Type-generic decryption helper

    >>> sk, pk = keygen()

    >>> pt_m = Fr() % (2 ** 12)
    >>> m = int(pt_m)
    >>> 0 <= m < 2 ** 12
    True

    >>> decrypt(sk, encrypt_G1(pk.p1, m)) == pt_m
    True

    >>> decrypt(sk, encrypt_G2(pk.p2, m)) == pt_m
    True

    >>> decrypt(sk, encrypt_GT(pk.p1, pk.p2, m)) == pt_m
    True

    >>> decrypt(sk, encrypt_lvl_1(pk, m)) == pt_m
    True

    >>> decrypt(sk, encrypt_lvl_2(pk, m)) == pt_m
    True

    """
    if type(ct) is CT2:
        return decrypt_GT(sk.s1, sk.s2, ct.ctgt)
    if type(ct) is CT1:
        pt = decrypt_G1(sk.s1, ct.ctg1)
        return pt or decrypt_G2(sk.s2, ct.ctg2)
        # `or` in case maybe one of them got corrupted?
    if type(ct) is CTGT:
        return decrypt_GT(sk.s1, sk.s2, ct)
    if type(ct) is CTG1:
        return decrypt_G1(sk.s1, ct)
    if type(ct) is CTG2:
        return decrypt_G2(sk.s2, ct)








