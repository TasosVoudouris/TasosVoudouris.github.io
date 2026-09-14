# DKG failure cases and adversarial lessons

Version 0.4 treats failure behavior as part of the construction rather than an
afterthought. A DKG that produces incompatible shares or keys is worse than one
that aborts visibly.

## Failure matrix

| Failure | Detection point | Version 0.4 result | Why |
|---|---|---|---|
| Missing or duplicate dealer package | Registration | Global abort | Every configured participant must have one unambiguous dealer role |
| Changed Pedersen share component | Hidden VSS verification | Complaint | Private delivery is inconsistent with the dealer commitment |
| Valid private replacement | Complaint response | Dealer may qualify | Replacement matches the original commitment vector |
| Unresolved Pedersen complaint | VSS finalization | Dealer excluded before $Q$ | Dealer never completed hidden qualification |
| Too few hidden-qualified dealers | Qualification policy | Global abort | Local availability policy is not met |
| Different participant views of $Q$ | Qualification agreement | Global abort | Different sets produce different distributed keys |
| Unknown or duplicate dealer in a view | Qualification validation | Global abort | View is malformed or replayed from another context |
| Value vector inconsistent with accepted secret shares | Public-key extraction | Global abort | $Q$ is already fixed; silently changing it would alter the key definition |
| Changed final aggregate key share | Final dual verification | Rejection/abort | Returned distributed state is inconsistent |
| Reusing a coordinator | State check | Rejection | One object represents one session and transcript |

## 1. Bad dealer before qualification

If dealer 2 sends participant 1 a changed share and never repairs it, only dealer
2's VSS session aborts. The provisional set becomes

$$
Q=\{1,3,4,5\}.
$$

If every participant agrees and the configured minimum is met, the remaining
four contributions aggregate correctly. This is shown in
`dkg_bad_dealer_demo.py`.

## 2. Bad dealer after qualification

The later value round has a different rule. Its dealer is already in $Q$, which
was fixed under hidden commitments. Removing it after observing the value vector
would redefine the output based on later information.

The complete GJKR design has a recovery procedure that reconstructs the faulty
dealer contribution publicly when necessary. Version 0.4 does not implement
that procedure, so it aborts the entire DKG.

This conservative abort preserves a clear claim but does not prevent selective
denial of service or prove unbiased output under repeated adversarial restarts.

## 3. Known Pedersen generator relation

In the toy group $h=g^{17}$. A pair can be changed as

$$
s'=s+1,
\qquad
t'=t-17^{-1}\pmod{41},
$$

without changing $g^sh^t$. The Pedersen equation therefore accepts the forged
pair in this insecure setup.

The separate value equation checks $g^{s'}$ against $A_{i,k}$ and fails. Because
the dealer already passed hidden qualification, Version 0.4 aborts. The example
`dkg_extraction_abort_demo.py` makes this boundary visible.

With production Pedersen parameters, nobody should know the generator relation.
The second round still remains necessary to extract and verify the public key.

## 4. Conflicting qualified sets

`dkg_qualification_abort_demo.py` gives participant 5 a set that omits dealer 1
while the other participants include all five. No aggregation occurs. The
coordinator moves to `aborted` and returns no `DKGResult`.

This is only a local assertion check. A real protocol needs reliable broadcast
or agreement to make a common qualified set emerge under faults; comparing
preconstructed Python tuples does not implement that mechanism.

## 5. Complaint repair

A dealer may replace a corrupted private delivery while the hidden VSS complaint
phase is open. The replacement must use the same participant identifier and
verify against the original Pedersen vector. Changing commitments is not a
repair.

The DKG tests confirm that a valid replacement returns the dealer to the
qualified path, while an invalid or missing replacement excludes it.

## 6. Tampering with final shares

Final key shares are checked against both aggregate vectors. Changing only the
secret component makes both equations fail. Changing only the blinding component
makes Pedersen fail. A pair forged through the toy generator relation can still
pass Pedersen but not the value equation.

These checks establish consistency with the transcript. They do not authenticate
who stored or transmitted the share.

Next: [Version 0.4 security boundary](21-version-04-security-boundary.md).
