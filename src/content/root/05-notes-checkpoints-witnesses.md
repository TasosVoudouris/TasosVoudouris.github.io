---
title: 'Notes, checkpoints, witnesses'
description: 'How the transparency ecosystem catches a log that shows different people different histories. Signed notes, checkpoints and witness cosignatures, implemented from the C2SP specifications and checked against their test vector; a witness that refuses forks with the exact status codes of the protocol; the quorum arithmetic that decides when a split view can still win; and timestamps against frozen views.'
part: 5
pubDate: 2026-11-20
tags:
  - transparency-logs
  - witnesses
  - checkpoints
  - signed-notes
  - certificate-transparency
companion: experiments/root-of-trust
---

Part 04 gave the log a Merkle tree and left one attack standing. A dishonest log can keep **two trees**: it serves one to the monitors and the other to its victim. Each audience receives perfectly valid signed tree heads, inclusion proofs and consistency proofs. Nobody, checking alone, can tell.

The cure is easy to state: make everybody see the same tree heads. This part is about how that is done in practice, with three small, sharp pieces of format and protocol that today secure Go's module checksums, Sigsum, Sigstore, firmware transparency logs and modern CT logs, and on which Merkle Tree Certificates are built: **signed notes**, **checkpoints** and **witness cosignatures**. We implement each one from its specification, check the implementation against the specification's own test vector, and then throw the split view at it.

By the end you should be able to:

1. write and verify a signed note by hand, and explain each rule for handling its signature lines;
2. read a checkpoint and say what every line commits to;
3. describe exactly what a witness stores, what it checks before cosigning, and what its cosignature means;
4. derive how many cosignatures a client must require to rule out a fork, given how many witnesses might be compromised;
5. explain what timestamps add, and what witnesses still do not check.

The code is [`experiments/root-of-trust/05_witness.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust), with tests in `test_05_witness.py`. It reuses Part 04's Merkle tree.

## The problem, precisely

A log's power is a signing key. With it, the log can sign *any* tree head, including two heads that cannot both be true: two different roots for the same size, or two heads with no consistency proof between them. Signing two incompatible statements is called **equivocation**, and a split view is just equivocation aimed at different audiences.

Every check from Part 04 happens *between one client and the log*. A client that sees only one branch has nothing to compare it with. Equivocation can only be detected by someone who sees **both** statements. So detection needs parties who compare notes.

The original CT design expected the comparing to happen by **gossip**: browsers, servers and auditors exchanging the tree heads they had seen. It proved hard to deploy. Among other problems, a browser that gossips the tree heads it received is telling someone which sites it visited. Gossip never became a working part of the Web PKI.

What replaced it is simpler. Instead of every client comparing with every other, a small set of independent servers, the **witnesses**, each keep the latest tree head they have seen for every log they watch, and refuse to sign anything inconsistent with it. A log that wants a client to accept a tree head must first get it signed by enough witnesses. Each witness can be held to one history. The client only has to count signatures.

## Signed notes

The container for everything in this part is the **signed note**, a format created for Go's checksum database and now specified at C2SP (the Community Cryptography Specification Project). It is deliberately plain text.

A signed note is a text that ends in a newline, then a blank line, then one or more signature lines. Each signature line is an **em dash** (the character U+2014, not a hyphen), a space, the **key name**, a space, and the base64 encoding of a 4-byte **key ID** followed by the signature. In the spec's words, a line has the form `— <key name> base64(32-bit key ID || signature)`. The signed bytes are the text, *including* its final newline, *excluding* the blank line.

The key ID is 4 bytes of a hash: `SHA-256(key name || 0x0A || signature type || public key)[:4]`, where the type byte is `0x01` for a plain Ed25519 note signature. It is not a security mechanism (four bytes are easy to collide on purpose); it lets a verifier quickly find the right key among the signature lines. Public keys are distributed as **verifier keys** of the form `<key name>+hex(32-bit key ID)+base64(signature type || public key)`.

```python
def key_id(name, sig_type, pub):
    return hashlib.sha256(name.encode() + b"\n" + bytes([sig_type]) + pub).digest()[:4]

def sign_note(text, name, sk):
    assert text.endswith("\n")
    sig = key_id(name, 0x01, raw(sk.public_key())) + sk.sign(text.encode())
    return f"{text}\n— {name} {b64(sig)}\n"
```

The rules for *verifying* matter more than the format, because they decide what an attacker can and cannot slip in. The tuple of key name and key ID identifies a key. Verifiers MUST ignore signatures from unknown keys, even if they share a name or an ID (but not both) with a known key. If the name and ID match a known key, the signature MUST be verified, and a client may reject the whole note when one fails. If no signature from a known key verifies, the note MUST be rejected.

```python
def open_note(note, verifiers):
    text, sigs = split_note(note)      # the text ends at the LAST blank line
    known = {(v.name, v.kid): v for v in verifiers}
    good = []
    for name, kid, sig in sigs:
        v = known.get((name, kid))
        if v is None:
            continue                   # unknown key: ignore, whatever it claims to be
        if not v.check(text, sig):
            raise ValueError(f"signature from known key {name} does not verify")
        good.append(v)
    if not good:
        raise ValueError("no signature from a known key")
    return text, good
```

One more rule hides in `split_note`. The note text may itself contain blank lines, so the text ends at the **last** blank line, not the first. Otherwise an attacker could append a fake "blank line plus signature" into a message and change where the text seems to end.

**Is it right?** The signed-note specification contains a worked example: the verifier key `example.com/foo+530d903a+AekyeRrm56hApGFkyQR4ZCbV54Id2LKaANYcrnKv3U2k`, the text `This is an example message.`, and its signature line. The script parses the key, recomputes the key ID `530d903a` from it, and verifies the note. Change one word of the text and verification fails. Our notes interoperate with everybody else's.

The design choice that matters most comes almost for free: **adding a signature never changes the text.** Anybody can append a signature line to a note without invalidating the others. That is exactly what cosigning will be.

## Checkpoints

A **checkpoint** is a signed note whose text is a tree head. Three lines:

```text
example.com/log
1000
AcWjVY4EmQlPJ4tm380spGWTDrMo9VvlyZM19fb5LRs=
```

**The origin line** names the log. It exists so that a checkpoint from one log can never be passed off as a checkpoint of another: the name is inside the signed text. (It need not be a reachable URL, only unique.) **The tree size**, in decimal. **The root hash**, in base64: Part 04's $\mathrm{MTH}$ of the first 1,000 entries. Extra *extension* lines may follow, for application data; witnesses make no promise about them.

This is Part 04's signed tree head with the size and root together, as that part said they must be, now in a format that anyone can extend with more signatures.

<figure class="plate">
<img src="/images/root/05-anatomy.svg" alt="A cosigned checkpoint: three text lines (origin example.com/log, size 1000, root hash in base64), a blank line, the log's signature line, and three witness cosignature lines. Inside one cosignature value: a 4-byte key ID, an 8-byte timestamp, and a 64-byte Ed25519 signature over cosignature/v1, time T and the checkpoint." width="1000" height="640" loading="lazy" />
<figcaption>One checkpoint, four signatures. The text never changes; signature lines are only appended.</figcaption>
</figure>

## Witnesses

A witness is a small server with a single job, specified in the C2SP tlog-witness document. It watches a fixed list of logs, and for each one it stores **one thing**: the latest checkpoint it has cosigned. A size and a root.

When a log produces a new checkpoint, it asks each witness for a cosignature with an `add-checkpoint` request: an `old <size>` line (the size the log believes the witness last cosigned), a consistency proof from that size to the new one, one hash per line, a blank line, and the new checkpoint with the log's signature:

```text
old 1000
EXDEexyzxlXa0OwlHDp7uQXq8UY2vQHx7lbXyUaRBtQ=
2aaYwPodxbTV1UesWUuxrFqcmRvzJ5+urXGV6SirT/I=
VaCpXGbi/s04HIYIr4FO5EoL6Cs8RoMVY0Fg+gAgI6E=
FZn+RY9cDfWgfUyBLAcL1eQTc5k8l6w8xIcmIDtXnq8=
ywEtKopgkhIVDFEYiDpXTjvlLFUtGpGknLPLnW9/2/8=
wncILJ3XRbiFv8NLFSU4ggA2bTOCWEf0i92i82b3sDk=
wt9wAfWRlIgxhQe503azfYwMRlsWhAAF/2/yMZ04Jd8=
ZrS8vHDEh4j0oxmlvcYZ+LFEa/9T+MNkgg74vSklIpc=
ONvgchJhc235pBcYYWfl3e8S9a/AOgqNyup6GzDBnfc=

example.com/log
1500
e6GwpdZpwbEILd/eE7Zy3jYOcaW/LFjeE2/+LG4aaS4=

— example.com/log sKX2TKqiz5pw24+Dt9Eq3QFl7YFWqf4OIKaY1d3LUq7xmD26Hem6xSiZu27t1uS5JlmapBvljPf6jIK1a51pA0xrGwM=
```

That is a real request from the script: nine proof hashes take the witness from 1,000 entries to 1,500 (Part 04's bound of $\lceil \log_2 1500 \rceil + 1 = 12$ is the worst case; this one is shorter). Notice that the log's signature line starts with the same five characters, `sKX2T`, as on the size-1,000 checkpoint above. Five base64 characters are 30 bits, all inside the 4-byte key ID, which depends only on the key's name and value.

The witness then runs a fixed sequence of checks, in the order the specification lists them, each with its own HTTP status:

| check | if it fails |
|---|---|
| is the origin a log I watch? | **404** Not Found |
| is the checkpoint signed by that log's key? | **403** Forbidden |
| is the old size at most the new size? | **400** Bad Request |
| is the old size exactly the size I last cosigned? | **409** Conflict, with my size in the body |
| does a size-0 checkpoint have the empty-tree root? | **422** |
| from size 0, is the proof empty? Otherwise, does the consistency proof verify from **my** stored root to the new root? | **422** |
| if old = new, are the roots equal? | **422** |
| all good | store the new checkpoint, **then** answer **200** with cosignature lines |

Two details deserve attention.

**409 is a conversation, not an error.** If the log guessed the witness's size wrong (perhaps another of its requests got lost), the witness answers with the size it actually has, and the log retries with a proof from that size. The witness never accepts a proof from a size *it* did not cosign, because then the old root in the proof would be the log's claim, not the witness's memory.

**Store, then sign.** The witness must persist the new checkpoint before it answers, and the size check and the update must be atomic. Otherwise two concurrent requests could both pass the "old size" check against the same stored state and the witness could end up cosigning two branches.

The script's witness implements exactly this table. Here is what it says to one bad request of each kind:

```text
unknown log                      -> 404 unknown log
signed by the wrong key          -> 403 not signed by the log
old size > new size              -> 400 old size is larger than the checkpoint
old size the witness never saw   -> 409 1000
same size, different root        -> 422 same size, different root: a fork
bad consistency proof            -> 422 consistency proof does not verify
```

### The cosignature

When every check passes, the witness signs. A cosignature is an ordinary note signature line, added to the checkpoint, with two twists that the tlog-cosignature specification fixes.

First, what is signed is **not** just the checkpoint text. It is two header lines followed by the whole checkpoint body: the fixed line `cosignature/v1`, then `time` and a space and the current time in seconds since 1970, then the checkpoint. The spec's own example of a signed message:

```text
cosignature/v1
time 1679315147
example.com/behind-the-sofa
20852163
CsUYapGGPo4dkMgIAUqom/Xajj7h2fB2MPA3j2jxq2I=
```

The header gives **domain separation**: a witness's key can never be tricked into producing something that also verifies as a plain note signature, or as some other future statement. The key ID uses a different type byte too, `0x04` instead of `0x01`, so the same public key has a different ID in each role.

Second, the signature value is **72 bytes**: an 8-byte big-endian timestamp (the same time as in the header) followed by the 64-byte Ed25519 signature. With the 4-byte key ID in front, a cosignature line carries 76 bytes. The script decodes the spec's example cosignature line, from the witness `witness.example.com/w1`: key ID `8d66cf3f`, timestamp `1679315147` (matching the `time` line of the example message above), signature 64 bytes.

```python
def cosigned_message(checkpoint_text, timestamp):
    return f"cosignature/v1\ntime {timestamp}\n".encode() + checkpoint_text.encode()

def cosign(checkpoint_text, name, sk, timestamp):
    kid = key_id(name, 0x04, raw(sk.public_key()))
    sig = sk.sign(cosigned_message(checkpoint_text, timestamp))
    return f"— {name} {b64(kid + struct.pack('>Q', timestamp) + sig)}\n"
```

**What a cosignature means** is stated in the specification and worth reading slowly: a v1 cosignature says that, as of the given time, the consistent tree head with the largest size this cosigner has observed for the log with that origin has the given root hash. Not "this log is honest". Not "these entries are good". Only: *at this time, this is the furthest point of the one consistent history I have seen.*

<figure class="plate">
<img src="/images/root/05-witness-flow.svg" alt="The log sends the witness old 1000, a proof and checkpoint 1500. The witness, which stores the size and root of the last checkpoint it cosigned, checks the log signature (else 403), the old size (else 409) and the proof from its root to the new root (else 422), then saves the new size and root and signs. The cosignature goes back to the log, which publishes the checkpoint with cosignatures; a client verifies the log key and k of n witness keys." width="1000" height="600" loading="lazy" />
<figcaption>A witness keeps one number and one hash per log, and never signs two histories.</figcaption>
</figure>

## Catching the split view

Now replay Part 04's attack. A log with three witnesses grows its tree: 100, 250, 1,000 entries. Each time, all three witnesses check a consistency proof and cosign. A client requiring 2 of 3 cosignatures accepts. Then the log forks: the main branch continues honestly, and a second branch inserts a rogue certificate right after entry 999.

```text
1. log grows 100 -> 250 -> 1000, 3 witnesses        ACCEPT: 3 of 3 witnesses (need 2)
2. split view: fork at 1500 after main at 1500      every witness refuses: [422, 422, 422] (same size, different root)
3. split view: fork grown to 1800                   every witness refuses: [422, 422, 422] (no consistency proof exists)
```

**2.** The witnesses have cosigned the main branch at size 1,500. The log asks for a cosignature on the fork, also at size 1,500. Same size, different root: refused by all three.

**3.** The log grows the fork to 1,800 and tries again. Now the witness needs a consistency proof from *its* stored head (main at 1,500) to the fork at 1,800. No such proof exists, because the fork rewrote entry 1,000. Refused.

<figure class="plate">
<img src="/images/root/05-fork-refused.svg" alt="A shared history of entries 0 to 999 branches in two. The main branch is cosigned at 1500 by witnesses a, b and c. The fork inserts a rogue certificate right after the branch point. A fork checkpoint at 1500 has the same size but another root: 422. A fork at 1800 has no proof from main: 422." width="1000" height="520" loading="lazy" />
<figcaption>Once a witness has seen one branch, it can only ever sign that branch's future.</figcaption>
</figure>

This is the whole trick. A witness's state only ever moves forward along one consistent history. The moment it cosigns a checkpoint on one branch, it is **locked** into that branch forever. The log cannot "move" it to the other branch, because every request must come with a consistency proof starting from the witness's own memory.

So a log that wants two branches witnessed has only two options. It can **partition** the witnesses: show some of them only the main branch and the others only the fork, from the moment the branches split. Or it can **compromise** some witnesses so that they cosign anything. Both options run into the client's threshold.

```text
4. witnesses partitioned 2 | 1, client needs 2 of 3  main ACCEPT (2 of 3 witnesses (need 2)); fork REJECT (1 of 3 witnesses (need 2))
5. one witness compromised, client needs 2 of 3     main ACCEPT, fork ACCEPT: both pass, the quorum was too small
6. same, client needs 3 of 3                        main REJECT, fork REJECT: safe, but one silent witness now blocks everyone
```

**4.** The log shows main to witnesses a and b, the fork to c. Main gets two cosignatures, the fork one. A client needing 2 of 3 accepts main and rejects the fork. The partition did not help.

**5.** Witness a is compromised and cosigns both branches. Main is cosigned by a and b, the fork by a and c. Both reach 2 of 3. **The fork wins.**

**6.** The same checkpoints, against a client needing 3 of 3: neither branch has all three. The fork is stopped, and so is the main branch, because witness c (busy being fooled) did not cosign it. A threshold of "everybody" is safe, and fragile: any one witness offline blocks every client.

## How many cosignatures?

Scenario 5 suggests a question with a clean answer. There are $n$ witnesses, of which up to $f$ may be compromised and cosign anything. A client requires $k$ cosignatures. When can a log get **two conflicting checkpoints** each cosigned by $k$ witnesses?

Each honest witness cosigns at most one of the two branches. The compromised ones cosign both. Say $a$ honest witnesses go to the first branch and the other $n - f - a$ to the second. The log needs:

$$
f + a \ge k \quad\text{and}\quad f + (n - f - a) \ge k .
$$

Adding the two: $2f + n - f \ge 2k$, that is $2k \le n + f$. Conversely, if $2k \le n + f$ the log can pick $a = k - f$ (or 0, if $f \ge k$) and both inequalities hold. So:

$$
\text{a fork can reach } k \text{ of } n \text{ cosignatures} \iff 2k \le n + f, \qquad \text{safe} \iff k > \frac{n + f}{2}.
$$

The same thing from a different angle: two groups of $k$ witnesses out of $n$ share at least $2k - n$ members. If $2k - n > f$, at least one shared member is honest, and an honest witness never signs two branches.

The script checks this rule by brute force, trying every split of the honest witnesses for every $n$ up to 8, every $f$ and every $k$. For five witnesses:

<figure class="plate">
<img src="/images/root/05-quorum.svg" alt="Grid for n = 5 witnesses, f from 0 to 3 compromised, k from 1 to 5 required. Fork possible (red) when 2k is at most 5 + f: for f = 0, k = 1 and 2; f = 1, k up to 3; f = 2, k up to 3; f = 3, k up to 4. Safe (green) otherwise. Safe if and only if k > (n + f) / 2. But k = n means one witness offline blocks every client." width="1000" height="560" loading="lazy" />
<figcaption>Safety needs a strict majority of n + f. Availability needs slack below n.</figcaption>
</figure>

The two pressures pull opposite ways. **Safety** wants $k$ large. **Availability** wants $k$ well below $n$, so that a few witnesses being offline or slow does not stop every client. A real deployment chooses $n$ larger than strictly needed, so that a $k$ above $(n + f)/2$ still leaves room for some witnesses to be down. And the parameter $f$ is a judgment about the world: how many witness operators might be coerced or breached *at the same time*, which is why witnesses are run by different organizations in different jurisdictions.

## Freshness

There is one attack a witness threshold alone does not stop, because it involves no fork at all. The log simply keeps showing the victim an **old** checkpoint, one that was honestly cosigned a month ago, and never anything newer. Everything logged since is invisible to the victim, including, perhaps, the certificate being used against them.

That is what the timestamp inside every cosignature is for. A client can demand that enough of the cosignatures are **recent**:

```text
7. freeze: a month-old checkpoint, no age limit     ACCEPT
8. freeze: same, cosignatures must be < 1 day old   REJECT: 0 of 3 witnesses (need 2)
```

<figure class="plate">
<img src="/images/root/05-freshness.svg" alt="Timeline: a checkpoint is cosigned at day 0; the log keeps serving it to one victim, hiding new entries; on day 30 the victim checks. With no age limit the client accepts a month-old world. With cosignatures required to be less than a day old, the client rejects it and the freeze becomes visible." width="1000" height="420" loading="lazy" />
<figcaption>A signed time turns "old" into something a client can measure.</figcaption>
</figure>

Witnesses cosign on every new checkpoint, and logs that are idle still produce new checkpoints regularly, so honest clients always have fresh cosignatures available. A frozen view stands out immediately.

## What witnesses do not do

It is worth being exact about the limits, because each one is somebody else's job:

- **Witnesses do not look at entries.** A witness checks hashes and proofs, never certificates. Whether an entry is a misissued certificate is the monitors' question (Part 03).
- **Witnesses do not keep the data.** A cosignature says the history is consistent, not that anyone can still download it. A log that cosigns honestly and then refuses to serve its entries is a separate failure; some cosigners also act as **mirrors** and say so (the specification allows a cosigner to add statements like "I also mirrored the log up to this size").
- **Witnesses do not vouch for extension lines.** Only the origin, size and root are covered by what a cosignature means.

## The bill, again

Each cosignature is a signature, and this series has been counting signatures since Part 00. With Ed25519 a cosignature line costs about 127 bytes, so three witnesses add about 381 bytes to a checkpoint. Ed25519, of course, is not quantum-safe.

The current version of the tlog-cosignature specification therefore defines two cosignature types, one based on Ed25519 and one based on ML-DSA-44, and says the ML-DSA version SHOULD be used for new deployments. At ML-DSA-44 sizes a cosignature line is about 3,267 bytes, and three of them about 9,800. The ML-DSA-44 type also signs a different message, a `subtree/v1` structure instead of the `cosignature/v1` lines, which lets a cosigner sign not only the latest checkpoint but any **subtree** of the log, with the timestamp set to zero for subtree cosignatures.

That last detail is a signpost. Let's Encrypt's Boulder CA already has code that implements ML-DSA-44 cosignatures over log checkpoints, accepts only ML-DSA-44 keys, and signs with a zero timestamp, which the Merkle Tree Certificates draft requires for cosignatures used in certificates. In MTCs, the CA's own log is cosigned by witnesses, the CA itself is one of the cosigners, and certificates refer to cosigned subtrees. The trick that keeps those 3,267-byte signatures *out* of the TLS handshake is the subject of Parts 07 and 08.

## Where this runs today

None of this is a proposal. The first significant witness network, OmniWitness, monitored logs that use this checkpoint format: Go SumDB, Sigsum, Sigstore, Android Binary Transparency, LVFS and the ArmoredWitness's own log. The ArmoredWitness is a small dedicated hardware device that runs witness code, intended to kick-start a cross-ecosystem witness network. Sigsum's log server moved to the same interoperable witness protocol. A checkpoint format first designed for one programming language's package checksums now carries the history of firmware, software releases and, soon, certificates.

## Try it

From the `experiments\root-of-trust` folder:

```text
python 05_witness.py
python -m unittest test_05_witness
```

Exercises:

1. Write a checkpoint by hand for a log of three entries (use Part 04 for the root), sign it with `sign_note`, and verify it with `open_note`. Then add a second blank line inside the text. What changes?
2. Make a note with two signature lines from the same key name but different keys, one known and one not. What does `open_note` do, and which rule of the spec is that?
3. Implement the race the spec warns about: a witness that checks the old size, *then* sleeps, *then* stores. Run two `add-checkpoint` calls for two branches concurrently. What does the witness sign?
4. For $n = 7$ witnesses and $f = 2$, what is the smallest safe $k$? How many witnesses can then be offline before honest checkpoints stop being accepted?
5. Add an ML-DSA-44 cosignature type to the script (Part 02 shows how to make ML-DSA keys). How big is a checkpoint with three of them, and how does that compare with Part 02's whole classical handshake?

## Reader checkpoint

<details>
<summary><strong>1.</strong> Why does a single client, however careful, never detect a split view on its own?</summary>

Because every statement it receives from the log is internally consistent. Equivocation means two incompatible statements; detecting it requires seeing both, so it needs some form of comparison between parties.

</details>

<details>
<summary><strong>2.</strong> A note carries a signature line whose name matches a trusted key but whose key ID does not. What must a verifier do?</summary>

Ignore it. A key is identified by the pair (name, key ID); a line matching only one of them is from an unknown key. The note is then accepted only if some other line from a known key verifies.

</details>

<details>
<summary><strong>3.</strong> Why does a witness answer 409 with its own size, instead of accepting a consistency proof from whatever old size the log sends?</summary>

Because the old root in that proof would then come from the log, not from the witness's memory. The guarantee comes from checking consistency against what the witness itself already cosigned.

</details>

<details>
<summary><strong>4.</strong> What exactly does a cosignature/v1 assert?</summary>

That at the given time, the largest consistent tree head the witness has seen for that origin has that root hash. Nothing about the entries, the extension lines, or the log's availability.

</details>

<details>
<summary><strong>5.</strong> With n = 5 witnesses and f = 1 possibly compromised, why is k = 3 unsafe while k = 4 is safe?</summary>

A fork needs 2k ≤ n + f = 6. With k = 3: 6 ≤ 6, so the compromised witness plus two honest ones on each side gives both branches 3. With k = 4: 8 > 6; any two groups of 4 share 3 witnesses, at least 2 of them honest.

</details>

<details>
<summary><strong>6.</strong> What attack do cosignature timestamps defend against, and why can a fork-free threshold not stop it?</summary>

A freeze: the log keeps showing a victim an old, honestly cosigned checkpoint, hiding newer entries. Nothing is inconsistent, so witnesses have nothing to refuse; only a requirement that cosignatures be recent exposes it.

</details>

## References

- C2SP, [*signed note*](https://github.com/C2SP/C2SP/blob/main/signed-note.md): format, key IDs, verifier keys, verification rules, examples.
- C2SP, *tlog-checkpoint*: the checkpoint body.
- C2SP, [*tlog cosignature*](https://github.com/C2SP/C2SP/blob/tlog-cosignature/v1.0.0/tlog-cosignature.md) (v1.0.0, and the current version with the ML-DSA-44 subtree type).
- C2SP, *tlog-witness*: the add-checkpoint protocol and the witness's checks.
- R. Cox, *Transparent Logs for Skeptical Clients*, research.swtch.com/tlog, 2019: the design behind Go's checksum database and its notes.
- S. Meiklejohn et al., [*Think Global, Act Local: Gossip and Client Audits in Verifiable Data Structures*](https://arxiv.org/abs/2011.04551), 2020.
- E. Syta et al., [*Keeping Authorities "Honest or Bust" with Decentralized Witness Cosigning*](https://arxiv.org/abs/1503.08768), IEEE S&P 2016.
- transparency.dev, [*Can I Get A Witness (Network)?*](https://blog.transparency.dev/can-i-get-a-witness-network), and the [ArmoredWitness](https://github.com/transparency-dev/armored-witness) project.
- [Sigsum documentation](https://www.sigsum.org/docs).
- Let's Encrypt Boulder, [*trees/cosignature: Sign and verify MTC checkpoint cosignatures*](https://github.com/letsencrypt/boulder/pull/8904).
