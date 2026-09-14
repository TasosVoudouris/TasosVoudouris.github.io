def norm_equation(D,p):
    """ Solves the norm equation 4p=t^2-v^2D for t and v given D and a probable prime p.  Either returns a solution (t,v) or () if no solution exists """
    assert D < 0 and D%4 in (0,1) and is_pseudoprime(p)
    if -D >= 4*p: return ()
    if p==2: return (ZZ(sqrt(D+8)),1) if is_square(D+8) else ()
    if kronecker(D,p) == -1: return ()
    F=GF(p,proof=false)
    x0=F(D).sqrt().lift()
    assert not (x0^2 - D) % p  # just in case p isn't prime
    if (x0-D)%2: x0 = p - x0
    a,t,m = 2*p, x0, integer_floor(2*sqrt(p))
    while t > m: a,t=t,a%t
    if (4*p-t^2) % (-D): return ()
    c = (4*p-t^2)//(-D)
    if not is_square(c): return ()
    v=sqrt(c)
    assert 4*p == t^2-v^2*D
    return (t,v)

print(norm_equation(-2267,2^66+9))