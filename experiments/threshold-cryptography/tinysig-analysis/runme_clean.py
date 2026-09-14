"""Minimal TinySig 0.1.0 example from the public API.

Run this only in an isolated Python 3.10/3.11 environment where
`tinysig==0.1.0` has been installed from PyPI.  The CryptoCave repository does
not vendor the third-party TinySig package.
"""

from tinysig import ECDSASetup, ThresholdSignature

N = 3
C = 1
CLIENT_ID = 1

setup = ECDSASetup(curve="P-256")
network = ThresholdSignature(N, C, setup=setup)

network.distributed_key_generation_protocol(CLIENT_ID)
network.ts_prep_protocol(CLIENT_ID)
network.ts_online_protocol("Let me tell you a secret about Nillion.", CLIENT_ID)
network.print_signature(CLIENT_ID)
