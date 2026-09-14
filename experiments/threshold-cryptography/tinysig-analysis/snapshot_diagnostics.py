"""Inspect the historical threshold-signatures/TinySig snapshot layout.

Usage:
    python snapshot_diagnostics.py /path/to/tinysig-main

The script does not import TinySig and therefore needs no third-party crypto
packages.  It explains whether the local snapshot contains installable TinySig
source or only docs/tests/bytecode and whether the experimental network layer is
present.
"""

from __future__ import annotations

import sys
from pathlib import Path


def yn(value: bool) -> str:
    return "yes" if value else "NO"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python snapshot_diagnostics.py /path/to/tinysig-main")
        return 2

    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.exists():
        print(f"not found: {root}")
        return 2

    project = root / "tinysig-main" if (root / "tinysig-main").is_dir() else root
    packaged = project / "resources" / "tinysig"
    expected_source = packaged / "src" / "tinysig"
    bytecode = project / "src" / "tinysig"
    runme = root / "testing" / "runme.py"

    print(f"snapshot root: {root}")
    print(f"project root:  {project}")
    print(f"resources/tinysig present:       {yn(packaged.is_dir())}")
    print(f"resources/tinysig/src/tinysig:   {yn(expected_source.is_dir())}")
    print(f"top-level src/tinysig present:   {yn(bytecode.is_dir())}")
    print(f"testing/runme.py present:        {yn(runme.is_file())}")

    if bytecode.is_dir():
        py = list(bytecode.glob("*.py"))
        pyc = list(bytecode.glob("__pycache__/*.pyc"))
        print(f"top-level TinySig source .py:    {len(py)}")
        print(f"top-level TinySig bytecode .pyc: {len(pyc)}")

    if packaged.is_dir() and not expected_source.is_dir():
        print("\nDIAGNOSIS: the bundled package has metadata/docs/tests but no src/tinysig source tree.")
        print("`testing/runme.py` therefore cannot import this copy as a normal source package.")
        print("Use an isolated environment with `tinysig==0.1.0`, or restore the complete upstream source tree.")

    if (project / "src" / "node.py").is_file() and (project / "src" / "server.py").is_file():
        print("\nNOTE: src/node.py + src/server.py are a separate WebSocket/FastAPI network experiment.")
        print("They are not the same execution path as the published in-memory TinySig 0.1.0 package.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
