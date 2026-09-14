from Crypto.Util.number import inverse, sieve_base


def isqrt(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def solve_simple_eq(a, b, c, p):
    """
    Solves the equation a + bx = c mod p
    Returns c % p
    """
    c = c - a
    c = (c * inverse(b, p)) % p
    return c % p


def crt(a_list, m_list):
    """
    Chinese remainder theorem for x = a % m for a, m in zip(a_list, m_list)
    """
    x = 0
    # starting values
    a = 0
    m = 1
    for i in range(len(m_list)):
        # general solution for the first equations x = a + m * y
        # plug it in into the next equation and solve
        x = solve_simple_eq(a, m, a_list[i], m_list[i])

        a = a + m * x
        m = m * m_list[i]
        # print(a, m)
    return a, m


def order_of_elem(g: int, p: int):
    """
    Parameters:
    -----------

    g: int
        generator element of a group G
    p: int
        prime modulus

    Returns:
    --------
    int
        Order of g such that g^n = 1 mod p
    """
    N = 1
    temp = 1
    while True:
        temp = (temp * g) % p
        # print(temp)
        if temp == 1:
            break
        N += 1
    return N


def bsgs(g: int, h: int, p: int, N: int = None):
    """
    Parameters:
    -----------

    g: int
        generator
    h: int
        h = g^x
    p: int
        prime modulus
    N: int, default = None
        Order of g. Will be computed if is None

    Returns:
    --------
    int
        x such that g^x= h or None if no such x was found
    """
    # calculate order of g
    if N is None:
        N = order_of_elem(g, p)
    n = isqrt(N) + 1

    # create the collision lists
    lookup_table = {pow(g, j, p): j for j in range(n + 1)}

    c = inverse(pow(g, n, p), p)
    temp = h
    for i in range(n + 1):
        temp = h * pow(c, i, p) % p
        if temp in lookup_table:
            return i * n + lookup_table[temp]
    return None


def ph_prime_power_order(g: int, h: int, p: int, q: int = None, e: int = None):
    """
    Solves the pohlic hellman in a group of prime order.

    Parameters:
    -----------

    g: int
        generator of group
    h: int
        h = g^x
    p: int
        prime modulus
    q: int, default = None
        Order of g. Will be computed if is None
    e: int, default = None
        p^e = n
    """

    if q is None and e is None:
        order_g = order_of_elem(g, p)

        # find prime q that divides the order
        for q in sieve_base:
            if order_g % q == 0:
                break

        # write order_g = q^e
        order_g_temp = order_g
        e = 0
        while order_g_temp % q == 0:
            e += 1
            order_g_temp //= q
        assert order_g_temp == 1, "order didnt reach 1"
        assert order_g == pow(q, e), "wrong p and q"
        print("order of G %s = %s^%s" % (order_g, q, e))

    x = 0
    gamma = pow(g, pow(p, e - 1), p)  # this element has order p and generates the subgroup where we will search
    for k in range(e):
        h_k = pow(pow(g, -x, p) * h, pow(p, e - 1 - k), p)
        d_k = bsgs(gamma, h_k, p)  # search for dlp in the subgroup
        x = x + pow(p, k) * d_k

    assert pow(g, x, p) == h, "x not found"
    return x, q, e

g = 5448
h = 6909
p = 11251

x, q, e = ph_prime_power_order(g, h, p)

print(pow(g, x, p) == h)

def pohlig_hellman(g: int, h: int, p: int):
    """
    Solves the pohlic hellman in a group of prime order.

    Parameters:
    -----------

    g: int
        generator of group
    h: int
        h = g^x
    p: int
        prime modulus
        
    Returns:
    --------
    int
        x such that g^x = h mod p
    """
        
    # find the prime factors
    q_list = []
    e_list = []
    a_list = []
    m_list = []
    order_g = order_of_elem(g, p)
    for q in sieve_base:
        if order_g % q != 0:
            continue
        else:
            order_g_temp = order_g
            e = 0
            while order_g_temp % q == 0:
                e += 1
                order_g_temp //= q
            q_list.append(q)
            e_list.append(e)
            x_i, _, _ = ph_prime_power_order(g, h, p, q, e)
            a_list.append(x_i)
            m_list.append(pow(q, e))

    x, m = crt(a_list, m_list)

    return x

g = 23
p = 11251
h = 9689
x = pohlig_hellman(g, h, p)

print(pow(g, x, p), pow(g, x, p) == h)
