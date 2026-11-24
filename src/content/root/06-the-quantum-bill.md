---
title: 'The quantum bill'
description: 'Every byte of the TLS handshake re-priced for every post-quantum signature we can run: ML-DSA, SLH-DSA, Falcon, and the NIST round-3 candidates, measured with real implementations. A role-by-role cost model that reproduces Part 02 to the byte, an exhaustive search for the cheapest mix of schemes, and the limit that no choice of signature can get past.'
part: 6
pubDate: 2026-11-22
tags:
  - post-quantum
  - signatures
  - ml-dsa
  - slh-dsa
  - falcon
  - tls
companion: experiments/root-of-trust
---

Part 02 measured one post-quantum handshake: ML-DSA everywhere, 15,802 bytes of authentication, one round trip lost. That was one point in a large space. There are other standardized signatures (SLH-DSA, and Falcon on its way), and a whole second generation under evaluation at NIST, each with its own trade between public key size, signature size and speed. Some of them are terrible for the web. Some are surprisingly good, but only in the right place.

This part prices the whole space. It measures every scheme we can actually run, builds a cost model of the handshake **by role** (because the leaf, the CA, the root and the logs pay for different things), checks that model against Part 02's real measurements, and then searches every way of assigning schemes to roles for the cheapest bill under stated constraints.

By the end you should be able to:

1. place each family of post-quantum signatures on the map of key size against signature size, and say where its standardization stands;
2. explain why a 412 KB public key can cost a TLS handshake **nothing**, and a 2,420-byte signature costs it five times over;
3. price any certificate chain from its schemes alone, and say whether it fits in one round trip;
4. name the cheapest combinations available today, with draft standards, and with candidates, and the caveats on each;
5. say why even the best choice leaves the problem only half solved.

The code is [`experiments/root-of-trust/06_quantum_bill.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust), with tests in `test_06_quantum_bill.py`. It measures classical schemes and ML-DSA with `cryptography`, and everything else with liboqs (`pip install liboqs-python`) when it is installed. Without liboqs it falls back to a table of the sizes measured here, which the specifications fix anyway.

## The menu

Post-quantum signatures come from a handful of mathematical families, and each family has a characteristic shape.

**Lattices.** ML-DSA (FIPS 204, the former CRYSTALS-Dilithium) and Falcon. Mid-sized keys and signatures, fast. Falcon is markedly smaller, but its signing algorithm samples from a Gaussian distribution using floating-point arithmetic, which is hard to implement in constant time and hard to validate; NIST's own status talk on FIPS 206 lists special challenges relating to floating point. NIST submitted the draft standard for FN-DSA (FIPS 206) for approval on 28 August 2025; at the time of writing it is still a draft, with the final standard expected in late 2026 or early 2027.

**Hash functions.** SLH-DSA (FIPS 205, the former SPHINCS+). Its security rests only on the hash function, the most conservative assumption on the table. The price is size: tiny 32-byte public keys, but signatures from 7.8 to 50 KB, and slow signing for the small variants.

**Multivariate equations.** UOV, MAYO, SNOVA. The extreme opposite of SLH-DSA: signatures of a hundred or two hundred bytes, public keys from 1 KB to hundreds of KB. UOV is old and well studied (1999), and its weakness is entirely the key size; MAYO and SNOVA are newer designs that shrink the key with more structure.

**MPC-in-the-head.** MQOM, FAEST, SDitH. Tiny keys, signatures of several kilobytes, built from symmetric primitives and zero-knowledge techniques.

**Isogenies** (SQIsign) and **other lattices** (HAWK). SQIsign has the smallest key plus signature of any candidate, at the price of slow signing, and HAWK is a compact lattice alternative to Falcon without the floating point; both rest on assumptions NIST itself calls relatively novel.

The first group of standards (ML-DSA, SLH-DSA) was published in August 2024. To diversify beyond lattices, NIST runs a second competition for additional signatures; on 14 May 2026 it announced nine third-round candidates: FAEST, HAWK, MAYO, MQOM, QR-UOV, SDitH, SNOVA, SQIsign and UOV. The third round is expected to last about two years, and candidates may still tweak their parameters.

Here is what we can measure. Sizes are as implemented in liboqs 0.16.0 (candidates are in their second-round form) and in `cryptography`; times are medians on the author's machine and only indicative:

| scheme | status | NIST category | public key | signature | sign | verify |
|---|---|---:|---:|---:|---:|---:|
| Ed25519 | classical | none | 32 | 64 | 0.031 ms | 0.102 ms |
| ECDSA P-256 | classical | none | 65 | ~71 | 0.023 ms | 0.078 ms |
| RSA-2048 | classical | none | 270 | 256 | 0.340 ms | 0.027 ms |
| ML-DSA-44 | FIPS 204 | 2 | 1,312 | 2,420 | 0.058 ms | 0.020 ms |
| ML-DSA-65 | FIPS 204 | 3 | 1,952 | 3,309 | 0.082 ms | 0.030 ms |
| ML-DSA-87 | FIPS 204 | 5 | 2,592 | 4,627 | 0.095 ms | 0.044 ms |
| Falcon-512 | draft FIPS 206 | 1 | 897 | ~655 | 0.236 ms | 0.041 ms |
| Falcon-1024 | draft FIPS 206 | 5 | 1,793 | ~1,270 | 0.406 ms | 0.074 ms |
| SLH-DSA-SHA2-128s | FIPS 205 | 1 | 32 | 7,856 | 553 ms | 0.542 ms |
| SLH-DSA-SHA2-128f | FIPS 205 | 1 | 32 | 17,088 | 27 ms | 1.871 ms |
| MAYO-1 | round 3 | 1 | 1,420 | 454 | 0.219 ms | 0.089 ms |
| MAYO-2 | round 3 | 1 | 4,912 | 186 | 0.110 ms | 0.024 ms |
| SNOVA-24-5-4 | round 3 | 1 | 1,016 | 248 | 0.433 ms | 0.088 ms |
| UOV-Ip-pkc | round 3 | 1 | 43,576 | 128 | 0.028 ms | 0.058 ms |
| UOV-Is | round 3 | 1 | 412,160 | 96 | 0.031 ms | 0.041 ms |
| MQOM-L1-short | round 3 | 1 | 60 | 2,916 | 1.987 ms | 1.862 ms |

Three notes. ML-DSA-44 is a category 2 scheme, slightly stronger than the category 1 sets it is compared with. Falcon's signatures vary in length (they are compressed); the script averages a few thousand, and a fixed-length "padded" variant at 666 bytes also exists. And HAWK, SQIsign, FAEST, SDitH and QR-UOV are not in liboqs 0.16, so they are not measured here; a table of their sizes from second-hand sources would be exactly the kind of number this series does not print.

<figure class="plate">
<img src="/images/root/06-menu.svg" alt="Log-log plot of public key size against signature size. Classical schemes cluster under 300 bytes in the bottom left. ML-DSA sits at 1.3 to 2.6 KB keys and 2.4 to 4.6 KB signatures, Falcon smaller. SLH-DSA has 32-byte keys and 7.8 to 17 KB signatures. MQOM has 60-byte keys and 2.9 KB signatures. UOV has 96 to 128-byte signatures and 43 to 412 KB keys. MAYO and SNOVA sit in between." width="1000" height="700" loading="lazy" />
<figcaption>Every scheme measured, public key against signature. Nothing post-quantum lands in the classical corner.</figcaption>
</figure>

The picture shows the problem in one glance: **no post-quantum scheme comes near the bottom-left corner** where Ed25519 and ECDSA live. Every family pays somewhere. The question is whether it can pay where it does not hurt.

## Not all bytes are paid the same way

Look again at Part 02's handshake and ask, for each party, two questions: does its public key travel over the wire, and when does it sign?

<figure class="plate">
<img src="/images/root/06-roles.svg" alt="The leaf: public key sent, signs every handshake online, needs a small key, small signature and fast signing. The intermediate CA: public key sent, signs each leaf offline, needs a small key and small signature. The root CA: public key in the client, signs intermediates rarely, needs only a small signature. The two CT logs: public keys in the client, sign each certificate offline, need a small signature and signing that keeps up." width="1000" height="560" loading="lazy" />
<figcaption>Four roles, four different bills. A key that stays in the client is free.</figcaption>
</figure>

- **The leaf** sends its public key in the certificate and signs CertificateVerify for **every handshake**, online. It pays for its key, its signature, and its signing speed.
- **The intermediate CA** sends its public key in its certificate and signs each leaf at issuance. It pays for key and signature.
- **The root CA** never sends its key: it is already in the client's trust store. It signs intermediates, rarely. It pays **only for its signature**.
- **The CT logs** never send their keys either: browsers ship the list of trusted logs and their keys. Each issued certificate carries two of their signatures. They pay **only for signatures**, but they sign every certificate the CA issues, so they must keep up.

So the bill, in bytes of authentication, is:

$$
\text{bill} = S + pk_{\text{leaf}} + \sigma_{\text{leaf}} + \sigma_{\text{CA}} + 2\,\sigma_{\text{log}} + \big[\, pk_{\text{CA}} + \sigma_{\text{root}} \,\big]
$$

where $\sigma_X$ is the size of a signature made by $X$, $S = 1{,}078$ bytes is everything else (names, extensions, SCT metadata, TLS framing, measured in Part 02), and the bracket disappears when the client already has the intermediate.

**Does the model hold?** It must reproduce Part 02's live measurements, and it does, exactly: ML-DSA-44 everywhere gives 15,802 bytes and a server flight of 17,169; ML-DSA-65 gives 21,527 and 22,916. Those were measured through OpenSSL, byte by byte, a part ago. The model is not an estimate; it is the measurement, made reusable.

The formula already says the most important thing in this part. **For the root and the logs, the public key is free.** UOV's 412 KB key costs those roles nothing per handshake; only its 96-byte signature travels. Three of the five signatures in the bill come from those roles.

## One scheme everywhere

First the naive question: pick one scheme and use it in every role.

<figure class="plate">
<img src="/images/root/06-uniform.svg" alt="Server first flight with one scheme in every role: ECDSA 2,930 bytes, SNOVA 5,717, Falcon-512 7,515, MAYO-1 7,555, Falcon-1024 12,384, MAYO-2 13,199, MQOM 17,145, ML-DSA-44 17,169, ML-DSA-65 22,916, ML-DSA-87 30,786, SLH-DSA-128s 41,833. Lines mark the QUIC budget at about 7,200 bytes and the TCP window at 14,600." width="1000" height="640" loading="lazy" />
<figcaption>One scheme everywhere. Only SNOVA joins today's ECDSA under both limits.</figcaption>
</figure>

| scheme everywhere | authentication | server flight | TCP 14,600 | QUIC ~7,200 |
|---|---:|---:|:---:|:---:|
| ECDSA P-256 (today) | 1,563 | 2,930 | fits | fits |
| SNOVA-24-5-4 | 4,350 | 5,717 | fits | fits |
| Falcon-512 | 6,148 | 7,515 | fits | no |
| MAYO-1 | 6,188 | 7,555 | fits | no |
| Falcon-1024 | 11,017 | 12,384 | fits | no |
| MAYO-2 | 11,832 | 13,199 | fits | no |
| MQOM-L1-short | 15,778 | 17,145 | no | no |
| ML-DSA-44 | 15,802 | 17,169 | no | no |
| ML-DSA-65 | 21,527 | 22,916 | no | no |
| ML-DSA-87 | 29,397 | 30,786 | no | no |
| SLH-DSA-SHA2-128s | 40,422 | 41,833 | no | no |
| UOV-Ip-pkc | 88,870 | 90,347 | no | no |

**No finalized standard fits even the TCP window.** ML-DSA misses it; SLH-DSA misses it by a factor of three. Falcon fits TCP but not QUIC. UOV, so attractive a moment ago, is the worst of all here, because in the leaf and CA roles its 43 KB keys do travel. The only scheme that fits both limits is SNOVA, a round-3 candidate.

## How often each role signs

Bytes are not the only constraint. A scheme can be small and still be useless in a role because it is too slow.

<figure class="plate">
<img src="/images/root/06-speed.svg" alt="Median time for one signature, on a logarithmic scale: UOV, ECDSA and Ed25519 about 0.03 ms; ML-DSA-44 0.07 ms; MAYO-2 0.1 ms; Falcon-512 0.2 ms; RSA-2048 0.3 ms; SNOVA 0.4 ms; MQOM 2 ms; SLH-DSA-128f 25 ms; SLH-DSA-128s 526 ms." width="1000" height="600" loading="lazy" />
<figcaption>Signing time spans more than four orders of magnitude.</figcaption>
</figure>

A busy TLS server signs once per handshake: thousands of times per second. At half a second per signature, SLH-DSA-128s is out of the question for the leaf. The CA and the logs sign once per certificate, and large CAs issue millions a day. The script encodes this as two explicit, adjustable constraints: the leaf must sign in under 5 ms, and the CA and logs in under 50 ms. Only the root, which signs a handful of intermediates in its lifetime, may be as slow as it likes.

As it happens, the constraints change almost nothing about bytes: SLH-DSA's signatures are so large that it never wins on size in any role anyway. Its place in the Web PKI, if any, is as the most conservative choice for long-lived roots, not as the cheapest.

## Mixing schemes by role

Now the real question: assign a scheme to each role separately, and find the cheapest bill. The script tries **every** assignment of the measured schemes to the four roles, and keeps the smallest that meets the constraints. With five pools of allowed schemes:

| allowed | authentication | flight | the winning assignment |
|---|---:|---:|---|
| final FIPS only (ML-DSA, SLH-DSA) | 15,802 | 17,169 | ML-DSA-44 everywhere |
| + draft FIPS 206 (Falcon) | 6,148 | 7,515 | Falcon-512 everywhere |
| + draft, but no Falcon for the online leaf | 8,327 | 9,694 | leaf ML-DSA-44, CA/root/logs Falcon-512 |
| + round-3 candidates | 3,894 | 5,261 | leaf + CA SNOVA, root + logs UOV-Is |
| + round-3, stored keys at most 64 KB | 3,990 | 5,357 | leaf + CA SNOVA, root + logs UOV-Ip-pkc |

Read the rows as a story.

**With final standards only, there is nothing to mix.** SLH-DSA is larger than ML-DSA in every role, so the best you can do today is ML-DSA everywhere.

**Falcon cuts the bill by more than half.** But it puts Falcon's tricky floating-point signing on every web server, online, thousands of times a second, where side-channel attacks are most practical. The third row keeps ML-DSA for the leaf and uses Falcon only in the offline roles, where signing happens rarely, in controlled environments and hardware security modules: 8,327 bytes. That fits the TCP window, but not QUIC's budget.

**The candidates change the picture.** SNOVA for the roles whose key travels, UOV for the roles whose key stays home: under 4 KB, and the only rows that fit both limits. The last row caps the keys that every client must store at 64 KB, because "free per handshake" is not free everywhere: every browser must ship and update those keys. With the 43 KB UOV variant, which has a 128-byte signature, the bill barely moves.

Cloudflare's 2024 survey of the candidates reached the same conclusion from the same argument. It notes that using UOV for the SCTs and the root CA, whose public keys are not sent, together with ML-DSA for the others, adds 7.2 KB, and that combinations of MAYO or SNOVA by role add 3.5 KB and 2.8 KB. Those are bytes *added* to today's chains. Recomputed with this part's model, the same three combinations add 7.3 KB, 3.8 KB and 2.3 KB over our ECDSA chain (8,830, 5,384 and 3,894 bytes in total): the same picture, with differences that come from baselines and parameter versions.

<figure class="plate">
<img src="/images/root/06-mixing.svg" alt="Three bills split by component. ML-DSA-44 everywhere: 15,802 bytes, with 4,840 in the two SCTs. ML-DSA-44 leaf with Falcon-512 elsewhere: 8,327 bytes. SNOVA leaf and CA with UOV root and logs: 3,990 bytes, in which the 1,078 bytes of structure are now about a quarter." width="1000" height="600" loading="lazy" />
<figcaption>The SCTs and the root signature shrink the most once their signers use small-signature schemes.</figcaption>
</figure>

Before celebrating the last row, read the fine print that applies to it:

- **SNOVA, MAYO and UOV are candidates.** Their round-3 parameters may change, and the security of the newer, more structured designs has had far less scrutiny than ML-DSA's. NIST's own report says that a primary challenge for HAWK and SQIsign will be a more complete understanding of their relatively novel security assumptions; similar caution applies across a young field.
- **Mixing schemes multiplies the work.** Every browser, server, CA and log must implement, test and secure every scheme in the mix. Each one is attack surface.
- **The timeline does not wait.** Standardization of the round-3 schemes will take years; the migration plans for the Web PKI are being made now.

## When the client already has the intermediate

Part 02 showed that dropping the intermediate (as abridged certificate compression would) saves a key and a signature. Re-running the search with the bracket removed from the formula:

| allowed | authentication | flight | the winning assignment |
|---|---:|---:|---|
| final FIPS only | 12,070 | 13,437 | ML-DSA-44 everywhere |
| + draft FIPS 206 | 4,595 | 5,962 | Falcon-512 everywhere |
| + round-3, stored keys at most 64 KB | 2,726 | 4,093 | leaf SNOVA, CA UOV-Ip-pkc, logs UOV-Ip-pkc |

Two changes are worth noticing. ML-DSA-44 everywhere now fits the TCP window. And with the candidates, the CA can switch to UOV too: when the client already stores the intermediate, its key no longer travels, and the intermediate joins the "key is free" roles.

## Hybrids

Many deployments will not trust a post-quantum scheme alone at first. A **composite** certificate pairs each post-quantum key and signature with a classical one (the IETF has drafts for this), so the chain stays secure as long as **either** algorithm holds. The cost is roughly additive: ML-DSA-44 plus ECDSA P-256 in every role comes to 16,287 bytes, 485 more than pure ML-DSA-44. Next to the post-quantum bill, the classical half is noise. Hybrids are a question of complexity and policy, not bytes.

## What is not on the menu

Two ideas fall outside this comparison and deserve a mention.

**Authentication by KEM.** The leaf's job in the handshake is to prove it holds a private key. A signature is one way; decrypting a challenge is another. KEMTLS (Schwabe, Stebila and Wiggers, 2020) and its successors replace CertificateVerify with a key encapsulation: the leaf certificate carries an ML-KEM public key (1,184 bytes for ML-KEM-768) and the client sends a ciphertext (1,088 bytes) that only the real server can decapsulate. That is 2,272 bytes against ML-DSA-44's 3,732 for key plus signature, but it changes the handshake's message flow, which is a far larger change to deploy than a new signature algorithm.

**The unmeasured candidates.** HAWK and SQIsign, SQIsign especially, would sit closer to the classical corner of the menu than anything measured here. If either survives the third round, the whole table shifts. Until it does, a migration cannot be planned around it.

## The limit

Step back from the tables. Every row, even the best, still sends **five signatures and two public keys**, plus the 1,078 bytes of structure that in the best bill are now a quarter of the total. Better signature schemes shrink each item. None of them removes an item.

And the items are not equally necessary. Part 02 already split them: the CertificateVerify signature and the leaf key are the server proving, right now, that it holds the key. The other three signatures prove facts settled once, at issuance: a CA vouched for the certificate, and two logs promised to publish it. Parts 04 and 05 built exactly the machinery that can prove such facts without per-certificate signatures: a log whose state is signed rarely and witnessed, and inclusion proofs of a few hundred bytes.

That is [Part 07](/root/07-merkle-tree-certificates/). Instead of choosing smaller signatures, Merkle Tree Certificates remove three of them, and with them most of the structure.

## Try it

From the `experiments\root-of-trust` folder:

```text
python 06_quantum_bill.py
python 06_quantum_bill.py --table
python -m unittest test_06_quantum_bill
```

The first measures what your machine can run; `--table` uses the fixed table, so its output is identical everywhere. To measure the candidates yourself, install liboqs-python (`pip install liboqs-python`). On first import it downloads and builds the liboqs C library, which needs Git, CMake and a C compiler; on Windows that means Visual Studio's build tools. Without it, the script measures what `cryptography` offers and takes the other sizes from the table.

Exercises:

1. Add Falcon-padded-512 (666-byte signatures) and SLH-DSA-SHA2-256s to the catalog. Does either ever win a role?
2. Change the constraints: allow SLH-DSA-128s for the logs (`issuance_ms=600`). Does the answer change? Why not?
3. Impose category 3 everywhere (`min_level=3`). What is the cheapest bill now, and does anything fit the TCP window?
4. Price a chain with **two** intermediates (some CAs still use them). Which roles does the extra certificate add, and what does that cost with ML-DSA-44?
5. Extend the model with a KEM-authenticated leaf (ML-KEM-768 key, 1,088-byte ciphertext instead of CertificateVerify). How far does it get the FIPS-only bill?

## Reader checkpoint

<details>
<summary><strong>1.</strong> Why does a UOV public key of 412 KB cost the root CA role nothing per handshake?</summary>

Because root keys are not sent: they are already in the client's trust store. Only the root's signature, on the intermediate certificate, travels, and UOV's signature is 96 bytes.

</details>

<details>
<summary><strong>2.</strong> Which roles pay for their public key, and which only for their signatures?</summary>

The leaf and the intermediate send their keys, so they pay for both. The root and the CT logs keep their keys in the client and pay only for signatures (one root signature, two SCTs). If the client already holds the intermediate, the intermediate joins the second group.

</details>

<details>
<summary><strong>3.</strong> With only finalized FIPS signatures, why is "ML-DSA everywhere" the best possible chain?</summary>

The only finalized alternative is SLH-DSA, whose signatures (7.8 KB or more) are larger than ML-DSA's in every role, and whose fast variants are even larger. Its small public key does not help in the roles where keys are free anyway.

</details>

<details>
<summary><strong>4.</strong> Why might a deployment use Falcon for the CA and logs but not for the leaf?</summary>

Falcon's signing uses floating-point Gaussian sampling, which is hard to implement in constant time. Offline signers (CAs, logs) sign in controlled environments; a web server signs online for every handshake, where side channels are most exploitable.

</details>

<details>
<summary><strong>5.</strong> The best mix of candidates costs under 4 KB. Name three reasons it is not the answer today.</summary>

They are round-3 candidates whose parameters may change and whose security has had less scrutiny; every scheme in the mix must be implemented and secured everywhere; and standardization will take years, while migration plans are being made now.

</details>

<details>
<summary><strong>6.</strong> What does no choice of signature scheme change about the bill?</summary>

The number of items: five signatures and two public keys, plus the structure. Better schemes shrink each item; only a different design, such as Merkle Tree Certificates, removes items.

</details>

## References

- NIST, FIPS 204, *Module-Lattice-Based Digital Signature Standard* (ML-DSA), and FIPS 205, *Stateless Hash-Based Digital Signature Standard* (SLH-DSA), August 2024.
- R. Perlner, [*FIPS 206 Status Update*](https://csrc.nist.gov/csrc/media/presentations/2025/fips-206-fn-dsa-%28falcon%29/images-media/fips_206-perlner_2.1.pdf), 6th NIST PQC Standardization Conference, 2025; and [draft-ietf-lamps-fn-dsa-certificates](https://datatracker.ietf.org/doc/draft-ietf-lamps-fn-dsa-certificates/).
- NIST, [*Additional Digital Signature Schemes*](https://csrc.nist.gov/Projects/post-quantum-cryptography/post-quantum-cryptography-standardization/additional-digital-signature-schemes), the round-3 announcement of 14 May 2026, and NIST IR 8610.
- B. Westerbaan, [*A look at the latest post-quantum signature standardization candidates*](https://blog.cloudflare.com/another-look-at-pq-signatures/), Cloudflare, 2024: the role-by-role argument and its totals.
- [Open Quantum Safe, liboqs](https://openquantumsafe.org/) 0.16.0, and liboqs-python: the implementations measured here.
- P. Schwabe, D. Stebila and T. Wiggers, *Post-Quantum TLS Without Handshake Signatures* (KEMTLS), ACM CCS 2020.
- [draft-ietf-lamps-pq-composite-sigs](https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/): composite ML-DSA signatures for X.509.
- A. Kipnis, J. Patarin and L. Goubin, *Unbalanced Oil and Vinegar Signature Schemes*, EUROCRYPT 1999.
