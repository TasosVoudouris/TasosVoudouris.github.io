import assert from 'node:assert/strict';
import {
  createSigner,
  signRegisteredNofN,
  verifyWithNoble,
} from './fixed-noble-v2.mjs';

const signers = ['Peer-A', 'Peer-B', 'Peer-C'].map(createSigner);

let fixed = 0;
for (let i = 0; i < 100; i++) {
  const result = signRegisteredNofN(signers, `message-${i}`);
  if (verifyWithNoble(result)) fixed++;
}
assert.equal(fixed, 100, 'fixed implementation must verify every session');

// Reproduce the historic parity symptom with a fixed aggregate key:
// omit ONLY the aggregate-nonce even-Y correction.
let parityBugSuccesses = 0;
for (let i = 0; i < 200; i++) {
  const result = signRegisteredNofN(signers, `broken-${i}`, { fixNonceParity: false });
  if (verifyWithNoble(result)) parityBugSuccesses++;
}

console.log(`fixed: ${fixed}/100`);
console.log(`nonce parity omitted: ${parityBugSuccesses}/200 (expected around 50%)`);
assert.ok(parityBugSuccesses > 55 && parityBugSuccesses < 145,
  'parity-bug success rate should be statistically near one half');
