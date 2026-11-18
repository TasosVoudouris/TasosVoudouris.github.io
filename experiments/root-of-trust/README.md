# Root of Trust: companion code

Code for the article series at https://tasosvoudouris.github.io/root/ .
Teaching models only: never use them to protect anything real.

| File | Article | Run |
|---|---|---|
| `00_toy_chain.py` | Part 00, "Who do you trust?" | `python 00_toy_chain.py` |
| `test_00_toy_chain.py` | checks the six verdicts the article quotes | `python -m unittest test_00_toy_chain` |
| `der.py` | Part 01, a DER encoder and strict decoder from scratch | imported by `01_certificate.py` |
| `01_certificate.py` | Part 01, "A certificate, byte by byte" | `python 01_certificate.py --write` |
| `test_01_certificate.py` | checks the encoder and every offset and size Part 01 quotes | `python -m unittest test_01_certificate` |
| `01_example_*.der` | the certificates Part 01 dissects (leaf, ML-DSA-44 leaf, toy CA) | `openssl asn1parse -inform DER -in 01_example_ed25519.der -i` |

Needs Python 3.10+ and `pip install cryptography` (version 46 or newer for the ML-DSA part of Part 01).
