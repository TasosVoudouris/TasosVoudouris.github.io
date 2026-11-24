---
title: 'Tiled logs'
description: 'How a transparency log serves millions of entries to thousands of clients without computing a single proof: the C2SP tlog-tiles layout, written and read from scratch and checked against the spec and Tessera examples. Tile paths, full and partial tiles, entry bundles, a client that authenticates every tile it uses and rebuilds Part 04, 07 and 08 proofs from them, tampering, a 98.9 percent cache hit rate, and what tailing costs a monitor.'
part: 9
pubDate: 2026-11-24
tags:
  - transparency-logs
  - tlog-tiles
  - merkle-trees
  - merkle-tree-certificates
  - caching
companion: experiments/root-of-trust
---

Every proof in Parts 04 to 08 was computed by a function that held the full list of entries. That is fine for a toy, but it is not how a log can work at scale. An MTC CA issuing millions of certificates a day, followed by witnesses, mirrors, monitors and the update services of every browser, cannot run a database query for every proof somebody wants. Certificate Transparency learned this the hard way. Its original API, from RFC 6962, answers questions like "give me the proof for this hash in this tree size" or "give me entries 1,000 to 1,999". Each answer is computed on demand and is different for almost every request, so caches do not help.

The answer that modern logs use is almost embarrassingly simple: **do not serve proofs, serve the tree**. Cut the Merkle tree into fixed blocks of 256 hashes, store each block as a file, and publish the files on any static web host. Clients fetch the few files they need and compute every proof themselves. A file that is complete never changes, so every cache on the path can keep it forever.

This is the C2SP **tlog-tiles** specification. Its design comes from the Go checksum database; today logs built with Tessera serve it, and static CT logs (the static-ct-api) use the same tile layout. Let's Encrypt's implementation of Merkle Tree Certificate logs also stores its trees in this format. This part implements it from scratch: a writer that publishes a log as tiles, and a client that verifies everything from them, with no server logic at all.

By the end you should be able to:

1. read and write tile paths, and say which tiles exist for a log of any size;
2. explain why full tiles are immutable and partial tiles are not, and what that means for caching;
3. compute any inclusion, consistency or MTC subtree proof from tiles, and say how many tiles it touches;
4. authenticate every tile you fetch, so a malicious host cannot feed you a wrong hash;
5. estimate what a monitor pays to follow a log, and when it should wait for full tiles.

The code is [`experiments/root-of-trust/09_tiles.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust), with tests in `test_09_tiles.py`. It uses Part 04's Merkle tree, Part 05's signed checkpoints, and Parts 07 and 08 for the MTC proofs. Run it with `--write DIR` and it also writes all 1,403 files of a 70,000-entry log into a folder you can browse.

## Three kinds of file

A tiled log is defined by a URL prefix, a checkpoint origin and the log's public key. Under the prefix it serves exactly three kinds of resource:

| path | what it is | changes? |
|---|---|---|
| `<prefix>/checkpoint` | the signed checkpoint from Part 05: origin, tree size, root hash, signatures | yes: every few seconds; must not be cached for longer |
| `<prefix>/tile/<L>/<N>[.p/<W>]` | up to 256 hashes from one level of the tree, concatenated, 32 bytes each | full tiles never; partial tiles are replaced as the log grows |
| `<prefix>/tile/entries/<N>[.p/<W>]` | the entries behind level 0 tile N, each with a 2-byte big-endian length | same as tiles |

The checkpoint is the only mutable file. It is small, signed, and must not be cached beyond a few seconds. Everything else is content addressed by position in a tree whose history cannot change: once tile `0/000` holds 256 hashes, those hashes are fixed for the life of the log, because the log is append only. That is the whole trick.

## Tiles

<img src="/images/root/09-pyramid.svg" alt="A log of 70,000 entries as tiles. Level 0: 273 full tiles of 256 leaf hashes, then a partial tile of 112. Level 1: one full tile whose hashes are the roots of level 0 tiles 0 to 255, then a partial tile of 17. Level 2: a partial tile of width 1. Entry bundles sit beside the level 0 tiles." width="1000" height="600" loading="lazy" />

A tile is a height 8 piece of the Merkle tree: 256 hashes at its bottom, and the 255 nodes above them, which are not stored because anyone can recompute them. Tiles are organized in **levels**:

- **Level 0** tiles hold leaf hashes. Tile N holds the leaf hashes of entries 256N to 256N + 255.
- **Level 1** tiles hold hashes at tree level 8: each is the root of one full level 0 tile. Tile N of level 1 holds the roots of level 0 tiles 256N to 256N + 255.
- In general, hash i of tile n at level l is the hash of entries `(256n + i) · 256^l` to `(256n + i + 1) · 256^l`, and the whole tile covers `n · 256^(l+1)` to `(n + 1) · 256^(l+1)`.

That last range starts at a multiple of its own size, a power of two, so by Part 07's rule **every full tile is a valid subtree**. The script checks this for every tile of its log. It means an MTC landmark or a cosigned subtree that happens to align with a tile is literally the root of that tile. Most do not align, but every proof hash is still a node of the tree, and as we will see, every node can be computed from tiles.

A tile is **full** when it has 256 hashes. While the log grows, the right edge of each level is incomplete; the spec serves it as a **partial tile** of width W (1 to 255), with the suffix `.p/<W>`. For a tree of size s, level l has `⌊s / 256^(l+1)⌋` full tiles and, if `⌊s / 256^l⌋ mod 256` is not zero, one partial tile of that width. The spec gives an example, and the script reproduces it:

```text
== which tiles exist for a tree of 70,000 entries (the spec's example) ==
  level 0: 273 full, partial of width 112
  level 1:   1 full, partial of width 17
  level 2:   0 full, partial of width 1
  (spec: 273 full level 0 tiles and a partial of 112; 1 full level 1 tile and a partial of 17; a level 2 partial of 1)
  every full tile covers a valid MTC subtree (Part 07): True
```

Work it by hand: 70,000 = 273 · 256 + 112, so 273 full level 0 tiles and a partial of 112. At level 1 there are ⌊70,000 / 256⌋ = 273 hashes, one per full level 0 tile: 256 of them fill tile `1/000` and 17 remain. At level 2 there is ⌊70,000 / 65,536⌋ = 1 hash, the root of tile `1/000`, in a partial tile of width 1. Partial hashes are never hashed into the level above: the 112 leaf hashes of the last level 0 tile appear nowhere at level 1, because they do not yet form a complete node of height 8.

A rule worth noticing: the log must serve partial tiles for **every tree size it has published a checkpoint for**. A client still holding yesterday's checkpoint must be able to fetch yesterday's right edge. The log may delete a partial tile once the full tile exists, and clients may fetch the full tile as a fallback.

## Paths

<img src="/images/root/09-path.svg" alt="The path tile/0/x001/x234/067.p/8: tile is the namespace, 0 the level, x001/x234/067 the index 1,234,067 in groups of three digits with an x on every group but the last, and .p/8 marks a partial tile of 8 hashes." width="1000" height="400" loading="lazy" />

The index N is written in groups of three decimal digits, zero padded, with an `x` in front of every group except the last. So 1,234,067 becomes `x001/x234/067`, and 1,000 becomes `x001/000`. Two reasons: no directory ever holds more than 1,000 names, which keeps file systems and object stores happy; and the `x` distinguishes directories from files, so `001` (a tile) and `x001/` (a directory of later tiles) never collide. The level is a plain decimal from 0 to 63 with no leading zeros, and W runs from 1 to 255, also with no leading zeros.

```text
== paths, checked against the spec and Tessera ==
  tile_path(0, 1234067, 8): tile/0/x001/x234/067.p/8  ok
  tile_path(1, 0): tile/1/000  ok
  tile_path(2, 999): tile/2/999  ok
  tile_path(0, 1000): tile/0/x001/000  ok
  entries_path(1234067, 8): tile/entries/x001/x234/067.p/8
  parse 'tile/0/x001/x234/067.p/8' -> ('0', 1234067, 8)
  node (level 8, index 123456789) lives in tile (level, index, node level, node index) = (1, 482253, 0, 21)
```

The first and the last lines are examples from the documentation of Tessera, the Go library many logs are built with: the path, and the mapping from a tree node to the tile that holds it. A node at tree level h and index i lives in tile level ⌊h / 8⌋; within that level's row it spans 2^(h mod 8) hashes, so it is the root of a small piece of one tile. Node (8, 123,456,789) is hash 21 of level 1 tile 482,253.

The parser is strict on purpose. The tests reject `tile/00/000` (leading zero in the level), `tile/0/x000/001` (a leading zero group), `.p/0`, `.p/256` and `.p/08`. If two spellings could name the same tile, caches would store it twice and clients could be confused about which one they verified.

## Entry bundles

Tiles hold hashes. The entries themselves are in **entry bundles**, at `tile/entries/<N>`, beside level 0 tile N. A bundle is the entries one after another, each prefixed by its length as a big-endian 16-bit integer. That matches MTC's limit from Part 07: an MTCLogEntry may not exceed 65,535 bytes, exactly what a 2-byte length can describe. Each entry in a bundle must hash, as a leaf, to the corresponding hash in level 0 tile N, so a bundle is authenticated by its tile.

Let's Encrypt's tile storage for its MTC logs, in its Boulder CA software, documents one more layer beside the entries: bundles of `MTCPublicKey` objects with the same number of elements as the entry bundles. Part 07 explained why such a thing is useful: the log entry contains only the hash of the subject's public key, so anyone who wants to see the key itself needs it from somewhere else.

## Writing a log

The writer keeps one row of hashes per tile level. Appending entries extends row 0 with leaf hashes; whenever 256 hashes of a row complete a tile, the tile's root is appended to the row above. Publishing a checkpoint writes:

- every full tile and bundle not written before; writing one twice with different content is an error;
- the partial tile and bundle of each level for the current size;
- the checkpoint, signed with Part 05's code, whose root is computed **from the rows**, not from the entries.

```text
== writing a log of 70,000 entries, one checkpoint per batch ==
  309 checkpoints published; root from the tiles equals Part 04's mth over all entries: True
  files: 547 full tiles and bundles (written once, never changed), 855 partial ones over time
  bytes written: 7,799,379, of which partial files 3,399,353 (44%)
```

The full files are the permanent log: 274 + 273 tiles and bundles here. The partial ones are the cost of publishing often: with batches of 50 to 400 entries, 44 percent of everything written was right-edge data that a later checkpoint superseded. That is the price of frequent checkpoints. It is paid in storage writes, not in anything a client must trust.

## Reading it: a client with no server

The client knows only the log's origin and public key. It fetches the checkpoint, verifies the signature, and from then on fetches tiles. To make every proof from tiles, the code has one small idea at its core: a `Hasher` that computes the hash of any range `[a, b)` of the log from **complete tree nodes**.

```python
def range_hash(self, a, b):
    n = b - a
    if n & (n - 1) == 0 and a % n == 0:
        return self.node(n.bit_length() - 1, a // n)          # an aligned node: one lookup
    k = 1 << ((n - 1).bit_length() - 1)                       # MTH's own split
    return node_hash(self.range_hash(a, a + k), self.range_hash(a + k, b))
```

If the range is an aligned power of two, it is one node of the tree, and `node(level, index)` finds it in a tile. Otherwise split it exactly as MTH does and recurse. With `range_hash`, Part 04's inclusion and consistency proofs and Part 08's subtree consistency proofs are the same recursions as before, with "the hash of this half" now answered from tiles instead of from a list. The writer and the client share this code; they differ only in where `node` gets its hashes.

```text
== a client that has only the tiles ==
  checkpoint verified: size 70000, root matches the tiles: True
  recomputing the root used 3 tiles
  inclusion of entry     5: 17 hashes from 5 tiles (3 fetched), equals Part 04 and verifies: True
  inclusion of entry 31337: 17 hashes from 4 tiles (2 fetched), equals Part 04 and verifies: True
  inclusion of entry 69999: 9 hashes from 3 tiles (1 fetched), equals Part 04 and verifies: True
  consistency 41000 -> 70000: 15 hashes, equals Part 04: True, verifies: True
```

Every proof computed from tiles is byte for byte the one Part 04 computes from the full list, and it verifies against the signed root with Part 04's verifier. A proof in a tree of 70,000 entries touches at most a handful of tiles: one per level on the entry's own path, plus the right edge. In a log of a billion entries there are four tile levels, so the count barely grows.

## Trust nothing the host sends

<img src="/images/root/09-proof.svg" alt="Verifying entry 31,337. The right-edge tiles 2/000.p/1, 1/001.p/17 and 0/273.p/112 must together rebuild the checkpoint root. Level 0 tile 122 gives 8 proof hashes; it must hash to hash 122 of level 1 tile 000, which gives 8 more and must hash to hash 0 of 2/000.p/1. The last hash comes from the right edge. The entry bundle must hash to leaf 31,337." width="1000" height="600" loading="lazy" />

The host is untrusted: it is a CDN, a mirror, a bucket anybody could have tampered with. A careless client would compute a proof from whatever hashes it receives, and in the end the proof would simply fail to verify. That is safe, but useless for diagnosis, and dangerous if the client caches the bad tile or uses tile contents for anything else. So the client **authenticates every tile before using it**:

- **Right-edge tiles** are authenticated together: right after verifying the checkpoint, the client rebuilds the root from them, and it must equal the signed root. For 70,000 entries that is the three partial tiles.
- **A full tile** is one hash in the tile above it: tile `0/122` must hash to hash 122 of tile `1/000`, and tile `1/000` to hash 0 of `2/000.p/1`. The check recurses upward until it reaches a tile that is already authenticated.
- **An entry** must hash, as a leaf, to its hash in the authenticated level 0 tile.

```text
== a tampered host ==
  one hash in tile/0/007 zeroed -> rejected: tile/0/007 does not match its hash in the tile above
  flipped byte in tile/entries/003 -> rejected: entry does not hash to its leaf
```

I note how I got here, because it is the most useful mistake in this part. My first client only checked that the root rebuilt from tiles matched the checkpoint. It accepted the tampered tile `0/007`, because the root of a 70,000-entry tree is computed from the top of the pyramid and never looks at tile `0/007` at all. The rejection only happened later, when an inclusion proof failed. Authenticating each tile against its parent moves the failure to the moment the bad data arrives, and points at the file that is wrong.

## Parts 07 and 08, served by files

Everything MTC needs from a log is a proof of one of three kinds: inclusion in a subtree (Part 07), consistency of a subtree with a checkpoint (Part 08), and consistency between checkpoints (Part 05). All three come from tiles:

```text
== Parts 07 and 08 from tiles: MTC proofs need no extra server ==
  subtree consistency [65536, 69632) in 70000: 2 hashes, equals Part 08: True, verifies: True
  subtree consistency [69632, 69888) in 70000: 3 hashes, equals Part 08: True, verifies: True
  subtree consistency [40960, 41984) in 70000: 7 hashes, equals Part 08: True, verifies: True
  batch [69000, 70000) covered by [68608, 69632) and [69632, 70000); subtree inclusion proof of entry 69500: 9 hashes, equals Part 07: True
```

This closes a loop from the last two parts. An MTC CA does not need a proof server. It publishes tiles and checkpoints. A server that wants a landmark-relative certificate fetches the tiles for its entry and builds the proof. An update service that validates landmarks fetches the tiles for each subtree consistency proof. A witness that checks a new checkpoint fetches the tiles for a consistency proof. All of them hit the same cacheable files.

## Why caches love tiles

<img src="/images/root/09-cache.svg" alt="5,000 clients verifying one random entry each. A per-proof API: 5,000 requests reach the server. Tiles: 24,666 requests by clients, 277 distinct tiles, 277 requests reach the host, a shared cache hit rate of 98.9 percent." width="1000" height="460" loading="lazy" />

The script runs 5,000 independent clients behind one shared cache, each verifying the checkpoint and one random entry:

```text
== caching: 5,000 clients, each verifying one random entry ==
  24,666 tile requests (4.9 per client), 277 distinct tiles, 277 reached the host: shared cache hit rate 98.88%
  a per-proof API (RFC 6962 get-proof-by-hash) would see up to 5,000 distinct queries: each one a cache miss and a database lookup
```

There are only 277 tiles in the whole log, and every client asks for the same files, so after the first few clients the cache answers everything. The host saw 277 requests in total, once per file. With an API that computes proofs, each query names a different entry and a different answer: nothing to share. The CT community has documented this in practice: operators report that the start and end parameters of RFC 6962's `get-entries` vary so much that CDN cache hit rates are very low.

The model is idealized: one shared cache, one checkpoint, no expiry. Real deployments add checkpoint churn and several caches. But the structure of the result holds: the number of distinct files grows with the size of the log, not with the number of clients.

## What a monitor pays

<img src="/images/root/09-monitor.svg" alt="Bytes downloaded per byte of new entries against entries added per checkpoint. Fetching every partial bundle costs 13.7 times at 10 per checkpoint, 2.7 at 75, 1.62 at 200, 1.04 at 3,000. Waiting for full bundles costs 3.1, 1.28, 1.10 and 1.01." width="1000" height="520" loading="lazy" />

A monitor follows a log entry by entry: it wants every certificate, as soon as possible. If it fetches the partial entry bundle at every checkpoint, it downloads the same entries again and again until the bundle fills up. The script computes the overhead for entries of about 190 bytes, the size of Part 07's log entries:

```text
== a monitor tailing the log (entries of about 190 bytes, like Part 07's) ==
     10 entries per checkpoint: fetch every partial bundle 13.68x the data, wait for full bundles 3.11x
     75 entries per checkpoint: fetch every partial bundle  2.70x the data, wait for full bundles 1.28x
    150 entries per checkpoint: fetch every partial bundle  1.85x the data, wait for full bundles 1.14x
    200 entries per checkpoint: fetch every partial bundle  1.62x the data, wait for full bundles 1.10x
    500 entries per checkpoint: fetch every partial bundle  1.25x the data, wait for full bundles 1.04x
   3000 entries per checkpoint: fetch every partial bundle  1.04x the data, wait for full bundles 1.01x
```

The spec's advice is in the second column. A client tailing a log that grows by more than 200 entries per checkpoint should avoid fetching partial bundles when it can. If it does skip them, it must still fetch the partial level 0 tile to verify each checkpoint, and check consistency between checkpoints; and it must fetch a bundle that stays partial too long, so entries are not delayed without limit. The partial tile costs 32 bytes per entry instead of about 192, which is where the remaining overhead comes from. The same effect has been reported for static CT logs: a log receiving 150 certificates in 10 seconds must serve a partial tile at every checkpoint, and monitors do fetch them.

For MTC the numbers are friendly. With a checkpoint every couple of seconds and thousands of certificates per checkpoint at web scale, most of the log arrives as full, immutable bundles, and the right edge is a small fraction of each update.

## What this part does not cover

The writer here keeps everything in memory and never crashes. A real log writes tiles to storage that can fail halfway, and must never publish a checkpoint whose tiles are not all durably written, or publish two checkpoints that disagree. The spec also allows pruning (refusing requests for very old tiles under a retention policy) and multiple mirrors of the same log. Crash safety and commit order are the subject of the next part.

## Try it

From the `experiments\root-of-trust` folder:

```text
python 09_tiles.py
python 09_tiles.py --write tiles_demo
python -m unittest test_09_tiles
```

The second command writes the whole 70,000-entry log into a folder `tiles_demo`. Open `tiles_demo\checkpoint` in a text editor, then look at `tiles_demo\tile\0`: 273 files of exactly 8,192 bytes, one partial directory `273.p` holding a file `112`, and so on.

Exercises:

1. Which tiles exist for a log of 65,536 entries? Of 65,537? Explain the difference using the rule for partial tiles.
2. How many tile levels does a log of 2<sup>40</sup> entries have, and at most how many tiles does an inclusion proof touch?
3. Serve the log with one full tile missing. Which clients fail, and how does the error message help an operator?
4. Change the monitor model so the client also fetches the partial bundle if it has waited more than 10 checkpoints. How does the overhead change at 10 entries per checkpoint?
5. Modify the writer to delete partial tiles once the full tile exists. Which test fails, and what does the spec say a client should do?
6. The `x` prefix keeps `001` and `x001` apart. Build two different indexes whose paths would collide without it.

## Reader checkpoint

<details>
<summary><strong>1.</strong> Why can full tiles be cached forever, but not the checkpoint?</summary>

A full tile holds 256 hashes of a part of the tree that is complete; the log is append-only, so those hashes never change. The checkpoint describes the current size and root, which change whenever the log grows.

</details>

<details>
<summary><strong>2.</strong> For a tree of 1,000 entries, which tiles exist?</summary>

1,000 = 3 · 256 + 232: three full level 0 tiles and a partial of width 232. Level 1 has ⌊1000 / 256⌋ = 3 hashes: a partial tile of width 3. Nothing at level 2.

</details>

<details>
<summary><strong>3.</strong> What does hash 21 of level 1 tile 482,253 represent?</summary>

The root of level 0 tile 482,253 · 256 + 21 = 123,456,789: the node at tree level 8, index 123,456,789, covering 256 entries.

</details>

<details>
<summary><strong>4.</strong> Why is checking the root from the right-edge tiles not enough?</summary>

The root depends on full lower tiles only through their roots stored higher up. A tampered level 0 tile in the middle of the log does not change the root computed from the right edge. Each full tile must be checked against its hash in the tile above.

</details>

<details>
<summary><strong>5.</strong> Why does a per-proof API defeat caches, while tiles do not?</summary>

Each proof request names a specific entry and tree size, so the answers differ across clients. Tiles are the same files for everyone, and their number grows with the log, not with the number of clients.

</details>

<details>
<summary><strong>6.</strong> When should a monitor skip partial bundles, and what must it still fetch?</summary>

When the log grows by more than about 200 entries per checkpoint. It must still fetch the partial level 0 tile to verify each checkpoint, verify consistency between checkpoints, and eventually fetch bundles that stay partial too long.

</details>

## What comes next

A tiled log is easy to read and easy to cache. Writing one correctly is harder: tiles, bundles and checkpoints must reach storage in an order that never lets a crash produce a checkpoint the files cannot support, or a history that changes. [Part 10](/root/10-a-log-that-never-forks/) builds a log that survives crashes without ever forking.

## References

- C2SP, [*tlog-tiles*](https://github.com/C2SP/C2SP/blob/main/tlog-tiles.md): paths, full and partial tiles, entry bundles, checkpoints, the 70,000-entry example, client guidance, pruning.
- transparency-dev, [*Tessera layout package*](https://pkg.go.dev/github.com/transparency-dev/tessera/api/layout): the path and node-to-tile examples used as test vectors here.
- Let's Encrypt, [*Boulder trees/tiles*](https://pkg.go.dev/github.com/letsencrypt/boulder/trees/tiles): tile storage for MTC logs, with entry, hash and public key layers.
- Chromium ct-policy, [*Optimizing RFC 6962 CT log data acquisition based on the static CT API format*](https://groups.google.com/a/chromium.org/g/ct-policy/c/LNvmpQUsKF8) and [*static-ct-api logs in Chrome*](https://groups.google.com/a/chromium.org/g/ct-policy/c/nuJOpwj06QA): cache hit rates of the old API and partial tiles in practice.
- C2SP, [*tlog-checkpoint*](https://c2sp.org/tlog-checkpoint) and [*signed-note*](https://c2sp.org/signed-note): the checkpoint format (Part 05).
