"""Root of Trust, part 00: a toy chain of trust.

A teaching model, NOT X.509 and NOT secure PKI. Real certificates use DER
(RFC 5280), many more fields and many more checks. What this file keeps is the
logic that matters for the article:

  * a certificate is a signed statement "this name has this key";
  * a chain is checked link by link, from the leaf up;
  * the last link must be signed by a key you ALREADY trust (the trust store);
  * nothing in the chain can prove the root is legitimate.

Run:  python 00_toy_chain.py      (needs: pip install cryptography)
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

NOW = 1_795_000_000  # a fixed "current time" (Unix seconds) so runs are repeatable
DAY = 86_400


def raw(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(Encoding.Raw, PublicFormat.Raw)


def canonical(body: dict) -> bytes:
    # One object must have exactly one byte encoding, or signatures break.
    # Sorted keys and no spaces give that here; X.509 uses DER for the same reason.
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()


@dataclass
class Cert:
    body: dict  # the "to be signed" part
    signature: bytes

    @property
    def subject(self) -> str:
        return self.body["subject"]

    @property
    def key(self) -> Ed25519PublicKey:
        return Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.body["key"]))


def issue(issuer: str, issuer_key: Ed25519PrivateKey, subject: str,
          subject_key: Ed25519PublicKey, days: int, is_ca: bool) -> Cert:
    body = {
        "subject": subject,
        "key": raw(subject_key).hex(),
        "issuer": issuer,
        "not_before": NOW - DAY,
        "not_after": NOW + days * DAY,
        "is_ca": is_ca,
    }
    return Cert(body, issuer_key.sign(canonical(body)))


def verify_chain(chain: list[Cert], trust_store: dict[str, Ed25519PublicKey],
                 name: str) -> tuple[bool, str]:
    """chain[0] is the leaf; each cert is signed by the next; the last one is
    signed by a key in trust_store."""
    if chain[0].subject != name:
        return False, f"leaf is for {chain[0].subject!r}, not {name!r}"
    for i, cert in enumerate(chain):
        b = cert.body
        if not b["not_before"] <= NOW <= b["not_after"]:
            return False, f"{cert.subject}: expired or not yet valid"
        if i + 1 < len(chain):
            parent = chain[i + 1]
            if parent.subject != b["issuer"]:
                return False, f"{cert.subject}: issuer name does not match"
            if not parent.body["is_ca"]:
                return False, f"{parent.subject} is not allowed to issue certificates"
            signer = parent.key
        else:
            signer = trust_store.get(b["issuer"])
            if signer is None:
                return False, f"{b['issuer']!r} is not in the trust store"
        try:
            signer.verify(cert.signature, canonical(b))
        except InvalidSignature:
            return False, f"{cert.subject}: bad signature"
    return True, "chain verifies up to a trusted root"


def main() -> None:
    # --- the honest world --------------------------------------------------
    root_sk = Ed25519PrivateKey.generate()
    inter_sk = Ed25519PrivateKey.generate()
    site_sk = Ed25519PrivateKey.generate()

    trust_store = {"Toy Root CA": root_sk.public_key()}  # shipped with your OS
    inter = issue("Toy Root CA", root_sk, "Toy Issuing CA", inter_sk.public_key(), 365, True)
    leaf = issue("Toy Issuing CA", inter_sk, "example.com", site_sk.public_key(), 47, False)
    chain = [leaf, inter]

    def show(label: str, chain: list[Cert], store=trust_store, name="example.com") -> None:
        ok, why = verify_chain(chain, store, name)
        print(f"{'ACCEPT' if ok else 'REJECT'}  {label:<44} {why}")

    show("1. honest chain", chain)

    # --- Mallory tries things ---------------------------------------------
    mal_sk = Ed25519PrivateKey.generate()

    swapped = Cert(dict(leaf.body, key=raw(mal_sk.public_key()).hex()), leaf.signature)
    show("2. leaf key swapped for Mallory's", [swapped, inter])

    show("3. honest chain, wrong site name", chain, name="bank.example")

    mal_root = Ed25519PrivateKey.generate()
    fake_leaf = issue("Mallory Root", mal_root, "example.com", mal_sk.public_key(), 47, False)
    show("4. Mallory signs with her own root", [fake_leaf])

    poisoned = dict(trust_store, **{"Mallory Root": mal_root.public_key()})
    show("5. ...after her root is in YOUR store", [fake_leaf], store=poisoned)

    misissued = issue("Toy Issuing CA", inter_sk, "example.com", mal_sk.public_key(), 47, False)
    show("6. a trusted CA issues to Mallory", [misissued, inter])

    # --- what it costs on the wire ----------------------------------------
    print()
    sig_ed, key_ed = len(leaf.signature), len(raw(site_sk.public_key()))
    SIG_MLDSA44, KEY_MLDSA44 = 2420, 1312  # FIPS 204, ML-DSA-44
    print(f"Ed25519   : signature {sig_ed:>5} B, public key {key_ed:>5} B")
    print(f"ML-DSA-44 : signature {SIG_MLDSA44:>5} B, public key {KEY_MLDSA44:>5} B")
    # Leaf public key + leaf signature + two SCT signatures (see the article).
    print(f"leaf key + 3 signatures: Ed25519 {key_ed + 3 * sig_ed} B   "
          f"ML-DSA-44 {KEY_MLDSA44 + 3 * SIG_MLDSA44} B")


if __name__ == "__main__":
    main()
