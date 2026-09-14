# Running every Python file directly

No installation is required. Extract the ZIP and use Python 3.10 or newer.

## Core files

From PowerShell:

```powershell
Set-Location .\CryptoCave-Threshold-Cryptography-v0.5\cryptocave_sss

python .\field.py
python .\polynomial.py
python .\additive.py
python .\shamir.py
python .\mpc.py
python .\robust.py
python .\ntt.py
python .\packed.py
python .\feldman.py
python .\pedersen.py
python .\vss_session.py
python .\dkg.py
python .\frost.py
python .\__init__.py
```

## Examples

```powershell
Set-Location ..\examples

python .\additive_demo.py
python .\shamir_demo.py
python .\arithmetic_demo.py
python .\robust_demo.py
python .\packed_demo.py
python .\ntt_demo.py
python .\feldman_demo.py
python .\feldman_tampering_demo.py
python .\feldman_leakage_demo.py
python .\pedersen_demo.py
python .\pedersen_hiding_demo.py
python .\pedersen_toy_trapdoor_demo.py
python .\vss_session_demo.py
python .\vss_complaint_demo.py
python .\vss_abort_demo.py
python .\dkg_demo.py
python .\dkg_bad_dealer_demo.py
python .\dkg_extraction_abort_demo.py
python .\dkg_qualification_abort_demo.py
python .\dkg_audit_demo.py
python .\frost_demo.py
python .\frost_simple_api_demo.py
python .\frost_nonce_reuse_demo.py
python .\frost_bad_share_demo.py
python .\frost_context_binding_demo.py
python .\frost_message_policy_demo.py
python .\run_all.py
```

## Individual test files

```powershell
Set-Location ..\tests

python .\test_field_and_polynomial.py
python .\test_additive.py
python .\test_shamir.py
python .\test_multiplication.py
python .\test_robust.py
python .\test_ntt.py
python .\test_packed.py
python .\test_feldman.py
python .\test_pedersen.py
python .\test_vss_session.py
python .\test_dkg.py
python .\test_frost.py
```

Each test command should end with `OK`.

## Complete test suite

Return to the project root and run:

```powershell
Set-Location ..
python -m unittest discover -v
```

Expected final lines:

```text
Ran 141 tests
OK
```

## If the window closes immediately

Do not double-click a `.py` file. Open PowerShell first, enter its folder with
`Set-Location`, and run `python .\filename.py` so output remains visible.

Files under `legacy/` are quarantined originals, not runnable Version 0.5
lessons. Exclude them from the active direct-execution check.
