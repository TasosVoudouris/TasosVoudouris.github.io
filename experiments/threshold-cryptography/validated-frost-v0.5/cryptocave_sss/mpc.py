"""Tiny MPC demonstrations built on the corrected Shamir implementation."""

from __future__ import annotations

from dataclasses import dataclass
import random

if __package__:
    from .shamir import ShamirScheme, Sharing
else:
    from shamir import ShamirScheme, Sharing


@dataclass(frozen=True)
class BeaverTriple:
    """Secret sharings of random values ``a``, ``b``, and ``c = a*b``."""

    a: Sharing
    b: Sharing
    c: Sharing


def generate_beaver_triple(scheme: ShamirScheme) -> BeaverTriple:
    """Generate a Beaver triple with a trusted educational dealer.

    Real MPC systems generate authenticated triples using a secure preprocessing
    protocol.  This helper centralizes the generation solely to explain the
    online multiplication equation.
    """

    a = scheme.rng.randrange(scheme.modulus)
    b = scheme.rng.randrange(scheme.modulus)
    c = a * b % scheme.modulus
    return BeaverTriple(scheme.share(a), scheme.share(b), scheme.share(c))


def beaver_multiply(x: Sharing, y: Sharing, triple: BeaverTriple) -> Sharing:
    """Multiply two sharings while restoring the original degree bound.

    The protocol publicly opens ``d = x-a`` and ``e = y-b``.  Because ``a`` and
    ``b`` are random and used only once, these openings do not reveal ``x`` or
    ``y`` in the passive model.
    """

    x._check_compatible(y)
    x._check_compatible(triple.a)
    x._check_compatible(triple.b)
    x._check_compatible(triple.c)

    d = (x - triple.a).reveal_field_element()
    e = (y - triple.b).reveal_field_element()

    # [xy] = [c] + d[b] + e[a] + de
    return triple.c + triple.b.scale(d) + triple.a.scale(e).add_public(d * e)


def demo() -> None:
    """Compare direct and Beaver multiplication."""

    scheme = ShamirScheme(41, 10, 5, rng=random.Random(4))
    x = scheme.share(7)
    y = scheme.share(6)
    direct = x * y
    beaver = beaver_multiply(x, y, generate_beaver_triple(scheme))
    print("Direct product degree:", direct.degree_bound)
    print("Direct product needs shares:", direct.reconstruction_threshold)
    print("Beaver product degree:", beaver.degree_bound)
    print("Beaver product result modulo 41:", beaver.reveal_field_element(beaver.shares[:5]))


if __name__ == "__main__":
    demo()
