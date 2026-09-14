/**
 * Dependency-free secp256k1/BIP340 reference model for the CryptoCave article.
 * Uses Node's built-in SHA-256 and CSPRNG only.
 *
 * The goal is transparency and reproducibility, not performance or production use.
 */
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2fn;
const N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141n;
const G = {
  x: 55066263022277343669578718895168534326250603453777594175500187360389116729240n,
  y: 32670510020758816978083085130507043184471273380659243275938904335757337482424n,
};

const mod = (x, m = P) => {
  const r = x % m;
  return r >= 0n ? r : r + m;
};
const modN = (x) => mod(x, N);

function invert(a, m = P) {
  let oldR = mod(a, m), r = m;
  let oldS = 1n, s = 0n;
  while (r !== 0n) {
    const q = oldR / r;
    [oldR, r] = [r, oldR - q * r];
    [oldS, s] = [s, oldS - q * s];
  }
  if (oldR !== 1n) throw new Error('not invertible');
  return mod(oldS, m);
}

const neg = (A) => (A ? { x: A.x, y: mod(-A.y) } : null);

function add(A, B) {
  if (!A) return B;
  if (!B) return A;
  if (A.x === B.x) {
    if (mod(A.y + B.y) === 0n) return null;
    const slope = mod(3n * A.x * A.x * invert(2n * A.y));
    const x3 = mod(slope * slope - 2n * A.x);
    return { x: x3, y: mod(slope * (A.x - x3) - A.y) };
  }
  const slope = mod((B.y - A.y) * invert(B.x - A.x));
  const x3 = mod(slope * slope - A.x - B.x);
  return { x: x3, y: mod(slope * (A.x - x3) - A.y) };
}

function mul(k, A = G) {
  k = modN(k);
  let R = null;
  let Q = A;
  while (k !== 0n) {
    if (k & 1n) R = add(R, Q);
    Q = add(Q, Q);
    k >>= 1n;
  }
  return R;
}

function powMod(a, e, m = P) {
  let r = 1n;
  a = mod(a, m);
  while (e !== 0n) {
    if (e & 1n) r = (r * a) % m;
    a = (a * a) % m;
    e >>= 1n;
  }
  return r;
}

function liftX(x) {
  if (!(0n < x && x < P)) throw new Error('x outside field');
  const c = mod(x * x * x + 7n);
  let y = powMod(c, (P + 1n) / 4n);
  if (mod(y * y) !== c) throw new Error('x does not lift to secp256k1');
  if (y & 1n) y = P - y;
  return { x, y };
}

function bytes32(x) {
  const out = Buffer.alloc(32);
  let n = x;
  for (let i = 31; i >= 0; i--) {
    out[i] = Number(n & 255n);
    n >>= 8n;
  }
  return out;
}
const bytesToInt = (b) => BigInt(`0x${Buffer.from(b).toString('hex')}`);

function taggedHash(tag, ...parts) {
  const t = createHash('sha256').update(tag, 'utf8').digest();
  return createHash('sha256').update(t).update(t).update(Buffer.concat(parts.map(Buffer.from))).digest();
}

const challenge = (rX, pX, msg32) =>
  bytesToInt(taggedHash('BIP0340/challenge', bytes32(rX), bytes32(pX), msg32)) % N;

let deterministicCounter = 0;
function randomScalar() {
  // Deterministic on purpose: this is a reproducible debugging model, not a signer.
  while (true) {
    const seed = `CryptoCave/schnorr-debug/reference-v1/${deterministicCounter++}`;
    const x = bytesToInt(createHash('sha256').update(seed, 'utf8').digest());
    if (0n < x && x < N) return x;
  }
}

function normalizeIndividualSecret(d) {
  let P_i = mul(d);
  if (P_i.y & 1n) {
    d = N - d;
    P_i = neg(P_i);
  }
  return { d, P_i };
}

function setupParticipants(count = 3) {
  const participants = [];
  for (let i = 0; i < count; i++) participants.push(normalizeIndividualSecret(randomScalar()));
  let Q = participants.reduce((acc, p) => add(acc, p.P_i), null);
  const keyNegated = !!(Q.y & 1n);
  if (keyNegated) Q = neg(Q);
  return { participants, Q, keyNegated };
}

function verifyBip340(signature, msg32, pX) {
  const r = bytesToInt(signature.subarray(0, 32));
  const s = bytesToInt(signature.subarray(32, 64));
  if (!(0n < r && r < P && 0n < s && s < N)) return false;
  let Q;
  try { Q = liftX(pX); } catch { return false; }
  const e = challenge(r, pX, msg32);
  const R = add(mul(s), neg(mul(e, Q)));
  return !!R && !(R.y & 1n) && R.x === r;
}

function signSession(setup, msg32, { fixKeyParity = true, fixNonceParity = true } = {}) {
  const nonces = setup.participants.map(() => {
    const k = randomScalar();
    return { k, R_i: mul(k) };
  });
  let R = nonces.reduce((acc, n) => add(acc, n.R_i), null);
  const nonceNegated = !!(R.y & 1n);
  if (fixNonceParity && nonceNegated) R = neg(R);

  const e = challenge(R.x, setup.Q.x, msg32);
  let s = 0n;
  for (let i = 0; i < setup.participants.length; i++) {
    let d = setup.participants[i].d;
    let k = nonces[i].k;
    if (fixKeyParity && setup.keyNegated) d = N - d;
    if (fixNonceParity && nonceNegated) k = N - k;
    s = modN(s + k + e * d);
  }
  return Buffer.concat([bytes32(R.x), bytes32(s)]);
}

const msg32 = createHash('sha256').update('CryptoCave distributed Schnorr debug').digest();
const fixedSetup = setupParticipants(3);

let fixedOk = 0;
for (let i = 0; i < 40; i++) {
  if (verifyBip340(signSession(fixedSetup, msg32), msg32, fixedSetup.Q.x)) fixedOk++;
}
assert.equal(fixedOk, 40);

let parityBugOk = 0;
for (let i = 0; i < 100; i++) {
  const sig = signSession(fixedSetup, msg32, { fixKeyParity: true, fixNonceParity: false });
  if (verifyBip340(sig, msg32, fixedSetup.Q.x)) parityBugOk++;
}

console.log(`corrected implementation: ${fixedOk}/40 verified`);
console.log(`aggregate-nonce parity fix removed: ${parityBugOk}/100 verified (deterministic sample; expected rate ≈50%)`);
assert.ok(parityBugOk > 20 && parityBugOk < 80);
