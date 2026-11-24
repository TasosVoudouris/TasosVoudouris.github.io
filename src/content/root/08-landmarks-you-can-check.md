---
title: 'Landmarks you can check'
description: 'What stands behind a signatureless certificate. Subtree consistency proofs generated and verified from draft-ietf-plants-merkle-tree-certs-07, checked against the draft examples, its Appendix C vectors and every subtree of every tree up to 64 entries; cosigned checkpoints; a week of hourly landmarks; an update service that validates them before any browser trusts them, including the draft example of lagging witnesses; three attacks; and how stale a client can be before it loses the small certificate.'
part: 8
pubDate: 2026-11-22
tags:
  - merkle-tree-certificates
  - transparency-logs
  - landmarks
  - consistency-proofs
  - post-quantum
companion: experiments/root-of-trust
---

Part 07 ended with a certificate of 1,855 bytes that carries no signature at all. The browser accepted it because it already held the hash of the landmark subtree `[0, 1024)`. The code did this in one line:

```python
trusted = {s: mk.mth(ca.entries[s[0] : s[1]]) for s in lm}   # predistributed after checking cosignatures
```

That comment hides the whole security argument. A landmark-relative certificate is exactly as trustworthy as the process that put that hash into the browser. If a CA could slip in the hash of a subtree that is not part of the log its witnesses saw, it could issue certificates nobody would ever see, which is precisely what transparency exists to prevent.

This part builds the process. The draft gives it in three pieces: **subtree consistency proofs** (§4.4), which show that a subtree is a node of a larger tree; **cosigned checkpoints** (§5.3), which show that cosigners saw that larger tree; and the **validation of landmarks** (§7.4), which joins the two before anything reaches a browser. Then we ask the practical question the design raises: a browser that has not updated for a while, how much does it lose?

By the end you should be able to:

1. generate a subtree consistency proof by hand and say which hashes it needs and why;
2. run the verification algorithm bit by bit, with its two running hashes;
3. say what a cosigned checkpoint is in MTC, and how it differs from a cosignature in a certificate;
4. list the three checks an update service makes before trusting a landmark, and what happens when one fails;
5. predict, for a given client, what fraction of its handshakes can use the small certificate.

The code is [`experiments/root-of-trust/08_landmarks.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust), with tests in `test_08_landmarks.py`. It builds on Part 07's toy CA and Part 04's Merkle tree. Section numbers (§) refer to draft -07.

## The question a landmark must answer

A landmark subtree is a triple: a range `[start, end)` of a CA's log, and the 32-byte hash of that range. To trust it, a browser (or a service acting for it) needs to know two things:

- **This hash is part of the log.** The range must be a node of some tree the CA committed to, not a hash the CA computed over entries that exist nowhere else.
- **That log is the one the cosigners saw.** The CA must not be able to show one tree to its witnesses and another to the browsers.

Part 05 answered the second question for whole trees: witnesses cosign checkpoints, and they refuse a checkpoint that is not consistent with what they cosigned before. What is new here is the first question: how to prove that a **subtree**, possibly in the middle of the log, is a node of a checkpoint's tree. That is what a subtree consistency proof does.

## Subtree consistency proofs

<img src="/images/root/08-tree.svg" alt="The tree of 14 entries. The root splits into [0,8) and [8,14); [8,14) into [8,12) and [12,14); [12,14) into entries 12 and 13. The subtree [8,13) is highlighted. Its proof is four hashes, in order: entry 12, entry 13, [8,12), [0,8)." width="1000" height="600" loading="lazy" />

Part 04 had two kinds of proof. An **inclusion proof** shows one leaf is in a tree. A **consistency proof** shows one tree is a prefix of another. A subtree consistency proof generalizes both: it shows that the hash of `[start, end)` is a node of the tree of size n. When `start` is 0 it is exactly a consistency proof (the subtree is a prefix), and when `end = start + 1` it is exactly an inclusion path (the subtree is one leaf). The script checks both reductions against Part 04's own functions:

```text
  [0, 6) equals Part 04's consistency proof: True
  [5, 6) equals Part 04's inclusion path: True
```

**Generating it** (§4.4.1) is the same recursion as Part 04, splitting the tree at k, the largest power of two smaller than n:

```python
def _subtree_subproof(start, end, d, b):
    n = len(d)
    if start == end:
        return []                                   # the empty subtree
    if start == 0 and end == n:
        return [] if b else [mk.mth(d)]             # the subtree IS this tree
    k = _k(n)
    if end <= k:                                    # entirely on the left
        return _subtree_subproof(start, end, d[:k], b) + [mk.mth(d[k:])]
    if k <= start:                                  # entirely on the right
        return _subtree_subproof(start - k, end - k, d[k:], b) + [mk.mth(d[:k])]
    return _subtree_subproof(0, end - k, d[k:], False) + [mk.mth(d[:k])]
```

Read it as a walk from the root down to the subtree. At each level, the subtree lies in one half; the proof records the hash of the **other** half, then descends. The flag `b` answers one question: when we reach a node that is exactly the subtree, does the verifier already know its hash? At the top level, yes: the verifier is checking a claimed subtree hash, so sending it would be redundant. But in the third case the subtree straddles the split. That can only happen when `start = 0` (a valid subtree never straddles a split otherwise), and then the part of the subtree on the right is a piece the verifier does not know, so the flag becomes false and that piece's hash is sent.

Run it by hand on the draft's two examples (§4.4.2), in the tree of 14 entries in the figure:

```text
[4, 8) in n = 14:   k = 8, end <= 8: go left, record [8, 14)
                    n = 8, k = 4, start >= 4: go right, record [0, 4)
                    n = 4: [0, 4) of this subtree is the whole thing, b = true: nothing
                    proof = [0, 4), [8, 14)

[8, 13) in n = 14:  k = 8, start >= 8: go right, record [0, 8)
                    n = 6, k = 4, 0 < 4 < 5: straddles, b = false, record [8, 12)
                    n = 2, k = 1, end <= 1: go left, record entry 13
                    n = 1, whole subtree, b = false: record entry 12
                    proof = entry 12, entry 13, [8, 12), [0, 8)
```

(The records come out innermost first, because each level appends after its recursive call.) The script prints the same:

```text
== subtree consistency proofs: the draft's examples (tree of size 14) ==
  [4, 8): proof = D[0:4], D[8:14]
  [8, 13): proof = D[12:13], D[13:14], D[8:12], D[0:8]
```

Notice what `[8, 13)` costs. The subtree is not a power of two in size, so its hash is not a single node at a single level; it is built from `[8, 12)` and entry 12. The verifier needs those pieces to rebuild the subtree hash, and the pieces outside it (entry 13, `[0, 8)`) to rebuild the root.

## Verifying one

<img src="/images/root/08-walk.svg" alt="Verification of [8,13) in the tree of size 14. Start: fr and sr are both entry 12. Entry 13 is a right sibling: only sr changes, to [12,14). [8,12) is a left sibling inside: fr becomes [8,13) and sr becomes [8,14). [0,8) is a left sibling outside: only sr changes, to the root. Accept when fr is the claimed subtree hash, sr is the root, and tn is zero." width="1000" height="560" loading="lazy" />

The verifier (§4.4.3) knows n, the range, the claimed subtree hash `node` and the tree hash `root`. It keeps **two** running hashes: `fr` rebuilds the subtree, `sr` rebuilds the whole tree. It also keeps three positions, `fn`, `sn` and `tn`, for `start`, `end − 1` and `n − 1`, and moves them up one level at a time by shifting right.

```python
fn, sn, tn = start, end - 1, n - 1
if sn == tn:                          # the subtree is on the right edge of the tree
    while fn != sn: fn, sn, tn = fn >> 1, sn >> 1, tn >> 1
else:                                 # climb while end - 1 is a right child
    while fn != sn and sn & 1: fn, sn, tn = fn >> 1, sn >> 1, tn >> 1
if fn == sn: fr = sr = node           # the subtree is one node: start from its hash
else:        fr = sr = proof.pop(0)   # otherwise its rightmost piece comes first
for c in proof:
    if tn == 0: return False          # proof too long
    if sn & 1 or sn == tn:            # c is a LEFT sibling
        if fn < sn: fr = H(c, fr)     #   still inside the subtree
        sr = H(c, sr)
        while not sn & 1: fn, sn, tn = fn >> 1, sn >> 1, tn >> 1
    else:                             # c is a RIGHT sibling: outside the subtree
        sr = H(sr, c)
    fn, sn, tn = fn >> 1, sn >> 1, tn >> 1
return tn == 0 and fr == node and sr == root
```

The logic follows from one fact about binary positions: at any level, a node at an odd position is a right child, and its sibling is on the left; at an even position, a left child with its sibling on the right (unless it is the last node of the level, where `sn == tn`, and there is no right sibling at all).

- **The opening climb.** If `end − 1` is a right child, then its whole parent ends at the subtree's end, so the subtree contains that parent's right half; climbing while `sn` is odd finds the largest node the subtree ends with. If that climb reaches `fn == sn`, the subtree is one node, and its claimed hash is the starting point. Otherwise the first proof hash is the subtree's rightmost node.
- **A left sibling** may be inside the subtree (if `fn < sn`, the subtree still extends to the left at this level), so it updates both hashes. It always updates the tree hash.
- **A right sibling** is beyond `end`, so it is never part of the subtree. It only updates `sr`.
- **tn** checks the length: when the tree is fully rebuilt, `tn` is zero, and any leftover or missing proof hash fails.

The script traces the walk for `[8, 13)`:

```text
== verifying [8, 13) in the tree of size 14, step by step ==
  first proof hash seeds fr and sr         then fn= 8 (1000) sn=12 (1100) tn=13 (1101)
  D[13:14] is a RIGHT sibling              then fn= 4 (0100) sn= 6 (0110) tn= 6 (0110)
  D[8:12]  is a LEFT  sibling              then fn= 1 (0001) sn= 1 (0001) tn= 1 (0001)
  D[0:8]   is a LEFT  sibling              then fn= 0 (0000) sn= 0 (0000) tn= 0 (0000)
  fr == hash of [8, 13), sr == root, tn == 0: True
```

`sn = 12` is even, so there is no opening climb: the subtree ends with the single leaf 12, which is the first proof hash. Entry 13 sits at an even position below a non-final node, so it is a right sibling, outside: only the tree hash grows. At the next level `sn = 6` equals `tn`: the node `[12, 14)` is the last of its level, so `[8, 12)` is its left sibling; `fn = 4 < 6`, so it is inside, and `fr` becomes `H([8, 12), entry 12)`, which is exactly the hash of `[8, 13)`. The inner climb lifts the positions past the level where `[8, 14)` has no sibling. Finally `[0, 8)` is a left sibling with `fn = sn`, outside the subtree, and `sr` becomes the root.

I want to note one honest detail. My first implementation inverted the opening climb: I read the rule as "climb while `sn` is even". The exhaustive test caught it immediately, because it rejected valid proofs for ranges like `[8, 13)`. A test suite that only checks a few hand examples might not have.

## Checked three ways

```text
== the draft's test vectors, and an exhaustive check ==
  draft Appendix C.1.2 subtree inclusion proofs: ac2a8f989e44d99e...  matches
  draft Appendix C.1.3 subtree consistency proofs: 10fa99b37bf9bf9f...  matches
  every valid subtree of every tree up to 64 entries: 7312 of 7312 proofs verify, longest 7 hashes
  45760 of 45760 tampered proofs or wrong subtree hashes rejected
```

The draft's Appendix C.1 vectors work as in Part 07: leaves are the single bytes 0x00, 0x01, and so on, and one text line per proof goes into a running SHA-256. For C.1.2 the line is `INDEX [START, END)` followed by the proof hashes, for every index of every valid subtree with end at most 130; for C.1.3 it is `[START, END) N` followed by the proof, for every valid subtree of every tree up to 130 entries. Both final hashes match, which means the generator produces exactly the draft's proofs, byte for byte, in 12,807 inclusion proofs and 42,893 consistency proofs.

The vectors only test the generator. The verifier is checked separately: every valid subtree of every tree up to 64 entries verifies, and every proof with one flipped byte in any hash, or paired with a wrong subtree hash, is rejected. The tests also check that a proof one hash short, one hash too long, or presented for a tree of size n + 1 fails.

## Checkpoints in MTC

The second half of the argument is the checkpoint. In Part 05 a checkpoint was a signed note. In MTC the draft expresses it with the same CosignedSubtree message as certificates (§5.3):

- In a **certificate**, a cosignature has timestamp **zero** and covers a subtree of the latest batch. It says: this subtree is in the log.
- A cosignature with a **nonzero** timestamp is a **checkpoint**: it must cover `[0, n)` where n is the largest consistent tree the cosigner has observed, and it asserts the cosigner's complete view of the log at that time.

So a checkpoint of size n is a cosigned "subtree" from 0 to n. The toy's `cosign_checkpoint` refuses to sign unless its own copy of the log has that hash, and the attack section shows a witness refusing after the CA rewrites an old entry:

```text
  forked log             -> witness refuses: oid/1.3.6.1.4.1.32473.2: checkpoint 500 does not match my view
```

A real witness checks more than this toy: it keeps the last checkpoint it signed and requires an RFC 9162 consistency proof from it to any new one, as in Part 05. The toy keeps a full mirror instead, which is the same check done the expensive way.

## Landmarks, precisely

Part 07 used landmarks loosely. The draft is precise (§6.4.1 and §6.4.2):

- A landmark has a **number**, a **tree size** and an **expiration** time.
- Landmark zero has tree size 0 and is never active.
- Tree sizes strictly increase; expirations never decrease.
- A landmark's expiration must be at least the `notAfter` of every entry below its tree size. The draft recommends now plus the maximum certificate lifetime.
- Landmark L's subtrees are the two covering subtrees of `[previous tree size, tree size)`, by Part 07's algorithm.
- A landmark is **active** until it expires. With a lifetime of 7 days and one landmark per hour, at most ⌈168 / 1⌉ + 1 = 169 are active, so 338 subtrees and 10,816 bytes.

The recommended allocation is simple: at most once per interval, if the tree has grown, append a landmark. The toy runs nine days of it, with 20 to 60 new certificates an hour:

```text
== a week of hourly landmarks (§6.4.2), 7-day certificates ==
  after 9 days: 8,695 entries, 216 landmarks allocated, 168 active
  draft bound: ceil(168 h / 1 h) + 1 = 169 active landmarks, 338 subtrees, 10,816 bytes
  this log: 168 active landmarks, 336 subtrees, 10,752 bytes of relying-party state
```

After the first week the number of active landmarks stops growing: one expires every hour as one is added. The draft's bound has one more because it allows for landmarks and expirations that do not fall exactly on the hour. This is the size the Chrome and Cloudflare experiment reported in practice: hourly landmarks and about 10 KB of client state.

## The update service

<img src="/images/root/08-service.svg" alt="The update service checks a reference checkpoint at least as large as the latest landmark; the CA cosigner and witness A cosign it directly; witness B cosigned a larger checkpoint linked by a consistency proof. Every landmark subtree has a subtree consistency proof against the reference. Only then are trusted subtrees shipped to browsers, about 10.8 KB per CA." width="1000" height="620" loading="lazy" />

Now the pieces fit together. Before a relying party trusts landmark subtrees, §7.4 requires:

1. a **reference checkpoint** whose tree size is at least that of the latest landmark;
2. for **each cosigner** its policy requires, either a cosignature on that reference checkpoint, or a cosignature on a larger checkpoint together with an RFC 9162 consistency proof from the reference to it;
3. for **each landmark subtree**, a subtree consistency proof against the reference checkpoint.

Notice what is absent: nobody signs the landmark subtrees themselves. The cosigners sign their view of the whole log, as they do anyway, and proofs connect each landmark to that view. A landmark that passes is a node of a tree the CA and the required witnesses all vouched for.

The draft does not prescribe how relying parties obtain these subtrees. In the toy, as in the Chrome experiment, an **update service** does the checking and ships the result. On the nine-day log:

```text
== the update service validates a bundle (§7.4) ==
  reference checkpoint 8695 vouched for by the CA and 2 witness(es)
  trusted: landmarks 49..216 (168) -> 336 subtrees, 10,752 bytes
  the service checked 336 subtree consistency proofs, 3,879 hashes (124,128 bytes), longest 15; plus 3 checkpoint cosignatures. A client that trusts the service needs only the result.
```

The asymmetry is the point. The service does 336 proof checks over about 124 KB once per update; each browser downloads 10.7 KB of hashes and checks nothing per connection. A browser that does not want to trust the service can run the same checks itself, if it is given the bundle.

## When the witnesses are behind

<img src="/images/root/08-lagging.svg" alt="Landmarks at tree sizes 200, 300, 400 and 500. The witnesses have only checked a checkpoint of size 350: landmarks 1 and 2 are kept, 3 and 4 discarded. Below, a forged hash for landmark 2 discards landmarks 2, 3 and 4 and keeps landmark 1." width="1000" height="540" loading="lazy" />

Witnesses are independent operators. Some will be behind. The draft works an example (§7.4): active landmarks at tree sizes 200, 300, 400 and 500, and no reference checkpoint of size 500 or more that enough cosigners vouch for, but one of size 350. The rule: a relying party that cannot validate a landmark may discard it **and every newer landmark in that log**, keeping the older ones it could validate. The toy reproduces it, with the CA's own cosigner up to date and both witnesses at 350:

```text
== the draft's example: landmarks at 200, 300, 400, 500; cosigners have only checked 350 ==
  reference 500: only 0 witness(es) vouch for the reference, need 1
  reference 500: nothing trusted
  reference 350: reference checkpoint 350 vouched for by the CA and 2 witness(es)
  reference 350: landmark 3 (size 400): beyond the reference checkpoint; discard landmarks 3..4
  reference 350: trusted: landmarks 1..2 (2) -> 4 subtrees, 128 bytes
```

The cost of lagging witnesses is not a security failure. It is a performance one: certificates relative to landmarks 3 and 4 are not usable yet, and servers fall back to standalone certificates for them. Safety does not depend on witnesses being fast, only on their being honest and consistent.

## Attacks

```text
== attacks on the update service ==
  forged landmark 2 hash  -> landmark 2 (size 300): subtree inconsistent with the checkpoint; discard landmarks 2..4
  forked log             -> witness refuses: oid/1.3.6.1.4.1.32473.2: checkpoint 500 does not match my view
  cap of 100 landmarks    -> 168 landmarks exceed the cap of 100: keep the oldest
```

**A forged landmark.** The CA publishes, for landmark 2, a hash that is not the hash of that range in the log the witnesses cosigned. No subtree consistency proof can connect it to the reference root, so landmark 2 fails and, by the rule above, 3 and 4 go with it. Landmark 1 survives. A CA that wants to give browsers a hidden subtree must get it into a checkpoint the witnesses sign, and witnesses sign only what they can see.

**A forked log.** The CA rewrites history after witnesses have seen it. A witness compares against its own view and refuses. The draft spells out the consequences (§12.2): if a CA shows different views to different cosigners, monitors can see that the cosigners disagree; relying parties can revoke the affected range of serials and will likely remove the CA. A CA that has signed inconsistent subtree hashes should move to a new issuance log (§12.2.1), because honest cosigners can no longer follow the old one.

**Too many landmarks.** A relying party keeps an upper bound on active landmarks per CA, so a CA cannot exhaust its storage. If the CA exceeds it, the **newest** landmarks are discarded (§7.4). The toy's cap of 100 keeps landmarks 49 to 148. Discarding the newest, not the oldest, keeps the relying party's view stable: a landmark it trusted yesterday is not dropped because the CA published too many today.

## Telling the server what you have

A server holding both a standalone and a landmark-relative certificate must know which the client can verify. The draft uses TLS trust anchor IDs (§8.2). A landmark-relative certificate from CA `caID`, log N, landmark L has the ID `{caID landmarks(1) N L}`; the client advertises a **landmark group** `{caID landmarkGroups(2) N L}` for the newest landmark it trusts. The group covers the CA itself (so every standalone certificate) and the landmark-relative certificates of every active landmark up to L. The draft's example: a client whose newest trusted landmark is landmark 42 of log 8 for CA 32473.100 sends `32473.100.2.8.42`, which matches any standalone certificate from that CA and landmark-relative certificates from landmarks 23 to 42. A client whose information is stale sends just `32473.100`, and gets a standalone certificate. A timestamped variant groups CAs by time ticks of about an hour instead of per-CA landmark numbers.

One observation for later in the series: by design this signal tells the server how recent the client's landmark information is, to the hour. Whether and how that matters for privacy is a question I will come back to, after reading the draft's privacy considerations closely; I note it here because it falls out of the mechanism.

## How stale can a client be?

<img src="/images/root/08-stale.svg" alt="Share of handshakes that can use a landmark-relative certificate against hours since the client last updated. It is 100 percent up to about 40 hours, then falls linearly: 94 percent at 48 hours, 75 at 72, 56 at 96, 38 at 120, 18 at 144, 0 at 168. Expected authentication bytes rise from 4,296 to 11,417." width="1000" height="580" loading="lazy" />

The draft is clear that landmark-relative certificates only work for sufficiently up-to-date relying parties. The question worth quantifying is how up to date. The model in `lr_share`:

- certificates last 7 days and the server renews at 75 percent of the lifetime (every 126 hours), keeping every unexpired certificate, as the draft recommends for renewal (§10.4);
- a certificate issued at time t becomes landmark-relative at the next hourly landmark, and that landmark reaches clients one hour later;
- a client that last updated s hours ago holds every landmark published up to then, and can use the small certificate if **any** unexpired certificate the server holds is relative to one of those landmarks.

```text
== how stale can a client be? (renew at 75% of 7 days, keep both certificates, 1 h distribution delay) ==
  client last updated   0 h ago: landmark-relative in 100.0% of handshakes, expected authentication   4,296 B
  client last updated  24 h ago: landmark-relative in 100.0% of handshakes, expected authentication   4,296 B
  client last updated  40 h ago: landmark-relative in 100.0% of handshakes, expected authentication   4,296 B
  client last updated  48 h ago: landmark-relative in  94.2% of handshakes, expected authentication   4,712 B
  client last updated  72 h ago: landmark-relative in  75.1% of handshakes, expected authentication   6,068 B
  client last updated  96 h ago: landmark-relative in  56.4% of handshakes, expected authentication   7,401 B
  client last updated 120 h ago: landmark-relative in  37.5% of handshakes, expected authentication   8,743 B
  client last updated 144 h ago: landmark-relative in  18.2% of handshakes, expected authentication  10,121 B
  client last updated 168 h ago: landmark-relative in   0.0% of handshakes, expected authentication  11,417 B
```

(The full output has a few more rows.) The shape has a simple explanation. Because the server keeps the old certificate until it expires, there is always one certificate at least 126 hours old and still valid for another 42 hours. So a client up to about 42 hours stale, minus the hour of waiting for a landmark and the hour of distribution, **always** gets the small certificate. Beyond that the share falls linearly, roughly (168 − s − 1.5) / 126, and reaches zero at the certificate lifetime. The bytes follow, between Part 07's 4,296 and 11,417.

Two consequences. Renewal policy is a performance parameter: renewing earlier lengthens the overlap and widens the plateau, at the cost of more issuance. And the clients that lose the small certificate are the ones offline for days, which for a browser that updates its components routinely is a minority; for devices without an update channel, it is everyone. The model is simple on purpose: it ignores server certificate selection subtleties, clients that update mid-connection, and per-CA differences, and the distribution delay is an assumption, not a measurement.

## Try it

From the `experiments\root-of-trust` folder:

```text
python 08_landmarks.py
python -m unittest test_08_landmarks
```

The script takes about ten seconds, mostly for the Appendix C vectors and the exhaustive check. Its output is deterministic except for the signatures, whose sizes are fixed anyway.

Exercises:

1. Generate the subtree consistency proof for `[12, 14)` in the tree of size 14 by hand. Why is it only two hashes? Run the verifier and follow `sn == tn` through the walk.
2. Find the longest subtree consistency proof for trees up to 1,000 entries. How does it compare with Part 04's worst consistency proof?
3. Make witness B honest but six hours behind. Which landmarks does the service keep, and how long until the newest is usable?
4. Change the renewal point to 50 percent and to 90 percent of the lifetime and rerun `lr_share`. Plot the plateau length against issuance volume.
5. Let the CA publish a landmark whose tree size is smaller than the previous one. Which rule of §6.4.1 does that break, and where should the update service reject it? Add the check.
6. Give the service a bundle in which witness A's larger checkpoint comes with a consistency proof to a **different** reference root. Which check fails?

## Reader checkpoint

<details>
<summary><strong>1.</strong> A subtree consistency proof with start = 0 is what, and with end = start + 1 is what?</summary>

With start = 0 it is Part 04's consistency proof: the subtree is a prefix of the tree. With end = start + 1 it is Part 04's inclusion path: the subtree is one leaf.

</details>

<details>
<summary><strong>2.</strong> Why does the verifier keep two running hashes?</summary>

One proves the claim about the subtree and the other about the tree. `fr` must come out equal to the claimed subtree hash and `sr` to the tree hash, from the same proof hashes. Checking only `sr` would show the proof hashes build some tree, not that the claimed hash is a node of it.

</details>

<details>
<summary><strong>3.</strong> Why does a right sibling never change fr?</summary>

A right sibling lies after position end − 1 at its level, so all its entries are at or beyond `end`, outside the subtree.

</details>

<details>
<summary><strong>4.</strong> Nobody signs landmark subtrees. Why are they still trustworthy?</summary>

The cosigners sign checkpoints, their whole view of the log. A subtree consistency proof shows the landmark subtree is a node of a checkpoint's tree, so it inherits that checkpoint's cosignatures.

</details>

<details>
<summary><strong>5.</strong> The witnesses have only checked a tree of size 350, and landmarks are at 200, 300, 400, 500. What does the relying party keep, and why discard 500 along with 400?</summary>

Landmarks 1 and 2 (sizes 200 and 300). A landmark that cannot be validated is discarded with every newer one in the log, so the trusted set is always a prefix of the landmark sequence that is fully covered by a vouched checkpoint.

</details>

<details>
<summary><strong>6.</strong> With 7-day certificates renewed at 75 percent and both kept, roughly how stale can a client be and still always get the small certificate?</summary>

About 40 hours: the 42 hours of overlap between the old and new certificates, minus the wait for the next landmark and the time to distribute it.

</details>

## What comes next

Parts 07 and 08 together implement Merkle Tree Certificates end to end: issuance, both certificate kinds, verification, and the landmark machinery behind the signatureless one, each checked against the draft's own vectors. [Part 09](/root/09-tiled-logs/) turns to how such a log is served in practice: tiled logs, published as static files that anyone can cache and any witness or mirror can follow.

## References

- D. Benjamin, D. O'Brien, B. E. Westerbaan, L. Valenta and F. Valsorda, [*Merkle Tree Certificates*](https://www.ietf.org/archive/id/draft-ietf-plants-merkle-tree-certs-07.html), draft-ietf-plants-merkle-tree-certs-07, October 2026: §4.4 (subtree consistency proofs), §5.3 (cosignatures and checkpoints), §6.4 (landmarks), §7.4 (trusted subtrees), §8.2 (trust anchor IDs), §12.2 (split views), Appendix C.1.2 and C.1.3 (test vectors).
- L. Valenta, [*MTC experiment early results*](https://datatracker.ietf.org/meeting/125/materials/slides-125-plants-mtc-experiment-early-results-01), PLANTS, IETF 125: hourly landmarks, about 10 KB of client state, an update service in Chrome.
- B. Laurie, E. Messeri and R. Stradling, RFC 9162, *Certificate Transparency Version 2.0*, 2021: the consistency proofs that link cosigned checkpoints.
- [C2SP tlog-witness](https://c2sp.org/tlog-witness): how witnesses check consistency before cosigning (see Part 05).
