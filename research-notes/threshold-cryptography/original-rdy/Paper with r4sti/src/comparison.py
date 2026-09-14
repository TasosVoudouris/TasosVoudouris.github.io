import os, time, random
from sage.all import GF, PolynomialRing
# ——— import your standalone FFT‐packed code ———
# assume it's in fft_packed.py with functions share, reconstruct, plus ORDER2, ORDER3, Q, K, T
from FFTonly import (
    share        as fft_share,
    reconstruct  as fft_reconstruct,
    ORDER2, ORDER3, Q, K, T
)

#
# ——— 1) CLASS-BASED FFT SETUP ———
#
class Interpolation:
    def __init__(self, p):
        self.p  = p
        self.F  = GF(p)
        self.PR = PolynomialRing(self.F, 'x')
        self.g  = self.F(3)

    def nrou(self, n):
        return self.g**((self.p - 1)//n)

class Fourier(Interpolation):
    def __init__(self, p):
        super().__init__(p)
        self.precomputed = False
        self.Ω = {}

    def toggle_precomputed(self):
        self.precomputed = not self.precomputed

    def precompute_nrous(self, max_pow):
        for i in range(max_pow+1):
            n = 2**i
            self.Ω[n]   = self.nrou(n)
            self.Ω[-n]  = self.nrou(-n)

    def fft_2(self, C, INV=False):
        n = len(C)
        if n == 1: return C
        F0 = self.fft_2(C[::2], INV)
        F1 = self.fft_2(C[1::2], INV)
        ω  = (self.Ω[-n] if INV and self.precomputed else
              self.Ω[n]  if not INV and self.precomputed else
              self.nrou(-n if INV else n))
        y = [self.F(0)]*n
        tw = self.F(1)
        for k in range(n//2):
            y[k]       = F0[k] + tw * F1[k]
            y[k+n//2]  = F0[k] - tw * F1[k]
            tw        *= ω
        return y

    def ifft_2(self, vals):
        n    = len(vals)
        inv  = self.fft_2(vals, INV=True)
        invn = self.F(1)/self.F(n)
        coeffs = [v*invn for v in inv]
        return coeffs          # list of length n

    def fft_3(self, C, INV=False):
        n = len(C)
        if n == 1: return C
        F0 = self.fft_3(C[::3], INV)
        F1 = self.fft_3(C[1::3], INV)
        F2 = self.fft_3(C[2::3], INV)
        ω  = self.nrou(-n if INV else n)
        if self.precomputed and n in self.Ω:
            ω = self.Ω[-n] if INV else self.Ω[n]
        y = [self.F(0)]*n
        tw = self.F(1)
        third = n//3
        for k in range(third):
            w0 = tw
            w1 = tw*tw
            y[k]          = F0[k] +  w0*F1[k] +  w1*F2[k]
            y[k+third]    = F0[k] + ω**third * w0*F1[k] + (ω**(2*third))*w1*F2[k]
            y[k+2*third]  = F0[k] + ω**(2*third)*w0*F1[k] + (ω**(4*third))*w1*F2[k]
            tw           *= ω
        return y

    def ifft_3(self, shares):
        n = len(shares)
        inv_fft = self.fft_3(shares, INV=True)
        # divide each entry by n in the field
        C= [ inv_fft[k] / n for k in range(n) ]
        return C


# wrap the packed‐share logic around the class
def share_class(F: Fourier, secrets):
    assert len(secrets) == K
    # build small_values in F
    small_vals = [F.F(0)] + [F.F(s) for s in secrets] + [F.F(random.randrange(Q)) for _ in range(T)]
    # inverse radix-2 → small_coeffs
    small_coeffs = F.ifft_2(small_vals)    
    # pad to ORDER3
    large_coeffs = small_coeffs + [F.F(0)]*(ORDER3-ORDER2)
    # forward radix-3 → large_values
    large_vals   = F.fft_3(large_coeffs)
    shares       = large_vals[1:]   # drop the 0‐th
    return [int(sh) for sh in shares]

def reconstruct_class(F: Fourier, shares):
    assert len(shares) == ORDER3-1
    large_vals   = [F.F(0)] + [F.F(s) for s in shares]
    large_coeffs = F.ifft_3(large_vals)
    small_coeffs = large_coeffs[:ORDER2]
    small_vals   = F.fft_2(small_coeffs)
    secrets      = small_vals[1:1+K]
    return [int(s) for s in secrets]


# ——— 2) RUN CORRECTNESS + BENCHMARK ———
def compare_once():
    # random secret‐vector
    sec = [ random.randrange(0, Q) for _ in range(K) ]

    # class-based
    F = Fourier(Q)
    F.toggle_precomputed()
    F.precompute_nrous( max_pow=int((ORDER2-1).bit_length()) )
    start = time.perf_counter()
    sh1   = share_class(F, sec)
    rec1  = reconstruct_class(F, sh1)
    t1    = time.perf_counter() - start

    # standalone
    start = time.perf_counter()
    sh2   = fft_share(sec)
    rec2  = fft_reconstruct(sh2)
    t2    = time.perf_counter() - start

    assert rec1 == rec2 == sec
    return t1, t2

# warm-up
for _ in range(3):
    compare_once()

# measure
Ntrials = 50
times1, times2 = [], []
for _ in range(Ntrials):
    a,b = compare_once()
    times1.append(a)
    times2.append(b)

print(f"Class-based FFT : {sum(times1)/Ntrials*1e3:.2f} ms / share+reconstruct")
print(f"Standalone FFT   : {sum(times2)/Ntrials*1e3:.2f} ms / share+reconstruct")
