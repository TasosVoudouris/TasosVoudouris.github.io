# Matsui Linear Cryptanalysis Lab

This directory is a self-contained, GitHub-ready introduction to linear
cryptanalysis. It develops the theory from Boolean masks and S-box linear
approximation tables through Matsui's two algorithms, then performs a checked
partial last-round subkey attack against a four-round 16-bit teaching SPN.

## Start here

- Read [Linear Cryptanalysis.md](Linear%20Cryptanalysis.md) for the complete
  chapter.
- Open [Linear Cryptanalysis.ipynb](Linear%20Cryptanalysis.ipynb) for an
  interactive walkthrough.
- Inspect [matsui1.py](matsui1.py) for the documented implementation.
- Run [test.py](test.py) to verify all mathematical checkpoints and cipher
  round trips.
- Use [references.bib](references.bib) for the cited primary literature.
- See [REVIEW_NOTES.md](REVIEW_NOTES.md) for the exact corrections and checks.

## Directory map

```text
Matsui/
├── README.md
├── Linear Cryptanalysis.md
├── Linear Cryptanalysis.ipynb
├── matsui1.py
├── test.py
├── references.bib
├── REVIEW_NOTES.md
├── requirements.txt
└── images/
    ├── addkey.PNG
    ├── lat2.PNG
    ├── linearapprox.PNG
    ├── matsui1example.PNG
    ├── matsui2.PNG
    ├── matsui2example.PNG
    └── moresbox.PNG
```

## Requirements and verification

Python 3.10 or newer is sufficient. The implementation uses only the standard
library.

```bash
python matsui1.py
python -m unittest -v test.py
```

The checks cover:

- bit-ordering and parity helpers;
- S-box and P-box inverses;
- mask propagation through the P-box;
- exact LAT, Walsh, bias, and correlation values;
- positive and negative approximation signs;
- the piling-up lemma;
- Matsui Algorithm 1 and Algorithm 2 scoring;
- SPN encryption/decryption; and
- deterministic recovery of two selected final-round key nibbles.

## Mathematical conventions

The code stores a LAT entry as the centered match count

```text
number_of_matches - 2^(n - 1)
```

so the Walsh coefficient is twice the stored entry, correlation is the Walsh
coefficient divided by `2^n`, and bias is half the correlation. Bit positions
are zero-based and most-significant-bit first.

## Scope

All ciphers in this directory are deliberately small teaching constructions.
The code is for study and authorized experimentation, not production
cryptography. Recovering two final-round nibbles in the example is partial
subkey recovery, not recovery of the complete master key.
