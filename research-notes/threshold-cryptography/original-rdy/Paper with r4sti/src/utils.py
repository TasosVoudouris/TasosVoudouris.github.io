import time, math
from math import log2
import matplotlib.pyplot as plt
import numpy as np

def interpolate_and_count_time(label, func, *args):
    start = time.time()
    P = func(*args)
    end = time.time()
    total = float("%0.4f" % (end - start))
    print(f"[+] {label} : {total}")
    return P, total

def case1_plot_nbf(times, nmin, nmax):
    plt.rcParams["font.size"] = 10

    ax = plt.subplot()

    expdiff = int(math.log2(nmax/nmin))
    N = [(nmin << i) for i in range(expdiff+1)]

    ax.plot(N, times['n'], 'ro-', linewidth=2.5)
    ax.plot(N, times['b'], 'bo-', linewidth=2.5)
    ax.plot(N, times['f'], 'go-', linewidth=2.5)

    ax.legend(['Newton', 'Barycentric', 'Fourier'])

    plt.xticks(N[:1]+N[2:], [str(j) for j in N[:1]+N[2:]])

    ax.set_xscale('log', base=2)

    show_labels(ax)
    
    plt.savefig("case1_plot_nbf.pdf", format="pdf", bbox_inches="tight")
    #plt.show()



def case1_plot_sl(times, nmin, nmax):
    plt.rcParams["font.size"] = 10

    ax = plt.subplot()

    N = [i for i in range(nmin, nmax+1, 100)]

    ax.plot(N, times['l'], 'ro-', linewidth=2.5)

    ax.legend(['Standard Lagrange'])
    
    plt.xticks(N, [str(j) for j in N])

    show_labels(ax)
    
    #plt.show()
    plt.savefig("case1_plot_sl.pdf", format="pdf", bbox_inches="tight")



def case2_plot(times, nmin, nmax):
    plt.rcParams["font.size"] = 10

    ax = plt.subplot()

    N = [i for i in range(nmin, nmax + 1)]

    ax.plot(N, times['n'], 'ro-', linewidth=2.5)
    ax.plot(N, times['b'], 'bo-', linewidth=2.5)

    ax.legend(['Newton', 'Barycentric'])

    plt.xticks([N[j] for j in range(0, len(N), 10)], [N[j] for j in range(0, len(N), 10)])
    
    show_labels(ax)
    
    #plt.show()
    plt.savefig("case2_plot_nb.pdf", format="pdf", bbox_inches="tight")



def case3_plot_all(times, nmin, nmax):
    plt.rcParams["font.size"] = 10

    ax = plt.subplot()

    expdiff = int(math.log2(nmax/nmin))
    N = [(nmin << i) for i in range(expdiff+1)]

    ax.plot(N, times['l'], 'co-', linewidth=2.5)
    ax.plot(N, times['n'], 'ro-', linewidth=2.5)
    ax.plot(N, times['b'], 'bo-', linewidth=2.5)
    ax.plot(N, times['f'], 'go-', linewidth=2.5)

    ax.legend(['Standard Lagrange', 'Newton', 'Barycentric', 'Fourier'])

    plt.xticks(N[:1]+N[2:], [str(j) for j in N[:1]+N[2:]])
    ax.set_scale('log', base=2)

    show_labels(ax)
    
    #plt.show()
    plt.savefig("case3_plot_all.pdf", format="pdf", bbox_inches="tight")
    


def case4_plot_fourier(times, nmin, nmax):
    plt.rcParams["font.size"] = 10

    ax = plt.subplot()

    expdiff = int(math.log2(nmax/nmin))
    N = [(nmin << i) for i in range(expdiff+1)]

    ax.plot(N, times['fo'], 'bo-', linewidth=2.5)
    ax.plot(N, times['fu'], 'go-', linewidth=2.5)

    ax.legend(['Optimized Fourier', 'Unoptimized Fourier'])

    plt.xticks(N[:1]+N[2:], [str(j) for j in N[:1]+N[2:]])
    ax.set_xscale('log', base=2)

    show_labels(ax)
    
    #plt.show()
    plt.savefig("case4_plot_fourier.pdf", format="pdf", bbox_inches="tight")



def tabular_print(times):
    for method, tl in times.items():
        print(method, '& ', end='')
        for t in tl:
            print(f'{t} & ', end='')
        print('\\\\')
def show_labels(ax):
    ax.set_xlabel('Number of shares')
    ax.set_ylabel('Seconds')