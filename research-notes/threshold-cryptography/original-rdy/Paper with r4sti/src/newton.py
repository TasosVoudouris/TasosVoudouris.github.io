from interpolation import Interpolation
import operator

class Newton(Interpolation):
    def __init__(self, p, precomputed=False):
        super().__init__(p)
        self.precomputed = precomputed
        self.diffs = []
    
    def toggle_precomputed(self, precomputed):
        self.precomputed = precomputed
        self.diffs = []

    def newton_interpolation(self, shares, optimized=False):
        if not self.diffs or not self.precomputed:
            self.diffs = self.PR.divided_difference(shares, full_table=True)
        else:
            self.diffs = self.precomputed_divided_differences(shares, self.diffs)
            
        diffs = list(map(operator.itemgetter(-1), self.diffs))

        X, _ = zip(*shares)
        x = 0 if optimized else self.x

        N = diffs[len(shares)-1]
        for i in range(len(shares)-2, -1, -1):
            N = N * (x - X[i]) + diffs[i]

        return N
    
    def precomputed_divided_differences(self, shares, diffs):
        X, Y = zip(*shares)

        i = len(Y) - 1
        diffs.append([Y[i]])  # append y of the last share

        for j in range(1, i+1):
            numer = diffs[i][j-1] - diffs[i-1][j-1]
            denom = X[i] - X[i-j]
            diffs[i].append(numer / denom)  # equivalent to precomputed[-1].append()
        
        return diffs