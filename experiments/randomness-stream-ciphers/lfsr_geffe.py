"""Small LFSR and Geffe-generator experiments for teaching correlation attacks."""
from dataclasses import dataclass


@dataclass
class LFSR:
    taps: tuple[int, ...]
    state: list[int]

    def __post_init__(self) -> None:
        if len(self.taps) != len(self.state):
            raise ValueError("tap and state lengths must match")
        if not any(self.state):
            raise ValueError("the all-zero LFSR state is absorbing")
        if any(b not in (0, 1) for b in self.taps + tuple(self.state)):
            raise ValueError("LFSR data must be bits")

    def bit(self) -> int:
        out = self.state[0]
        new = sum(t * s for t, s in zip(self.taps, self.state)) & 1
        self.state = self.state[1:] + [new]
        return out

    def stream(self, n: int) -> list[int]:
        return [self.bit() for _ in range(n)]


def geffe(selector: int, left: int, right: int) -> int:
    return (selector & left) ^ ((selector ^ 1) & right)


def agreement(a: list[int], b: list[int]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("equal non-empty sequences required")
    return sum(x == y for x, y in zip(a, b)) / len(a)
