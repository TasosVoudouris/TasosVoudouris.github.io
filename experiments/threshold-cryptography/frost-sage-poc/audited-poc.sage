"""Audited educational FROST proof of concept for SageMath + secp256k1.

This keeps the collaborator's original architecture but fixes the main
correctness/engineering issues found during review:

* all protocol scalars are reduced modulo q;
* threshold / participant counts are instance state, not hidden globals;
* binding-factor transcripts include the group key and canonical encodings;
* failures raise and abort instead of only printing;
* signer subsets are explicit and must contain at least t participants;
* signature shares are verified before aggregation;
* the final aggregate Schnorr equation is verified;
* preprocessed nonces are consumed exactly once;
* empty messages are accepted;
* key generation is reset-safe.

It is intentionally an educational construction, NOT an RFC 9591 wire-
compatible implementation. RFC 9591 uses ciphersuite-specific H1-H5 functions
and encodings (including hash_to_field for the secp256k1 ciphersuite).
"""

from hashlib import sha256
from secrets import randbelow

# secp256k1
p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
q = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
Kp = GF(p)
E = EllipticCurve(Kp, (0, 7))
G = E(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8,
)
E.set_order(q)
Kq = GF(q)


def scalar(x):
    return int(Kq(x))


def sample_nonzero():
    # 1 <= x <= q-1, using Python's CSPRNG-backed secrets module.
    return randbelow(q - 1) + 1


def encode_scalar(x):
    return scalar(x).to_bytes(32, "big")


def encode_point(point):
    if point.is_zero():
        raise ValueError("identity point is not a valid commitment")
    x, y = map(int, point.xy())
    return (b"\x02" if y % 2 == 0 else b"\x03") + x.to_bytes(32, "big")


def frame(part):
    return len(part).to_bytes(8, "big") + part


def hash_to_scalar(domain, *parts):
    # Educational transcript hash. This is NOT RFC 9591 hash_to_field.
    h = sha256()
    h.update(frame(domain))
    for part in parts:
        h.update(frame(part))
    return int.from_bytes(h.digest(), "big") % q


def lagrange_at_zero(identifier, signer_ids):
    lam = Kq(1)
    for other in signer_ids:
        if other == identifier:
            continue
        lam *= Kq(other) / Kq(other - identifier)
    return int(lam)


class Participant:
    def __init__(self, identifier, threshold, participant_count):
        self.id = identifier
        self.t = threshold
        self.n = participant_count
        self.shares = {i: None for i in range(1, self.n + 1)}
        self.nonce_pool = []
        self.commitment_pool = []

    # ---------- DKG / VSS ----------
    def generate_polynomial(self):
        self.poly = [Kq(sample_nonzero())]
        self.poly += [Kq(randbelow(q)) for _ in range(self.t - 1)]
        # Ensure exact degree t-1 for a teaching example.
        if self.t > 1 and self.poly[-1] == 0:
            self.poly[-1] = Kq(sample_nonzero())
        self.a0 = scalar(self.poly[0])

    def f(self, x):
        out = Kq(0)
        power = Kq(1)
        xx = Kq(x)
        for coeff in self.poly:
            out += coeff * power
            power *= xx
        return scalar(out)

    def generate_share(self, receiver_id):
        return (receiver_id, self.f(receiver_id))

    def compute_public_commitment(self):
        self.C = [G * scalar(coeff) for coeff in self.poly]

    def compute_proof_of_knowledge(self):
        k = sample_nonzero()
        R = G * k
        c = hash_to_scalar(
            b"CryptoCave/FROST-DKG/PoK",
            encode_scalar(self.id),
            encode_point(G * self.a0),
            encode_point(R),
        )
        mu = scalar(k + self.a0 * c)
        self.pok = (R, mu)

    def verify_participants(self, parties):
        for party in parties:
            if party.id == self.id:
                continue
            R, mu = party.pok
            c = hash_to_scalar(
                b"CryptoCave/FROST-DKG/PoK",
                encode_scalar(party.id),
                encode_point(party.C[0]),
                encode_point(R),
            )
            if R != G * mu - party.C[0] * c:
                raise ValueError(f"Party {party.id} failed DKG proof of knowledge")

    def send_shares(self, parties):
        for receiver in parties:
            receiver.shares[self.id] = self.generate_share(receiver.id)
        # Erase the polynomial after distribution. Keep only public commitments.
        self.poly = None

    def verify_received_shares(self, parties):
        for dealer in parties:
            share = self.shares[dealer.id]
            if share is None:
                raise ValueError(f"missing share from Party {dealer.id}")
            _, value = share
            rhs = E(0)
            for k in range(self.t):
                rhs += dealer.C[k] * (self.id ** k)
            if G * value != rhs:
                raise ValueError(f"invalid Feldman share from Party {dealer.id}")

    def finalize_signing_share(self):
        self.si = scalar(sum(self.shares[j][1] for j in range(1, self.n + 1)))
        self.Y = G * self.si
        # Erase the individual dealer shares after aggregation.
        self.shares = {i: None for i in range(1, self.n + 1)}

    # ---------- Signing ----------
    def preprocess(self, count):
        self.nonce_pool = []
        self.commitment_pool = []
        for _ in range(count):
            d = sample_nonzero()
            e = sample_nonzero()
            D, E_ = G * d, G * e
            self.nonce_pool.append((d, e))
            self.commitment_pool.append((D, E_))

    def consume_nonce(self):
        if not self.nonce_pool or not self.commitment_pool:
            raise ValueError(f"Party {self.id} has no unused nonce pair")
        nonces = self.nonce_pool.pop(0)
        commitments = self.commitment_pool.pop(0)
        return nonces, commitments


class FROSTEducational:
    def __init__(self, threshold, participant_count):
        if not (2 <= threshold <= participant_count):
            raise ValueError("require 2 <= threshold <= participant_count")
        self.t = threshold
        self.n = participant_count
        self.parties = [Participant(i, threshold, participant_count) for i in range(1, participant_count + 1)]
        self.groupY = None

    def keygen(self):
        # Reset-safe: every invocation derives a fresh group key.
        self.groupY = E(0)
        for party in self.parties:
            party.generate_polynomial()
            party.compute_public_commitment()
            party.compute_proof_of_knowledge()

        for party in self.parties:
            party.verify_participants(self.parties)

        for dealer in self.parties:
            dealer.send_shares(self.parties)

        for party in self.parties:
            party.verify_received_shares(self.parties)
            party.finalize_signing_share()

        for dealer in self.parties:
            self.groupY += dealer.C[0]
        if self.groupY.is_zero():
            raise ValueError("identity group public key")

    def preprocess(self, count):
        for party in self.parties:
            party.preprocess(count)

    def encode_commitment_list(self, commitments):
        out = b""
        for identifier, D, E_ in sorted(commitments, key=lambda x: x[0]):
            out += encode_scalar(identifier) + encode_point(D) + encode_point(E_)
        return out

    def binding_factor(self, identifier, message, encoded_commitments):
        # Educational transcript with the same conceptual inputs as RFC 9591.
        return hash_to_scalar(
            b"CryptoCave/FROST/rho",
            encode_point(self.groupY),
            sha256(message).digest(),
            sha256(encoded_commitments).digest(),
            encode_scalar(identifier),
        )

    def challenge(self, R, message):
        return hash_to_scalar(
            b"CryptoCave/FROST/chal",
            encode_point(R),
            encode_point(self.groupY),
            message,
        )

    def sign(self, message, signer_ids):
        signer_ids = sorted(signer_ids)
        if len(signer_ids) < self.t:
            raise ValueError("not enough signers")
        if len(set(signer_ids)) != len(signer_ids):
            raise ValueError("duplicate signer identifier")
        if any(i < 1 or i > self.n for i in signer_ids):
            raise ValueError("unknown signer identifier")

        signers = [self.parties[i - 1] for i in signer_ids]

        # Round one: consume one private nonce pair and publish commitments.
        private = {}
        B = []
        for signer in signers:
            nonce_pair, (D, E_) = signer.consume_nonce()
            private[signer.id] = nonce_pair
            B.append((signer.id, D, E_))
        B.sort(key=lambda x: x[0])
        Bencoded = self.encode_commitment_list(B)

        rho = {
            i: self.binding_factor(i, message, Bencoded)
            for i, _, _ in B
        }
        Ri = {
            i: D + E_ * rho[i]
            for i, D, E_ in B
        }
        R = sum(Ri.values(), E(0))
        if R.is_zero():
            raise ValueError("identity group commitment")
        c = self.challenge(R, message)

        # Round two: signature shares.
        shares = {}
        lambdas = {}
        for signer in signers:
            d, e = private[signer.id]
            lam = lagrange_at_zero(signer.id, signer_ids)
            z_i = scalar(d + e * rho[signer.id] + lam * signer.si * c)
            shares[signer.id] = z_i
            lambdas[signer.id] = lam

        # Coordinator verifies every signature share before aggregation.
        for signer in signers:
            left = G * shares[signer.id]
            right = Ri[signer.id] + signer.Y * scalar(c * lambdas[signer.id])
            if left != right:
                raise ValueError(f"invalid signature share from Party {signer.id}")

        z = scalar(sum(shares.values()))

        # Final aggregate Schnorr verification.
        if G * z != R + self.groupY * c:
            raise ValueError("aggregate signature verification failed")

        return (R, z)


messages = [b"FROST demo 1", b"FROST demo 2", b"FROST demo 3"]
frost = FROSTEducational(threshold=4, participant_count=5)
frost.keygen()
frost.preprocess(len(messages))

subsets = [
    [1, 2, 3, 4],
    [1, 2, 4, 5],
    [1, 3, 4, 5],
]

for message, signer_ids in zip(messages, subsets):
    R, z = frost.sign(message, signer_ids)
    print(f"[+] signers={signer_ids} message={message!r}")
    print(f"    R={R}")
    print(f"    z={z}")
