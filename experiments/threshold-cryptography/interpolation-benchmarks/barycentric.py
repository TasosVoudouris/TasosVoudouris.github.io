from interpolation import Interpolation

class Barycentric(Interpolation):
    def __init__(self, p, precomputed=False):
        super().__init__(p)
        self.precomputed = precomputed
        self.W = []

    def toggle_precomputed(self, precomputed):
        self.precomputed = precomputed
        self.W = []

    def weight(self, j, X):
        W = 1
        for k in range(len(X)): 
            if j != k:
                W *= (X[j] - X[k])
        return 1 / W
    
    def update_weight(self, j, X):
        return self.W[j] / (X[j] - X[-1])
    
    def barycentric_interpolation(self, shares, optimized=False):
        X, Y = zip(*shares)

        numer = 0
        denom = 0
        common = 0

        if not self.W or not self.precomputed:
            self.W = [self.weight(j, X) for j in range(len(shares))]
        else:
            new_j = len(shares)
            self.W = [self.update_weight(j, X) for j in range(len(self.W))]
            self.W.append(self.weight(new_j-1, X))

        W = self.W

        x = 0 if optimized else self.x

        for j in range(len(shares)):
            common = (W[j] / (x - X[j]))
            numer += common * Y[j]
            denom += common
        return numer / denom