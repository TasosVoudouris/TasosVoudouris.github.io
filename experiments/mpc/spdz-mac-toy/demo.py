"""Transparent SPDZ-style authenticated-sharing invariant demo.

This simulator exposes the global MAC key inside a dealer/checker object so the
invariant is easy to inspect. Real SPDZ keeps alpha secret-shared and performs a
distributed MAC check.
"""
from __future__ import annotations
from dataclasses import dataclass
import secrets

P = 2**61 - 1
N = 3


def split(x: int, n: int = N) -> list[int]:
    out = [secrets.randbelow(P) for _ in range(n - 1)]
    out.append((x - sum(out)) % P)
    return out


@dataclass
class AuthShare:
    x: list[int]
    mac: list[int]

    def __add__(self, other: "AuthShare") -> "AuthShare":
        return AuthShare([(a+b) % P for a,b in zip(self.x, other.x)],
                         [(a+b) % P for a,b in zip(self.mac, other.mac)])

    def __sub__(self, other: "AuthShare") -> "AuthShare":
        return AuthShare([(a-b) % P for a,b in zip(self.x, other.x)],
                         [(a-b) % P for a,b in zip(self.mac, other.mac)])

    def scale(self, c: int) -> "AuthShare":
        return AuthShare([c*a % P for a in self.x], [c*g % P for g in self.mac])


class Dealer:
    def __init__(self):
        self.alpha = secrets.randbelow(P-1) + 1
        self.alpha_shares = split(self.alpha)

    def auth_share(self, value: int) -> AuthShare:
        value %= P
        return AuthShare(split(value), split(self.alpha * value % P))

    def add_public(self, a: AuthShare, c: int) -> AuthShare:
        xs = list(a.x)
        xs[0] = (xs[0] + c) % P
        macs = [(g + c * ai) % P for g, ai in zip(a.mac, self.alpha_shares)]
        return AuthShare(xs, macs)

    def open_and_check(self, a: AuthShare) -> int:
        x = sum(a.x) % P
        gamma = sum(a.mac) % P
        if gamma != self.alpha * x % P:
            raise ValueError("MAC check failed")
        return x

    def triple(self):
        a = secrets.randbelow(P)
        b = secrets.randbelow(P)
        return self.auth_share(a), self.auth_share(b), self.auth_share(a*b % P)

    def multiply(self, x: AuthShare, y: AuthShare, triple) -> AuthShare:
        a,b,c = triple
        e = self.open_and_check(x - a)
        f = self.open_and_check(y - b)
        z = c + b.scale(e) + a.scale(f)
        return self.add_public(z, e*f % P)


def main():
    d = Dealer()
    for _ in range(50):
        xv = secrets.randbelow(P)
        yv = secrets.randbelow(P)
        x = d.auth_share(xv)
        y = d.auth_share(yv)
        z = d.multiply(x, y, d.triple())
        assert d.open_and_check(z) == xv*yv % P

    x = d.auth_share(7)
    x.x[0] = (x.x[0] + 1) % P
    try:
        d.open_and_check(x)
    except ValueError:
        pass
    else:
        raise AssertionError("tampering should fail the MAC invariant")

    print("PASS: authenticated-share invariant, Beaver multiplication, and tamper detection.")


if __name__ == '__main__':
    main()
