---
title: 'Who do you trust?'
description: 'Before Merkle trees, before post-quantum signatures, there is one question every secure connection must answer: is this really the server I meant to reach? Signatures, certificates, chains, and the root of trust that nothing proves.'
part: 0
pubDate: 2026-11-18
tags:
  - pki
  - signatures
  - certificates
  - trust-store
  - post-quantum
companion: experiments/root-of-trust
---

Every time you open a website, your computer accepts a claim from a machine it has never met: *"I am `example.com`, and this is my key."* It accepts it in a few milliseconds, without asking you, and it is almost always right.

This series is about how that works, why the way it works today will not survive post-quantum cryptography, and what the people redesigning it are building instead. It starts at the bottom. This first part needs no mathematics beyond "a function that is easy one way and hard the other way", and no knowledge of certificates at all. By the end you should be able to explain, in your own words, three things:

1. what a digital signature proves, and what it does **not** prove;
2. why a certificate is nothing more than a signed sentence;
3. why every chain of trust ends in a list that someone simply decided to trust.

The third point gives the series its name.

## The stranger problem

Picture your laptop, a server called `example.com`, and everything in between: your Wi-Fi router, your provider, a dozen networks you have never heard of. You control none of them.

<figure class="plate">
<img src="/images/root/00-stranger.svg" alt="Your laptop, the server example.com, and Mallory sitting on the network path between them, able to read, drop and answer messages." width="1000" height="430" loading="lazy" />
<figcaption>The starting point of all of this. Anyone on the path can answer in the server's place.</figcaption>
</figure>

Cryptographers call the person on the path **Mallory** (the malicious one). Mallory can read every packet, drop it, change it, or send her own. So when a message arrives that says *"I am example.com"*, the message itself proves nothing. Mallory can type that sentence as easily as the real server.

You need two things from a connection:

- **Confidentiality**: nobody on the path can read what you send.
- **Authentication**: the other end really is `example.com`.

The first one sounds like the hard part, but it is the easy one. A key exchange such as Diffie–Hellman lets two parties agree on a shared secret over a public channel, and an eavesdropper who only *listens* cannot compute it. (The [Diffie–Hellman article](/blog/05-diffie-hellman-build-break/) builds one from scratch.)

The trouble is that Mallory does not just listen. She can run one key exchange with you and another one with the server, and sit in the middle relaying and reading everything. You end up with a perfectly encrypted, perfectly private conversation **with Mallory**. This is the classic man-in-the-middle attack, worked through in [Diffie–Hellman and the man in the middle](/blog/06-diffie-hellman-mitm/).

<div class="warning">

Encryption without authentication is a private conversation with someone you have not identified. It protects you from people who only listen, and from nobody else.

</div>

So the real question is not *"how do we encrypt?"* It is *"how do we know whose key we are using?"* Everything in this series, from certificates to Merkle trees to post-quantum signatures, is an answer to that one question.

## What a signature proves

The tool for authentication is the **digital signature**. A signature scheme is three algorithms:

- $\mathsf{KeyGen}() \to (sk, pk)$ creates a key pair: a **secret key** $sk$ you keep, and a **public key** $pk$ you can give to anyone.
- $\mathsf{Sign}(sk, m) \to s$ takes a message $m$ and produces a signature $s$.
- $\mathsf{Verify}(pk, m, s) \to \{\text{yes}, \text{no}\}$ checks a signature using only public information.

<figure class="plate">
<img src="/images/root/00-signature.svg" alt="Sign takes a message and a secret key and outputs a signature. Verify takes the message, the signature and the public key and outputs yes or no." width="1000" height="470" loading="lazy" />
<figcaption>Sign needs the secret key; Verify needs only public things.</figcaption>
</figure>

Two properties make this useful.

**Correctness.** An honest signature always verifies:

$$
\mathsf{Verify}\big(pk,\; m,\; \mathsf{Sign}(sk, m)\big) = \text{yes}.
$$

**Unforgeability.** Without $sk$, nobody can produce a pair $(m, s)$ that verifies, even after seeing as many genuine signatures on messages of their choice as they like, unless $m$ is one of the messages that was actually signed. The formal name is *existential unforgeability under chosen-message attack* (EUF-CMA). In practice it means: if a signature verifies under $pk$, then whoever holds the matching $sk$ signed **exactly** that message. Changing a single bit of $m$ makes the signature fail.

Now read the figure's last line again, because the whole series hangs on it:

> A signature proves that *the holder of $sk$* signed $m$. It does not tell you *who* holds $sk$.

If Mallory sends you her own public key and a signature made with her own secret key, the signature verifies perfectly. The mathematics is satisfied. You are still talking to Mallory.

Signatures move the problem; they do not solve it. Instead of *"is this server `example.com`?"* you now ask *"is this public key `example.com`'s key?"* That smaller question is called the **binding problem**: binding a *name* to a *key*.

## Binding a name to a key

There are only a few ways to learn which key belongs to a name.

**Remember it the first time.** This is what SSH does. The first time you connect, it shows you a key fingerprint and asks whether to trust it; after that it remembers. It is called *trust on first use* (TOFU). It works well for a few machines you set up yourself. It fails exactly at the first contact (if Mallory is there that day, you remember *her* key), and it cannot work for a browser that meets thousands of new sites.

**Ask someone you already trust.** If there is a party whose public key you already have, that party can sign a statement for you: *"the key of `example.com` is this one."* You check the signature with the key you already have. If it verifies, you know that party vouched for the binding.

The second idea is the whole of public-key infrastructure (PKI). The signed statement has a name.

## A certificate is a signed sentence

A **certificate** is a short, structured statement, signed by an **issuer**:

<figure class="plate">
<img src="/images/root/00-certificate.svg" alt="An index card labelled certificate, with subject example.com, a public key, a validity period, the issuer Toy Issuing CA and a 'may sign' field, signed by the issuer." width="1000" height="470" loading="lazy" />
<figcaption>Strip away the encoding and a certificate is one sentence with a signature under it.</figcaption>
</figure>

Read aloud, the card says: *"I, Toy Issuing CA, say that the key `3b6a…` belongs to `example.com`, from November 17 to January 3, and that this key may not sign other certificates."* An issuer whose job is to sign such sentences is a **certification authority** (CA).

The certificates your browser handles every day are written in a format called **X.509** (profiled for the internet in RFC 5280) and encoded with a strict binary encoding called **DER**. [Part 01](/root/01-a-certificate-byte-by-byte/) of this series takes one apart byte by byte. For now, the fields on the card map onto the real ones like this:

| On the card | In X.509 (RFC 5280) | What it is for |
|---|---|---|
| subject | `subjectAltName` extension (and the older `subject` field) | the names the key is bound to; browsers match the site name against `subjectAltName` |
| key | `subjectPublicKeyInfo` | the algorithm and the public key itself |
| valid | `validity` (`notBefore`, `notAfter`) | the time window in which the sentence holds |
| issuer | `issuer` | who signed it; used to find the next card in the chain |
| may sign? | `basicConstraints` (`cA`) and `keyUsage` | whether this key may issue certificates itself |
| signature | `signatureAlgorithm`, `signatureValue` | the issuer's signature over all of the above |

<div class="note">

Why a strict encoding at all? Because a signature covers **bytes**, not meaning. If the same certificate could be written in two different byte strings, one signature would cover one spelling and not the other, and parsers that disagree about which bytes mean what have caused real vulnerabilities. DER gives every value exactly one encoding. The toy code below gets the same effect by serialising JSON with sorted keys and no spaces.

</div>

Notice what the signature does and does not do. It makes the sentence **tamper-evident**: change the key, the name or a date, and verification fails. It does **not** make the sentence **true**. If the issuer is careless, compromised or malicious, it can sign a false sentence just as easily, and the signature on the lie will verify perfectly. Keep that in mind; it comes back below and returns in force in Part 03.

## Chains: who vouches for the voucher?

You checked the certificate with the issuer's public key. Where did *that* key come from? From another certificate, signed by another issuer. And that one?

In practice there are three levels:

- the **leaf** certificate, for the site;
- one or more **intermediate** certificates, for the CA's day-to-day signing keys;
- a **root** certificate at the top.

The root's private key is precious, so it is kept offline, often in a hardware security module in a locked room, and used only rarely to sign intermediates. The intermediates do the daily work. If an intermediate key leaks, the root can stop trusting it without replacing itself.

<figure class="plate">
<img src="/images/root/00-chain.svg" alt="Three certificate cards in a row: leaf, intermediate and root. Each is checked with the key in the next card. The root sits inside a box labelled trust store, on your machine, and is signed by itself." width="1100" height="620" loading="lazy" />
<figcaption>Verification walks up the chain; trust flows down from the store.</figcaption>
</figure>

Checking a chain is a loop, from the leaf upwards:

1. The leaf must be for the name you asked for, and the current time must be inside its validity window.
2. Its issuer must match the subject of the next certificate, which must be allowed to issue certificates.
3. The leaf's signature must verify under the next certificate's public key.
4. Repeat for the next link, until a certificate is signed by a key that is **already in your trust store**.

That is a simplified version of *path validation*. The real algorithm (RFC 5280 §6) adds many more checks: key usage, name constraints, policies, path length limits, revocation. But the shape is exactly this loop, and the last step is the one that matters most.

## The root of trust

Look at the root card in the figure. It says *"issuer: Toy Root CA"* and it is *"signed by itself"*. A root certificate is usually **self-signed**: its own key signed it.

What does that self-signature prove? Almost nothing. Anyone can generate a key pair and sign a card that says *"I am a trustworthy root"*. The signature verifies, because the key that made it is right there in the card. It shows the card was not corrupted, and that is all.

So the chain cannot prove the root. Something outside the chain must say *"this root is trusted"*, and that something is the **trust store**: a list of root certificates that ships with your operating system or browser. Mozilla, Apple, Microsoft and Google each run a *root program* that decides which CAs get into their list and on what conditions. Mozilla's list, for example, lives in a file called `certdata.txt` in its source code, and each root carries "trust bits" for what it may be used for, such as websites or email ([Mozilla wiki](https://wiki.mozilla.org/CA/Included_Certificates)). The rules a CA must follow to stay in Mozilla's store are published as the Mozilla Root Store Policy, whose version 3.1 took effect on July 1, 2026 ([Mozilla](https://www.mozilla.org/en-GB/about/governance/policies/security-group/certs/policy/), [Mozilla Security Blog](https://blog.mozilla.org/security/2026/06/29/improving-transparency-and-assurance-in-the-web-pki-mozilla-root-store-policy-v3-1/)).

That is the **root of trust**: the place where verification stops and configuration begins. Nothing cryptographic proves that a root deserves to be there. People decided it, based on audits, policies and track records, and you inherited their decision when you installed your system.

<div class="note">

The newest designs admit this openly. The Merkle Tree Certificates draft says a CA certificate used as a trust anchor *"SHOULD be an unsigned certificate"* (RFC 9925), instead of carrying a pointless self-signature (draft-ietf-plants-merkle-tree-certs-08, §5.5). A root is a configured fact, not a proven one.

</div>

## Try it: six verdicts

Reading about a chain is one thing; breaking one is better. The companion file [`experiments/root-of-trust/00_toy_chain.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust) builds a toy PKI in about a hundred lines of Python with real Ed25519 signatures. Its certificates are JSON instead of X.509, but the verification loop is the one above. The core of it:

```python
def verify_chain(chain, trust_store, name):
    """chain[0] is the leaf; each cert is signed by the next; the last one
    is signed by a key in trust_store."""
    if chain[0].subject != name:
        return False, f"leaf is for {chain[0].subject!r}, not {name!r}"
    for i, cert in enumerate(chain):
        b = cert.body
        if not b["not_before"] <= NOW <= b["not_after"]:
            return False, f"{cert.subject}: expired or not yet valid"
        if i + 1 < len(chain):                      # signed by the next card
            parent = chain[i + 1]
            if parent.subject != b["issuer"]:
                return False, f"{cert.subject}: issuer name does not match"
            if not parent.body["is_ca"]:
                return False, f"{parent.subject} is not allowed to issue certificates"
            signer = parent.key
        else:                                       # the last card: ask the store
            signer = trust_store.get(b["issuer"])
            if signer is None:
                return False, f"{b['issuer']!r} is not in the trust store"
        try:
            signer.verify(cert.signature, canonical(b))
        except InvalidSignature:
            return False, f"{cert.subject}: bad signature"
    return True, "chain verifies up to a trusted root"
```

The script then plays honest world and Mallory in turn. This is its real output (`python 00_toy_chain.py`, checked by `test_00_toy_chain.py`):

```text
ACCEPT  1. honest chain                              chain verifies up to a trusted root
REJECT  2. leaf key swapped for Mallory's            example.com: bad signature
REJECT  3. honest chain, wrong site name             leaf is for 'example.com', not 'bank.example'
REJECT  4. Mallory signs with her own root           'Mallory Root' is not in the trust store
ACCEPT  5. ...after her root is in YOUR store        chain verifies up to a trusted root
ACCEPT  6. a trusted CA issues to Mallory            chain verifies up to a trusted root
```

Go through them one at a time.

1. **Honest chain.** Every link verifies and the last one reaches the store. Accepted, correctly.
2. **Swapped key.** Mallory takes the real leaf and replaces the public key with hers. The issuer's signature no longer matches the bytes. Rejected: this is what tamper-evidence buys you.
3. **Wrong name.** A valid certificate for `example.com` is presented for `bank.example`. Rejected: a certificate binds a key to *specific* names, and the name check is as important as the signature check.
4. **Mallory's own root.** Mallory builds a complete, internally valid chain under a root she created. Every signature is mathematically fine. Rejected, and only because her root is not in your store.
5. **Poisoned store.** Same chain, but Mallory's root has been added to your trust store. **Accepted.** Nothing in the cryptography can notice. This is not hypothetical: corporate inspection proxies install their own root on company laptops on purpose, and malware does it without asking.
6. **A trusted CA misbehaves.** A CA that *is* in your store signs a certificate binding `example.com` to Mallory's key. **Accepted.** The signature is genuine; the sentence is false.

Cases 5 and 6 are the uncomfortable ones, and they are the honest summary of this whole part: a chain of signatures can only ever be as trustworthy as its root of trust, and as honest as every CA under it.

<div class="warning">

Case 6 has happened. In 2011 the Dutch CA DigiNotar was compromised, and attackers issued fraudulent certificates for sites including `*.google.com` that were then used against real users. Every one of those certificates verified. Browsers had to remove DigiNotar from their trust stores, and the company went bankrupt. Part 03 tells this story properly, because it is the reason the next idea exists.

</div>

The answer the web settled on is **Certificate Transparency** (CT): every publicly trusted certificate must be recorded in public, append-only logs, so a misissued certificate cannot stay secret. Your browser asks for proof of logging, in the form of signed receipts from the logs called SCTs, before it accepts a certificate. Chrome has required this for years, and Firefox enforces it on desktop since version 135 ([Mozilla dev-security-policy](https://groups.google.com/a/mozilla.org/g/dev-security-policy)). Logs are built from Merkle trees, which is where Part 04 is going.

## The bill: why post-quantum changes everything

Count what a browser receives to authenticate one site today. Assume, as the Merkle Tree Certificates draft does in its own example, that the browser already knows the intermediate. It still needs:

- the leaf's **public key**;
- the CA's **signature** on the leaf certificate;
- **two SCTs**, each containing a log's signature.

With today's elliptic-curve signatures those are tiny. Ed25519 public keys are 32 bytes and signatures are 64 bytes. With **ML-DSA-44**, the smallest parameter set of the post-quantum signature standard FIPS 204, a public key is 1,312 bytes and a signature is 2,420 bytes.

<figure class="plate">
<img src="/images/root/00-bill.svg" alt="Bar chart: leaf public key plus three signatures is 224 bytes with Ed25519 and 8,572 bytes with ML-DSA-44, about 38 times more." width="1000" height="400" loading="lazy" />
<figcaption>The same structure, two signature schemes. The companion script prints these numbers.</figcaption>
</figure>

$$
\underbrace{32 + 3 \times 64}_{\text{Ed25519}} = 224 \text{ bytes}
\qquad\text{versus}\qquad
\underbrace{1312 + 3 \times 2420}_{\text{ML-DSA-44}} = 8572 \text{ bytes}.
$$

The three signatures alone are $3 \times 2420 = 7260$ bytes, the figure the draft itself gives: *"two SCTs and a leaf certificate signature add 7,260 bytes of authentication overhead with ML-DSA-44"* (draft-ietf-plants-merkle-tree-certs-08, §1). And this does not yet count the server's own handshake signature, which proves it holds the leaf's secret key and which every design needs.

Kilobytes matter here. They arrive before the page can start loading, on every new connection, and the first round trip of a connection can only carry a limited amount of data before the client must wait for an acknowledgement. Part 02 measures exactly where those bytes go in a TLS 1.3 handshake.

<div class="note">

Why change at all? Because a large enough quantum computer would break the signatures used today (RSA and elliptic curves) using Shor's algorithm. Signatures only need to be unforgeable *at the moment you check them*, so the urgency is lower than for encryption, where recorded traffic can be decrypted later ("harvest now, decrypt later"). But a PKI takes many years to change, which is why the redesign is happening now.

</div>

## Where this is going

Here is the idea that the rest of the series builds towards, in one paragraph.

Today every certificate carries its own signatures: the CA's and the logs'. **Merkle Tree Certificates** turn this around. The CA writes certificates into its own append-only log, a Merkle tree, and signs the tree once in a while, not each certificate. A certificate then carries a short **inclusion proof**: a handful of hashes showing that this entry is inside a tree whose root the browser already trusts. Hashes are 32 bytes each and stay that size with post-quantum security, so the proof costs hundreds of bytes instead of kilobytes, and the signature cost is shared by every certificate in the batch.

To get there honestly we need the pieces underneath: how X.509 is really encoded (Part 01), where the bytes go in TLS (Part 02), why logs exist (Part 03), how Merkle trees and their proofs work (Part 04), and how logs sign what they saw (Part 05). The full map is on the [series page](/root/).

## Reader checkpoint

<details>
<summary><strong>1.</strong> Key exchange already gives you a shared secret that eavesdroppers cannot compute. Why is that not enough?</summary>

Because an active attacker can run a separate key exchange with each side and relay between them. You get a secret shared with the attacker. Key exchange gives confidentiality against listeners, not authentication.

</details>

<details>
<summary><strong>2.</strong> A signature verifies under a public key. Exactly what have you learned?</summary>

That whoever holds the matching secret key signed exactly this message. Nothing about who that is.

</details>

<details>
<summary><strong>3.</strong> Why does the self-signature on a root certificate prove almost nothing?</summary>

The key that checks it is inside the same certificate, so anyone can produce one. It only shows the certificate was not corrupted. Trust in a root comes from its presence in the trust store, which is a decision, not a proof.

</details>

<details>
<summary><strong>4.</strong> In the toy output, cases 5 and 6 are accepted. Which one does Certificate Transparency address, and why can't more signatures fix it?</summary>

Case 6, a trusted CA issuing a false certificate. Every signature in that chain is genuine, so adding more signatures changes nothing; what helps is making every issued certificate public, so the false one is seen. (Case 5 is outside the web PKI: whoever controls your trust store controls your trust.)

</details>

<details>
<summary><strong>5.</strong> Where does the number 7,260 come from, and what does it leave out?</summary>

Three ML-DSA-44 signatures of 2,420 bytes: the CA's signature on the leaf and two SCT signatures, with the intermediate assumed already known. It leaves out the leaf public key (1,312 bytes) and the server's own handshake signature.

</details>

## References

- RFC 5280, *Internet X.509 Public Key Infrastructure Certificate and CRL Profile*: certificate fields (§4.1, §4.2) and path validation (§6).
- RFC 9162, *Certificate Transparency Version 2.0*, and its predecessor RFC 6962.
- FIPS 204, *Module-Lattice-Based Digital Signature Standard* (ML-DSA): key and signature sizes (Table 2).
- [RFC 9925](https://www.rfc-editor.org/rfc/rfc9925), *Unsigned X.509 Certificates* (February 2026).
- draft-ietf-plants-merkle-tree-certs-08, *Merkle Tree Certificates*, §1 (size estimate) and §5.5 (representing CAs).
- Mozilla, [Included CA certificates](https://wiki.mozilla.org/CA/Included_Certificates) and the [Mozilla Root Store Policy](https://www.mozilla.org/en-GB/about/governance/policies/security-group/certs/policy/).
- On this site: [Diffie–Hellman from scratch](/blog/05-diffie-hellman-build-break/) and [Diffie–Hellman and the man in the middle](/blog/06-diffie-hellman-mitm/).
