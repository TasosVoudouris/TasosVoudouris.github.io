from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parent
SCRIPTS=[
    ROOT/'sigma'/'schnorr_sigma.py',
    ROOT/'fiat-shamir'/'schnorr_fiat_shamir.py',
    ROOT/'r1cs'/'r1cs_demo.py',
    ROOT/'qap'/'qap_demo.py',
    ROOT/'merkle'/'merkle_commitment.py',
    ROOT/'fri'/'fri_folding_toy.py',
]
for s in SCRIPTS:
    print(f"\n== {s.relative_to(ROOT)} ==")
    subprocess.run([sys.executable,str(s)],check=True)
print("\nAll zero-knowledge companion checks passed.")
