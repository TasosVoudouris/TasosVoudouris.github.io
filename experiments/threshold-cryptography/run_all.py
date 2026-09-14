"""Run the dependency-free threshold-cryptography toy checks."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    ROOT / "additive" / "additive_secret_sharing.py",
    ROOT / "shamir" / "shamir_secret_sharing.py",
    ROOT / "packed-sharing" / "packed_secret_sharing.py",
    ROOT / "polynomial-splitting" / "polynomial_splitting.py",
    ROOT / "fft-packed-sharing" / "fft_packed_sharing.py",
]

for script in SCRIPTS:
    print(f"\n==> {script.relative_to(ROOT)}")
    subprocess.run([sys.executable, str(script)], check=True)

print("\nall dependency-free threshold-cryptography checks passed")
