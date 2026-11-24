---
title: 'Merkle trees from zero'
description: 'The data structure under Certificate Transparency and Merkle Tree Certificates, built from its definition. Tree hashes, inclusion proofs and consistency proofs exactly as RFC 6962 defines them; the RFC 9162 verification algorithms traced step by step with real hashes; why leaves and nodes are hashed differently; and what a log that must answer with proofs can no longer get away with.'
part: 4
pubDate: 2026-11-20
tags:
  - merkle-trees
  - certificate-transparency
  - hash-functions
  - transparency-logs
companion: experiments/root-of-trust
---

Part 03 ended with a hole. A CT log signs an SCT, a *promise* to publish a certificate, and if the log breaks the promise nothing in the SCT can show it. To close the hole we asked for three things: a short commitment to a whole log, a way to prove that an entry is in it, and a way to prove that the log only ever grew. One data structure gives all three, and it is the foundation of everything left in this series: CT logs, witnesses, tiled logs, and Merkle Tree Certificates themselves.

This part builds it from nothing. Not "a Merkle tree" in general, but **the** Merkle tree of RFC 6962 and RFC 9162, byte for byte, with the two verification algorithms that clients really run. Those algorithms are short but tricky: they walk the tree using only the entry's index and the tree size, with bit operations that look like magic until you trace them. So we will trace them, by hand, with real hashes.

By the end you should be able to:

1. compute the tree hash of any list the way CT does, including the odd sizes;
2. explain why the tree splits at a power of two, and why leaves and nodes get different prefixes;
3. produce and verify an **inclusion proof**, and say what each step of the RFC 9162 verifier is doing;
4. produce and verify a **consistency proof**, and explain why it proves "append-only";
5. say exactly what a log can still do wrong once it must answer with proofs.

The code is [`experiments/root-of-trust/04_merkle.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust), with tests in `test_04_merkle.py`. It has no dependencies beyond the standard library, except the last section, which uses `cryptography` for signatures.

## What we want from a log

A log is a list of entries $d_0, d_1, \dots, d_{n-1}$ that only grows. We want three operations, and for each a size target, because Part 02 taught us that bytes matter:

| operation | question it answers | target size |
|---|---|---|
| **commit** | "what is the whole log, right now?" | a few dozen bytes, whatever $n$ is |
| **prove inclusion** | "is $d_i$ the entry at position $i$ in the log I committed to?" | much less than $n$ |
| **prove consistency** | "is the log of size $m$ I saw last week a prefix of the log of size $n$ today?" | much less than $n$ |

The only tool is a cryptographic hash function $H$, here SHA-256 (32-byte output). We rely on two of its properties:

- **Collision resistance**: nobody can find two different inputs $x \ne y$ with $H(x) = H(y)$.
- **Second-preimage resistance**: given an input $x$, nobody can find another $y \ne x$ with $H(y) = H(x)$. (This follows from collision resistance.)

The practical meaning: a hash value *pins down* its input. If you know $H(x)$ and someone shows you an $x'$ that hashes to it, then $x' = x$.

### Two ideas that almost work

**Hash everything.** Commit to $C = H(d_0 \| d_1 \| \dots \| d_{n-1})$. Thirty-two bytes, perfect. But to check that $d_i$ is in it you need *all* the other entries, because there is no way to recompute $C$ from less. Proof size: the whole log.

**Hash chain.** Let $c_0 = H(d_0)$ and $c_i = H(c_{i-1} \| d_i)$, and commit to $c_{n-1}$. Now appending is cheap, and a consistency proof from $m$ to $n$ is "here are entries $m$ to $n-1$; start from $c_{m-1}$ and recompute". But that is $n - m$ entries, and an inclusion proof for an early entry still needs everything after it. Proof size: linear.

What we need is a structure where any single entry is connected to the commitment by a **short** path. That is a tree.

## The tree

Ralph Merkle introduced hash trees in 1979, to build digital signatures out of a hash function alone (Merkle signatures, the ancestor of today's SPHINCS+ and SLH-DSA). The idea: hash the entries, then hash them in pairs, then hash the pairs in pairs, until one hash is left. Each entry is then connected to the top by one hash per level.

RFC 6962 fixes every detail, so that two implementations always produce the same root. Its definition, for a list $D[n] = (d_0, \dots, d_{n-1})$:

$$
\begin{aligned}
\mathrm{MTH}(\{\}) &= \mathrm{SHA256}() \\
\mathrm{MTH}(\{d_0\}) &= \mathrm{SHA256}(\texttt{0x00} \,\|\, d_0) \\
\mathrm{MTH}(D[n]) &= \mathrm{SHA256}(\texttt{0x01} \,\|\, \mathrm{MTH}(D[0{:}k]) \,\|\, \mathrm{MTH}(D[k{:}n])) \quad \text{for } n > 1
\end{aligned}
$$

where $k$ is **the largest power of two strictly smaller than $n$**, and $D[a{:}b]$ is the sublist from $a$ up to (not including) $b$. In Python:

```python
def leaf_hash(d):         return sha256(b"\x00" + d)
def node_hash(left, right): return sha256(b"\x01" + left + right)

def split(n):
    """The largest power of two strictly smaller than n (n > 1)."""
    return 1 << ((n - 1).bit_length() - 1)

def mth(d):
    n = len(d)
    if n == 0:
        return sha256(b"")
    if n == 1:
        return leaf_hash(d[0])
    k = split(n)
    return node_hash(mth(d[:k]), mth(d[k:]))
```

`(n - 1).bit_length() - 1` is the position of the highest set bit of $n-1$, so `split` returns: 2 → 1, 3 → 2, 4 → 2, 5 → 4, 7 → 4, 8 → 4, 9 → 8. Note that for $n = 8$ the split is 4, not 8: *strictly* smaller.

Here is the tree for seven entries, with the node names RFC 6962 uses in its examples (we will use them all through this part):

<figure class="plate">
<img src="/images/root/04-tree.svg" alt="A Merkle tree of seven entries d0 to d6. Leaf hashes a to f, and j for d6. Inner nodes g = H(a, b), h = H(c, d), i = H(e, f); k = H(g, h), l = H(i, j); root = H(k, l). Leaves are H(0x00 || entry), nodes H(0x01 || left || right). The tree splits 7 into 4 and 3, then 4 into 2 and 2, and 3 into 2 and 1." width="1000" height="680" loading="lazy" />
<figcaption>Seven entries. The split rule decides the shape; the prefixes decide the hashes.</figcaption>
</figure>

With the entries being the ASCII strings `d0` … `d6`, the script computes (first 4 bytes of each hash):

| node | definition | hash |
|---|---|---|
| a … f | $H(\texttt{00} \| d_0)$ … $H(\texttt{00} \| d_5)$ | `c67f9ffe` `49b717e4` `f366df47` `5e0c4e11` `39298be9` `6d1bb6bb` |
| j | $H(\texttt{00} \| d_6)$ | `d750ca92` |
| g, h, i | $H(\texttt{01} \| a \| b)$, $H(\texttt{01} \| c \| d)$, $H(\texttt{01} \| e \| f)$ | `46c78708` `c59e9a6d` `a4f2a847` |
| k, l | $H(\texttt{01} \| g \| h)$, $H(\texttt{01} \| i \| j)$ | `8df3870b` `3cf05ff1` |
| root | $H(\texttt{01} \| k \| l)$ | `73a590fb` |

Notice $j$: entry $d_6$ has no partner at the bottom level, so its leaf hash is used directly one level up. Nothing is duplicated and nothing is padded.

**Does our `mth` really match CT's?** The Certificate Transparency test suites use eight fixed entries (the empty string, then `00`, `10`, `2021`, `3031`, `40414243`, …) and list the tree hash after each prefix. The script reproduces all nine, from the empty tree (`e3b0c442…`, SHA-256 of nothing) to the eight-entry tree (`5dc9da79…`).

### Why split at a power of two

There are many ways to shape a tree over $n$ leaves. RFC 6962's rule has a property that everything else in this part depends on: **the left subtree is always a perfect binary tree whose size is a power of two, and it never changes as the log grows.**

Write $n$ in binary. $7 = 4 + 2 + 1$: the tree for seven entries is a perfect tree of 4 (entries 0–3, node $k$), a perfect tree of 2 (entries 4–5, node $i$), and a single leaf (entry 6, node $j$), joined along the right edge. Add an eighth entry and $i$ and $j$'s side becomes a perfect tree of 4, but $k$ is untouched. Every perfect subtree, once complete, is frozen forever.

This is what makes consistency proofs short (the old tree's subtrees are literally nodes of the new tree), and it is also what makes logs cacheable: a frozen subtree can be stored, served and cached forever. Part 09, on tiled logs, is built entirely on that fact.

Compare Bitcoin, whose Merkle tree handles an odd number of nodes by **duplicating the last one**. Then the lists $[a, b, c]$ and $[a, b, c, c]$ have the same root, so two different lists of transactions share one commitment. That ambiguity was a real vulnerability (CVE-2012-2459): an attacker could take a valid block, duplicate its last transactions to make an invalid copy with the *same* block hash, and send it around; nodes that saw the bad copy marked that hash as invalid and then refused the real block. RFC 6962's rule never duplicates anything, so different lists always give different trees.

## Why 0x00 and 0x01

Every leaf hash starts with a `0x00` byte and every node hash with `0x01`. This is called **domain separation**, and it is not decoration. Remove it and the tree has a second-preimage attack.

<figure class="plate">
<img src="/images/root/04-second-preimage.svg" alt="Without prefixes, the tree over four certificates a, b, c, d has root R = H(H(A || B) || H(C || D)). A forged tree over two 64-byte entries x = A || B and y = C || D has root H(H(x) || H(y)), which is the same R. With 0x00 for leaves and 0x01 for nodes, a leaf hash and a node hash can never be swapped." width="1000" height="560" loading="lazy" />
<figcaption>Without prefixes, an inner node can pose as a leaf.</figcaption>
</figure>

Without prefixes, a leaf is $H(d)$ and a node is $H(L \| R)$. Take an honest log of four certificates $a, b, c, d$ with leaf hashes $A, B, C, D$. Its root is $H(H(A \| B) \| H(C \| D))$. Now take the 64-byte strings $x = A \| B$ and $y = C \| D$ and treat them as *entries* of a two-entry log. Its root is $H(H(x) \| H(y)) = H(H(A \| B) \| H(C \| D))$, the same value. Two different logs, one commitment: the attacker can "prove" that $x$ is entry 0 of a log that never contained it. The script shows exactly this:

```text
no prefixes: 4 certificates and 2 fake 64-byte entries give the same root? True
RFC 6962   : same attack, same root?                                     False
```

With the prefixes, $H(\texttt{00} \| x)$ and $H(\texttt{01} \| A \| B)$ hash different byte strings, so a leaf can never stand in for a node. (The forged entry would also have to be a valid certificate to fool CT, which a 64-byte string of hashes is not, but a security proof should not depend on that kind of luck. And other logs store other things.)

## Inclusion proofs

To prove that $d_3$ is in the seven-entry tree, the log sends the hashes the verifier cannot compute itself: the **siblings** along the path from $d_3$ to the root.

<figure class="plate">
<img src="/images/root/04-inclusion.svg" alt="The inclusion proof for d3 in the seven-entry tree is c, g, l (red). The verifier computes d = H(00 || d3), h = H(01 || c || d), k = H(01 || g || h), root = H(01 || k || l) (blue) and compares with the signed root." width="1000" height="700" loading="lazy" />
<figcaption>Three hashes prove one entry out of seven. A billion entries need thirty.</figcaption>
</figure>

RFC 6962 defines the proof, which it calls the *audit path* $\mathrm{PATH}(m, D[n])$ for entry $m$, recursively, with the same split as the tree:

- if $n = 1$: the path is empty;
- if $m < k$: $\mathrm{PATH}(m, D[0{:}k])$ followed by $\mathrm{MTH}(D[k{:}n])$;
- if $m \ge k$: $\mathrm{PATH}(m - k, D[k{:}n])$ followed by $\mathrm{MTH}(D[0{:}k])$.

In words: go down into the half that contains $m$, and on the way back up, append the root of the *other* half.

```python
def path(m, d):
    n = len(d)
    if n <= 1:
        return []
    k = split(n)
    if m < k:
        return path(m, d[:k]) + [mth(d[k:])]
    return path(m - k, d[k:]) + [mth(d[:k])]
```

RFC 6962 §2.1.3 gives four examples for the seven-entry tree, and the script, naming its hashes after the RFC's nodes, reproduces them exactly:

| proof | RFC 6962 | ours |
|---|---|---|
| entry 0 | b, h, l | b, h, l |
| entry 3 | c, g, l | c, g, l |
| entry 4 | f, j, k | f, j, k |
| entry 6 | i, k | i, k |

The proof for entry 6 is one hash shorter: $d_6$ sits higher in the tree, because it had no partner.

### Verifying without knowing the shape

The verifier has the entry, its index $m$, the tree size $n$, the proof, and a root signed by the log. It must combine the proof hashes in the right order, left or right at each step, and that order depends on the tree's shape. RFC 9162 §2.1.3.2 gives an algorithm that works out the shape on the fly, using two numbers:

- `fn`: the index, at the current level, of the node on our path;
- `sn`: the index, at the current level, of the **last** node in the tree.

At the bottom level these are $m$ and $n - 1$. Going up one level halves both (shift right by one).

```python
def verify_inclusion(leaf, index, size, proof, root):
    if index >= size:
        return False
    fn, sn, r = index, size - 1, leaf
    for p in proof:
        if sn == 0:
            return False                     # proof is longer than the tree is tall
        if fn & 1 or fn == sn:
            r = node_hash(p, r)              # sibling is on the LEFT
            if not fn & 1:
                while fn and not fn & 1:     # we were promoted: skip levels with no sibling
                    fn, sn = fn >> 1, sn >> 1
        else:
            r = node_hash(r, p)              # sibling is on the RIGHT
        fn, sn = fn >> 1, sn >> 1
    return sn == 0 and r == root
```

There are three cases at each level:

1. **`fn` is odd**: our node is a right child, so its sibling, the proof hash, goes on the left.
2. **`fn` is even and `fn < sn`**: our node is a left child with a right sibling; the proof hash goes on the right.
3. **`fn` is even and `fn == sn`**: our node is the *last* node at this level and has no right sibling. It is promoted unchanged (like $j$), possibly several levels, until it becomes a right child. The inner `while` skips those levels; then the proof hash, which is the left subtree at that height, goes on the left.

At the end, `sn == 0` checks that we reached the top level exactly: the proof was neither too short nor too long for this tree size.

Trace it for **entry 3, size 7, proof [c, g, l]**, with real hashes. In the tables, node(x, y) means $H(\texttt{01} \,\|\, x \,\|\, y)$:

| step | fn | sn | proof hash | case | r becomes |
|---|---|---|---|---|---|
| start | 3 | 6 | | | `5e0c4e11` (d, the leaf hash of d3) |
| 1 | 3 | 6 | c `f366df47` | fn odd: sibling on the left | node(c, d) = `c59e9a6d` (h) |
| shift | 1 | 3 | | | |
| 2 | 1 | 3 | g `46c78708` | fn odd: sibling on the left | node(g, h) = `8df3870b` (k) |
| shift | 0 | 1 | | | |
| 3 | 0 | 1 | l `3cf05ff1` | fn even, fn < sn: sibling on the right | node(k, l) = `73a590fb` |
| shift | 0 | 0 | | | |

`sn` is 0 and `r` equals the root `73a590fb`. Accepted. Now the promoted case, **entry 6, size 7, proof [i, k]**:

| step | fn | sn | proof hash | case | r becomes |
|---|---|---|---|---|---|
| start | 6 | 6 | | | `d750ca92` (j) |
| 1 | 6 | 6 | i `a4f2a847` | fn == sn, even: last node, promoted | node(i, j) = `3cf05ff1` (l) |
| skip | 3 | 3 | | fn now odd, stop skipping | |
| shift | 1 | 1 | | | |
| 2 | 1 | 1 | k `8df3870b` | fn odd: sibling on the left | node(k, l) = `73a590fb` |
| shift | 0 | 0 | | | |

Look at step 1: $j$ had no sibling at the bottom level, so the first proof hash $i$ is its sibling one level up, and it goes on the left. The verifier never saw a picture of the tree. Two integers carried all the shape information.

### What the proof does not bind

A detail the tests turned up, and one that matters. Take a 13-entry tree and the proof for entry 5. Verify it against the right root, but claim the tree has **12** entries instead of 13: it still passes. For this entry, a tree of 12 and a tree of 13 have the same shape along the path (both split as 8 + the rest, and entry 5 lives in the frozen left 8), so the hashes combine identically.

This is not a bug in the verifier. The proof binds the *entry and its index* to the *root*. Nothing in it binds the *size*. That is why a log never publishes a root alone: it signs the pair **(size, root)** together, in a *signed tree head*. A verifier must take both numbers from the same signed head, never the size from one place and the root from another.

## Consistency proofs

An inclusion proof says "this entry is in this tree". A consistency proof says something about whole histories: **the tree of size $m$ is a prefix of the tree of size $n$.** Nothing was removed, nothing reordered, nothing rewritten; entries were only appended. This is what turns a sequence of signed tree heads into a single, append-only history.

<figure class="plate">
<img src="/images/root/04-consistency.svg" alt="Consistency proof from 3 entries to 7: c, d, g, l. The old root is H(01 || g || c). The new root is H(01 || H(01 || g || H(01 || c || d)) || l). The same c and g build both roots, so the old tree is inside the new one." width="1000" height="770" loading="lazy" />
<figcaption>One proof, two roots: the old one and the new one, built from shared pieces.</figcaption>
</figure>

The idea comes straight from the power-of-two split. The old tree of size $m$ is a handful of perfect subtrees (by the binary digits of $m$: $3 = 2 + 1$ gives $g$ and $c$). Each of those is **also a node of the new tree**, since perfect subtrees are frozen. So the proof sends those nodes, plus the extra nodes needed to climb from them to the new root. From the first group alone the verifier rebuilds the old root; from both groups, the new root. If both match the signed heads, the old tree sits, unchanged, inside the new one.

RFC 6962 defines $\mathrm{PROOF}(m, D[n]) = \mathrm{SUBPROOF}(m, D[n], \text{true})$ with:

- if $m = n$: empty if the flag is true (the verifier already knows this subtree's hash: it *is* the old root), otherwise $[\mathrm{MTH}(D[n])]$;
- if $m \le k$: $\mathrm{SUBPROOF}(m, D[0{:}k], b)$ followed by $\mathrm{MTH}(D[k{:}n])$;
- if $m > k$: $\mathrm{SUBPROOF}(m - k, D[k{:}n], \text{false})$ followed by $\mathrm{MTH}(D[0{:}k])$.

```python
def proof(m, d):
    return [] if m == len(d) or m == 0 else _subproof(m, d, True)

def _subproof(m, d, b):
    n = len(d)
    if m == n:
        return [] if b else [mth(d)]
    k = split(n)
    if m <= k:
        return _subproof(m, d[:k], b) + [mth(d[k:])]
    return _subproof(m - k, d[k:], False) + [mth(d[:k])]
```

The flag `b` records whether we are still on the left edge of the tree. On the left edge, the subtree we reach is exactly the old tree, whose root the verifier already holds, so sending it would waste 32 bytes. Off the left edge, the subtree is just one piece of the old tree, and must be sent.

Again the RFC's examples, reproduced exactly:

| proof | RFC 6962 | ours |
|---|---|---|
| from 3 to 7 | c, d, g, l | c, d, g, l |
| from 4 to 7 | l | l |
| from 6 to 7 | i, j, k | i, j, k |

From 4 to 7 the proof is a single hash: the old tree of 4 *is* node $k$, the verifier knows it (the old root), and only $l$ is needed to reach the new root.

### Verifying a consistency proof

RFC 9162 §2.1.4.2 uses the same `fn`/`sn` walk, now carrying **two** running hashes: `fr` rebuilds the old root, `sr` the new one.

```python
def verify_consistency(first, second, first_root, second_root, proof):
    if first == second:
        return not proof and first_root == second_root
    if first == 0:
        return not proof
    if not proof:
        return False
    if first & (first - 1) == 0:          # first is a power of two:
        proof = [first_root] + proof      # the old root is itself a node of the new tree
    fn, sn = first - 1, second - 1
    while fn & 1:                         # climb to the first level where the old tree's
        fn, sn = fn >> 1, sn >> 1         # last node is a left child
    fr = sr = proof[0]
    for c in proof[1:]:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            fr, sr = node_hash(c, fr), node_hash(c, sr)   # c is on the left: part of BOTH trees
            if not fn & 1:
                while fn and not fn & 1:
                    fn, sn = fn >> 1, sn >> 1
        else:
            sr = node_hash(sr, c)                         # c is on the right: NEW entries only
        fn, sn = fn >> 1, sn >> 1
    return sn == 0 and fr == first_root and sr == second_root
```

The key line is the split between the two branches. A proof hash on the **left** covers entries that existed in the old tree too, so it goes into both `fr` and `sr`. A proof hash on the **right** covers only entries appended since, so it goes into `sr` alone. If the log changed any old entry, `fr` cannot come out equal to the old root, because the old root is fixed and signed.

Trace **from 3 to 7, proof [c, d, g, l]**. The old root is node(g, c) = `c64c5b93`, the new root `73a590fb`:

| step | fn | sn | proof hash | case | fr | sr |
|---|---|---|---|---|---|---|
| start | 2 | 6 | | 3 is not a power of two; fn = 2 is even, no climbing | c `f366df47` | c `f366df47` |
| 1 | 2 | 6 | d `5e0c4e11` | fn even, fn < sn: right, new only | `f366df47` | node(c, d) = `c59e9a6d` (h) |
| shift | 1 | 3 | | | | |
| 2 | 1 | 3 | g `46c78708` | fn odd: left, both | node(g, c) = `c64c5b93` | node(g, h) = `8df3870b` (k) |
| shift | 0 | 1 | | | | |
| 3 | 0 | 1 | l `3cf05ff1` | fn even, fn < sn: right, new only | `c64c5b93` | node(k, l) = `73a590fb` |
| shift | 0 | 0 | | | | |

`sn` is 0, `fr` equals the old root and `sr` the new one. The same two hashes, $c$ and $g$, went into both roots: that shared material is the proof that the old tree survived intact.

## How big are the proofs?

One hash per level, and the tree has $\lceil \log_2 n \rceil$ levels:

| entries | inclusion proof | bytes | worst consistency proof | bytes |
|---|---:|---:|---:|---:|
| 8 | 3 | 96 | 4 | 128 |
| 1,000 | 10 | 320 | 11 | 352 |
| 1,000,000 | 20 | 640 | 21 | 672 |
| 1,000,000,000 | 30 | 960 | 31 | 992 |
| $2^{40} \approx 1.1 \times 10^{12}$ | 40 | 1,280 | 41 | 1,312 |

The consistency column is exact, not an estimate: the script computes the length of every consistency proof for every tree size from 4 to 2,048 (the length depends only on $m$ and $n$, not on the hashes), and the worst case is always $\lceil \log_2 n \rceil + 1$.

<figure class="plate">
<img src="/images/root/04-sizes.svg" alt="Inclusion proof size against log size on a logarithmic axis: 96 bytes for 8 entries, 320 for a thousand, 640 for a million, 960 for a billion, 1,280 for a trillion. A line marks one ML-DSA-44 signature at 2,420 bytes, above all of them." width="1000" height="520" loading="lazy" />
<figcaption>Doubling the log adds 32 bytes to a proof. A trillion entries still cost less than one post-quantum signature.</figcaption>
</figure>

Hold that last row next to Part 02. One ML-DSA-44 signature is 2,420 bytes. A proof that a certificate is one of **a trillion** in a log is 1,280 bytes, and hashes do not get bigger when quantum computers arrive: SHA-256's security against them is still comfortable, and nothing in this part changes.

## Testing it like we mean it

Proof code is easy to get almost right, and "almost" means a verifier that accepts something it should not. So the script tests the two halves against each other:

- The **generators** (`path`, `proof`) follow RFC 6962's recursive definitions. The **verifiers** follow RFC 9162's iterative algorithms. They share no code apart from the two hash functions.
- For **every** tree size from 1 to 64, **every** index and **every** prefix size, it generates a proof and verifies it: 4,224 proofs, all accepted. Each inclusion proof is also checked against the wrong index, which must fail.
- It then flips single bits in inclusion proofs for a 37-entry tree: 3,360 corrupted proofs, all rejected.
- The tree hash matches the nine CT test vectors, and the proofs match the RFC's seven worked examples.

The test file adds proofs that are too short, too long, for the wrong entry, against a rewritten log, and random trees of 3,000 entries.

## Part 03's broken promises, revisited

Now give Part 03's log a Merkle tree. Every so often it publishes a **signed tree head (STH)**: the tree size, the root, a timestamp, and the log's signature over all three. RFC 6962 logs do exactly this. Clients and monitors can ask the log for inclusion and consistency proofs against any tree head. The script replays the dishonest logs:

```text
A. honest log, browser asks for a proof        proof of 10 hashes verifies: entry 500 of 1001, the monitor will see it
B. log skipped the entry (scenario 8)          no proof exists; signed SCT + signed head past the deadline = evidence against the log
C. log rewrote history after a monitor saw it  consistency proof fails: two signed heads that cannot both be true
D. split view: two trees, two audiences        victim's proof verifies, monitor's tree is clean: nobody alone can tell (Part 05)
```

**A.** The browser, holding an SCT, asks for a proof of inclusion against a tree head signed after the deadline. Ten hashes. The certificate is provably in the same tree the monitors read, so the monitor *will* see it.

**B is Part 03's scenario 8**, and it is no longer silent. The log signed an SCT ("in by T + 24 h") and later signed a tree head with a timestamp past that deadline. If the entry is not in that tree, the log cannot produce an inclusion proof, however hard it tries: forging one means finding a SHA-256 collision. And since the entries of a log are public, anyone can download the first $n$ of them, recompute the root, check it equals the signed one, and see that the certificate is missing. The log has signed two statements that contradict each other.

**C.** The log included the rogue certificate, a monitor saw tree head #1, and then the log quietly removed the entry and rebuilt the tree. Now no consistency proof from head #1 to head #2 exists. Again the log holds two of its own signatures that cannot both be honest, and anyone can check it. This is the strongest form of evidence in the system: **a log that rewrites history convicts itself.**

**D is what is left.** The log keeps two trees. The monitor is always served one, the victim's browser the other. Each audience gets valid signed heads, valid inclusion proofs and valid consistency proofs, all internally perfect. No single party can tell. The only way to catch it is for the parties to **compare notes**: if anyone ever sees two signed tree heads of the same size with different roots, or two heads with no consistency proof between them, the split is exposed. Making sure everyone sees the same heads is the job of gossip, checkpoints and witnesses. That is [Part 05](/root/05-notes-checkpoints-witnesses/).

## Toward Merkle Tree Certificates

Step back to the bill. Part 02 left about 7,260 bytes of ML-DSA-44 offline signatures per handshake: the CA's signature on the leaf and two SCTs, all saying "this certificate was issued and is public". This part shows what a public log can offer instead: a proof of a few hundred bytes that a certificate is in a tree whose head is signed **once**, for millions of certificates.

That is the core idea of Merkle Tree Certificates: the CA runs the log, and a certificate is little more than an inclusion proof in it. The draft adds clever tricks so that browsers can know the relevant tree heads in advance and need no signature at all in the handshake, but every one of those tricks is built from the three functions in this part. Before getting there we need Part 05's checkpoints and witnesses, because a proof is only as good as the agreement on which root it leads to.

## Try it

From the `experiments\root-of-trust` folder (the last section needs `cryptography`):

```text
python 04_merkle.py
python -m unittest test_04_merkle
```

Exercises:

1. Compute $\mathrm{MTH}$ of three entries by hand from the `split` rule, and check against the script. Then do it for a tree of 5.
2. Find all pairs (index, wrong size) for a 13-entry tree for which an inclusion proof still verifies with the wrong size. Can you predict them from the binary expansions of the sizes?
3. Implement Bitcoin's "duplicate the last node" tree and find two different lists with the same root. Then show the same trick fails against `mth`.
4. Write `verify_inclusion` recursively instead of iteratively, from the definition of `path`. Test it against the iterative one for all sizes up to 64.
5. Why does the consistency verifier prepend the old root when the old size is a power of two? Find the smallest example where removing that line makes a valid proof fail.

## Reader checkpoint

<details>
<summary><strong>1.</strong> What is the split point k for n = 8, and why does it matter that it is "strictly smaller"?</summary>

k = 4. With "smaller or equal" it would be 8, and the left subtree would be the whole tree; the recursion would not terminate. With the strict rule, 8 splits into two perfect trees of 4.

</details>

<details>
<summary><strong>2.</strong> Why does the tree never duplicate the last node when a level has an odd number of nodes, and what goes wrong if it does?</summary>

RFC 6962 promotes the lone node instead (like j). Duplicating it, as Bitcoin does, makes [a, b, c] and [a, b, c, c] share a root, so one commitment matches two different lists: the CVE-2012-2459 problem.

</details>

<details>
<summary><strong>3.</strong> In the inclusion verifier, what do fn and sn mean, and what is special about the case fn == sn?</summary>

fn is the index of our node at the current level, sn the index of the last node at that level. When fn == sn and fn is even, our node is the last one and has no right sibling: it is promoted up, possibly several levels, until it becomes a right child.

</details>

<details>
<summary><strong>4.</strong> An inclusion proof verifies against the root of a 13-entry tree even when the verifier is told the size is 12. Why is that not a vulnerability in practice?</summary>

Because logs sign size and root together in a tree head. A correct verifier takes both from the same signed head, so it never pairs a root with a size the log did not sign.

</details>

<details>
<summary><strong>5.</strong> In the consistency verifier, why do left-side proof hashes go into both fr and sr, but right-side ones only into sr?</summary>

A hash on the left covers entries that are older than the old tree's boundary, so it belongs to both trees. A hash on the right covers only entries appended afterwards, so it belongs to the new tree only.

</details>

<details>
<summary><strong>6.</strong> Which of the four dishonest logs can a single honest monitor catch on its own, and which needs more than one party?</summary>

A skipped entry (B) and a rewritten history (C) produce signed statements that contradict each other, and anyone holding them can prove it. A split view (D) is internally consistent for each audience; it is only caught when parties compare the tree heads they were given.

</details>

## References

- R. C. Merkle, *Secrecy, Authentication, and Public Key Systems*, PhD thesis, Stanford, 1979; and *A Digital Signature Based on a Conventional Encryption Function*, CRYPTO '87.
- S. A. Crosby and D. S. Wallach, *Efficient Data Structures for Tamper-Evident Logging*, USENIX Security 2009: the history trees behind consistency proofs.
- RFC 6962, *Certificate Transparency*: Merkle Tree Hash (§2.1), audit paths and their examples (§2.1.1, §2.1.3), consistency proofs and their examples (§2.1.2, §2.1.3), signed tree heads (§3.5).
- RFC 9162, *Certificate Transparency Version 2.0*: the same tree (§2.1.1), and the verification algorithms for inclusion (§2.1.3.2) and consistency (§2.1.4.2) used in this part.
- [CVE-2012-2459](https://nvd.nist.gov/vuln/detail/CVE-2012-2459): the Bitcoin Merkle tree duplicate-node issue.
- B. Laurie, *Certificate Transparency*, ACM Queue 12(8), 2014: the log design explained by one of its authors.
- [transparency-dev](https://github.com/transparency-dev): today's open-source libraries for Merkle logs, proofs and witnesses.
