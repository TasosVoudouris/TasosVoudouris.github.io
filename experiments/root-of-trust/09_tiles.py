"""Root of Trust, part 09: tiled logs.

Parts 04 to 08 computed every proof from the full list of entries. A real log
has millions of entries and thousands of clients, and it cannot run a database
query for each proof. The C2SP tlog-tiles spec (c2sp.org/tlog-tiles) serves a
log as static files instead:

  * <prefix>/checkpoint                  the signed tree head (Part 05's checkpoint)
  * <prefix>/tile/<L>/<N>[.p/<W>]        256 hashes of one tree level, 8,192 bytes
  * <prefix>/tile/entries/<N>[.p/<W>]    the 256 entries behind a level 0 tile

Full tiles never change, so any cache can keep them forever. Clients fetch the
few tiles they need and compute every proof themselves.

This script writes a tiled log, checks the spec's own examples, builds a client
that verifies checkpoints, inclusion and consistency proofs and Parts 07 and 08's
subtree proofs from tiles alone, and measures caching and monitor bandwidth.

Run:  python 09_tiles.py                (needs: pip install cryptography)
      python 09_tiles.py --write DIR    (also writes the log's files into DIR to browse)
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import random
import struct
import sys
from dataclasses import dataclass, field

HERE = pathlib.Path(__file__).parent


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


mk = _load("merkle04", "04_merkle.py")          # leaf_hash, node_hash, mth, path, proof, verifiers
m5 = _load("witness05", "05_witness.py")        # signed notes and checkpoints
m8 = _load("landmarks08", "08_landmarks.py")    # subtree proofs (and, through it, Part 07)
m7 = m8.m7

HEIGHT = 8
WIDTH = 1 << HEIGHT                             # 256 hashes per full tile
HASH = 32


# --------------------------------------------------------------------------- paths

def n_path(n: int) -> str:
    """Zero-padded 3-digit path elements; every element but the last starts with x."""
    groups = []
    while True:
        groups.append(n % 1000)
        n //= 1000
        if n == 0:
            break
    groups.reverse()
    return "/".join([f"x{g:03d}" for g in groups[:-1]] + [f"{groups[-1]:03d}"])


def tile_path(level: int, index: int, width: int = WIDTH) -> str:
    assert 0 <= level <= 63 and 1 <= width <= WIDTH
    suffix = "" if width == WIDTH else f".p/{width}"
    return f"tile/{level}/{n_path(index)}{suffix}"


def entries_path(index: int, width: int = WIDTH) -> str:
    suffix = "" if width == WIDTH else f".p/{width}"
    return f"tile/entries/{n_path(index)}{suffix}"


def parse_tile_path(p: str) -> tuple[str, int, int]:
    """Returns (level or 'entries', index, width), rejecting anything the spec forbids."""
    parts = p.split("/")
    if parts[0] != "tile" or len(parts) < 3:
        raise ValueError(p)
    level = parts[1]
    rest = parts[2:]
    width = WIDTH
    if len(rest) >= 2 and rest[-2].endswith(".p"):
        w = rest[-1]
        if not w.isdigit() or w != str(int(w)) or not 1 <= int(w) <= 255:
            raise ValueError(f"bad width in {p}")
        width = int(w)
        rest = rest[:-2] + [rest[-2][:-2]]
    if level != "entries" and (not level.isdigit() or level != str(int(level)) or int(level) > 63):
        raise ValueError(f"bad level in {p}")
    *xs, last = rest
    if any(len(x) != 4 or x[0] != "x" or not x[1:].isdigit() for x in xs) or len(last) != 3 or not last.isdigit():
        raise ValueError(f"bad index in {p}")
    index = 0
    for x in xs:
        index = index * 1000 + int(x[1:])
    index = index * 1000 + int(last)
    if xs and int(xs[0][1:]) == 0:
        raise ValueError(f"leading zero group in {p}")
    return level, index, width


def node_to_tile(level: int, index: int) -> tuple[int, int, int, int]:
    """Tree node (level, index) -> (tile level, tile index, level inside the tile, index inside it)."""
    tl, r = divmod(level, HEIGHT)
    return tl, (index << r) // WIDTH, r, ((index << r) % WIDTH) >> r


def layout(size: int) -> list[tuple[int, int, int]]:
    """Every tile that exists for a tree of `size` entries: (level, index, width)."""
    out = []
    level = 0
    while size >> (HEIGHT * level):
        row = size >> (HEIGHT * level)                  # hashes at the bottom of this tile level
        out += [(level, i, WIDTH) for i in range(row // WIDTH)]
        if row % WIDTH:
            out.append((level, row // WIDTH, row % WIDTH))
        level += 1
    return out


# --------------------------------------------------------------------------- hashing with a node oracle

def mth_nodes(hs: list[bytes]) -> bytes:
    """MTH over values that are already node hashes (a power-of-two count here)."""
    while len(hs) > 1:
        hs = [mk.node_hash(hs[i], hs[i + 1]) for i in range(0, len(hs), 2)]
    return hs[0]


class Hasher:
    """Computes any MTH(D[a:b]) and every Part 04/07/08 proof from complete tree nodes.
    Subclasses supply node(level, index), the hash of leaves [index * 2^level, (index + 1) * 2^level)."""

    def node(self, level: int, index: int) -> bytes:
        raise NotImplementedError

    def range_hash(self, a: int, b: int) -> bytes:
        n = b - a
        if n == 0:
            return hashlib.sha256(b"").digest()
        if n & (n - 1) == 0 and a % n == 0:
            return self.node(n.bit_length() - 1, a // n)          # an aligned node: one lookup
        k = 1 << ((n - 1).bit_length() - 1)                       # MTH's own split
        return mk.node_hash(self.range_hash(a, a + k), self.range_hash(a + k, b))

    def inclusion(self, m: int, a: int, b: int) -> list[bytes]:
        """Part 04's path(m, D[a:b]), for the leaf at absolute index m."""
        n = b - a
        if n <= 1:
            return []
        k = 1 << ((n - 1).bit_length() - 1)
        if m - a < k:
            return self.inclusion(m, a, a + k) + [self.range_hash(a + k, b)]
        return self.inclusion(m, a + k, b) + [self.range_hash(a, a + k)]

    def consistency(self, m: int, n: int) -> list[bytes]:
        """Part 04's proof(m, D[:n])."""
        return [] if m in (0, n) else self._sub(0, m, 0, n, True)

    def _sub(self, start: int, end: int, a: int, b: int, flag: bool) -> list[bytes]:
        """§4.4.1 SUBTREE_SUBPROOF over D[a:b] (absolute indices); also gives RFC 9162 consistency."""
        if start == end:
            return []
        if start == a and end == b:
            return [] if flag else [self.range_hash(a, b)]
        k = 1 << ((b - a - 1).bit_length() - 1)
        if end <= a + k:
            return self._sub(start, end, a, a + k, flag) + [self.range_hash(a + k, b)]
        if a + k <= start:
            return self._sub(start, end, a + k, b, flag) + [self.range_hash(a, a + k)]
        return self._sub(a + k, end, a + k, b, False) + [self.range_hash(a, a + k)]

    def subtree_proof(self, start: int, end: int, n: int) -> list[bytes]:
        return self._sub(start, end, 0, n, True)


# --------------------------------------------------------------------------- the log (writer)

@dataclass
class TiledLog(Hasher):
    origin: str = "example.org/rot/09"
    sk: object = None
    entries: list = field(default_factory=list)
    rows: list = field(default_factory=lambda: [[]])       # rows[L]: the hashes at tree level 8L
    files: dict = field(default_factory=dict)              # path -> bytes: what a static host serves
    published: int = 0
    stats: dict = field(default_factory=lambda: {"writes": 0, "bytes": 0, "partial_writes": 0, "partial_bytes": 0})

    def __post_init__(self):
        self.sk = self.sk or m5.key("part 09 log")

    def node(self, level: int, index: int) -> bytes:
        tl, r = divmod(level, HEIGHT)
        return mth_nodes(self.rows[tl][index << r : (index + 1) << r])

    def append(self, batch: list[bytes]) -> None:
        self.entries += batch
        self.rows[0] += [mk.leaf_hash(e) for e in batch]
        level = 0
        while len(self.rows[level]) >= WIDTH:
            if level + 1 == len(self.rows):
                self.rows.append([])
            above = self.rows[level + 1]
            while (len(above) + 1) * WIDTH <= len(self.rows[level]):     # a tile just filled up
                i = len(above)
                above.append(mth_nodes(self.rows[level][i * WIDTH : (i + 1) * WIDTH]))
            level += 1

    def _put(self, path: str, data: bytes, partial: bool) -> None:
        old = self.files.get(path)
        if old is not None:
            assert old == data, f"{path} would change: full tiles are immutable"
            return
        self.files[path] = data
        self.stats["writes"] += 1
        self.stats["bytes"] += len(data)
        if partial:
            self.stats["partial_writes"] += 1
            self.stats["partial_bytes"] += len(data)

    def publish(self) -> str:
        """Write every new full tile and bundle, the partial ones for this size, and a checkpoint."""
        s = len(self.entries)
        for level, index, width in layout(s):
            if width == WIDTH and tile_path(level, index) in self.files:
                continue                                                  # written once, done
            row = self.rows[level]
            self._put(tile_path(level, index, width),
                      b"".join(row[index * WIDTH : index * WIDTH + width]), width < WIDTH)
            if level == 0:
                bundle = b"".join(struct.pack(">H", len(e)) + e
                                  for e in self.entries[index * WIDTH : index * WIDTH + width])
                self._put(entries_path(index, width), bundle, width < WIDTH)
        note = m5.sign_note(m5.checkpoint_body(self.origin, s, self.range_hash(0, s)), self.origin, self.sk)
        self.files["checkpoint"] = note.encode()                          # the only mutable file
        self.published = s
        return note

    @property
    def verifier(self):
        return m5.Verifier(self.origin, self.sk.public_key(), 0x01)


# --------------------------------------------------------------------------- the client (reader)

class FetchCounter:
    """A static host plus a shared cache in front of it, counting what crosses each."""

    def __init__(self, files: dict):
        self.files = files
        self.cache: dict = {}
        self.requests = self.misses = self.bytes = 0

    def get(self, path: str) -> bytes:
        self.requests += 1
        if path in self.cache and path != "checkpoint":
            return self.cache[path]
        self.misses += 1
        data = self.files[path]
        self.bytes += len(data)
        if path != "checkpoint":
            self.cache[path] = data
        return data


class TileClient(Hasher):
    def __init__(self, host: FetchCounter, verifier):
        self.host, self.verifier = host, verifier
        self.size = 0
        self.root = b""
        self.tiles_used: set = set()
        self.authenticated: set = set()
        self._trusting = False
        self.local: dict = {}                       # the client's own cache of tiles

    def _get(self, path: str) -> bytes:
        if path not in self.local:
            self.local[path] = self.host.get(path)
        return self.local[path]

    def update(self) -> tuple[int, bytes]:
        """Verify the checkpoint, then authenticate the right-edge tiles: together they must rebuild the root."""
        text, _ = m5.open_note(self.host.get("checkpoint").decode(), [self.verifier])
        _, self.size, self.root = m5.parse_checkpoint(text)
        self.authenticated = set()
        self.tiles_used = set()
        self._trusting = True                       # fetch without checks, then judge them all at once
        ok = self.range_hash(0, self.size) == self.root
        self._trusting = False
        if not ok:
            raise ValueError("the right-edge tiles do not rebuild the checkpoint's root")
        self.authenticated |= self.tiles_used
        return self.size, self.root

    def tile(self, level: int, index: int) -> list[bytes]:
        row = self.size >> (HEIGHT * level)
        width = WIDTH if (index + 1) * WIDTH <= row else row % WIDTH
        p = tile_path(level, index, width)
        self.tiles_used.add(p)
        data = self._get(p)
        if len(data) != width * HASH:
            raise ValueError(f"{p}: {len(data)} bytes, expected {width * HASH}")
        hs = [data[i : i + HASH] for i in range(0, len(data), HASH)]
        if p not in self.authenticated and not self._trusting:
            # a full tile is one hash in the tile above it: check it there, recursively
            if width != WIDTH:
                raise ValueError(f"{p}: a partial tile that is not on the right edge")
            parent = self.tile(level + 1, index // WIDTH)
            if mth_nodes(hs) != parent[index % WIDTH]:
                raise ValueError(f"{p} does not match its hash in the tile above")
            self.authenticated.add(p)
        return hs

    def node(self, level: int, index: int) -> bytes:
        tl, t, r, j = node_to_tile(level, index)
        hs = self.tile(tl, t)
        return mth_nodes(hs[j << r : (j + 1) << r])

    def entry(self, index: int) -> bytes:
        row = self.size
        b = index // WIDTH
        width = WIDTH if (b + 1) * WIDTH <= row else row % WIDTH
        data = self._get(entries_path(b, width))
        out, off = [], 0
        while off < len(data):
            (ln,) = struct.unpack(">H", data[off : off + 2])
            if off + 2 + ln > len(data):
                raise ValueError("bad bundle")
            out.append(data[off + 2 : off + 2 + ln])
            off += 2 + ln
        if len(out) != width:
            raise ValueError("bundle size does not match")
        e = out[index % WIDTH]
        if mk.leaf_hash(e) != self.node(0, index):          # the bundle must match the level 0 tile
            raise ValueError("entry does not hash to its leaf")
        return e


# --------------------------------------------------------------------------- measurements

def monitor_cost(per_checkpoint: int, checkpoints: int = 2000, entry_bytes: int = 190,
                 skip_partials: bool = False) -> float:
    """Bytes a tailing monitor downloads per byte of new entries.

    Every checkpoint adds `per_checkpoint` entries. Fetching every partial bundle refetches
    the same entries until the bundle fills; the spec's optimisation waits for full bundles
    (fetching only the small partial level 0 tile to verify each checkpoint)."""
    size = got = 0
    fetched = 0
    for _ in range(checkpoints):
        size += per_checkpoint
        full = size // WIDTH
        while got < full:                                  # newly completed bundles: fetch once
            fetched += WIDTH * (entry_bytes + 2)
            got += 1
        w = size % WIDTH
        if w:
            fetched += w * HASH if skip_partials else w * (entry_bytes + 2)
    return fetched / (size * (entry_bytes + 2))


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    write_dir = None
    if "--write" in sys.argv:
        write_dir = pathlib.Path(sys.argv[sys.argv.index("--write") + 1])

    print("== paths, checked against the spec and Tessera ==")
    for args, want in (((0, 1234067, 8), "tile/0/x001/x234/067.p/8"), ((1, 0), "tile/1/000"), ((2, 999), "tile/2/999"),
                       ((0, 1000), "tile/0/x001/000")):
        got = tile_path(*args)
        print(f"  tile_path{args}: {got}  {'ok' if got == want else 'MISMATCH ' + want}")
    print(f"  entries_path(1234067, 8): {entries_path(1234067, 8)}")
    print(f"  parse 'tile/0/x001/x234/067.p/8' -> {parse_tile_path('tile/0/x001/x234/067.p/8')}")
    print(f"  node (level 8, index 123456789) lives in tile (level, index, node level, node index) = {node_to_tile(8, 123456789)}")

    print("\n== which tiles exist for a tree of 70,000 entries (the spec's example) ==")
    lay = layout(70000)
    for level in range(3):
        full = sum(1 for l, _, w in lay if l == level and w == WIDTH)
        part = [w for l, _, w in lay if l == level and w < WIDTH]
        print(f"  level {level}: {full:>3} full, partial of width {part[0] if part else '-'}")
    print("  (spec: 273 full level 0 tiles and a partial of 112; 1 full level 1 tile and a partial of 17;"
          " a level 2 partial of 1)")
    covers = [(i * WIDTH ** (l + 1), (i + 1) * WIDTH ** (l + 1)) for l, i, w in lay if w == WIDTH]
    print(f"  every full tile covers a valid MTC subtree (Part 07): {all(m7.valid_subtree(a, b) for a, b in covers)}")

    print("\n== writing a log of 70,000 entries, one checkpoint per batch ==")
    rnd = random.Random(9)
    log = TiledLog()
    batches = 0
    while len(log.entries) < 70000:
        k = min(rnd.randint(50, 400), 70000 - len(log.entries))
        log.append([f"entry {len(log.entries) + i}: {rnd.getrandbits(64):016x}".encode() for i in range(k)])
        log.publish()
        batches += 1
    root = mk.mth(log.entries)
    print(f"  {batches} checkpoints published; root from the tiles equals Part 04's mth over all entries:"
          f" {log.range_hash(0, 70000) == root}")
    full_files = sum(1 for p in log.files if p != "checkpoint" and ".p/" not in p)
    st = log.stats
    print(f"  files: {full_files} full tiles and bundles (written once, never changed),"
          f" {st['partial_writes']} partial ones over time")
    print(f"  bytes written: {st['bytes']:,}, of which partial files {st['partial_bytes']:,}"
          f" ({st['partial_bytes'] / st['bytes']:.0%})")

    print("\n== a client that has only the tiles ==")
    host = FetchCounter(log.files)
    c = TileClient(host, log.verifier)
    size, croot = c.update()
    print(f"  checkpoint verified: size {size}, root matches the tiles: {c.range_hash(0, size) == croot}")
    tiles_for_root = len(c.tiles_used)
    print(f"  recomputing the root used {tiles_for_root} tiles")
    for idx in (5, 31337, 69999):
        c.tiles_used = set()
        before = host.misses
        p = c.inclusion(idx, 0, size)
        ok = p == mk.path(idx, log.entries) and mk.verify_inclusion(mk.leaf_hash(c.entry(idx)), idx, size, p, croot)
        print(f"  inclusion of entry {idx:>5}: {len(p)} hashes from {len(c.tiles_used)} tiles"
              f" ({host.misses - before} fetched), equals Part 04 and verifies: {ok}")
    old = 41_000
    cp = c.consistency(old, size)
    print(f"  consistency {old} -> {size}: {len(cp)} hashes, equals Part 04: {cp == mk.proof(old, log.entries)},"
          f" verifies: {mk.verify_consistency(old, size, mk.mth(log.entries[:old]), croot, cp)}")

    print("\n== Parts 07 and 08 from tiles: MTC proofs need no extra server ==")
    for s in ((65536, 69632), (69632, 69888), (40960, 41984)):
        p = c.subtree_proof(*s, size)
        ref = m8.subtree_proof(*s, log.entries)
        ok = m8.verify_subtree_consistency(size, *s, p, mk.mth(log.entries[s[0]:s[1]]), croot)
        print(f"  subtree consistency [{s[0]}, {s[1]}) in {size}: {len(p)} hashes, equals Part 08: {p == ref}, verifies: {ok}")
    (a, b), (cc, d) = m7.covering_subtrees(69_000, 70_000)
    p = c.inclusion(69_500, cc, d)
    print(f"  batch [69000, 70000) covered by [{a}, {b}) and [{cc}, {d}); subtree inclusion proof of entry 69500:"
          f" {len(p)} hashes, equals Part 07: {p == m8.subtree_inclusion(cc, d, 69_500, log.entries)}")

    print("\n== a tampered host ==")
    bad = dict(log.files)
    t = tile_path(0, 7)
    bad[t] = bad[t][:32] + bytes(32) + bad[t][64:]
    cb = TileClient(FetchCounter(bad), log.verifier)
    cb.update()
    try:
        cb.inclusion(7 * WIDTH + 1, 0, size)
        print(f"  one hash in {t} zeroed -> accepted")
    except ValueError as e:
        print(f"  one hash in {t} zeroed -> rejected: {e}")
    bad = dict(log.files)
    bp = entries_path(3)
    bad[bp] = bad[bp][:5] + bytes([bad[bp][5] ^ 1]) + bad[bp][6:]
    cb = TileClient(FetchCounter(bad), log.verifier)
    cb.update()
    try:
        cb.entry(3 * WIDTH)
        print("  flipped byte in a bundle -> accepted")
    except ValueError as e:
        print(f"  flipped byte in {bp} -> rejected: {e}")

    print("\n== caching: 5,000 clients, each verifying one random entry ==")
    host = FetchCounter(log.files)
    total_tiles = set()
    for _ in range(5000):
        cl = TileClient(host, log.verifier)
        cl.update()
        cl.inclusion(rnd.randrange(size), 0, size)
        total_tiles |= cl.tiles_used
    reqs = host.requests - 5000
    misses = host.misses - 5000
    print(f"  {reqs:,} tile requests ({reqs / 5000:.1f} per client), {len(total_tiles)} distinct tiles,"
          f" {misses} reached the host: shared cache hit rate {1 - misses / reqs:.2%}")
    print(f"  a per-proof API (RFC 6962 get-proof-by-hash) would see up to 5,000 distinct queries:"
          f" each one a cache miss and a database lookup")

    print("\n== a monitor tailing the log (entries of about 190 bytes, like Part 07's) ==")
    for per in (10, 75, 150, 200, 500, 3000):
        a1 = monitor_cost(per)
        a2 = monitor_cost(per, skip_partials=True)
        print(f"  {per:>5} entries per checkpoint: fetch every partial bundle {a1:5.2f}x the data,"
              f" wait for full bundles {a2:4.2f}x")

    if write_dir:
        for p, data in log.files.items():
            f = write_dir / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
        print(f"\nwrote {len(log.files)} files into {write_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
