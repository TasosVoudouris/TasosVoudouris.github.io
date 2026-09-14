# Audit of the Original VSS Experiments

The uploaded archive is a useful research notebook, but it combines several
different constructions and operational experiments. Versions 0.2 and 0.3
preserve the sound Feldman and Pedersen ideas in new validated modules while
preventing unfinished material from being mistaken for one working VSS system.

## File-by-file classification

| Original file or group | Classification | Main finding |
|---|---|---|
| `Feldman.py` | Useful Feldman core | The secp256k1 coefficient-commitment equation is structurally correct. Participant key generation is unused; randomness is not cryptographic. |
| `vss.py` | Best basis in the archive | Sharing and Feldman verification use one curve group correctly, but reconstruction uses symbolic/floating evaluation and should use exact modular interpolation. |
| `main.py` | Invalid multiprocess simulation | Every simulated participant calls `participant_work()` independently and receives a share from a different random polynomial. Those shares are not one distribution. |
| `PVSS (python)/feldman.py` | Small modular demonstration | The subgroup idea is useful, but secret-range validation uses `or` instead of `and`, coefficients can equal $q$, and reconstruction uses floating division. |
| bundled `algo/feldman.py` | Incomplete/broken | Constructor names and attributes are inconsistent, and required functions are missing. |
| bundled `algo/pedersen.py` | Empty placeholder | It contains no Pedersen implementation. |
| Pedersen branch in bundled `algo/shamir.py` | Unvalidated attempt | It mixes Shamir, commitment, and parameter-generation code with external dependencies; Version 0.3 implements the construction independently instead of patching this branch. |
| `exampleVSS.py` | Invalid threshold-BLS experiment | Partial signatures are added without Lagrange coefficients, so the result is not a signature under the shared secret key. |
| `vssKZG.py`, `mainKZG.py` | Invalid KZG sketch | They do not construct a standard polynomial commitment and evaluation proof; a coefficient commitment is reused as its own proof. |
| `server.py`, `client.py` | Unsafe local-network sketch | The client disables certificate and hostname verification; the server generates a new polynomial for every request. |
| `mqtt_broker.py`, `mqtt_client.py` | Unsafe network sketch | All shares are placed in `public_parameters` and sent through a public unauthenticated broker, destroying share confidentiality. |
| `generate_cert.py`, certificate/key files | Credential experiment | The included certificate is expired, certificate verification is disabled in the client, and the included private key must not be published or reused. |
| screenshots and PDF | Execution notes | Useful provenance, but not part of the executable cryptographic core. |

## VSS is not PVSS

Feldman VSS lets the recipient of a private share verify it against public
commitments. A public observer does not possess the private share and therefore
cannot perform the same check.

Publicly verifiable secret sharing normally publishes encrypted shares together
with proofs that the ciphertexts contain values consistent with the committed
polynomial. The empty `pedersen.py` file and the directory name `PVSS (python)`
do not themselves implement that stronger property.

## Why KZG was deferred

A KZG polynomial commitment normally commits once to a whole polynomial and
provides an evaluation proof derived from the quotient

$$
q(X)=\frac{f(X)-f(z)}{X-z}.
$$

Verification uses a pairing equation relating the commitment, claimed value,
evaluation point, proof, and structured reference string. The archive instead
creates separate group values for coefficients and sets a commitment equal to
its proof. Patching a few lines would not repair the protocol.

KZG-based VSS can be studied later as a separate construction with test vectors,
trusted-setup assumptions, subgroup checks, serialization rules, and a maintained
pairing library.

## Version 0.3 boundary

The active code is dependency-free and offline. It now implements:

1. one Shamir polynomial per distribution;
2. Feldman and Pedersen coefficient commitments as separate constructions;
3. verification of explicitly labelled private shares;
4. an offline session transcript and consistent-broadcast model;
5. complaint, response, qualification, and abort states;
6. reconstruction from enough verified shares after qualification.

Authenticated networking, real reliable broadcast, public complaint evidence,
DKG, signatures, and encryption remain outside Version 0.3.

Version 0.4 adds a new offline DKG simulator in `dkg.py`; it does not promote or
reuse the archive's invalid threshold-BLS or KZG sketches.
