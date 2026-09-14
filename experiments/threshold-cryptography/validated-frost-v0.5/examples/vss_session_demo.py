"""Example 13: complete an honest offline VSS session."""

import random
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptocave_sss.pedersen import PedersenVSS
from cryptocave_sss.vss_session import VSSSession


def main() -> None:
    vss = PedersenVSS.educational(rng=random.Random(71))
    distribution = vss.share(17)
    session = VSSSession(vss, session_id="vss-lesson-001", dealer_id="alice")

    transcript = session.broadcast_commitments(distribution.commitments)
    session.distribute_shares(list(distribution.shares))
    session.verify_all()
    session.finalize()
    opened = session.reconstruct([1, 2, 5])

    print("Transcript:", transcript.digest)
    print(
        "Participant states:",
        {identifier: status.value for identifier, status in session.statuses.items()},
    )
    print("Final state:", session.state.value)
    print("Reconstructed secret:", opened.secret)


if __name__ == "__main__":
    main()
