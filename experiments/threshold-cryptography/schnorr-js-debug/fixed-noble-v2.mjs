/**
 * CryptoCave: corrected n-of-n aggregate Schnorr demonstration.
 *
 * This is intentionally NOT FROST and NOT a replacement for MuSig2.
 * It is a BIP340-compatible educational reconstruction of the original
 * three-party experiment under a registered-key / honest-protocol model.
 *
 * Tested API target: @noble/curves 2.4.0, @noble/hashes 2.4.0.
 */
import { secp256k1, schnorr } from '@noble/curves/secp256k1.js';
import {
  bytesToHex,
  bytesToNumberBE,
  concatBytes,
  equalBytes,
  numberToBytesBE,
  randomBytes,
} from '@noble/curves/utils.js';
import { sha256 } from '@noble/hashes/sha2.js';

const Point = secp256k1.Point;
const G = Point.BASE;
const ZERO = Point.ZERO;
const N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141n;
const utf8 = new TextEncoder();
const DOMAIN_POP = utf8.encode('CryptoCave/SchnorrPoP/v1');
const DOMAIN_NONCE_COMMIT = utf8.encode('CryptoCave/SchnorrNonceCommit/v1');

const modN = (x) => {
  const r = x % N;
  return r >= 0n ? r : r + N;
};
const isEvenY = (P) => (P.y & 1n) === 0n;
const xOnly = (P) => numberToBytesBE(P.x, 32);
const sumPoints = (points) => points.reduce((acc, P) => acc.add(P), ZERO);

function scalarFromSecretKey(secretKey) {
  const d = bytesToNumberBE(secretKey);
  if (d <= 0n || d >= N) throw new Error('invalid secp256k1 secret scalar');
  return d;
}

/** BIP340 x-only normalization for one ordinary key. */
function normalizeIndividualKey(secretKey) {
  let d = scalarFromSecretKey(secretKey);
  let P = G.multiply(d);
  if (!isEvenY(P)) {
    d = N - d;
    P = P.negate();
  }
  return { d, P, publicKey: xOnly(P) };
}

function popMessage(publicKey) {
  return sha256(concatBytes(DOMAIN_POP, publicKey));
}

/**
 * Registration uses a normal BIP340 proof-of-possession to avoid treating an
 * arbitrary attacker-chosen point as an authenticated signer key.
 * This is still an educational construction, not a MuSig2 security proof.
 */
export function createSigner(id) {
  const { secretKey } = schnorr.keygen();
  const normalized = normalizeIndividualKey(secretKey);
  const proofOfPossession = schnorr.sign(popMessage(normalized.publicKey), secretKey);
  if (!schnorr.verify(proofOfPossession, popMessage(normalized.publicKey), normalized.publicKey)) {
    throw new Error(`proof of possession failed for ${id}`);
  }
  return { id, secretKey, ...normalized, proofOfPossession };
}

export function aggregateRegisteredKeys(signers) {
  for (const signer of signers) {
    if (!schnorr.verify(signer.proofOfPossession, popMessage(signer.publicKey), signer.publicKey)) {
      throw new Error(`invalid proof of possession for ${signer.id}`);
    }
  }
  let Q = sumPoints(signers.map((s) => s.P));
  if (Q.is0()) throw new Error('aggregate public key is point at infinity');
  const keyNegated = !isEvenY(Q);
  if (keyNegated) Q = Q.negate();
  return { Q, keyNegated, publicKey: xOnly(Q) };
}

function nonceCommitment(sessionId, signerId, publicKey, msg32, compressedNoncePoint) {
  return sha256(
    concatBytes(
      DOMAIN_NONCE_COMMIT,
      sessionId,
      utf8.encode(signerId),
      publicKey,
      msg32,
      compressedNoncePoint,
    ),
  );
}

export function commitNonce(signer, sessionId, publicKey, msg32) {
  const k = bytesToNumberBE(schnorr.utils.randomSecretKey());
  const R = G.multiply(k);
  const reveal = R.toBytes(true); // full compressed point: parity is preserved internally
  const commitment = nonceCommitment(sessionId, signer.id, publicKey, msg32, reveal);
  return { signerId: signer.id, k, R, reveal, commitment, used: false };
}

export function verifyNonceReveal(sessionId, publicKey, msg32, nonceState, frozenCommitment) {
  const expected = nonceCommitment(sessionId, nonceState.signerId, publicKey, msg32, nonceState.reveal);
  if (!equalBytes(expected, frozenCommitment)) {
    throw new Error(`bad nonce reveal for ${nonceState.signerId}`);
  }
  const decoded = Point.fromBytes(nonceState.reveal);
  if (!decoded.equals(nonceState.R)) throw new Error('nonce reveal / local point mismatch');
}

function challenge(rX, publicKey, msg32) {
  return modN(
    bytesToNumberBE(
      schnorr.utils.taggedHash('BIP0340/challenge', rX, publicKey, msg32),
    ),
  );
}

/**
 * One signing session.
 * Message is hashed to 32 bytes before entering the BIP340 transcript.
 */
export function signRegisteredNofN(signers, message, options = {}) {
  const { fixKeyParity = true, fixNonceParity = true } = options;
  const sessionId = randomBytes(32);
  const msg32 = sha256(typeof message === 'string' ? utf8.encode(message) : message);

  // Key aggregation phase.
  const keyAgg = aggregateRegisteredKeys(signers);

  // Round 1: commit. No R_i is revealed until all commitments are fixed.
  const nonces = signers.map((s) => commitNonce(s, sessionId, keyAgg.publicKey, msg32));
  const commitments = new Map(
    nonces.map((n) => [n.signerId, Uint8Array.from(n.commitment)]),
  );

  // Round 2: reveal and verify each R_i against the prior commitment.
  for (const nonce of nonces) {
    const frozen = commitments.get(nonce.signerId);
    if (!frozen) throw new Error('missing nonce commitment');
    verifyNonceReveal(sessionId, keyAgg.publicKey, msg32, nonce, frozen);
  }

  let R = sumPoints(nonces.map((n) => n.R));
  if (R.is0()) throw new Error('aggregate nonce is point at infinity');
  const nonceNegated = !isEvenY(R);
  if (fixNonceParity && nonceNegated) R = R.negate();

  const rX = xOnly(R);
  const e = challenge(rX, keyAgg.publicKey, msg32);

  const partials = [];
  for (let i = 0; i < signers.length; i++) {
    const signer = signers[i];
    const nonce = nonces[i];
    if (nonce.used) throw new Error(`nonce reuse detected for ${signer.id}`);

    let d = signer.d;
    let k = nonce.k;
    if (fixKeyParity && keyAgg.keyNegated) d = N - d;
    if (fixNonceParity && nonceNegated) k = N - k;

    const s_i = modN(k + e * d);
    nonce.used = true;
    partials.push({ signerId: signer.id, s_i });
  }

  const s = partials.reduce((acc, p) => modN(acc + p.s_i), 0n);
  const signature = concatBytes(rX, numberToBytesBE(s, 32));

  return {
    signature,
    publicKey: keyAgg.publicKey,
    msg32,
    partials,
    diagnostics: {
      keyNegated: keyAgg.keyNegated,
      nonceNegated,
      rX: bytesToHex(rX),
      publicKey: bytesToHex(keyAgg.publicKey),
    },
  };
}

export function verifyWithNoble(result) {
  return schnorr.verify(result.signature, result.msg32, result.publicKey);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const signers = ['Peer-A', 'Peer-B', 'Peer-C'].map(createSigner);
  const result = signRegisteredNofN(signers, 'Hello from CryptoCave');
  console.log(result.diagnostics);
  console.log('signature:', bytesToHex(result.signature));
  console.log('verified:', verifyWithNoble(result));
}
