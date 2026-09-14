from interpolation import Interpolation
from lagrange import Lagrange
from newton import Newton
from barycentric import Barycentric
from fourier import Fourier
from utils import interpolate_and_count_time, case2_plot, tabular_print

import time

def precomputed_newton_barycentric_case(mode):
    global interpolation, newton, barycentric

    newton.toggle_precomputed(mode)
    barycentric.toggle_precomputed(mode)

    nmin = 3000
    nmax = nmin + 10
    times = {'n': [], 'b': []}
    
    P = interpolation.gen_poly(nmin-1)

    n = nmin
    while n <= nmax:
        shares = interpolation.compute_shares(n)
        print(f'[+] {n = }')
        ### NEWTON
        N, total = interpolate_and_count_time('Newton', newton.newton_interpolation, shares, True)
        times['n'].append(total)
        ### BARYCENTRIC
        B, total = interpolate_and_count_time('Barycentric', barycentric.barycentric_interpolation, shares, True)
        times['b'].append(total)

        assert P[0] == N == B
        # ----------------------------------
        print('-'*60)

        n += 1
    
    tabular_print(times)

    case2_plot(times, nmin, nmax)

def run_use_case_2(p):
    global interpolation, newton, barycentric

    interpolation = Interpolation(p)
    newton = Newton(p)
    barycentric = Barycentric(p)

    precomputed_newton_barycentric_case(True)

    precomputed_newton_barycentric_case(False)