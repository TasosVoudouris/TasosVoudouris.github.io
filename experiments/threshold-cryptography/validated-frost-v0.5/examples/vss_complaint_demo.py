"""Example 14: detect, complain about, and replace one bad share."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.pedersen import PedersenShare, PedersenVSS
from cryptocave_sss.vss_session import VSSSession


def main() -> None:
    vss = PedersenVSS.educational(rng=random.Random(72))
    distribution = vss.share(17)
    session = VSSSession(vss, session_id="vss-lesson-complaint")
    session.broadcast_commitments(distribution.commitments)

    received = list(distribution.shares)
    honest_share = received[1]
    received[1] = PedersenShare(
        honest_share.x,
        honest_share.value + 1,
        honest_share.blinding,
    )
    session.distribute_shares(received)
    session.verify_all()

    print("State after verification:", session.state.value)
    print("Complaining participants:", list(session.active_complaints))

    response = session.dealer_respond(2, honest_share)
    print("Replacement accepted?", response.accepted)
    print("State after dealer response:", session.state.value)

    session.finalize()
    print("Final state:", session.state.value)
    print("Reconstructed secret:", session.reconstruct([1, 2, 3]).secret)


if __name__ == "__main__":
    main()
