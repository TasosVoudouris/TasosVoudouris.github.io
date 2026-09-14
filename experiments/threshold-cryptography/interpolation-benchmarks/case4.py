from interpolation import Interpolation
from fourier import Fourier
from utils import interpolate_and_count_time, case4_plot_fourier, tabular_print
import time


def optimized_unoptimized_fourier():
    global fourier

    nmin = 2**14
    nmax = 2**15
    times = { 'fu' : [] , 'fo' : [] }

    fourier.precompute_nrous(nmax)

    n = nmin
    while n <= nmax:
        P = interpolation.gen_poly(n-1)
        print('computing shares')
        shares = interpolation.compute_shares(n)
        print('computed shares')
        print(f'[+] {n = }')

        assert fourier.precomputed == False

        ### FOURIER UNOPTIMIZED
        shares = fourier.fft_2(P.coefficients())
        FU, total = interpolate_and_count_time('Unoptimized Fourier', fourier.ifft_2, shares)
        times['fu'].append(total)

        fourier.toggle_precomputed()    # set to optimized

        assert fourier.precomputed == True

        shares = fourier.fft_2(P.coefficients())
        FO, total = interpolate_and_count_time('Optimized Fourier', fourier.ifft_2, shares)
        times['fo'].append(total)

        fourier.toggle_precomputed()    # set back to unoptimized

        assert P[0] == FO[0] == FU[0]
        # ----------------------------------
        print('-'*60)

        n *= 2
    
    tabular_print(times)

    case4_plot_fourier(times, nmin, nmax)

def run_use_case_4(p):
    global interpolation, fourier

    interpolation = Interpolation(p)
    fourier = Fourier(p)

    optimized_unoptimized_fourier()