from pathlib import Path
import subprocess, sys

root = Path(__file__).resolve().parent
scripts = [
    root/'beaver-triples'/'demo.py',
    root/'spdz-mac-toy'/'demo.py',
    root.parent/'secret-sharing'/'shamir-arithmetic'/'demo.py',
    root.parent/'secret-sharing'/'ntt-engineering'/'ntt_demo.py',
]
for script in scripts:
    print(f"==> {script.relative_to(root.parent.parent)}")
    subprocess.run([sys.executable, str(script)], check=True)
print('ALL PASS')
