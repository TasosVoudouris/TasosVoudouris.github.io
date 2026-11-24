"""Root of Trust, part 03: when authorities lie.

Builds on Part 00's toy PKI and adds Certificate Transparency to it:

  * logs that sign SCTs (promises to publish a certificate within a deadline);
  * a browser that checks the chain AND a CT policy (enough valid SCTs, from
    at least two distinct log operators, like Chrome and Firefox);
  * a monitor that reads the logs and alerts a domain owner about any
    certificate for their domain with a key they do not recognise.

Then it replays the attack patterns of real incidents and prints one verdict per
scenario. A teaching model, NOT RFC 6962: real SCTs sign the precertificate in a
TLS structure (see Part 02), and real logs are Merkle trees (Part 04). What it
keeps is the logic: who must lie, to whom, and who finds out.

Run:  python 03_ct_toy.py      (needs: pip install cryptography)
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import sys
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

HERE = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("toy00", HERE / "00_toy_chain.py")
toy = importlib.util.module_from_spec(_spec)
sys.modules["toy00"] = toy
_spec.loader.exec_module(toy)

Cert, canonical, issue, raw, verify_chain = toy.Cert, toy.canonical, toy.issue, toy.raw, toy.verify_chain
NOW, DAY = toy.NOW, toy.DAY
HOUR = 3600
MMD = 24 * HOUR  # maximum merge delay: a log promises to publish within this time (RFC 6962 §3)


def key(label: str) -> Ed25519PrivateKey:
    """Deterministic keys, so every run prints the same thing."""
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(f"root-of-trust part 03: {label}".encode()).digest())


def cert_hash(cert: Cert) -> str:
    return hashlib.sha256(canonical(cert.body) + cert.signature).hexdigest()


# --------------------------------------------------------------------------- logs

@dataclass
class SCT:
    log: str
    timestamp: int
    signature: bytes

    def signed_bytes(self, cert: Cert) -> bytes:
        return canonical({"v": 1, "log": self.log, "ts": self.timestamp, "cert": cert_hash(cert)})


@dataclass
class Log:
    name: str
    operator: str
    sk: Ed25519PrivateKey
    honest: bool = True
    pending: list = field(default_factory=list)    # (deadline, cert): promised, not yet public
    published: list = field(default_factory=list)  # what anyone who reads the log sees

    def submit(self, cert: Cert, at: int) -> SCT:
        """Sign a promise to publish `cert` within MMD. A dishonest log signs and forgets."""
        sct = SCT(self.name, at, b"")
        sct.signature = self.sk.sign(sct.signed_bytes(cert))
        if self.honest:
            self.pending.append((at + MMD, cert))
        return sct

    def tick(self, now: int) -> None:
        """Publish everything whose deadline has passed (an honest log does it sooner or on time)."""
        due = [c for d, c in self.pending if d <= now]
        self.pending = [(d, c) for d, c in self.pending if d > now]
        self.published += due


# --------------------------------------------------------------------------- the browser

@dataclass
class Browser:
    roots: dict                     # trust store: name -> public key
    logs: dict                      # known logs: name -> (operator, public key)
    enforce_ct: bool = True
    min_scts: int = 2               # Chrome and Firefox: 2 for certificates of 180 days or less
    distrust_after: dict = field(default_factory=dict)  # issuer name -> cutoff time, by SCT timestamp

    def check(self, chain: list[Cert], scts: list[SCT], name: str, now: int = NOW) -> tuple[bool, str]:
        ok, why = verify_chain(chain, self.roots, name)
        if not ok:
            return False, why
        if not self.enforce_ct:
            return True, "chain ok (no CT check)"
        good = []
        for s in scts:
            if s.log not in self.logs:
                continue  # an SCT from a log the browser does not know counts for nothing
            operator, pub = self.logs[s.log]
            try:
                pub.verify(s.signature, s.signed_bytes(chain[0]))
            except InvalidSignature:
                return False, f"SCT claiming to be from {s.log} has a bad signature"
            good.append((s, operator))
        if len({s.log for s, _ in good}) < self.min_scts:
            return False, f"only {len(good)} valid SCT(s), policy needs {self.min_scts}"
        if len({op for _, op in good}) < 2:
            return False, "SCTs all come from one log operator"
        issuer = chain[0].body["issuer"]
        if issuer in self.distrust_after:
            earliest = min(s.timestamp for s, _ in good)
            if earliest > self.distrust_after[issuer]:
                return False, f"{issuer} is distrusted for certificates logged after the cutoff"
        return True, "chain ok, CT policy met"


# --------------------------------------------------------------------------- the monitor

@dataclass
class Monitor:
    """A domain owner's watcher: reads every log, flags certificates it did not ask for."""
    domain: str
    known_keys: set

    def scan(self, logs: list[Log]) -> list[str]:
        alerts = []
        for log in logs:
            for c in log.published:
                if c.subject == self.domain and c.body["key"] not in self.known_keys:
                    alerts.append(f"{log.name}: certificate for {self.domain} from {c.body['issuer']!r} with an unknown key")
        return sorted(set(alerts))


# --------------------------------------------------------------------------- the world

def world():
    root_sk, inter_sk = key("root"), key("intermediate")
    roots = {"Toy Root CA": root_sk.public_key()}
    inter = issue("Toy Root CA", root_sk, "Toy Issuing CA", inter_sk.public_key(), 365, True)
    logs = {
        "argon": Log("argon", "Google", key("log argon")),
        "xenon": Log("xenon", "Google", key("log xenon")),
        "oak": Log("oak", "Let's Encrypt", key("log oak")),
        "nimbus": Log("nimbus", "Cloudflare", key("log nimbus")),
    }
    return root_sk, inter_sk, roots, inter, logs


def known(logs: dict) -> dict:
    return {n: (l.operator, l.sk.public_key()) for n, l in logs.items()}


def scenarios() -> list[tuple[str, str, str, str]]:
    """Returns (label, verdict, reason, what the domain owner sees)."""
    out = []

    def run(label: str, browser: Browser, chain, scts, logs, monitor: Monitor, after: int = MMD):
        ok, why = browser.check(chain, scts, "example.com")
        for l in logs.values():
            l.tick(NOW + after)
        alerts = monitor.scan(list(logs.values()))
        seen = f"ALERT ({len(alerts)} log(s))" if alerts else "nothing"
        out.append((label, "ACCEPT" if ok else "REJECT", why, seen))

    site_sk, mal_sk = key("example.com"), key("mallory")
    owner_keys = {raw(site_sk.public_key()).hex()}

    # 1. The honest case: the CA logs the certificate in two logs of different operators.
    _, inter_sk, roots, inter, logs = world()
    leaf = issue("Toy Issuing CA", inter_sk, "example.com", site_sk.public_key(), 47, False)
    scts = [logs["argon"].submit(leaf, NOW), logs["oak"].submit(leaf, NOW)]
    run("1. honest certificate, 2 SCTs", Browser(roots, known(logs)), [leaf, inter], scts, logs,
        Monitor("example.com", owner_keys))

    # 2. DigiNotar, 2011: the CA's own systems are compromised and sign a rogue
    #    certificate. Before CT nothing records it; the owner never hears of it.
    _, inter_sk, roots, inter, logs = world()
    rogue = issue("Toy Issuing CA", inter_sk, "example.com", mal_sk.public_key(), 47, False)
    run("2. rogue cert, browser without CT", Browser(roots, known(logs), enforce_ct=False), [rogue, inter], [],
        logs, Monitor("example.com", owner_keys))

    # 3. The same rogue certificate meets a browser that enforces CT.
    run("3. rogue cert, CT browser, no SCTs", Browser(roots, known(logs)), [rogue, inter], [], logs,
        Monitor("example.com", owner_keys))

    # 4. So the attacker logs it. The browser accepts, but the logs publish within the
    #    MMD and the owner's monitor finds a key it never saw. Detection, not prevention.
    _, inter_sk, roots, inter, logs = world()
    rogue = issue("Toy Issuing CA", inter_sk, "example.com", mal_sk.public_key(), 47, False)
    scts = [logs["argon"].submit(rogue, NOW), logs["nimbus"].submit(rogue, NOW)]
    run("4. rogue cert, logged honestly", Browser(roots, known(logs)), [rogue, inter], scts, logs,
        Monitor("example.com", owner_keys))

    # 5. Two SCTs, but both logs belong to one operator: not enough independence.
    _, inter_sk, roots, inter, logs = world()
    scts = [logs["argon"].submit(rogue, NOW), logs["xenon"].submit(rogue, NOW)]
    run("5. two SCTs, same operator", Browser(roots, known(logs)), [rogue, inter], scts, logs,
        Monitor("example.com", owner_keys))

    # 6. The attacker forges an SCT with their own key and a real log's name.
    _, inter_sk, roots, inter, logs = world()
    forged = SCT("oak", NOW, b"")
    forged.signature = mal_sk.sign(forged.signed_bytes(rogue))
    scts = [logs["argon"].submit(rogue, NOW), forged]
    run("6. one SCT forged", Browser(roots, known(logs)), [rogue, inter], scts, logs,
        Monitor("example.com", owner_keys))

    # 7. One log is dishonest: it signs the SCT and never publishes. The other log is
    #    honest and publishes, so the owner still finds out. One honest log is enough.
    _, inter_sk, roots, inter, logs = world()
    logs["nimbus"].honest = False
    scts = [logs["argon"].submit(rogue, NOW), logs["nimbus"].submit(rogue, NOW)]
    run("7. one log lies, one is honest", Browser(roots, known(logs)), [rogue, inter], scts, logs,
        Monitor("example.com", owner_keys))

    # 8. Both logs lie (two operators compromised or coerced). The browser accepts, the
    #    monitor sees nothing, and nothing in an SCT can show the promise was broken.
    _, inter_sk, roots, inter, logs = world()
    logs["argon"].honest = logs["nimbus"].honest = False
    scts = [logs["argon"].submit(rogue, NOW), logs["nimbus"].submit(rogue, NOW)]
    run("8. both logs lie", Browser(roots, known(logs)), [rogue, inter], scts, logs,
        Monitor("example.com", owner_keys), after=30 * DAY)

    # 9. Entrust, 2024: a CA is distrusted for certificates issued after a cutoff. The CA
    #    could backdate notBefore, so the cutoff is checked against the SCTs, which the
    #    logs timestamp and sign. The CA cannot backdate those.
    _, inter_sk, roots, inter, logs = world()
    body = dict(issue("Toy Issuing CA", inter_sk, "example.com", site_sk.public_key(), 47, False).body)
    body["not_before"] = NOW - 60 * DAY  # backdated by the CA
    late = Cert(body, inter_sk.sign(canonical(body)))
    scts = [logs["argon"].submit(late, NOW), logs["oak"].submit(late, NOW)]
    cutoff = {"Toy Issuing CA": NOW - 30 * DAY}
    run("9. backdated cert from distrusted CA", Browser(roots, known(logs), distrust_after=cutoff),
        [late, inter], scts, logs, Monitor("example.com", owner_keys))
    return out


def main() -> int:
    print(f"{'scenario':38s} {'browser':7s}  {'owner sees':16s} reason")
    for label, verdict, why, seen in scenarios():
        print(f"{label:38s} {verdict:7s}  {seen:16s} {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
