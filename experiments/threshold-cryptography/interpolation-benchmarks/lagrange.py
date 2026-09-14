from interpolation import Interpolation

class Lagrange(Interpolation):
    def __init__(self, p):
        super().__init__(p)
    
    def L(self, i, X):
        numer = 1
        denom = 1
        for j in range(len(X)):
            if j != i:
                numer *= (self.x - X[j])
                denom *= (X[i] - X[j])
        return numer / denom

    def lagrange_interpolation(self, shares, optimized=False):
        F = 0
        X, Y = zip(*shares)
        for i in range(len(Y)):
            L = self.optimized_L(i, X) if optimized else self.L(i, X)
            F += Y[i] * L
        return F

    def optimized_L(self, i, X):
        numer = 1
        denom = 1
        for j in range(len(X)):
            if j != i:
                numer *= (0 - X[j])
                denom *= (X[i] - X[j])
        return numer / denom