# Zero-Knowledge Proof Systems — companion experiments

Small, dependency-free educational experiments supporting the canonical CryptoCave ZK series.

These are **not production proof systems**. They isolate specific algebraic ideas:

- `sigma/`: Schnorr Sigma protocol and special-soundness extraction;
- `fiat-shamir/`: domain-separated Fiat–Shamir transform of the Schnorr transcript;
- `r1cs/`: a finite-field R1CS witness check;
- `qap/`: interpolation of the R1CS into a QAP and the target-polynomial divisibility condition;
- `merkle/`: Merkle commitment and authentication path;
- `fri/`: one correct algebraic FRI folding step, not a full STARK prover.

Run everything with:

```bash
python experiments/zero-knowledge/run_all.py
```

The original `ZKPs.zip` also contained several third-party educational repositories. Those are **not copied into the canonical repository**. Their useful concepts were reviewed and synthesized into the articles, while the per-file cleanup ledger records provenance.
