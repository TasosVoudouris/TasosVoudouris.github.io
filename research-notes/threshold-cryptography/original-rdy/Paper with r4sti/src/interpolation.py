from sage.all import *

class Interpolation:
    def __init__(self, p):
        self.p = p
        self.PR = PolynomialRing(GF(p), 'x')
        self.F = GF(self.p)
        self.x = self.PR.gens()[0]
        self.g = self.F(3)

    def gen_poly(self, d):
        key = int.from_bytes(os.urandom(16), byteorder='big')
        coeffs = [key] + [self.F.random_element() for _ in range(d)]
        self.P = self.PR(coeffs)
        return self.P

    def set_poly(self, coeffs):
        self.P = self.PR(coeffs)

    def compute_shares(self, n):
        return [(self.F(i), self.P(i)) for i in range(1, n+1)]

    def nrou(self, n):
        return self.g**((self.p-1)//n)