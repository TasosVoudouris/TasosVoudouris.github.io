"""Example 15: abort when a complaint remains unresolved."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.pedersen import PedersenShare, PedersenVSS
from cryptocave_sss.vss_session import VSSSession


def main() -> None:
    vss = PedersenVSS.educational(rng=random.Random(73))
    distribution = vss.share(17)
    session = VSSSession(vss, session_id="vss-lesson-abort")
    session.broadcast_commitments(distribution.commitments)

    received = list(distribution.shares)
    honest_share = received[3]
    received[3] = PedersenShare(
        honest_share.x,
        honest_share.value,
        honest_share.blinding + 1,
    )
    session.distribute_shares(received)
    session.verify_all()

    print("Open complaints:", list(session.active_complaints))
    session.finalize()
    print("Final state:", session.state.value)
    print("No reconstruction is permitted after abort.")


if __name__ == "__main__":
    main()
