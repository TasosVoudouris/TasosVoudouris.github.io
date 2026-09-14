# Comparing SSS, Multisignatures, BLS Aggregation, DKG, and Threshold Signatures

## Introduction: Cryptographic Key Management Without a Single Point of Failure

Consider Alice, a high-value individual who controls a cryptographic private key used to sign transactions. Her key is a valuable target—if compromised, all her assets could be stolen. Cryptography offers various approaches to mitigate this risk by **distributing trust** and **eliminating single points of failure (SPOFs)** in key management.

This report compares the main techniques designed for this purpose:

* **Shamir Secret Sharing (SSS)**
* **Multisignature schemes (Multisig)**
* **Aggregated signatures (e.g., BLS)**
* **Distributed Key Generation (DKG)**
* **Threshold signature schemes**

We explore their theoretical foundations, security assumptions, operational models, and trade-offs.

---

## 1. Shamir Secret Sharing (SSS)

### Overview

Shamir's Secret Sharing scheme is a “threshold secret sharing” mechanism based on polynomial interpolation over a finite field.

### How it Works

To split a secret $s \in \mathbb{F}_p$ among $n$ parties such that any $t+1$ can reconstruct it:

1. Choose a random degree-$t$ polynomial:
   $f(x) = a_0 + a_1x + \cdots + a_t x^t, \quad \text{with } a_0 = s.$
2. Each share is a point on this polynomial: $s_i = f(i)$.
3. Any subset of $t+1$ shares can reconstruct $f(0) = s$ using Lagrange interpolation.

### Security

* **Perfect secrecy**: Any $t$ or fewer shares reveal nothing about $s$.
* **SPOF warning**: If one entity (the dealer) constructs and knows all shares, then we still rely on their integrity.

### Extensions

* **Verifiable Secret Sharing (VSS)**: Allows participants to verify the shares (e.g., Feldman VSS).
* **Proactive Secret Sharing (PSS)**: Allows periodic resharing to defend against long-term compromise.

### Use Case Limitation

SSS is not interactive after share distribution, but it requires a trusted dealer. To sign or decrypt, the secret must be reconstructed somewhere, creating a temporary SPOF.

---

## 2. Multisignature Schemes

### Overview

A **multisignature (multisig)** scheme requires multiple parties to sign the same message individually. Their signatures are then sent to the verifying system.

### Properties

* All participants use their **own key pairs**.
* Final output is a **set of $n$** signatures.
* The verifier must maintain all $n$ public keys.

### Advantages

* **No secret reconstruction**: The key remains distributed.
* **No trusted dealer**: Each signer generates their own key.

### Limitations

* **Signature size scales linearly** with the number of signers.
* **Verification cost** grows with the number of public keys.

---

## 3. Aggregated Signatures (e.g., BLS)

### Overview

**BLS (Boneh-Lynn-Shacham)** signatures enable aggregation: multiple signatures on the same message can be compressed into a single signature.

### BLS Aggregation

Given multiple signers with public keys $pk_1, \ldots, pk_n$ and signatures $\sigma_1, \ldots, \sigma_n$, all signing the same message:
$\sigma = \prod_{i=1}^n \sigma_i \in \mathbb{G}_1.$
This single $\sigma$ can be verified against the **aggregated public key**.

### Advantages

* **Single signature** verification.
* **Space efficiency**: Verifiers handle only one signature.

### Limitations

* **Slower signing/verification** due to pairing operations.
* All signatures must be on the **same message** (basic BLS).
* Requires bilinear pairings (not as fast as ECDSA/EdDSA).

### Advanced Notes

* **Threshold BLS** is possible.
* **Aggregate public keys** are supported, allowing for reduced verification overhead.

---

## 4. Distributed Key Generation (DKG)

### Overview

**DKG** removes the need for a trusted dealer. Instead, parties jointly generate a key pair using Multi-Party Computation (MPC).

Each party:

* Samples its own secret and shares it via VSS.
* Receives and verifies shares from others.
* Combines results to derive a **common secret** and corresponding public key.

### Advantages

* **No single point ever knows the secret**.
* Supports threshold cryptographic operations directly.

### Example Use Case

* Generate a group signing key without any party learning it.

### Limitations

* Requires multiple rounds of interaction.
* Usually assumes **synchronous networks**.
* Can be complex to implement and verify securely.

---

## 5. Threshold Signature Schemes

### Overview

Threshold signatures allow any $t+1$ out of $n$ parties to generate a **single, valid group signature**, without ever reconstructing the full secret key.

### Properties

* **Signing is distributed**.
* **Final signature is compact** (like a regular signature).
* Can be constructed over ECDSA, BLS, Schnorr, etc.

### Advantages

* Removes SPOFs.
* Supports fault tolerance.
* Often indistinguishable from a standard signature.

### Notes on Construction

* Usually built on top of DKG or using threshold adaptations of known signature schemes.
* E.g., BLS is particularly friendly to thresholdization.

---

## Comparison Table

| Technique             | Dealer Required | SPOF Risk | Compact Output | Threshold Capable | Public Key Aggregation | Signature Overhead    |
| --------------------- | --------------- | --------- | -------------- | ----------------- | ---------------------- | --------------------- |
| Shamir Secret Sharing | Yes             | Yes       | No             | Yes               | No                     | N/A (not a signature) |
| Multisig              | No              | No        | No             | Yes               | No                     | Linear in n           |
| BLS Aggregated Sig.   | No              | No        | **Yes**        | Yes               | Yes                    | Constant              |
| DKG                   | No              | **No**    | N/A            | Yes               | Yes (depends)          | N/A                   |
| Threshold Signatures  | No              | No        | **Yes**        | **Yes**           | Yes                    | Constant              |

---

## Final Notes

* Most of these schemes assume **honest-but-curious** participants. Handling malicious parties often requires additional complexity (e.g., verifiable secret sharing, robust DKG).
* There is active research on extending these protocols to asynchronous networks and real-world cryptographic curves.
* Recently, **zero-knowledge proofs (ZKPs)** have been proposed to verify multiple signatures across **distinct messages** in compressed form. These could generalize aggregation beyond single-message cases.

Threshold cryptography is a rich and evolving field. While many schemes remain under standardization, they are already being used in cryptocurrencies, secure multi-party computation (MPC), and distributed ledger technologies.
