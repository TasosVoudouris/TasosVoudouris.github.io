# CryptoCave integration

Version 0.5 should become the current downloadable threshold-cryptography
learning package. Keep Versions 0.1–0.4 as tagged historical stages so the
progression remains inspectable.

Suggested repository placement:

```text
threshold-cryptography/
├── README.md
├── code/
│   ├── v0.1/
│   ├── v0.2/
│   ├── v0.3/
│   ├── v0.4/
│   └── v0.5/
├── foundations/
├── verifiable-secret-sharing/
├── distributed-key-generation/
│   ├── from-vss-to-dkg.md
│   ├── multi-dealer-construction.md
│   ├── qualification-and-public-key.md
│   ├── failure-cases.md
│   └── security-boundary.md
├── threshold-signatures/
│   ├── from-dkg-to-signing.md
│   ├── schnorr-and-interpolation.md
│   ├── frost-protocol.md
│   ├── code-walkthrough.md
│   ├── nonces-validation-and-failure.md
│   ├── rfc-conformance-map.md
│   └── security-boundary.md
└── roadmap.md
```

Use chapters 22–28 under `docs/cryptocave/` for the new threshold-signatures
website section. Keep chapters 17–21 for DKG. Preserve relative links or update
every moved link together.

Do not publish the original uploaded VSS ZIP. It contains a private key and
bundled material with unclear redistribution status. The included `legacy/`
selection is already sanitized and quarantined.

## Local verification before committing

In PowerShell:

```powershell
Set-Location .\threshold-cryptography\code\v0.5
python -m unittest discover -v
python .\examples\run_all.py
git status
```

Then review and commit only the intended project paths:

```powershell
git add threshold-cryptography
git commit -m "Add educational FROST signing v0.5"
git push
```

Do not replace the repository's top-level README blindly. Merge its navigation
and site-specific links with the package README during review.
