from interpolation import Interpolation

class Fourier(Interpolation):
    def __init__(self, p):
        super().__init__(p)
        self.precomputed = False
        self.Ω = {}

    def toggle_precomputed(self):
        self.precomputed = not self.precomputed

    def precompute_nrous(self, nmax):
        for i in range(nmax+1):
            self.Ω[2**i] = self.nrou(2**i)
            self.Ω[-2**i] = self.nrou(-2**i)

    def fft_2(self, C, INV=False):
        n = len(C)
        if n == 1:
            return C
        
        F0 = self.fft_2(C[::2], INV)
        F1 = self.fft_2(C[1::2], INV)

        if self.precomputed:
            ω = self.Ω[-n if INV else n]
        else:
            ω = self.nrou(-n if INV else n)
        
        y = [0] * n
        for k in range(n//2):
            y[k]        = F0[k] + ω**k * F1[k]
            y[k + n//2] = F0[k] - ω**k * F1[k]

        return y
    
    def ifft_2(self, shares):
        n = len(shares)

        inv_fft = self.fft_2(shares, True)

        C = [inv_fft[k] / n for k in range(n)]
        
        return self.PR(C)

    def fft_3(self, C):
        n = len(C)
        if n == 1:
            return C

        F0 = self.fft_3(C[::3])
        F1 = self.fft_3(C[1::3])
        F2 = self.fft_3(C[2::3])

        y = [0] * n

        ωn = self.nrou(n)
        for k in range(n//3):
            y[k]            = F0[k] +                ωn**k * F1[k] +                (ωn**2)**k * F2[k] # 1st share
            y[k + n//3]     = F0[k] + ωn**(n//3)   * ωn**k * F1[k] + ωn**(2*n//3) * (ωn**2)**k * F2[k] # 2nd share
            y[k + (2*n)//3] = F0[k] + ωn**(2*n//3) * ωn**k * F1[k] + ωn**(4*n//3) * (ωn**2)**k * F2[k] # 3rd share
        return y
    
    def ifft_3(self, shares):
        pass