def prime_form(D,p):
    """ Given an imaginary quadratic discrimint D and a prime p returns a binary quadratic form (p,b,c) of discriminant D or None if no such form exists """
    assert D < 0 and D%4 in (0,1) and is_prime(p)
    u = D/fundamental_discriminant(D)
    print(u)
    if u%p == 0 or kronecker(D,p) < 0:
        return None
    if kronecker(D,p) == 0:
        if p == 2 and D%4 == 0 and D%8 != 0:
            return (2,2,(4-D)//(4*p))
        return (p,0,-D//(4*p)) if D%4 == 0 else (p,p,(p^2-D)//(4*p))
    b = ZZ(Integers(4*p)(D).sqrt())
    if b >= 2*p:
        b = 4*p-b
    return (p,b,(b^2-D)//(4*p))

print(prime_form(-2267,2^66+9))