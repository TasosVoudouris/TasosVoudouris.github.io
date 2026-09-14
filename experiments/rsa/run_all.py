"""Run the recovered RSA Deep Dive experiment checks in their intended folders."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PYTEST_DIRS = [
    "15-rsa-hastad-broadcast",
    "16-rsa-wiener-attack",
    "17-rsa-coppersmith-from-zero",
]

MODEL_CHECKS = [
    "18-boneh-durfee/18-boneh-durfee-model-check.py",
    "19-partial-key-exposure/19-partial-key-exposure-model-check.py",
    "20-franklin-reiter/20-franklin-reiter-model-check.py",
    "21-rsa-short-pad/21-rsa-short-pad-model-check.py",
    "22-bleichenbacher-interval/22-bleichenbacher-interval-model-check.py",
    "23-manger-interval/23-manger-interval-model-check.py",
    "24-roca-fingerprint/24-roca-fingerprint-model-check.py",
]


def run(command: list[str], cwd: Path) -> None:
    print(f"\n$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    for folder in PYTEST_DIRS:
        run([sys.executable, "-m", "pytest", "-q"], ROOT / folder)

    for relative in MODEL_CHECKS:
        script = ROOT / relative
        run([sys.executable, script.name], script.parent)

    print("\nAll recovered RSA experiment checks passed.")


if __name__ == "__main__":
    main()
