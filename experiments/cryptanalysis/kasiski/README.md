# Kasiski Examination Lab

This directory is a self-contained, GitHub-ready study of the Kasiski
examination and ciphertext-only cryptanalysis of the repeating-key Vigenère
cipher. It connects repeated n-gram spacings, divisor evidence, Index of
Coincidence, Friedman estimation, chi-squared Caesar-column recovery, and
end-to-end decryption.

## Start here

- Read [Kasiski Test.md](Kasiski%20Test.md) for the complete analysis.
- Open [kasiski.ipynb](kasiski.ipynb) for the interactive walkthrough.
- Inspect [kasiski.py](kasiski.py) for the documented implementation.
- Run [test_kasiski.py](test_kasiski.py) for the verification suite.
- Review [REVIEW_NOTES.md](REVIEW_NOTES.md) for the exact corrections.
- Use [references.bib](references.bib) for the cited literature.

## Directory map

```text
Kasiski Test/
├── README.md
├── Kasiski Test.md
├── kasiski.ipynb
├── kasiski.py
├── test_kasiski.py
├── input-1-50.txt
├── references.bib
├── requirements.txt
└── REVIEW_NOTES.md
```

## Run and verify

Python 3.10 or newer is recommended. The project uses only the standard
library.

```bash
python kasiski.py
python -m unittest -v test_kasiski.py
```

The deterministic demonstration encrypts the bundled 2,634-letter normalized
English sample with `MOUSE`, recovers fundamental period `5`, recovers the key,
and verifies the entire normalized plaintext.

## Scope

This is educational code for obsolete classical ciphers. It is not a general
password cracker and not a security tool for modern encryption. Kasiski analysis
does not break AES, ChaCha20, or properly used authenticated encryption.
