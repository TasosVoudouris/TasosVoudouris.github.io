"""A readable two-round threshold Schnorr/FROST lesson for Version 0.5.

The equations and round structure follow RFC 9591 closely, but the ciphersuite
does not: this module reuses CryptoCave's deliberately tiny order-41 subgroup.
It is therefore an executable protocol notebook, not an RFC-compatible or
production-secure FROST implementation.

The normal path consumes a :class:`~cryptocave_sss.dkg.DKGResult`, generates
one-time nonce commitments, creates signature shares, verifies every share,
and emits an ordinary Schnorr signature.  It never reconstructs the group
secret.
"""

from __future__ import annotations

import hashlib
import json
import random
import secrets
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass

if __package__:
    from .dkg import DKGResult, MultiDealerDKG
    from .field import inverse, is_prime
else:
    from dkg import DKGResult, MultiDealerDKG
    from field import inverse, is_prime


RandomBytesSource = Callable[[int], bytes]
MessageValidator = Callable[["FrostSigningPackage"], bool]


# ---------------------------------------------------------------------------
# Canonical public encodings and protocol errors
# ---------------------------------------------------------------------------


def _canonical_digest(public_object: object) -> str:
    """Hash a public object using one deterministic JSON representation."""

    encoded = json.dumps(
        public_object,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _frame(parts: Sequence[bytes]) -> bytes:
    """Encode variable-length fields without ambiguous concatenation."""

    output = bytearray()
    for part in parts:
        output.extend(len(part).to_bytes(8, "big"))
        output.extend(part)
    return bytes(output)


class FrostError(ValueError):
    """Base class for a rejected Version 0.5 operation."""


class FrostAbortError(FrostError):
    """Raised when a signing session must stop without a signature."""


class NonceReuseError(FrostAbortError):
    """Raised when a signer is asked to use deleted nonce state again."""


class MessageRejectedError(FrostAbortError):
    """Raised when a signer's application policy rejects the payload."""


# ---------------------------------------------------------------------------
# Toy ciphersuite and public group information
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ToyFROSTSuite:
    """The small multiplicative group and domain-separated toy hashes.

    RFC 9591 writes its prime-order group additively.  CryptoCave's existing
    commitment group is multiplicative, so RFC group addition becomes modular
    multiplication and scalar multiplication becomes modular exponentiation.

    ``H1`` through ``H5`` use the RFC labels ``rho``, ``chal``, ``nonce``,
    ``msg``, and ``com``.  Reducing SHA-256 output modulo the tiny scalar field
    is easy to inspect, but this is not one of RFC 9591's named ciphersuites.
    """

    group_modulus: int
    scalar_modulus: int
    generator: int
    context_string: bytes = b"CryptoCave-FROST-toy-SHA256-v1"

    def __post_init__(self) -> None:
        if not is_prime(self.group_modulus):
            raise ValueError("group_modulus must be prime")
        if not is_prime(self.scalar_modulus):
            raise ValueError("scalar_modulus must be prime")
        if (self.group_modulus - 1) % self.scalar_modulus != 0:
            raise ValueError("scalar_modulus must divide group_modulus - 1")
        generator = self.generator % self.group_modulus
        if generator in (0, 1):
            raise ValueError("generator must be a non-identity group element")
        if pow(generator, self.scalar_modulus, self.group_modulus) != 1:
            raise ValueError("generator is outside the requested subgroup")
        if not self.context_string:
            raise ValueError("the ciphersuite context string must not be empty")
        object.__setattr__(self, "generator", generator)

    @classmethod
    def from_dkg(cls, result: DKGResult) -> "ToyFROSTSuite":
        parameters = result.value_parameters
        return cls(
            parameters.group_modulus,
            parameters.scalar_modulus,
            parameters.generator,
        )

    @property
    def scalar_size(self) -> int:
        return max(1, (self.scalar_modulus.bit_length() + 7) // 8)

    @property
    def element_size(self) -> int:
        return max(1, (self.group_modulus.bit_length() + 7) // 8)

    def serialize_scalar(self, scalar: int) -> bytes:
        """Return one fixed-width canonical scalar encoding."""

        if not isinstance(scalar, int) or not 0 <= scalar < self.scalar_modulus:
            raise ValueError("scalar must be canonically represented in [0, q)")
        return scalar.to_bytes(self.scalar_size, "big")

    def is_group_element(self, element: int, *, allow_identity: bool = False) -> bool:
        if not isinstance(element, int) or not 1 <= element < self.group_modulus:
            return False
        if not allow_identity and element == 1:
            return False
        return pow(element, self.scalar_modulus, self.group_modulus) == 1

    def serialize_element(self, element: int) -> bytes:
        """Validate and canonically encode a non-identity subgroup element."""

        if not self.is_group_element(element):
            raise ValueError("element must be a non-identity subgroup element")
        return element.to_bytes(self.element_size, "big")

    def base_mult(self, scalar: int) -> int:
        """Return ``g^scalar`` (RFC ``G.ScalarBaseMult``)."""

        return pow(self.generator, scalar % self.scalar_modulus, self.group_modulus)

    def scalar_mult(self, element: int, scalar: int) -> int:
        """Return ``element^scalar`` (RFC ``G.ScalarMult``)."""

        if not self.is_group_element(element, allow_identity=True):
            raise ValueError("cannot multiply an invalid group element")
        return pow(element, scalar % self.scalar_modulus, self.group_modulus)

    def _hash_to_scalar(self, label: bytes, data: bytes) -> int:
        digest = hashlib.sha256(self.context_string + label + data).digest()
        return int.from_bytes(digest, "big") % self.scalar_modulus

    def h1(self, data: bytes) -> int:
        return self._hash_to_scalar(b"rho", data)

    def h2(self, data: bytes) -> int:
        return self._hash_to_scalar(b"chal", data)

    def h3(self, data: bytes) -> int:
        return self._hash_to_scalar(b"nonce", data)

    def h4(self, data: bytes) -> bytes:
        return hashlib.sha256(self.context_string + b"msg" + data).digest()

    def h5(self, data: bytes) -> bytes:
        return hashlib.sha256(self.context_string + b"com" + data).digest()


@dataclass(frozen=True, order=True)
class FrostVerifyingShare:
    """One public verification key ``Y_i = g^x_i``."""

    participant_id: int
    element: int


@dataclass(frozen=True)
class FrostGroupInfo:
    """Public information shared by the coordinator and every signer."""

    suite: ToyFROSTSuite
    threshold: int
    participant_ids: tuple[int, ...]
    group_public_key: int
    verifying_shares: tuple[FrostVerifyingShare, ...]
    dkg_transcript_digest: str

    def __post_init__(self) -> None:
        q = self.suite.scalar_modulus
        if not 1 <= self.threshold <= len(self.participant_ids):
            raise ValueError("threshold must be between 1 and participant count")
        if tuple(sorted(self.participant_ids)) != self.participant_ids:
            raise ValueError("participant identifiers must be in ascending order")
        if len(set(self.participant_ids)) != len(self.participant_ids):
            raise ValueError("participant identifiers must be distinct")
        if any(not 1 <= identifier < q for identifier in self.participant_ids):
            raise ValueError("participant identifiers must be nonzero scalars")
        if not self.suite.is_group_element(self.group_public_key):
            raise ValueError("group public key must be a non-identity element")
        if tuple(item.participant_id for item in self.verifying_shares) != self.participant_ids:
            raise ValueError("provide one ordered verifying share per participant")
        if not all(
            self.suite.is_group_element(item.element)
            for item in self.verifying_shares
        ):
            raise ValueError("verifying shares must be non-identity group elements")
        try:
            digest = bytes.fromhex(self.dkg_transcript_digest)
        except ValueError as error:
            raise ValueError("DKG transcript digest must be hexadecimal") from error
        if len(digest) != 32:
            raise ValueError("DKG transcript digest must encode 32 bytes")

    @classmethod
    def from_dkg(cls, result: DKGResult) -> "FrostGroupInfo":
        """Derive all public FROST inputs from one completed DKG result."""

        if not all(check.accepted for check in result.verify_all()):
            raise ValueError("DKG result contains an invalid participant share")
        suite = ToyFROSTSuite.from_dkg(result)
        verifying_shares = tuple(
            FrostVerifyingShare(
                participant_id,
                result.value_commitments.expected_share_commitment(participant_id),
            )
            for participant_id in result.shamir.participant_ids
        )
        return cls(
            suite=suite,
            threshold=result.shamir.threshold,
            participant_ids=result.shamir.participant_ids,
            group_public_key=result.public_key,
            verifying_shares=verifying_shares,
            dkg_transcript_digest=result.transcript.digest,
        )

    def verifying_share_for(self, participant_id: int) -> int:
        for item in self.verifying_shares:
            if item.participant_id == participant_id:
                return item.element
        raise ValueError("unknown participant identifier")

    def as_public_dict(self) -> dict[str, object]:
        return {
            "suite": self.suite.context_string.decode("ascii"),
            "group_modulus": self.suite.group_modulus,
            "scalar_modulus": self.suite.scalar_modulus,
            "generator": self.suite.generator,
            "threshold": self.threshold,
            "participant_ids": list(self.participant_ids),
            "group_public_key": self.group_public_key,
            "verifying_shares": [
                {
                    "participant_id": item.participant_id,
                    "element": item.element,
                }
                for item in self.verifying_shares
            ],
            "dkg_transcript_digest": self.dkg_transcript_digest,
        }

    @property
    def digest(self) -> str:
        return _canonical_digest(self.as_public_dict())


# ---------------------------------------------------------------------------
# Public round messages, responses, signatures, and transcripts
# ---------------------------------------------------------------------------

@dataclass(frozen=True, order=True)
class NonceCommitment:
    """Round-one public output; no secret nonce is present here."""

    participant_id: int
    hiding: int
    binding: int
    nonce_id: str

    def __post_init__(self) -> None:
        if self.participant_id <= 0:
            raise ValueError("participant identifier must be positive")
        if not self.nonce_id:
            raise ValueError("nonce identifier must not be empty")

    def encode_rfc_tuple(self, suite: ToyFROSTSuite) -> bytes:
        """Encode ``(identifier, D_i, E_i)`` as in RFC 9591 Section 4.3."""

        return (
            suite.serialize_scalar(self.participant_id)
            + suite.serialize_element(self.hiding)
            + suite.serialize_element(self.binding)
        )

    def as_public_dict(self) -> dict[str, object]:
        return {
            "participant_id": self.participant_id,
            "hiding": self.hiding,
            "binding": self.binding,
            "nonce_id": self.nonce_id,
        }


@dataclass(frozen=True)
class FrostSigningPackage:
    """Coordinator message for round two.

    The ``message`` field is the application payload.  ``message_to_sign``
    wraps it with session, counter, context, DKG, and signer-set data.  That
    complete byte string is supplied as RFC 9591's ``msg`` input.
    """

    protocol: str
    version: str
    session_id: str
    counter: int
    application_context: str
    message: bytes
    group_info_digest: str
    commitments: tuple[NonceCommitment, ...]

    def __post_init__(self) -> None:
        if self.protocol != "CryptoCave-FROST":
            raise ValueError("unexpected signing protocol identifier")
        if self.version != "0.5":
            raise ValueError("unexpected signing protocol version")
        if not self.session_id.strip():
            raise ValueError("session_id must not be empty")
        if self.counter < 1:
            raise ValueError("counter must be at least one")
        if not self.application_context.strip():
            raise ValueError("application_context must not be empty")
        if not isinstance(self.message, bytes):
            raise TypeError("message must be bytes")
        try:
            group_digest = bytes.fromhex(self.group_info_digest)
        except ValueError as error:
            raise ValueError("group-info digest must be hexadecimal") from error
        if len(group_digest) != 32:
            raise ValueError("group-info digest must encode 32 bytes")
        identifiers = tuple(item.participant_id for item in self.commitments)
        if identifiers != tuple(sorted(identifiers)):
            raise ValueError("commitment list must be sorted by participant")
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("commitment list contains duplicate participants")

    @property
    def participant_ids(self) -> tuple[int, ...]:
        return tuple(item.participant_id for item in self.commitments)

    def commitment_for(self, participant_id: int) -> NonceCommitment:
        for commitment in self.commitments:
            if commitment.participant_id == participant_id:
                return commitment
        raise ValueError("participant does not appear in the signing package")

    def message_to_sign(self, suite: ToyFROSTSuite) -> bytes:
        """Return the unambiguous application envelope signed by FROST."""

        signer_set = b"".join(
            suite.serialize_scalar(identifier) for identifier in self.participant_ids
        )
        return _frame(
            (
                b"CryptoCave-FROST-application-message-v0.5",
                suite.context_string,
                self.session_id.encode("utf-8"),
                self.counter.to_bytes(8, "big"),
                self.application_context.encode("utf-8"),
                bytes.fromhex(self.group_info_digest),
                signer_set,
                self.message,
            )
        )

    def as_public_dict(self) -> dict[str, object]:
        return {
            "protocol": self.protocol,
            "version": self.version,
            "session_id": self.session_id,
            "counter": self.counter,
            "application_context": self.application_context,
            "message_hex": self.message.hex(),
            "group_info_digest": self.group_info_digest,
            "commitments": [item.as_public_dict() for item in self.commitments],
        }

    @property
    def digest(self) -> str:
        return _canonical_digest(self.as_public_dict())


@dataclass(frozen=True, order=True)
class FrostSignatureShare:
    """One round-two response scalar ``z_i``."""

    participant_id: int
    value: int
    package_digest: str


@dataclass(frozen=True)
class FrostSignature:
    """An ordinary Schnorr signature ``(R, z)``."""

    group_commitment: int
    response: int

    def encode(self, suite: ToyFROSTSuite) -> bytes:
        """Encode ``R || z`` using the suite's fixed-width encodings."""

        return (
            suite.serialize_element(self.group_commitment)
            + suite.serialize_scalar(self.response)
        )


@dataclass(frozen=True)
class FrostSignatureShareVerification:
    """Public audit of ``g^z_i = D_i E_i^rho_i Y_i^(c lambda_i)``."""

    participant_id: int
    accepted: bool
    left: int
    right: int
    reason: str


@dataclass(frozen=True)
class FrostSigningTranscript:
    """Canonical public record of a completed signing session."""

    protocol: str
    version: str
    session_id: str
    counter: int
    application_context: str
    group_info_digest: str
    package_digest: str
    payload_digest: str
    signed_message_digest: str
    participant_ids: tuple[int, ...]
    commitments: tuple[NonceCommitment, ...]
    binding_factors: tuple[tuple[int, int], ...]
    group_commitment: int
    challenge: int
    signature_shares: tuple[tuple[int, int], ...]
    signature: FrostSignature
    final_verified: bool

    def as_public_dict(self) -> dict[str, object]:
        return {
            "protocol": self.protocol,
            "version": self.version,
            "session_id": self.session_id,
            "counter": self.counter,
            "application_context": self.application_context,
            "group_info_digest": self.group_info_digest,
            "package_digest": self.package_digest,
            "payload_digest": self.payload_digest,
            "signed_message_digest": self.signed_message_digest,
            "participant_ids": list(self.participant_ids),
            "commitments": [item.as_public_dict() for item in self.commitments],
            "binding_factors": [
                {"participant_id": identifier, "value": value}
                for identifier, value in self.binding_factors
            ],
            "group_commitment": self.group_commitment,
            "challenge": self.challenge,
            "signature_shares": [
                {"participant_id": identifier, "value": value}
                for identifier, value in self.signature_shares
            ],
            "signature": {
                "group_commitment": self.signature.group_commitment,
                "response": self.signature.response,
            },
            "final_verified": self.final_verified,
        }

    @property
    def digest(self) -> str:
        return _canonical_digest(self.as_public_dict())


@dataclass(frozen=True)
class FrostSigningResult:
    signature: FrostSignature
    share_verifications: tuple[FrostSignatureShareVerification, ...]
    transcript: FrostSigningTranscript


@dataclass(frozen=True)
class FrostSigningRun:
    """Convenient return value containing the package and final result."""

    package: FrostSigningPackage
    result: FrostSigningResult


@dataclass
class _NonceState:
    """Secret round-one state retained only inside one signer object."""

    hiding_nonce: int
    binding_nonce: int
    commitment: NonceCommitment
    session_id: str
    counter: int


# ---------------------------------------------------------------------------
# Pure RFC-shaped helper equations
# ---------------------------------------------------------------------------

def derive_interpolating_value(
    participant_ids: Sequence[int],
    participant_id: int,
    scalar_modulus: int,
) -> int:
    """Return the Lagrange coefficient at zero for ``participant_id``."""

    selected = tuple(participant_ids)
    if participant_id not in selected:
        raise ValueError("participant is absent from the interpolation set")
    if len(set(selected)) != len(selected):
        raise ValueError("interpolation identifiers must be distinct")
    if any(identifier % scalar_modulus == 0 for identifier in selected):
        raise ValueError("interpolation identifiers must be nonzero scalars")

    numerator = 1
    denominator = 1
    for other in selected:
        if other == participant_id:
            continue
        numerator = numerator * other % scalar_modulus
        denominator = denominator * (other - participant_id) % scalar_modulus
    return numerator * inverse(denominator, scalar_modulus) % scalar_modulus


def encode_group_commitment_list(
    commitments: Sequence[NonceCommitment],
    suite: ToyFROSTSuite,
) -> bytes:
    """Encode an ascending RFC-style commitment list."""

    identifiers = tuple(item.participant_id for item in commitments)
    if identifiers != tuple(sorted(identifiers)):
        raise ValueError("commitment list must be sorted by participant")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("commitment list contains duplicate participants")
    return b"".join(item.encode_rfc_tuple(suite) for item in commitments)


def _validate_package(group_info: FrostGroupInfo, package: FrostSigningPackage) -> None:
    if package.group_info_digest != group_info.digest:
        raise FrostAbortError("signing package uses different group information")
    if not group_info.threshold <= len(package.commitments) <= len(
        group_info.participant_ids
    ):
        raise FrostAbortError("signer count must be between threshold and n")
    if any(
        identifier not in group_info.participant_ids
        for identifier in package.participant_ids
    ):
        raise FrostAbortError("signing package contains an unknown participant")
    encode_group_commitment_list(package.commitments, group_info.suite)


def compute_binding_factors(
    group_info: FrostGroupInfo,
    package: FrostSigningPackage,
) -> tuple[tuple[int, int], ...]:
    """Compute RFC-style per-signer binding factors ``rho_i``."""

    _validate_package(group_info, package)
    suite = group_info.suite
    prefix = (
        suite.serialize_element(group_info.group_public_key)
        + suite.h4(package.message_to_sign(suite))
        + suite.h5(encode_group_commitment_list(package.commitments, suite))
    )
    return tuple(
        (
            commitment.participant_id,
            suite.h1(prefix + suite.serialize_scalar(commitment.participant_id)),
        )
        for commitment in package.commitments
    )


def _binding_factor_for(
    binding_factors: Sequence[tuple[int, int]],
    participant_id: int,
) -> int:
    for identifier, value in binding_factors:
        if identifier == participant_id:
            return value
    raise ValueError("binding factor is missing for participant")


def compute_group_commitment(
    group_info: FrostGroupInfo,
    package: FrostSigningPackage,
    binding_factors: Sequence[tuple[int, int]] | None = None,
) -> int:
    """Compute ``R = product(D_i * E_i^rho_i)``."""

    factors = (
        compute_binding_factors(group_info, package)
        if binding_factors is None
        else tuple(binding_factors)
    )
    suite = group_info.suite
    result = 1
    for commitment in package.commitments:
        rho = _binding_factor_for(factors, commitment.participant_id)
        result = (
            result
            * commitment.hiding
            * suite.scalar_mult(commitment.binding, rho)
            % suite.group_modulus
        )
    return result


def compute_challenge(
    group_info: FrostGroupInfo,
    package: FrostSigningPackage,
    group_commitment: int,
) -> int:
    """Compute ``c = H2(Serialize(R) || Serialize(Y) || msg)``."""

    suite = group_info.suite
    challenge_input = (
        suite.serialize_element(group_commitment)
        + suite.serialize_element(group_info.group_public_key)
        + package.message_to_sign(suite)
    )
    return suite.h2(challenge_input)


def verify_schnorr_signature(
    message: bytes,
    signature: FrostSignature,
    group_public_key: int,
    suite: ToyFROSTSuite,
) -> bool:
    """Verify the final signature with the ordinary Schnorr equation."""

    if not isinstance(message, bytes):
        return False
    if not suite.is_group_element(group_public_key):
        return False
    if not suite.is_group_element(signature.group_commitment):
        return False
    if not 0 <= signature.response < suite.scalar_modulus:
        return False
    try:
        challenge_input = (
            suite.serialize_element(signature.group_commitment)
            + suite.serialize_element(group_public_key)
            + message
        )
    except ValueError:
        return False
    challenge = suite.h2(challenge_input)
    left = suite.base_mult(signature.response)
    right = (
        signature.group_commitment
        * suite.scalar_mult(group_public_key, challenge)
        % suite.group_modulus
    )
    return left == right


# ---------------------------------------------------------------------------
# Stateful signer and coordinator roles
# ---------------------------------------------------------------------------

class FrostSigner:
    """One participant holding one DKG signing share and private nonce state."""

    def __init__(
        self,
        group_info: FrostGroupInfo,
        participant_id: int,
        signing_share: int,
        message_validator: MessageValidator | None = None,
    ) -> None:
        if participant_id not in group_info.participant_ids:
            raise ValueError("signer is not part of the configured group")
        if not 0 <= signing_share < group_info.suite.scalar_modulus:
            raise ValueError("signing share must be a canonical scalar")
        if (
            group_info.suite.base_mult(signing_share)
            != group_info.verifying_share_for(participant_id)
        ):
            raise ValueError("private signing share does not match public group info")
        self.group_info = group_info
        self.participant_id = participant_id
        self._signing_share = signing_share
        self._message_validator = message_validator
        self._pending_nonces: dict[str, _NonceState] = {}

    @classmethod
    def from_dkg(
        cls,
        result: DKGResult,
        participant_id: int,
        message_validator: MessageValidator | None = None,
    ) -> "FrostSigner":
        group_info = FrostGroupInfo.from_dkg(result)
        participant_share = result.share_for(participant_id)
        verification = result.verify_share(participant_share)
        if not verification.accepted:
            raise ValueError("participant's DKG share failed verification")
        return cls(
            group_info,
            participant_id,
            participant_share.secret_share % result.shamir.modulus,
            message_validator,
        )

    @property
    def pending_nonce_count(self) -> int:
        return len(self._pending_nonces)

    def _nonce_generate(self, random_bytes_source: RandomBytesSource) -> int:
        """Follow RFC 9591's fresh-randomness-plus-secret-share construction."""

        suite = self.group_info.suite
        secret_encoding = suite.serialize_scalar(self._signing_share)
        # A zero scalar would produce the identity commitment, which RFC group
        # deserialization rejects.  This is common only because q=41 is tiny.
        for _ in range(256):
            random_bytes = random_bytes_source(32)
            if not isinstance(random_bytes, bytes) or len(random_bytes) != 32:
                raise ValueError("random byte source must return exactly 32 bytes")
            nonce = suite.h3(random_bytes + secret_encoding)
            if nonce != 0:
                return nonce
        raise FrostAbortError("could not sample a nonzero nonce")

    def commit(
        self,
        session_id: str,
        counter: int,
        random_bytes_source: RandomBytesSource | None = None,
    ) -> NonceCommitment:
        """Run round one and retain the two secret nonces locally."""

        if not session_id.strip():
            raise ValueError("session_id must not be empty")
        if counter < 1:
            raise ValueError("counter must be at least one")
        source = random_bytes_source or secrets.token_bytes
        suite = self.group_info.suite
        hiding_nonce = self._nonce_generate(source)
        binding_nonce = self._nonce_generate(source)
        hiding_commitment = suite.base_mult(hiding_nonce)
        binding_commitment = suite.base_mult(binding_nonce)
        nonce_id_input = _frame(
            (
                b"CryptoCave-FROST-nonce-id-v0.5",
                self.group_info.digest.encode("ascii"),
                session_id.encode("utf-8"),
                counter.to_bytes(8, "big"),
                suite.serialize_scalar(self.participant_id),
                suite.serialize_element(hiding_commitment),
                suite.serialize_element(binding_commitment),
            )
        )
        nonce_id = hashlib.sha256(nonce_id_input).hexdigest()
        if nonce_id in self._pending_nonces:
            raise NonceReuseError("duplicate nonce commitment was generated")
        commitment = NonceCommitment(
            self.participant_id,
            hiding_commitment,
            binding_commitment,
            nonce_id,
        )
        self._pending_nonces[nonce_id] = _NonceState(
            hiding_nonce,
            binding_nonce,
            commitment,
            session_id,
            counter,
        )
        return commitment

    def discard_nonce(self, nonce_id: str) -> bool:
        """Delete unused round-one state after an aborted coordination attempt."""

        return self._pending_nonces.pop(nonce_id, None) is not None

    def sign(self, package: FrostSigningPackage) -> FrostSignatureShare:
        """Validate round two, burn the nonce pair, and return ``z_i``."""

        _validate_package(self.group_info, package)
        if self.participant_id not in package.participant_ids:
            raise FrostAbortError("signer was not selected for this package")
        commitment = package.commitment_for(self.participant_id)
        state = self._pending_nonces.get(commitment.nonce_id)
        if state is None:
            raise NonceReuseError("nonce state is absent, deleted, or already used")
        if state.commitment != commitment:
            raise FrostAbortError("package changed the signer's public commitment")
        if state.session_id != package.session_id or state.counter != package.counter:
            raise FrostAbortError("nonce state belongs to another session or counter")
        if self._message_validator is not None:
            try:
                approved = self._message_validator(package)
            except Exception as error:
                # A broken policy check is a rejection, not permission to sign
                # or to recycle an already packaged commitment.
                self._pending_nonces.pop(commitment.nonce_id)
                raise MessageRejectedError(
                    "application message policy could not validate the request"
                ) from error
            if not approved:
                # The coordinator has already associated this commitment with
                # a concrete package.  Deleting it keeps the failure terminal.
                self._pending_nonces.pop(commitment.nonce_id)
                raise MessageRejectedError(
                    "application message policy rejected the request"
                )

        factors = compute_binding_factors(self.group_info, package)
        group_commitment = compute_group_commitment(
            self.group_info,
            package,
            factors,
        )
        challenge = compute_challenge(self.group_info, package, group_commitment)
        interpolation = derive_interpolating_value(
            package.participant_ids,
            self.participant_id,
            self.group_info.suite.scalar_modulus,
        )
        rho = _binding_factor_for(factors, self.participant_id)

        # Burn before returning the response.  A second call cannot recover the
        # nonce pair, even if the coordinator later aborts the whole session.
        state = self._pending_nonces.pop(commitment.nonce_id)
        q = self.group_info.suite.scalar_modulus
        response = (
            state.hiding_nonce
            + state.binding_nonce * rho
            + interpolation * self._signing_share * challenge
        ) % q
        return FrostSignatureShare(
            self.participant_id,
            response,
            package.digest,
        )


class FrostCoordinator:
    """Build signing packages, verify shares, and aggregate signatures."""

    def __init__(self, group_info: FrostGroupInfo) -> None:
        self.group_info = group_info
        self._seen_commitments: set[tuple[int, int, int]] = set()
        self._issued_packages: set[str] = set()
        self._closed_packages: set[str] = set()

    @classmethod
    def from_dkg(cls, result: DKGResult) -> "FrostCoordinator":
        return cls(FrostGroupInfo.from_dkg(result))

    def create_signing_package(
        self,
        *,
        session_id: str,
        counter: int,
        application_context: str,
        message: bytes,
        commitments: Iterable[NonceCommitment],
    ) -> FrostSigningPackage:
        """Validate and canonically sort round-one commitments."""

        supplied = tuple(commitments)
        if any(not isinstance(item, NonceCommitment) for item in supplied):
            raise TypeError("every commitment must be a NonceCommitment")
        selected = tuple(sorted(supplied, key=lambda item: item.participant_id))
        package = FrostSigningPackage(
            protocol="CryptoCave-FROST",
            version="0.5",
            session_id=session_id,
            counter=counter,
            application_context=application_context,
            message=message,
            group_info_digest=self.group_info.digest,
            commitments=selected,
        )
        _validate_package(self.group_info, package)
        public_ids = {
            (item.participant_id, item.hiding, item.binding) for item in selected
        }
        if public_ids & self._seen_commitments:
            raise NonceReuseError("coordinator has already seen a nonce commitment")

        # Computing the challenge here catches malformed elements and the rare
        # identity aggregate before any signer consumes private nonce state.
        factors = compute_binding_factors(self.group_info, package)
        group_commitment = compute_group_commitment(
            self.group_info,
            package,
            factors,
        )
        compute_challenge(self.group_info, package, group_commitment)

        self._seen_commitments.update(public_ids)
        self._issued_packages.add(package.digest)
        return package

    def verify_signature_share(
        self,
        package: FrostSigningPackage,
        signature_share: FrostSignatureShare,
    ) -> FrostSignatureShareVerification:
        """Check one response before aggregation."""

        _validate_package(self.group_info, package)
        suite = self.group_info.suite
        participant_id = signature_share.participant_id
        if signature_share.package_digest != package.digest:
            return FrostSignatureShareVerification(
                participant_id,
                False,
                0,
                0,
                "signature share is bound to another package",
            )
        if participant_id not in package.participant_ids:
            return FrostSignatureShareVerification(
                participant_id,
                False,
                0,
                0,
                "signature share belongs to an unselected participant",
            )
        if not 0 <= signature_share.value < suite.scalar_modulus:
            return FrostSignatureShareVerification(
                participant_id,
                False,
                0,
                0,
                "signature share is not a canonical scalar",
            )

        factors = compute_binding_factors(self.group_info, package)
        rho = _binding_factor_for(factors, participant_id)
        group_commitment = compute_group_commitment(
            self.group_info,
            package,
            factors,
        )
        challenge = compute_challenge(self.group_info, package, group_commitment)
        interpolation = derive_interpolating_value(
            package.participant_ids,
            participant_id,
            suite.scalar_modulus,
        )
        commitment = package.commitment_for(participant_id)

        left = suite.base_mult(signature_share.value)
        commitment_share = (
            commitment.hiding
            * suite.scalar_mult(commitment.binding, rho)
            % suite.group_modulus
        )
        key_term = suite.scalar_mult(
            self.group_info.verifying_share_for(participant_id),
            challenge * interpolation,
        )
        right = commitment_share * key_term % suite.group_modulus
        accepted = left == right
        return FrostSignatureShareVerification(
            participant_id,
            accepted,
            left,
            right,
            "signature share equation holds"
            if accepted
            else "signature share equation failed",
        )

    def verify_final(
        self,
        package: FrostSigningPackage,
        signature: FrostSignature,
    ) -> bool:
        return verify_schnorr_signature(
            package.message_to_sign(self.group_info.suite),
            signature,
            self.group_info.group_public_key,
            self.group_info.suite,
        )

    def aggregate(
        self,
        package: FrostSigningPackage,
        signature_shares: Iterable[FrostSignatureShare],
    ) -> FrostSigningResult:
        """Verify every selected share, sum responses, and verify ``(R, z)``."""

        package_digest = package.digest
        if package_digest not in self._issued_packages:
            raise FrostAbortError("coordinator did not issue this signing package")
        if package_digest in self._closed_packages:
            raise FrostAbortError("signing package is already closed")
        self._closed_packages.add(package_digest)

        selected = tuple(signature_shares)
        if any(not isinstance(item, FrostSignatureShare) for item in selected):
            raise TypeError("every response must be a FrostSignatureShare")
        identifiers = tuple(item.participant_id for item in selected)
        if len(set(identifiers)) != len(identifiers):
            raise FrostAbortError("duplicate signature shares are not allowed")
        if set(identifiers) != set(package.participant_ids):
            raise FrostAbortError("provide exactly one share per selected signer")
        ordered = tuple(sorted(selected, key=lambda item: item.participant_id))
        verifications = tuple(
            self.verify_signature_share(package, item) for item in ordered
        )
        rejected = tuple(
            item.participant_id for item in verifications if not item.accepted
        )
        if rejected:
            raise FrostAbortError(f"invalid signature shares from {rejected}")

        factors = compute_binding_factors(self.group_info, package)
        group_commitment = compute_group_commitment(
            self.group_info,
            package,
            factors,
        )
        challenge = compute_challenge(self.group_info, package, group_commitment)
        response = sum(item.value for item in ordered) % self.group_info.suite.scalar_modulus
        signature = FrostSignature(group_commitment, response)
        final_verified = self.verify_final(package, signature)
        if not final_verified:
            raise FrostAbortError("aggregate Schnorr signature failed verification")

        message_to_sign = package.message_to_sign(self.group_info.suite)
        transcript = FrostSigningTranscript(
            protocol="CryptoCave-FROST",
            version="0.5",
            session_id=package.session_id,
            counter=package.counter,
            application_context=package.application_context,
            group_info_digest=self.group_info.digest,
            package_digest=package.digest,
            payload_digest=hashlib.sha256(package.message).hexdigest(),
            signed_message_digest=hashlib.sha256(message_to_sign).hexdigest(),
            participant_ids=package.participant_ids,
            commitments=package.commitments,
            binding_factors=factors,
            group_commitment=group_commitment,
            challenge=challenge,
            signature_shares=tuple(
                (item.participant_id, item.value) for item in ordered
            ),
            signature=signature,
            final_verified=final_verified,
        )
        return FrostSigningResult(signature, verifications, transcript)


# ---------------------------------------------------------------------------
# Small orchestration helper and direct-run lesson
# ---------------------------------------------------------------------------

def run_frost_signing(
    coordinator: FrostCoordinator,
    signers: Sequence[FrostSigner],
    *,
    session_id: str,
    counter: int,
    application_context: str,
    message: bytes,
    random_byte_sources: Mapping[int, RandomBytesSource] | None = None,
) -> FrostSigningRun:
    """Run both rounds while keeping their data objects visible to the caller."""

    if not signers:
        raise ValueError("at least one signer is required")
    if any(signer.group_info != coordinator.group_info for signer in signers):
        raise ValueError("all signers and the coordinator need identical group info")
    identifiers = tuple(signer.participant_id for signer in signers)
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("signer list contains duplicate participants")
    sources = random_byte_sources or {}
    if any(identifier not in identifiers for identifier in sources):
        raise ValueError("random byte source names an unselected participant")

    commitments: list[NonceCommitment] = []
    try:
        for signer in signers:
            commitments.append(
                signer.commit(
                    session_id,
                    counter,
                    sources.get(signer.participant_id),
                )
            )
        package = coordinator.create_signing_package(
            session_id=session_id,
            counter=counter,
            application_context=application_context,
            message=message,
            commitments=commitments,
        )
        shares = tuple(signer.sign(package) for signer in signers)
        result = coordinator.aggregate(package, shares)
        return FrostSigningRun(package, result)
    except Exception:
        # If coordination fails before a signer uses its state, delete that
        # state anyway.  Conservative nonce disposal is easier to reason about.
        for signer in signers:
            for commitment in commitments:
                if commitment.participant_id == signer.participant_id:
                    signer.discard_nonce(commitment.nonce_id)
        raise


def _deterministic_source(seed: int) -> RandomBytesSource:
    """Create repeatable bytes for this module's direct-run lesson only."""

    rng = random.Random(seed)
    return rng.randbytes


def _direct_demo() -> None:
    dkg = MultiDealerDKG.educational(session_id="frost-module-dkg")
    packages = [
        dkg.create_dealer_package(
            dealer_id,
            rng=random.Random(500 + dealer_id),
        )
        for dealer_id in dkg.shamir.participant_ids
    ]
    dkg_result = dkg.run(packages)
    coordinator = FrostCoordinator.from_dkg(dkg_result)
    signers = [
        FrostSigner.from_dkg(dkg_result, participant_id)
        for participant_id in (1, 2, 3)
    ]
    run = run_frost_signing(
        coordinator,
        signers,
        session_id="frost-module-signing",
        counter=1,
        application_context="CryptoCave direct module demonstration",
        message=b"threshold signatures without reconstructing the key",
        random_byte_sources={
            participant_id: _deterministic_source(700 + participant_id)
            for participant_id in (1, 2, 3)
        },
    )
    print("CryptoCave Version 0.5 educational FROST")
    print("Selected signers:", run.package.participant_ids)
    print("Group public key:", dkg_result.public_key)
    print("Signature (R, z):", run.result.signature)
    print("Final Schnorr verification:", run.result.transcript.final_verified)
    print("The group secret was not reconstructed.")


if __name__ == "__main__":
    _direct_demo()
