from interpolation import Interpolation
from lagrange import Lagrange
from newton import Newton
from barycentric import Barycentric
from fourier import Fourier
from utils import interpolate_and_count_time, case3_plot_all, tabular_print

import time

def optimized_lnbf():
    global interpolation, lagrange, newton, barycentric, fourier

    nmin = 2**9
    nmax = 2**14
    times = {'l': [], 'n': [], 'b': [], 'f': []}

    n = nmin
    while n <= nmax:
        P = interpolation.gen_poly(n-1)
        shares = interpolation.compute_shares(n)
        print(f'[+] {n = }')
        ### LAGRANGE
        L, total = interpolate_and_count_time('Standard Lagrange', lagrange.lagrange_interpolation, shares, True)
        times['l'].append(total)
        ### NEWTON
        N, total = interpolate_and_count_time('Newton', newton.newton_interpolation, shares, True)
        times['n'].append(total)
        ### BARYCENTRIC
        B, total = interpolate_and_count_time('Barycentric', barycentric.barycentric_interpolation, shares, True)
        times['b'].append(total)
        ### FOURIER
        shares = fourier.fft_2(P.coefficients())
        F, total = interpolate_and_count_time('Fourier', fourier.ifft_2, shares)
        times['f'].append(total)

        assert P[0] == L == N == B == F[0]
        # ----------------------------------
        print('-'*60)

        n *= 2
    
    tabular_print(times)

    case3_plot_all(times, nmin, nmax)

def run_use_case_3(p):
    global interpolation, lagrange, newton, barycentric, fourier

    interpolation = Interpolation(p)
    lagrange = Lagrange(p)
    newton = Newton(p)
    barycentric = Barycentric(p)
    fourier = Fourier(p)

    optimized_lnbf()