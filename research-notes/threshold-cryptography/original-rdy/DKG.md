# Eliminating the Single Point of Failure in Cryptographic Systems

In many cryptographic applications today, a trusted third party is required to generate and/or store sensitive secrets, such as private keys. This setup introduces a **single point of failure (SPOF)**—a vulnerability where the compromise or unavailability of a single node endangers the security or availability of the entire system.

Technically, a node constitutes a SPOF if **any** of the following conditions hold:

* The correct operation of the system depends on the availability of that node.
* The node obtains full access to the secret at any point in time.
* A malicious or faulty behavior from the node can result in incorrect or inconsistent system behavior.

Removing such a centralized trust assumption leads to more **resilient, decentralized, and trustworthy cryptographic systems**.

---

## Threshold Cryptography and Secret Sharing

A powerful solution to eliminate SPOFs is **threshold cryptography**. In this paradigm, a secret (e.g., a private key) is never known to any single party. Instead, it is **distributed among multiple parties** using a **secret sharing scheme**, such as **Shamir's Secret Sharing (SSS)**. Each party holds a **key share**, and a cryptographic operation—like decryption or signing—requires a **quorum** of parties (more than a certain threshold $t$) to collaborate.

When such a quorum is formed:

* Each participant computes a **partial result** (e.g., a decryption or signature share) using their share.
* These partial results are then combined by a **non-privileged aggregator** (who learns nothing about the secret) to reconstruct the final result.

This model works for both **symmetric** and **asymmetric** keys. In the asymmetric case, the distributed secret has a corresponding **public key**, which external users can use for encryption or signature verification.

### Example: Threshold Decryption

Consider a sender encrypting a message under a public key whose private counterpart is secret-shared among $n$ parties. The receiver, who is not trusted with the private key, forwards the ciphertext to these parties. Each party computes a **decryption share** and sends it back. Once the receiver collects at least $t+1$ valid shares, they can **reconstruct the plaintext** without learning any party’s private share.

A similar process applies to **threshold signatures**: the parties produce signature shares on a message, and a combiner aggregates them into a **group signature**, which can be verified using the group's public key.

> “If you want to keep a secret, you must also hide it from yourself.”
> — *George Orwell, 1984*

---

## From Secret Sharing to Verifiable Secret Sharing (VSS)

At this point, we must address a key concern: **what if the dealer (the entity distributing shares) is malicious**?

In Shamir’s Secret Sharing (SSS), we assume the dealer behaves honestly—i.e., all shares are generated using the **same polynomial**. If not, different quorums might reconstruct **inconsistent secrets**, breaking the correctness of the scheme and reintroducing a SPOF via the dishonest dealer.

To overcome this, we move to **Verifiable Secret Sharing (VSS)**. In VSS, parties can verify that the shares they received are **consistent**, without knowing the secret. A prominent example is **Feldman’s VSS (Fel-VSS)**, which extends SSS by requiring the dealer to **broadcast homomorphic commitments** to the polynomial coefficients:

$$
F_j = g^{a_j}, \quad \text{for } j = 0, \ldots, t.
$$

Each participant then verifies their share $s_i$ satisfies:

$$
g^{s_i} \stackrel{?}{=} \prod_{j=0}^{t} F_j^{i^j},
$$

ensuring the share is a valid evaluation of the committed polynomial.

Thus, VSS removes the need to **trust the dealer’s honesty**, protecting against malicious behavior during the share distribution.

---

## Distributed Key Generation (DKG)

While VSS removes the need to **trust** the dealer, it still assumes the dealer is **operational** and correctly generates the secret. This residual centrality is problematic in highly adversarial settings.

**Distributed Key Generation (DKG)** eliminates this issue by **removing the dealer altogether**. Instead of one party generating the secret, **all parties jointly generate it**, each acting as a dealer in parallel. The result is that the secret is never known in full to any single party, and the group ends up with a collectively generated shared secret and corresponding public key.

Each party:

* Acts as a VSS dealer and shares a random secret,
* Verifies others’ shares using VSS,
* Contributes to the global secret through their share.

Once the process completes, the parties collectively hold a valid secret sharing of a group secret key, suitable for use in **threshold cryptographic protocols**.

We now turn to a concrete instantiation of DKG: **Pedersen’s DKG**—a synchronous, VSS-based protocol built upon Feldman’s commitment scheme.

# Pedersen’s DKG (Ped-DKG)

Pedersen’s Distributed Key Generation (Ped-DKG) is a threshold DKG protocol in which **every party acts as a dealer**, each executing a **Feldman Verifiable Secret Sharing (Fel-VSS)** sub-protocol. This method—having all parties act as dealers in parallel—is foundational to many DKG designs.

## Protocol Description

The Ped-DKG protocol proceeds as follows:

1. **Polynomial Generation and Commitment**:

   * Each party $P_i$ chooses a random polynomial:

     $$
     f_i(x) = \sum_{j=0}^{t} a_{i,j} x^j \in \mathbb{Z}_q[x],
     $$

     where $a_{i,0} = s_i \in \mathbb{Z}_q$ is its secret contribution.
   * Party $P_i$ computes a **Feldman commitment** to each coefficient:

     $$
     F_{i,j} = g^{a_{i,j}} \in \mathbb{G}, \quad \text{for } j = 0, \ldots, t.
     $$

     The commitment vector is $\mathbf{F}_i = (F_{i,0}, \ldots, F_{i,t})$.

2. **Share Distribution**:

   * For every other party $P_j$, $P_i$ computes:

     $$
     s_{i,j} = f_i(j),
     $$

     and privately sends it to $P_j$.
   * $P_i$ also computes its own public key share $p_i = g^{s_i}$ and optionally broadcasts a commitment to it.

3. **Verification and Complaint Round**:

   * Upon receiving a share $s_{i,j}$, party $P_j$ verifies its validity using the commitments:

     $$
     g^{s_{i,j}} \stackrel{?}{=} \prod_{k=0}^t F_{i,k}^{j^k}.
     $$
   * If verification fails, $P_j$ **broadcasts a complaint** against $P_i$.
   * If a party receives more than $t$ complaints, it is **disqualified**.
   * If it receives between $1$ and $t$ complaints, it must **open all disputed shares**. If any of those fail verification, the party is also disqualified.
   * **Disqualified parties** are excluded from contributing to the group secret. Their shares are set to $1$ multiplicatively (i.e., they contribute nothing to the final key).

4. **Commitment Broadcast**:

   * After all parties have completed verification and complaint rounds, they open their commitments (e.g., reveal $p_i$) and the **group public key** is computed as:

     $$
     \text{pk} = \prod_{i \in \mathcal{H}} p_i = g^{s}, \quad \text{where } s = \sum_{i \in \mathcal{H}} s_i,
     $$

     with $\mathcal{H}$ the set of non-disqualified (honest) dealers.

---

## System State After Sharing Phase

Once the sharing phase is complete:

* Each party $P_j$ holds:

  * Its own secret $s_j = f_j(0)$,
  * A share $s_{i,j} = f_i(j)$ from every other honest dealer $P_i \neq P_j$.
* Thus, each party has $n-1$ received shares and its own.

---

## Secret Reconstruction

To reconstruct the shared secret:

* Each dealer’s secret $s_i$ must be reconstructed by interpolating $f_i(x)$ at $x = 0$.
* Since each $f_i(x)$ is of degree $t$, any $t+1$ valid shares $s_{i,j}$ are sufficient to recover $s_i$.
* The overall group secret is:

  $$
  s = \sum_{i \in \mathcal{H}} s_i,
  $$

  and can be computed if at least $t+1$ shares per polynomial are available.

---

## Assumptions and Fault Tolerance

* **Synchronous Model**: Ped-DKG assumes a fully synchronous network, where all messages are delivered within known time bounds. This ensures that:

  * Complaint rounds complete in time,
  * The protocol always terminates.

* **Fault Tolerance**:

  * The protocol can tolerate up to $t$ **Byzantine faults**, provided:

    $$
    n \geq 2t + 1 \quad \Longrightarrow \quad t \leq \left\lfloor \frac{n-1}{2} \right\rfloor.
    $$
  * This ensures a strict majority of honest parties and sufficient redundancy for polynomial reconstruction.

---

## Summary

| Feature               | Description                                         |
| --------------------- | --------------------------------------------------- |
| Secret sharing        | Parallel Fel-VSS by all parties                     |
| Share verification    | Public with Feldman commitments                     |
| Complaint mechanism   | Yes, during the sharing phase                       |
| Disqualification      | More than $t$ complaints or invalid revealed shares |
| Secret reconstruction | $t+1$ shares per polynomial                         |
| Fault tolerance       | Up to $t < \frac{n}{2}$ malicious parties           |
| Synchrony required    | Yes, fully synchronous model                        |
| Compatibility         | Works with schemes requiring field elements         |


Absolutely! Let's now continue with a **rigorous academic write-up** of **Aggregatable DKG (Agg-DKG)**, including its use of the **Scrape PVSS** scheme. This is written as a continuation of the previously structured Ped-DKG section.

---

# Aggregatable DKG (Agg-DKG)

**Aggregatable DKG (Agg-DKG)** is a scalable and efficient DKG protocol that leverages **aggregation** to reduce communication and verification overhead. It is built upon a modified version of the **Scrape** protocol— a **Publicly Verifiable Secret Sharing (PVSS)** scheme based on Feldman-VSS—allowing aggregation of publicly verifiable shares and eliminating the need for complaint rounds.

---

## Scrape: Modified Publicly Verifiable Secret Sharing

Scrape enhances standard VSS by making shares **publicly verifiable** and **encrypting** them so that each recipient can uniquely decrypt their corresponding share.

### Key Features

* **Public Verifiability**: Any party (including third parties) can verify the validity of shares using public data.
* **Encrypted Sharing**: Shares are encrypted under each recipient's public key, allowing only the intended recipient to decrypt.
* **No Complaint Round**: Verification is deterministic and does not rely on participant interaction or dispute resolution.
* **Aggregation-Friendly**: Cryptographic structures used allow for aggregation of multiple PVSS transcripts.

---

## Scrape Setup

### Initialization

All parties share a **Common Reference String (CRS)** containing:

* A **bilinear group** $\mathbb{G}_1, \mathbb{G}_2, \mathbb{G}_T$ with pairing $e: \mathbb{G}_1 \times \mathbb{G}_2 \rightarrow \mathbb{G}_T$,
* A generator $g_1 \in \mathbb{G}_1$ and $h_1 \in \mathbb{G}_2$,
* **Encryption key** for each party $P_i$: $\mathsf{ek}_i = h_1^{\mathsf{dk}_i} \in \mathbb{G}_2$,
* The corresponding **secret decryption key** $\mathsf{dk}_i \in \mathbb{Z}_q$ is kept private.

---

## Scrape Protocol

### Sharing Phase

The dealer $D$ performs the following:

1. Chooses a **random degree-$t$ polynomial**:

   $$
   f(x) = a_0 + a_1x + \cdots + a_tx^t, \quad \text{where } s = f(0).
   $$

2. Computes:

   * **Commitments to the polynomial coefficients**:

     $$
     F_j = g_1^{a_j} \in \mathbb{G}_1 \quad \text{for } j = 0, \ldots, t.
     $$
   * **Share commitments**:

     $$
     A_i = g_1^{f(i)}.
     $$
   * **Encrypted shares** for each party $P_i$:

     $$
     Y_i = \text{Enc}_{\mathsf{ek}_i}(f(i)) = \mathsf{ek}_i^{f(i)} = h_1^{\mathsf{dk}_i \cdot f(i)} \in \mathbb{G}_2.
     $$

3. Publishes the **PVSS transcript**:

   $$
   \text{PVSS} = \left( (F_0, \ldots, F_t), (A_1, \ldots, A_n), (Y_1, \ldots, Y_n) \right).
   $$

### Verification Phase

Any party can verify the validity of each share $Y_i$ as follows:

1. Confirm that the share commitment matches the polynomial commitment:

   $$
   A_i \stackrel{?}{=} \prod_{j=0}^t F_j^{i^j}.
   $$

2. Confirm that the encrypted share matches the committed share using bilinear pairing:

   $$
   e(g_1, Y_i) \stackrel{?}{=} e(A_i, \mathsf{ek}_i).
   $$

This ensures that:

* $A_i = g_1^{f(i)}$,
* $Y_i = \mathsf{ek}_i^{f(i)}$,
* Therefore, $f(i)$ is consistent, encrypted properly, and committed correctly.

---

## Secret Reconstruction

To reconstruct the secret:

1. A **quorum** of parties decrypt their shares $Y_i$ using $\mathsf{dk}_i$ to obtain $f(i)$.
2. Lagrange interpolation is applied in the exponent to recover:

   $$
   g_1^{f(0)} = \prod_{i \in S} A_i^{\lambda_i(0)} \quad \text{(where \( \lambda_i(0) \) are Lagrange coefficients)}.
   $$
3. If necessary, the plaintext $f(0)$ (i.e., the secret) can be obtained via discrete logarithm in a small domain or through additional protocol mechanisms.

---

## Aggregation of PVSS Transcripts

Let two dealers share secrets with their own PVSS transcripts:

* Commitments: $F^{(1)}_j = g_1^{a^{(1)}_j}$, $F^{(2)}_j = g_1^{a^{(2)}_j}$,
* Share commitments: $A^{(1)}_i = g_1^{f^{(1)}(i)}$, $A^{(2)}_i = g_1^{f^{(2)}(i)}$,
* Encrypted shares: $Y^{(1)}_i = \mathsf{ek}_i^{f^{(1)}(i)}$, etc.

Then the **aggregated PVSS transcript** is:

* Aggregated commitments:

  $$
  F^{(agg)}_j = F^{(1)}_j \cdot F^{(2)}_j = g_1^{a^{(1)}_j + a^{(2)}_j},
  $$
* Aggregated share commitments:

  $$
  A^{(agg)}_i = A^{(1)}_i \cdot A^{(2)}_i = g_1^{f^{(1)}(i) + f^{(2)}(i)},
  $$
* Aggregated encrypted shares:

  $$
  Y^{(agg)}_i = Y^{(1)}_i \cdot Y^{(2)}_i = \mathsf{ek}_i^{f^{(1)}(i) + f^{(2)}(i)}.
  $$

This supports **verifiable aggregation** of secrets in public view, enabling efficient distributed key generation.

---

## Advantages of Scrape in Agg-DKG

| Feature                         | Benefit                                                      |
| ------------------------------- | ------------------------------------------------------------ |
| Public verifiability            | Anyone can verify shares without interaction                 |
| No complaint round              | Deterministic validity check reduces protocol rounds         |
| Homomorphic aggregation         | Transcripts can be combined efficiently                      |
| Asynchronous-friendly structure | Easier extension to eventual-sync or gossip-based models     |
| Crashed node recovery           | Lost nodes can retrieve shares post-factum using public data |

Great! Let's now **formally continue** the write-up from the **Scrape-based PVSS** into the **Aggregatable DKG (Agg-DKG)** protocol, using the information from the image and maintaining academic precision.

---

## Aggregatable DKG (Agg-DKG)

**Agg-DKG** is a scalable DKG protocol constructed by instantiating every party as a **Scrape PVSS dealer**, as opposed to Ped-DKG where Feldman VSS is used. This results in a total of $n$ PVSS transcripts being generated, one per party. It supports **aggregation**, **gossiping**, and **lightweight verification**, offering significant performance improvements over traditional DKGs.

---

### Key Setup and Group Secret

* Each party $P_i$ generates a **Scrape transcript** and a **secret value** $c_i \in \mathbb{F}_q$.
* The public commitment to $c_i$ is:

  $$
  C_i = g_1^{c_i} \in \mathbb{G}_1.
  $$
* The group’s **public key** is:

  $$
  \text{pk} = \left( g_1^a, \hat{u}_1^a \right) \in \mathbb{G}_1 \times \mathbb{G}_2,
  $$

  and the group **secret key** is:

  $$
  \text{sk} = \hat{u}_1^a \in \mathbb{G}_2, \quad \text{where } a = \sum_{P_i \in \mathcal{Q}} c_i,
  $$

  and $\mathcal{Q}$ is the set of honest dealers determined via public verification.

---

### Signature of Knowledge (SoK)

To ensure that a dealer knows its committed secret $c_i$, it generates a **Signature of Knowledge** (SoK) on its commitment:

* Dealer uses signing key pair $(\mathsf{sk}_i, \mathsf{vk}_i)$.
* First commits to $c_i$: $C_i = g_1^{c_i}$.
* Then produces:

  $$
  \sigma_i = (\sigma_{i,1}, \sigma_{i,2}) = \left( \text{Hash}_{\mathbb{G}_2}(C_i)^{c_i},\ \text{Hash}_{\mathbb{G}_2}(\mathsf{vk}_i, C_i)^{\mathsf{sk}_i} \right).
  $$

This proves knowledge of $c_i$ **without revealing** it, binding the dealer to its transcript.

---

### Verification and Aggregation

* The **simplest approach** would require every participant to verify every individual PVSS transcript, leading to $\mathcal{O}(n^2)$ complexity.
* However, due to **Scrape's public verifiability** and **homomorphic structure**, PVSS transcripts can be **aggregated**.
* Agg-DKG uses a **gossip protocol** to circulate and merge transcripts, reducing the total verification complexity to:

  $$
  \mathcal{O}(n \log^2 n).
  $$
* Since gossip is random, some transcripts may be **included multiple times**. Therefore, each dealer’s contribution is assigned a **weight** $w_i$, and the secret is now computed as a **weighted sum**:

  $$
  \text{sk} = \sum_{i \in \mathcal{Q}} w_i \cdot c_i.
  $$

---

### Transcript Format

To encapsulate all the required data, Agg-DKG defines the following **DKG transcript**:

$$
\mathsf{tr} = \left( (C_0, \ldots, C_n),\ (w_0, \ldots, w_n),\ (\sigma_0, \ldots, \sigma_n),\ \mathsf{pvss} \right),
$$

where:

* $C_i = g_1^{c_i}$: commitment to secret,
* $w_i$: share weight for aggregation,
* $\sigma_i$: SoK for $c_i$,
* $\mathsf{pvss}$: aggregated PVSS transcript from Scrape.

This transcript is publicly verifiable and **determines the group key** that will be used for threshold cryptography.

---

### Benefits of Agg-DKG

| Feature                | Advantage                                                     |
| ---------------------- | ------------------------------------------------------------- |
| Aggregatable PVSS      | Reduces verification overhead and supports gossiping          |
| Public verifiability   | No complaint rounds; no trusted setup                         |
| Signature of Knowledge | Ensures correctness and non-equivocation of dealer shares     |
| Gossip protocol        | Avoids all-to-all communication                               |
| Crashed node recovery  | Nodes can retrieve shares post-factum using public transcript |

Certainly! Here's the **completed and formally structured markdown** for the **Aggregatable DKG (Agg-DKG)** protocol, now including the final sections on transcript finalization, aggregation, protocol operation, communication complexity, and concluding thoughts. All parts are rewritten clearly and rigorously for academic and cryptographic precision.




### Full Transcript and Finalization

A **transcript** in Agg-DKG is called a **full transcript** if it:

* Is **valid**, meaning all of its components pass verification (see below),
* Includes at least $t+1$ valid contributions from dealers (i.e., those with non-zero weight).

> Multiple full transcripts may exist simultaneously, as validity and inclusion depend on the aggregated set of contributions.

---

### Aggregation Process

Aggregation of DKG transcripts proceeds as follows:

* **Commitments** $C_i = g_1^{c_i}$, **SoKs** $\sigma_i$, and **weights** $w_i$ are merged.
* Transcripts are combined by **element-wise addition** of the PVSS structures (which are homomorphic), and the weights $w_i$ are **summed** accordingly.

The result is a new transcript referring to the aggregated, combined polynomial that corresponds to the weighted shares:

$$
\text{sk} = \sum_{i \in \mathcal{Q}} w_i \cdot c_i.
$$

---

### Verification

The **verification** of a DKG transcript proceeds in three steps:

1. **Verify the aggregated PVSS transcript** using Scrape's bilinear pairing checks.
2. For every $i$ such that $w_i \neq 0$, verify:

   * The Signature-of-Knowledge $\sigma_i$,
   * The consistency between the commitment $C_i$ and the aggregated polynomial.
3. Confirm that all aggregated components agree with the polynomial commitment structure.

If all checks pass, the transcript is considered **valid**.

---

### Protocol Execution

Agg-DKG operates under the **fully synchronous communication model**, assuming strict bounds on message delivery. The protocol runs as follows:

1. **Initialization (Round 0)**:

   * Each dealer $P_i$:

     * Generates its PVSS transcript $\text{pvss}_i$,
     * Computes its commitment $C_i$ and Signature-of-Knowledge $\sigma_i$,
     * Sets its initial transcript with weight $w_i = 1$, and others as $\perp$ or 0.

2. **Gossip Phase (Rounds 1 to termination)**:

   * Parties receive, verify, and **aggregate** incoming DKG transcripts.
   * Each party gossips its **non-full, aggregated transcript** to a small random subset of other parties.
   * If a full transcript is created, it is broadcast to all parties with some fixed probability.
   * Eventually, **all parties agree** to keep the full transcript whose resulting public key has the **lowest bit-length** (binary representation).

---

### Termination

* The protocol is guaranteed to terminate in a synchronous setting once a full transcript is broadcast.
* The **first round** in which a full transcript is observed is considered the **last round** of the protocol.
* If multiple full transcripts are observed, the one with the smallest key representation is selected.

---

### Communication Complexity

* Communication cost is significantly reduced:

  $$
  \mathcal{O}(c \log^2 n), \quad \text{for some constant } c \geq 4.
  $$
* This compares favorably with $\mathcal{O}(n^2)$ of naive all-to-all verification.

---

### Fault Tolerance

Agg-DKG is resilient to both crash and Byzantine faults:

* Let $t_c$ be the number of **crashed** parties, and $t_b$ the number of **Byzantine (malicious)** parties.
* Fault thresholds must satisfy:

  $$
  t_c < \frac{n}{2 \log n}, \quad t_b \leq \log n,
  $$

  $$
  \Rightarrow t < n - t_c - t_b \quad \text{so in practice, } t < \frac{2n}{3}.
  $$

---

## Final Thoughts

Agg-DKG offers several critical advantages:

* **Scalability**: Efficient aggregation makes it suitable for large-scale deployments.
* **No complaint rounds**: Public verifiability replaces interactive dispute resolution.
* **Fault tolerance**: Can handle both crashed and malicious participants robustly.
* **Post-failure recovery**: Since the protocol is public and non-interactive, crashed nodes can recover their shares upon rejoining, as long as they retain their decryption key.

However, some limitations must be acknowledged:

* **Synchronous assumption**: Agg-DKG relies on bounded-delay message delivery, which may not always hold in Internet-scale or asynchronous environments.
* **Group elements**: Shares and secrets are group elements rather than field elements, which may restrict compatibility with cryptosystems expecting scalar (field) secrets.

---

Would you like a full LaTeX version of this document next, or a visual diagram summarizing the Agg-DKG flow?

