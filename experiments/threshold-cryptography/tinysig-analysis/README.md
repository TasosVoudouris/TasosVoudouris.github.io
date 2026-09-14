# TinySig analysis companions

This directory supports the CryptoCave TinySig deep dive.  It deliberately does
**not** vendor the third-party TinySig repository.

- `masked_factor_walkthrough.py` is a dependency-free toy proof that the mask
  exponents cancel to the ordinary ECDSA scalar equation.
- `snapshot_diagnostics.py` diagnoses the historical local snapshot that mixed
  the published TinySig package, legacy source, and a separate network experiment.
- `runme_clean.py` is the minimal public TinySig 0.1.0 API example.  It requires
  an isolated Python 3.10/3.11 environment with `tinysig==0.1.0` installed.

## Reproducible historical environment

On Windows PowerShell, prefer a clean environment rather than editing `PATH`
manually:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "tinysig==0.1.0"
python experiments/threshold-cryptography/tinysig-analysis/runme_clean.py
```

TinySig 0.1.0 is a 2023 educational prototype with old, tightly pinned
scientific-Python dependencies.  Python 3.10/3.11 is a much safer reproduction
target than trying to force the package into a modern Python environment.
