# Validation record for Version 0.5

## Automated suite

The complete dependency-free suite passes:

```text
Ran 141 tests
OK
```

Version 0.5 adds 44 FROST-specific tests. The inherited 97 tests remain intact.

### FROST-specific coverage

The Version 0.5 tests check:

- an honest 3-out-of-5 execution produces individually valid response shares
  and a valid final Schnorr signature;
- all ten threshold-size subsets sign successfully;
- 4-out-of-5 and 5-out-of-5 signer sets sign successfully;
- unordered signer input produces an ascending canonical package;
- Lagrange coefficients reproduce a degree-two polynomial's constant and reject
  missing, duplicate, or zero identifiers;
- binding factors cover the exact signer set and bind message and commitment
  list inputs;
- commitment-list encoding is the exact concatenation of canonical
  `(identifier, D_i, E_i)` tuples;
- group commitment and challenge helpers match their documented equations;
- every signature share satisfies its individual public verification equation;
- the final output passes the standalone ordinary Schnorr verifier;
- the raw payload is different from the bound application envelope;
- changes to the message, session, counter, application context, or signer set
  invalidate the demonstrated signature when they produce a distinct toy
  challenge;
- changed final commitment/response and changed partial response are rejected;
- an invalid response identifies the participant and forces abort;
- responses bound to another package are rejected;
- missing, duplicate, and extra response sets abort;
- signer nonce state disappears after one use and a second call raises
  `NonceReuseError`;
- a changed own commitment, wrong session/counter, and unselected signer abort;
- a rejecting message policy burns the associated nonce state;
- a different DKG/group-information digest aborts;
- too few signers, duplicate/unknown identifiers, and invalid subgroup elements
  are rejected before signing;
- the coordinator tracks reused public commitments, refuses unissued packages,
  and closes a package after one aggregation attempt;
- malformed randomness sources are rejected;
- identity public/verification keys are rejected;
- signature encoding is fixed-width `R || z`;
- public signing transcripts omit private key-share and nonce-scalar fields;
- normal signing succeeds while both Shamir reconstruction methods are replaced
  by exceptions;
- deterministic example inputs reproduce package, signature, and transcript;
- message and commitment hash roles are domain-separated;
- noncanonical final scalar values fail safely; and
- the suite context is explicitly distinct from RFC named ciphersuites.

### DKG-specific coverage

The DKG tests check:

- an honest 3-out-of-5 execution reaches `complete` with all five dealers;
- every final key share verifies under both aggregate commitment vectors;
- all ten threshold coalitions reconstruct the same scalar in explicit audit
  mode and satisfy $Y=g^x$;
- normal execution completes while both Shamir reconstruction methods are
  replaced by exceptions;
- neither `DKGResult` nor the public transcript exposes a group-secret field;
- the public key equals the product of qualified constant value commitments;
- every aggregate coefficient commitment equals the product of the corresponding
  qualified dealer commitments;
- one unresolved Pedersen complaint excludes only that dealer before $Q$;
- a valid private replacement returns that dealer to the qualified path;
- a mismatched post-qualification value vector causes global abort;
- a forged pair exploiting the toy relation $h=g^{17}$ passes Pedersen but is
  rejected by the value round, causing global abort;
- conflicting, missing, duplicate, and unknown qualification entries abort;
- too few hidden-qualified dealers abort under the configured local policy;
- missing and duplicate dealer packages are rejected;
- unknown overrides and responses are rejected;
- one coordinator cannot be reused for another execution;
- transcript digests bind the global session and qualified set;
- a changed final key share is rejected;
- a mathematically valid key share bound to the wrong qualified set is rejected;
- a dealer response without an active complaint is rejected;
- audit reconstruction rejects insufficient, duplicate, and unknown identifiers;
- invalid minimum-qualified-dealer policies are rejected;
- every final share records the exact common source-dealer set.

The Pedersen-extension tests check explicit coefficient-vector distribution and
length validation for the DKG dealer builder.

The inherited DKG section below records Version 0.4 coverage. Versions 0.1–0.3
continue to cover the mathematical foundation, Feldman VSS, Pedersen VSS, and
session state.

## Direct execution

All 55 active Python files under `cryptocave_sss/`, `examples/`, and `tests/`
are run individually from their own folders. Representative DKG files are also
run by absolute path from an unrelated working directory. Quarantined files
under `legacy/` remain excluded.

## Documentation and safety checks

Validation also covers:

- Python byte-compilation;
- every local Markdown link;
- balanced Markdown code fences;
- absence of credential files, certificate files, bytecode caches, and unsafe
  network scripts from the distributable archive;
- ZIP integrity;
- a clean extracted run of all 97 tests and all examples.

These checks establish consistency with the documented educational model. They
are not a production security audit, an RFC conformance certification, or proof
of a distributed DKG/FROST system.
