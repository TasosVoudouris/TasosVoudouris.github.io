"""Root of Trust, part 10: a log that never forks.

Part 09 wrote tiles in a perfect world. A real log runs on machines that crash,
storage that times out, operators who restore backups, and the occasional second
copy of the service started by mistake. One rule matters above all others:

    never sign two checkpoints that disagree about the past.

Witnesses (Part 05) will catch a log that breaks it, and for an MTC CA the only
remedy is to abandon the log (draft -07, §12.2.1). This script builds four commit
protocols for a tiled log, crashes each of them at every step, rolls its storage
back, starts a twin on the same storage, and counts what goes wrong:

  naive        sign, publish the checkpoint, then upload tiles
  tiles first  upload tiles, sign, publish (storage is the only record)
  lock first   sign, compare-and-swap a lock, then upload tiles, then publish
  sunlight     upload tiles, sign, compare-and-swap a lock, then publish
               (the order of the Sunlight CT log's design document)
  staged       write tiles to a staging area named by size and root, sign, lock,
               then copy them into place and publish; recovery rolls forward

Run:  python 10_never_fork.py        (needs: pip install cryptography)
"""
from __future__ import annotations

import importlib.util
import pathlib
import random
import struct
import sys
from dataclasses import dataclass, field

HERE = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("tiles09", HERE / "09_tiles.py")
m9 = importlib.util.module_from_spec(_spec)
sys.modules["tiles09"] = m9
_spec.loader.exec_module(m9)
mk, m5 = m9.mk, m9.m5

ORIGIN = "example.org/rot/10"
KEY = m5.key("part 10 log")
VERIFIER = m5.Verifier(ORIGIN, KEY.public_key(), 0x01)

PROTOCOLS = {
    "naive":       ["drain", "sign", "publish", "tiles", "ack"],
    "tiles first": ["drain", "tiles", "sign", "publish", "ack"],
    "lock first":  ["drain", "sign", "lock", "tiles", "publish", "ack"],
    "sunlight":    ["drain", "tiles", "sign", "lock", "publish", "ack"],
    "staged":      ["drain", "stage", "sign", "lock", "copy", "publish", "ack"],
}


class Crash(Exception):
    """The process dies: everything in memory is gone, storage and lock survive."""


class Stuck(Exception):
    """Recovery refuses to continue: safe, but an operator must act."""


# --------------------------------------------------------------------------- storage and lock

@dataclass
class Store:
    """Object storage: durable once a write returns. `immutable` models conditional
    writes (If-None-Match) that refuse to replace an existing full tile with different bytes."""
    files: dict = field(default_factory=dict)
    immutable: bool = False

    def put(self, path: str, data: bytes) -> None:
        full = ".p/" not in path and path != "checkpoint"
        if self.immutable and full and path in self.files and self.files[path] != data:
            raise Stuck(f"{path} exists with different content")
        self.files[path] = data


@dataclass
class Lock:
    """A tiny strongly consistent database with compare-and-swap, keyed by log."""
    value: bytes | None = None

    def cas(self, old: bytes | None, new: bytes) -> None:
        if self.value != old:
            raise Stuck("compare-and-swap failed: someone else moved the log")
        self.value = new


# --------------------------------------------------------------------------- what the world observes

@dataclass
class World:
    store: Store
    lock: Lock
    signed: list = field(default_factory=list)      # (size, root, entries) for every checkpoint ever signed
    visible: list = field(default_factory=list)     # the subset that reached storage, where witnesses read
    durable: list = field(default_factory=list)     # the subset that left memory at all: lock or storage
    acked: set = field(default_factory=set)         # submissions that got their SCT or certificate
    history: dict = field(default_factory=dict)     # root -> the entries behind it (for the referee only)

    def forks(self, which: list) -> int:
        """Pairs of checkpoints where the smaller is not a prefix of the larger."""
        n = 0
        for i, (s1, r1, e1) in enumerate(which):
            for s2, r2, e2 in which[i + 1 :]:
                a, b = (e1, e2) if s1 <= s2 else (e2, e1)
                n += b[: len(a)] != a
        return n


def tile_files(entries: tuple) -> dict:
    """Every tile and bundle of a tree, as Part 09 lays them out."""
    log = m9.TiledLog()
    log.append(list(entries))
    out = {}
    for level, index, width in m9.layout(len(entries)):
        out[m9.tile_path(level, index, width)] = b"".join(log.rows[level][index * 256 : index * 256 + width])
        if level == 0:
            out[m9.entries_path(index, width)] = b"".join(
                struct.pack(">H", len(e)) + e for e in entries[index * 256 : index * 256 + width])
    return out


def read_entries(store: Store, size: int) -> tuple:
    """Rebuild the first `size` entries from entry bundles; Stuck if any is missing."""
    out = []
    for level, index, width in m9.layout(size):
        if level:
            continue
        data = store.files.get(m9.entries_path(index, width))
        if data is None:
            raise Stuck(f"bundle {m9.entries_path(index, width)} missing for size {size}")
        off = 0
        while off < len(data):
            (ln,) = struct.unpack(">H", data[off : off + 2])
            out.append(data[off + 2 : off + 2 + ln])
            off += 2 + ln
    return tuple(out)


def longest_prefix_in_store(store: Store) -> tuple:
    """What a careless recovery does: take whatever entries it can find, in order."""
    out, index = [], 0
    while True:
        full = store.files.get(m9.entries_path(index))
        if full is not None:
            data, index = full, index + 1
        else:
            parts = [p for p in store.files if p.startswith(m9.entries_path(index) + ".p/")]
            if not parts:
                break
            data = store.files[max(parts, key=lambda p: int(p.rsplit("/", 1)[1]))]
            index = None
        off = 0
        while off < len(data):
            (ln,) = struct.unpack(">H", data[off : off + 2])
            out.append(data[off + 2 : off + 2 + ln])
            off += 2 + ln
        if index is None:
            break
    return tuple(out)


def staging_prefix(size: int, root: bytes) -> str:
    """Private, never served, and unique per tree: two different trees can never write the same staged path."""
    return f"staging/{size}/{root.hex()}/"


def checkpoint_of(note: bytes) -> tuple[int, bytes]:
    text, _ = m5.open_note(note.decode(), [VERIFIER])
    _, size, root = m5.parse_checkpoint(text)
    return size, root


# --------------------------------------------------------------------------- the sequencer

@dataclass
class Sequencer:
    world: World
    protocol: str
    entries: tuple = ()
    lock_seen: bytes | None = None
    pool: list = field(default_factory=list)
    state: dict = field(default_factory=dict)
    crash_at: tuple | None = None                   # (round, step) to die at
    round: int = 0

    def recover(self) -> None:
        st, lk = self.world.store, self.world.lock
        cp = st.files.get("checkpoint")
        if self.protocol == "naive":
            self.entries = longest_prefix_in_store(st)       # trusts whatever data it finds
            return
        if self.protocol == "tiles first":
            if cp is None:
                self.entries = ()
                return
            size, root = checkpoint_of(cp)
            self.entries = read_entries(st, size)
            if mk.mth(list(self.entries)) != root:
                raise Stuck("tiles do not match the checkpoint")
            return
        # lock first, sunlight: the lock is the source of truth
        if lk.value is None:
            if cp is not None:
                raise Stuck("storage has a checkpoint but the lock has none: wrong lock or a reused key")
            self.entries, self.lock_seen = (), None
            return
        size, root = checkpoint_of(lk.value)
        if self.protocol == "staged":
            staged = staging_prefix(size, root)
            if any(p.startswith(staged) for p in st.files):
                for p in [p for p in st.files if p.startswith(staged)]:
                    st.put(p[len(staged):], st.files[p])                     # roll forward
                st.put("checkpoint", lk.value)
                cp = lk.value
        if cp is None and size:
            raise Stuck("the lock has a checkpoint but storage is empty: wrong bucket or lost storage")
        if cp is not None:
            s2, r2 = checkpoint_of(cp)
            if s2 > size:
                raise Stuck("storage is ahead of the lock: the lock was rolled back")
        self.entries = read_entries(st, size)
        if mk.mth(list(self.entries)) != root:
            raise Stuck("tiles do not match the locked checkpoint")
        self.lock_seen = lk.value

    def step(self, name: str, state: dict) -> None:
        if self.crash_at == (self.round, name):
            raise Crash(f"crash before '{name}' in round {self.round}")
        w = self.world
        if name == "drain":
            state["batch"], self.pool = self.pool, []
            state["new"] = self.entries + tuple(state["batch"])
        elif name == "sign":
            new = state["new"]
            root = mk.mth(list(new))
            state["note"] = m5.sign_note(m5.checkpoint_body(ORIGIN, len(new), root), ORIGIN, KEY).encode()
            w.signed.append((len(new), root, new))
        elif name == "tiles":
            for p, data in tile_files(state["new"]).items():
                w.store.put(p, data)
        elif name == "stage":
            new = state["new"]
            prefix = staging_prefix(len(new), mk.mth(list(new)))
            for p, data in tile_files(new).items():
                w.store.put(prefix + p, data)
        elif name == "copy":
            new = state["new"]
            prefix = staging_prefix(len(new), mk.mth(list(new)))
            for p in [p for p in w.store.files if p.startswith(prefix)]:
                w.store.put(p[len(prefix):], w.store.files[p])
        elif name == "lock":
            w.lock.cas(self.lock_seen, state["note"])
            self.lock_seen = state["note"]
            new = state["new"]
            w.durable.append((len(new), mk.mth(list(new)), new))
        elif name == "publish":
            w.store.put("checkpoint", state["note"])
            new = state["new"]
            w.visible.append((len(new), mk.mth(list(new)), new))
            if "lock" not in PROTOCOLS[self.protocol]:
                w.durable.append(w.visible[-1])
        elif name == "ack":
            w.acked |= set(state["batch"])
            self.entries = state["new"]

    def sequence(self) -> None:
        self.state = {}
        for name in PROTOCOLS[self.protocol]:
            self.step(name, self.state)
        self.round += 1


# --------------------------------------------------------------------------- experiments

def run(protocol: str, scenario: str, seed: int, rounds: int = 6, immutable: bool = False) -> dict:
    """One log's life. Returns what the referee saw."""
    rnd = random.Random(seed)
    world = World(Store(immutable=immutable), Lock())
    counter = [0]

    def submit(seq: Sequencer, k: int) -> None:
        for _ in range(k):
            counter[0] += 1
            seq.pool.append(f"cert {counter[0]} seed {seed}".encode())

    seq = Sequencer(world, protocol)
    seq.recover()
    outcome = "ok"
    crash_round = rnd.randrange(1, rounds - 1)
    if scenario.startswith("crash"):
        seq.crash_at = (crash_round, scenario.split(":", 1)[1])
    backup = None
    try:
        r = 0
        while r < rounds:
            submit(seq, rnd.randint(30, 300))
            if scenario == "rollback" and r == 1:
                backup = Store(dict(world.store.files), immutable)            # a backup is taken
            try:
                seq.sequence()
            except Crash:
                # memory is gone; the clients whose submissions were in flight never got an answer,
                # so they retry, in whatever order their retries happen to arrive
                retry = [e for e in seq.state.get("batch", []) + seq.pool if e not in world.acked]
                rnd.shuffle(retry)
                seq = Sequencer(world, protocol, round=seq.round + 1)
                seq.recover()
                seq.pool = retry
            if scenario == "rollback" and r == 3:
                world.store = backup                                           # storage restored from backup
                seq = Sequencer(world, protocol, round=seq.round)
                seq.recover()
            if scenario == "twin" and r == 2:
                twin = Sequencer(world, protocol, round=seq.round)             # a second instance, same storage
                twin.recover()
                submit(twin, rnd.randint(30, 300))
                twin.sequence()
            r += 1
    except Stuck as e:
        outcome = f"stuck: {e}"
    final = world.durable[-1][2] if world.durable else ()      # the log as its latest durable checkpoint says
    lost = sum(1 for a in world.acked if a not in set(final))
    return {"outcome": outcome, "visible_forks": world.forks(world.visible), "signed_forks": world.forks(world.durable),
            "lost": lost, "world": world}


SCENARIOS = ["crash:sign", "crash:tiles", "crash:stage", "crash:lock", "crash:copy", "crash:publish", "crash:ack",
             "rollback", "twin", "reused key"]


def summarize(protocol: str, scenario: str, trials: int = 20, immutable: bool = False) -> dict:
    if scenario.startswith("crash:") and scenario[6:] not in PROTOCOLS[protocol]:
        return {}
    if scenario == "reused key":
        return reused_key(protocol)
    agg = {"forked": 0, "signed_forked": 0, "stuck": 0, "lost": 0, "trials": trials}
    for seed in range(trials):
        r = run(protocol, scenario, seed, immutable=immutable)
        agg["forked"] += r["visible_forks"] > 0
        agg["signed_forked"] += r["signed_forks"] > 0
        agg["stuck"] += r["outcome"].startswith("stuck")
        agg["lost"] += r["lost"] > 0
    return agg


def reused_key(protocol: str) -> dict:
    """An operator starts a fresh log with the same key and an empty bucket."""
    world = World(Store(), Lock())
    seq = Sequencer(world, protocol)
    seq.recover()
    seq.pool = [b"first life %d" % i for i in range(100)]
    seq.sequence()
    world.store = Store()                                   # new, empty storage; same key and lock
    out = {"forked": 0, "signed_forked": 0, "stuck": 0, "lost": 0, "trials": 1}
    try:
        seq2 = Sequencer(world, protocol)
        seq2.recover()
        seq2.pool = [b"second life %d" % i for i in range(50)]
        seq2.sequence()
    except Stuck:
        out["stuck"] = 1
    out["forked"] = int(world.forks(world.visible) > 0)
    out["signed_forked"] = int(world.forks(world.durable) > 0)
    return out


def cell(a: dict) -> str:
    if not a:
        return "-"
    bits = []
    if a["forked"]:
        bits.append(f"FORK {a['forked']}")
    elif a["signed_forked"]:
        bits.append(f"hidden fork {a['signed_forked']}")
    if a["stuck"]:
        bits.append(f"stuck {a['stuck']}")
    if a["lost"]:
        bits.append(f"lost {a['lost']}")
    return " ".join(bits) or "safe"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("== one crash, told step by step: the naive protocol ==")
    r = run("naive", "crash:tiles", seed=3)
    w = r["world"]
    for size, root, _ in w.visible:
        print(f"  witnesses saw checkpoint size {size:>5}  root {root.hex()[:16]}")
    print(f"  -> {r['visible_forks']} pair(s) of published checkpoints disagree about the past")
    a = next((x, y) for i, x in enumerate(w.visible) for y in w.visible[i + 1 :]
             if y[2][: len(x[2])] != x[2] if x[0] <= y[0])
    first = next(i for i, (p, q) in enumerate(zip(a[0][2], a[1][2])) if p != q)
    print(f"  checkpoints {a[0][0]} and {a[1][0]} first differ at entry {first}:"
          f" {a[0][2][first].decode()!r} vs {a[1][2][first].decode()!r}")

    print("\n== every protocol, every failure (runs out of 20, reused key: 1 run; faults injected before the named step) ==")
    head = f"  {'':15s}" + "".join(f"{p:>25s}" for p in PROTOCOLS)
    print(head)
    for sc in SCENARIOS:
        print(f"  {sc:15s}" + "".join(f"{cell(summarize(p, sc)):>25s}" for p in PROTOCOLS))

    print("\n== the same, with storage that refuses to overwrite a full tile (conditional writes) ==")
    print(head)
    for sc in ("crash:lock", "crash:copy", "crash:publish", "twin"):
        print(f"  {sc:15s}" + "".join(f"{cell(summarize(p, sc, immutable=True)):>25s}" for p in PROTOCOLS))

    print("\n== what a witness does with a fork (Part 05): tiles first, storage restored from a backup ==")
    r = run("tiles first", "rollback", seed=1, rounds=10)
    w = r["world"]
    last = None
    for size, root, entries in w.visible:
        if last is None or (size >= last[0] and entries[: last[0]] == last[2]):
            print(f"  checkpoint {size:>5}: consistent with what it cosigned before, cosigns")
            last = (size, root, entries)
        elif size < last[0]:
            print(f"  checkpoint {size:>5}: older than the {last[0]} it already cosigned, refuses (the backup)")
        else:
            print(f"  checkpoint {size:>5}: no consistency proof from {last[0]} can exist, refuses: the log has forked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
