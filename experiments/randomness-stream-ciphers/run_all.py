from pathlib import Path
import subprocess, sys

HERE = Path(__file__).resolve().parent
TESTS = ["test_lcg.py", "test_lfsr_geffe.py", "test_rc4.py", "test_chacha20.py"]
for test in TESTS:
    print(f"== {test} ==")
    subprocess.run([sys.executable, str(HERE / test)], cwd=HERE, check=True)
print("Randomness/stream-cipher experiments: ALL PASS")
