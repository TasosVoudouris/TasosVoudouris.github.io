# RSA experiment companions

This directory contains the executable material recovered from the RSA Deep Dive packages.

The experiments are intentionally small, fixed, educational/research models that accompany the corresponding articles. They are not workflows for targeting external systems.

## Test suites

The Håstad, Wiener, and Coppersmith/LLL folders each contain their own local `test_attack.py`. Run them from their own directories because the historical files use the same test-module name and local imports:

```bash
cd experiments/rsa/15-rsa-hastad-broadcast && python -m pytest -q
cd ../16-rsa-wiener-attack && python -m pytest -q
cd ../17-rsa-coppersmith-from-zero && python -m pytest -q
```

Or from the repository root run:

```bash
python experiments/rsa/run_all.py
```

The runner also executes the fixed model-check scripts for Deep Dives VI–XII.
