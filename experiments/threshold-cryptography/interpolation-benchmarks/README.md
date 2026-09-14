# Finite-field interpolation benchmark notes

This folder preserves the research code from the uploaded material comparing:

- standard Lagrange interpolation,
- Newton interpolation,
- barycentric interpolation,
- finite-field Fourier/FFT interpolation.

## Environment

The benchmark code is SageMath-oriented and imports `sage.all`; plotting helpers also use NumPy and Matplotlib. The timing plots are preserved under `figures/`.

The code is retained as research/benchmark material rather than presented as a production benchmark suite. Timings depend on hardware, Sage/Python versions, point-set structure, precomputation, and which interpolation output is measured.

`comparison.py` refers to an `FFTonly` module that was not present in the uploaded archive. The main case files (`case1.py`-`case4.py`) and their dependencies are preserved unchanged; the missing module is documented rather than silently fabricated.
