# Given curve parameters and points
p = 1331169830894825846283645180581
a = -35
b = 98
E = EllipticCurve(GF(p), [a,b])
G = E(479691812266187139164535778017, 568535594075310466177352868412)
A = E(1110072782478160369250829345256, 800079550745409318906383650948)



#curve = EllipticCurve(GF(22216045306240170001), [15703735179364572855, 10469156786243048570])
#gen = curve.gen(1)
#n = int(gen.order())
#l = randint(1, n - 1)



# Estimate a possible range for embedding degree k
log_p = log(p, 2).n(digits = 10)
G_order = G.order()
k = 1
for i in range(1, int(log_p)):
    if pow(p, i, G_order) == 1:
        k = i
        break


def MOV(E, P, Q, k, p):
    """
    Solves ECDLP: Find n such that Q = nP using the MOV attack.

    Parameters:
    -----------
    E: EllipticCurve         -- The base elliptic curve over F_p
    P: Point                 -- Point of known order m
    Q: Point                 -- Target point, Q = nP
    k: int                  -- Embedding degree (minimum such that m divides p^k - 1)
    p: int                  -- Prime field characteristic

    Returns:
    --------
    int: n such that Q = nP
    """
    
    # Step 1: Work over the field extension F_{p^k}
    E_k = E.base_extend(GF(p^k))
    N = E_k.order()       # Not used further, but available
    m = P.order()
    PK = E_k(P)
    QK = E_k(Q)

    while True:
        # Step 2: Select a random point T not defined over base field F_p
        T = E_k.random_point()
        try:
            # Try to coerce it into E(F_p); if it succeeds, discard
            E(*T.xy())
            continue
        except:
            pass

        # Step 3: Construct T' ∈ E[m] using T
        t = T.order()
        d = gcd(m, t)
        T_prime = (t // d) * T
        if T_prime.is_zero():
            continue  # invalid pairing input

        # Step 4: Compute Weil pairing values
        alpha = PK.weil_pairing(T_prime, m)
        if alpha == 1:
            continue  # degenerate pairing
        beta = QK.weil_pairing(T_prime, m)

        # Step 5: Solve beta = alpha^n for n in F_{p^k}*
        n = beta.log(alpha)
        break

    return n

# Recover n using the MOV attack
n = MOV(E, G, A, k, p)

# Validate solution
assert(n * G == A)

def MOV2(E, P, Q, k, p):
    """
    Generalized MOV attack: Finds n such that Q = nP using multiple pairings.

    Parameters:
    -----------
    Same as above

    Returns:
    --------
    int: n such that Q = nP
    """

    m = P.order()
    E_k = E.base_extend(GF(p**k))
    QK = E_k(Q)
    PK  = E_k(P)

    n_list = []   # collected values n_i
    d_list = []   # corresponding moduli d_i
    least_common_multiple = 1

    while least_common_multiple != m:
        # Step 1: Select a random point T on E_k
        T = E_k.random_point()
        t = T.order()
        d = gcd(t, m)
        if d in d_list:
            continue

        # Step 2: Construct T' in E[m] of order dividing m
        T_prime = (t // d) * T

        # Step 3: Compute Weil pairings
        alpha = PK.weil_pairing(T_prime, m)
        beta = QK.weil_pairing(T_prime, m)

        # Step 4: Solve DLP in µ_d ⊆ F_{p^k}^*
        n = beta.log(alpha)  # this gives n mod d
        n_list.append(n)
        d_list.append(d)

        # Track total modulus collected so far
        least_common_multiple = lcm(least_common_multiple, d)

    print(n_list)
    return n_list[-1]  # last congruence (can also CRT full system)
    # return n_list[0] if len(n_list) == 1 else crt(n_list, d_list)


n_fin = MOV2(E, G, A, k, p)

assert(n_fin * G==A)


