# RSA Module Review Handoff

This package is a review candidate for CryptoCave. It mirrors the intended
repository destination:

```text
docs/public-key-cryptography/rsa/
```

No GitHub repository was changed or published during this review.

## Proposed structure

```text
rsa/
├── README.md
├── fundamentals.md
├── encoding-and-key-formats.md
├── attacks/
│   ├── README.md
│   ├── common-modulus.md
│   ├── coppersmith.md
│   ├── key-generation-and-implementation.md
│   └── low-public-exponent.md
├── src/
│   ├── common_modulus_attack.py
│   ├── low_exponent_attacks.py
│   ├── shared_prime_attack.py
│   └── textbook_rsa.py
└── tests/
    └── test_rsa_examples.py
```

The order is foundations, safe construction and formats, attack taxonomy,
focused attack notes, then executable demonstrations.

## How the uploaded material was reorganized

| Uploaded material | Review candidate |
| --- | --- |
| Existing `RSA.md`, `EulersTheorem.md`, and introductory notebook ideas | Rewritten as `README.md` and `fundamentals.md` |
| `PEMattack.md` | Corrected and expanded as `encoding-and-key-formats.md` |
| `Commonmodulus.md` | Rewritten as `attacks/common-modulus.md` with signed-exponent conditions |
| `CubeRootAttack.md` and `Hastad.md` | Combined and corrected in `attacks/low-public-exponent.md` |
| `CoppersmithStereotyped.md` and related notebook ideas | Rewritten with theorem boundaries in `attacks/coppersmith.md` |
| `Infineon Numbers` material | Replaced by an accurate ROCA overview in `attacks/key-generation-and-implementation.md` |
| Existing toy RSA, Sage, and signature scripts | Replaced by small dependency-free Python modules and tests |
| Attack collection topics | Categorized in `attacks/README.md`; selected ideas were independently rewritten |

## Important technical corrections

- RSA-OAEP encryption and RSA-PSS signatures are distinguished from textbook
  RSA. A signature is not described as "private-key encryption."
- Key generation uses $\lambda(n)=\operatorname{lcm}(p-1,q-1)$ and the
  correctness proof covers representatives that are not coprime to $n$ by
  applying CRT modulo $p$ and $q$.
- Factoring is described as sufficient to break the private key, not as proven
  equivalent to solving the RSA problem.
- The message-representative bound $0\le m<n$ is explicit. Decimal
  concatenation is not presented as an encoding.
- The common-modulus derivation handles negative Bézout coefficients as modular
  inverses and explains the $\gcd(e_1,e_2)>1$ case.
- Low $e$ is not called inherently insecure. Exact-root and broadcast attacks
  are tied to their raw-RSA and representative-reuse assumptions.
- Coppersmith's method is not reduced to an inaccurate "half the bits" rule;
  degree, factor-size, variable-count, and heuristic conditions are separated.
- PEM is treated as a text envelope for DER data, not encryption and not an
  attack. PKCS #1, PKCS #8, SPKI, and X.509 roles are distinguished.
- ROCA is described as a restricted-subgroup prime-generation flaw. Repeated
  powers modulo $n$ are not accepted as a ROCA detector.
- Padding-oracle, timing, blinding, CRT-fault, shared-prime, and private-key
  lifecycle topics were added because the uploaded notes did not cover them
  consistently.

## Files deliberately not carried forward

The following items remain outside the proposed public module:

- `RSA-Attacks-main/` matches the public
  [Giapppp/RSA-Attacks repository](https://github.com/Giapppp/RSA-Attacks).
  The uploaded copy contains no license, and the repository page reviewed on
  2026-08-11 did not show one. It should not be redistributed here without a
  documented license or permission.
- `RSA Explained (With Examples) - Kendrick.pdf` is a saved copy of
  [Kendrick Tan's article](https://kndrck.co/posts/zk_rsa_explained_with_examples/).
  The review candidate links to primary references instead of republishing the
  downloaded page.
- `RSA2/` contains notebooks with unclear repository provenance and cells that
  explicitly copy external implementations. They were not republished. Their
  useful topic order was considered during the independent rewrite.
- `rsa-bleichenbacher-master.zip` contains another project and a paper but no
  license file. The padding-oracle concept was independently summarized instead.
- `index_calculus_attack/` targets an elliptic-curve discrete-log problem, not
  RSA. Its example point is a placeholder and its algorithm calls a discrete-log
  solver as a subroutine, so it is neither correctly categorized nor a working
  attack implementation.
- `Infineon Numbers/infineon.sage` does not implement the published ROCA
  fingerprint. Its cycle test would produce false conclusions.
- Generated `output.txt` files, `flag.txt`, notebook outputs, nested archives,
  and duplicate files were excluded as noise or unreviewed artifacts.
- `RSASignature.py` used Python's process-randomized `hash()`, raw RSA, tiny
  random keys, and a modular-inverse loop that can raise instead of retrying. It
  was replaced rather than repaired into another unsafe signature example.

The original upload is preserved in its prior file version, so excluded material
can be recovered for private study or a later provenance review.

## Validation performed

The candidate was inserted into the cleaned CryptoCave tree and checked there:

- 10 Python unit tests passed.
- All 5 Python files parsed successfully.
- All 4 demonstration programs ran and reproduced their documented results.
- All 59 repository Markdown/MDX files passed `markdownlint-cli2` with zero
  errors.
- Docusaurus TypeScript checking passed.
- The complete Docusaurus production build passed, including internal link
  validation.

Review commands from the CryptoCave repository root:

```bash
python -m unittest discover -s docs/public-key-cryptography/rsa/tests -v
npx --yes markdownlint-cli2@0.18.1 '**/*.md' '**/*.mdx' '#website/node_modules'
npm --prefix website run typecheck
npm --prefix website run build
```

## Suggested merge review

1. Read `rsa/README.md`, then follow its learning path.
2. Confirm the tone and depth match the rest of CryptoCave.
3. Review the exclusion list, especially before restoring any third-party code.
4. Replace the current `docs/public-key-cryptography/rsa/` directory with the
   candidate directory.
5. Run the validation commands above before committing.
6. Commit the RSA change separately so its documentation and example-code
   review remains easy to inspect.
