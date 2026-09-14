"""Legacy prime192v1/secp192r1 domain parameters for educational examples.

The curve provides about 96 bits of classical security and is retained only to
match the supplied CryptoSage material. Do not select it for a new deployment.
"""

FIELD_PRIME = Integer(2) ** 192 - Integer(2) ** 64 - 1
CURVE_A = Integer(-3)
CURVE_B = Integer(0x64210519E59C80E70FA7E9AB72243049FEB8DEECC146B9B1)
GENERATOR_X = Integer(0x188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012)
GENERATOR_Y = Integer(0x07192B95FFC8DA78631011ED6B24CDD573F977A11E794811)
SUBGROUP_ORDER = Integer(0xFFFFFFFFFFFFFFFFFFFFFFFF99DEF836146BC9B1B4D22831)
COFACTOR = Integer(1)

BASE_FIELD = FiniteField(FIELD_PRIME)
CURVE = EllipticCurve(BASE_FIELD, [CURVE_A, CURVE_B])
GENERATOR = CURVE((GENERATOR_X, GENERATOR_Y))
SCALAR_FIELD = FiniteField(SUBGROUP_ORDER)

if SUBGROUP_ORDER * GENERATOR != CURVE(0):
    raise ValueError("invalid prime192v1 generator order")

# Short aliases preserve the mathematical notation used by the old programs.
F = BASE_FIELD
E = CURVE
P = GENERATOR
n = SUBGROUP_ORDER
h = COFACTOR
Fn = SCALAR_FIELD

