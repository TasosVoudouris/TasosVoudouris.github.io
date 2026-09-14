# Technical review notes

## Review policy

The source was not rewritten merely for style. Correct implementations retain
their mathematical structure. Changes were limited to demonstrable execution,
logic, validation, or security-clarity problems, plus comments needed to make
the examples understandable.

## Corrections made

| Area | Problem in supplied source | Correction |
| --- | --- | --- |
| Python 3 | Python 2 `print` syntax and mixed text/bytes | Modern calls and explicit UTF-8/byte conversion |
| Loading | Hard-coded `cryptosage/...` paths did not match the archive root | Root-relative, categorized load order in examples/tests |
| Hashing | `hashlib` received text rather than bytes | Central `to_bytes` conversion |
| RSA | Prime size was not guaranteed; `p = q` and non-invertible `e` were not rejected | Exact lower bound, distinct primes, and `gcd(e, phi) = 1` loop |
| Paillier | Randomizer could be `0`, `n`, or non-invertible | Sample from `Z_n^*`; add message and ciphertext checks |
| Paillier | Nonstandard private exponent and unfinished homomorphic addition | Standard `lcm(p-1,q-1)` form and multiplication modulo `n^2` |
| ECDSA | A zero `s` could cause an infinite retry with the same nonce | Fresh nonce on every retry; add signature range and infinity checks |
| EC-KCDSA | Generic EC key generation used the wrong public-key convention | Dedicated key generation with `Q = d^(-1)P` |
| ECIES/PSEC | Implicit ECB mode, zero padding, missing unpadding, implicit HMAC digest | Random-IV AES-CBC, PKCS#7, HMAC-SHA-256, constant-time tag comparison |
| ECIES/PSEC | EC ciphertext points were not validated | Curve, non-infinity, and subgroup checks |
| ECMQV | Functions were called before definition and relied on local variables as globals | Explicit party state and a complete two-sided shared-point calculation |
| ECMQV | Point reduction used the full order length | Standard half-length MQV reduction |
| Pairing demo | `T + P` concatenated Python lists instead of adding EC points | Call the point-addition routine |
| Pairing demo | Doubling a point with `y = 0` divided by zero | Return the point at infinity |

## Material deliberately not represented as working code

`archive/incomplete/rfc5091_draft.sage.txt` is preserved for provenance and
future study. It was not a runnable RFC 5091 implementation. Among other issues,
it contained an incomplete tangent evaluation, an invalid function definition,
missing returns, inconsistent pairing signatures, a broken signed-window
decomposition, and placeholder parameters such as `q = 2`. Renaming it to
`.sage.txt` prevents accidental execution while retaining every original line.

The STS file in the supplied archive did not implement Station-to-Station:
there were no long-term signing keys or signatures. The reviewed version is
therefore named an **STS-inspired key-confirmation study** and explicitly states
that it does not authenticate the peers.

## Compatibility and validation scope

The reviewed files target current SageMath/Python 3 conventions. Static checks
cover file inventory, Markdown links/fences, Python-level syntax where Sage
preparser syntax is not required, and known error patterns. A native SageMath
runtime is still required for mathematical execution and should be used before
merging the package into a public repository.
