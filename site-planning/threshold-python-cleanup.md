# Threshold Python cleanup — v6.7

This pass consolidates the uploaded `Threshold Python.zip` into the canonical CryptoCave threshold-cryptography path. The goal was **not** to vendor every historical repository. The batch was used to recover the TinySig work, explain why the old local snapshot was difficult to execute, preserve the useful threshold-ECDSA algebra, and reject/supersede unrelated or weaker material.

## Source accounting

- Original archive files: **241**
- Migration-ledger rows: **241**
- Unclassified files: **0**
- Source archive SHA-256: `9731918e31a43494ed453c2bf83ad3bbe5e726a2a4fad5f810a73e1205eb4581`
- Raw source ZIP bundled in canonical master: **no**
- PDFs bundled: **no**
- Nested third-party ZIPs bundled: **no**

Exact per-file decisions are recorded in `site-planning/threshold-python-source-ledger.csv`.

## Canonical additions

Two articles were inserted into **Threshold Cryptography Engineering** immediately after the generic Schnorr/interpolation chapter and before FROST:

18. **Why Threshold ECDSA Is Hard: Nonlinearity, Nonces, and Preprocessing**
19. **TinySig Deep Dive: Masked Factors, Preprocessing, and the Python Prototype**

The old FROST/ChillDKG sequence was shifted to Parts 20–26 without rewriting its scientific content.

The new companion directory is:

```text
experiments/threshold-cryptography/tinysig-analysis/
├── README.md
├── masked_factor_walkthrough.py
├── runme_clean.py
└── snapshot_diagnostics.py
```

The recovered fork architecture figure is retained as:

`public/images/blog/tinysig-fork-architecture.png`

and is explicitly labeled as the later WebSocket/service design, **not** as the execution architecture of the published TinySig 0.1.0 in-memory package.

## Main forensic finding

The historical `tinysig-main` snapshot mixed multiple abstraction layers:

1. package metadata/docs/tests under `resources/tinysig/`, but without the expected `src/tinysig/` source tree;
2. older TinySig-like Python sources under `resources/old/`;
3. a separate FastAPI/WebSocket experiment under top-level `src/node.py`, `src/server.py`, and `src/crypto_utils.py`;
4. generated `.pyc` bytecode under `src/tinysig/__pycache__/`; and
5. `testing/runme.py`, which imports `tinysig` as if a complete package were installed.

The canonical diagnostic therefore does **not** claim the recovered tree is an installable TinySig source checkout. It recommends an isolated historical environment with `tinysig==0.1.0` or a restored complete upstream source tree.

## Technical corrections and clarifications

### Naive Shamir + ECDSA aggregation

The uploaded `tECDSA.py` is retained conceptually as a negative example. It treats each Shamir private-key share as an independent ECDSA key, signs independently, and Lagrange-interpolates the resulting `s` values. This is not threshold ECDSA: independent ECDSA signatures use independent nonces and generally different `r` values, while ECDSA's \(k^{-1}(m+rx)\) equation is nonlinear in the shared secrets.

### TinySig is not generic Shamir/FROST \(t\)-of-\(n\)

The recovered prototype's `Network.share()` uses additive sharing across all \(N\) nodes and reconstruction sums all \(N\) shares. The public constructor accepts `N` and client count `C`, but no threshold `t`. The article therefore describes the Python package as an **N-of-N additive-sharing emulator of the masked-factor threshold-ECDSA construction**, not a drop-in generic threshold library.

### Masked-factor derivation

The canonical walkthrough explicitly derives the cancellation

\[
\widetilde s = s h^{-\lambda_{gap}}
\quad\Longrightarrow\quad
s=\widetilde s h^{\lambda_{gap}},
\]

starting from the ECDSA scalar equation and the prototype's \(\lambda_x,\lambda_k,\lambda_1,\lambda_2,\lambda_m,\lambda_{gap}\) bookkeeping. The dependency-free companion script verifies the same identity over a deliberately tiny finite field.

### Prototype engineering caveats

The article records, rather than silently copying, several prototype limitations found in the recovered source:

- use of Python `random.randrange` for secret/random values;
- private PyCryptodome curve internals;
- incomplete ECDSA verification edge handling;
- in-memory `broadcast`/`send` instead of a real authenticated network;
- incomplete/ambiguous multi-client plumbing;
- precondition handlers that print warnings and can continue into downstream errors; and
- string-label state management that obscures the algebraic domain of values.

These are reasons to study the code as a prototype rather than deploy it.

## Material intentionally not promoted

- **FROST `poc.sage`**: superseded by the existing validated FROST v0.5/RFC 9591 path.
- **Threshold RSA repository**: separate subject/reference; not needed for the TinySig task.
- **Ring-signature code**: separate signature/anonymity topic.
- **Garbled-circuit material**: better handled in a future MPC-specific batch.
- **TSSHOCK PDFs**: useful external security references, but PDFs are excluded by compact-master policy.
- **Nested Rust threshold-signature ZIP**: third-party/raw archive; excluded from the active master.
- **Embedded `.git` objects and Python bytecode**: generated/repository metadata, discarded.

## Local validation

The following checks were executed during this pass:

```text
CryptoCave content preflight                    PASS (192 articles / 23 series / 30 topics)
TinySig masked-factor cancellation demo         PASS
Historical snapshot diagnostic                  PASS / expected incomplete-package diagnosis
Threshold/FROST v0.5 regression suite           141/141 tests + 29 subtests PASS
Active Python syntax compilation                PASS
```

The full third-party TinySig 0.1.0 package was **not** installed inside the consolidation sandbox, so the canonical article does not claim end-to-end revalidation of the upstream package. `runme_clean.py` is provided as the clean reproduction path for an isolated Python 3.10/3.11 environment.
