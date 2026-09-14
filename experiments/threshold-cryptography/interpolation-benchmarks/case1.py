from interpolation import Interpolation
from lagrange import Lagrange
from newton import Newton
from barycentric import Barycentric
from fourier import Fourier
from utils import interpolate_and_count_time, case1_plot_sl, case1_plot_nbf, tabular_print

import time

def unoptimized_newton_barycentric_fft():
    global interpolation, lagrange, newton, barycentric, fourier

    nmin = 2**7
    nmax = 2**13
    times = {'n': [], 'b': [], 'f': []}

    print('='*20, 'NEWTON | BARYCENTRIC | FFT', '='*20)

    n = nmin
    while n <= nmax:
        P = interpolation.gen_poly(n-1)
        shares = interpolation.compute_shares(n)
        print(f'[+] {n = }')
        ### NEWTON
        N, total = interpolate_and_count_time('Newton', newton.newton_interpolation, shares)
        times['n'].append(total)
        ### BARYCENTRIC
        B, total = interpolate_and_count_time('Barycentric', barycentric.barycentric_interpolation, shares)
        times['b'].append(total)
        ### FOURIER
        shares = fourier.fft_2(P.coefficients())
        F, total = interpolate_and_count_time('Fourier', fourier.ifft_2, shares)
        times['f'].append(total)

        assert P == N == B == F
        # ----------------------------------
        print('-'*60)

        n *= 2
    
    tabular_print(times)

    case1_plot_nbf(times, nmin, nmax)

def unoptimized_standard_lagrange():
    global interpolation
    nmin = 100
    nmax = 1000
    times = {'l': []}

    P = interpolation.P
    
    print('='*20, 'STANDARD LAGRANGE', '='*20)

    n = nmin
    while n <= nmax:
        ### STANDARD LAGRANGE
        shares = interpolation.compute_shares(n)
        print(f'[+] {n = }')
        L, total = interpolate_and_count_time('Standard Lagrange', lagrange.lagrange_interpolation, shares)
        times['l'].append(total)
        assert P == L
        print('-'*60)
        
        n += 100
    
    # times['l'] = [0.5433 , 3.1385 , 6.5299 , 16.1861 , 25.2504 , 49.3655 , 64.2438 , 80.3796 , 107.0505 , 152.7803]

    tabular_print(times)

    case1_plot_sl(times, nmin, nmax)

def run_use_case_1(p):
    global interpolation, lagrange, newton, barycentric, fourier

    interpolation = Interpolation(p)
    lagrange = Lagrange(p)
    newton = Newton(p)
    barycentric = Barycentric(p)
    fourier = Fourier(p)
    
    # unoptimized_newton_barycentric_fft()

    precomputed_poly = [41286979313026075155646421774560708912, 74612904901391537960311108055132647625, 133245948441180022800446128944610045462, 91690056412895084559284774872259205543, 50953375824930380892852433872041453101, 104158290628876048247996085110926603262]
    interpolation.set_poly(precomputed_poly)

    unoptimized_standard_lagrange()