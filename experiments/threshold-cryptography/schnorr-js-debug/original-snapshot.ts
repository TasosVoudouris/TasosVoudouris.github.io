import * as utils from "./utils";
import { Hex, PrivKey, Point } from "./utils";
/**
 * ### Schnorr Signature Scheme
 * Class containing static Schnorr Signatures methods
 * @author Doth-J
 */
export default class SchnorrSignatures {
  /**
   * ### Create new Private Key
   * Create a new random a private key.
   * @returns {PrivKey} A new private key in hexadecimal format.
   */
  static createPrivateKey(): PrivKey {
    return utils.bytesToHex(utils.secp256k1.utils.randomPrivateKey());
  }

  /**
   * ### Public Key from Private Key
   * Gets the public key from a private key.
   * @param {PrivKey} privateKey - The private key.
   * @returns {Hex} The public key in hexadecimal format.
   */
  static getPublicKey(privateKey: PrivKey): string {
    return utils.bytesToHex(this.getExtendedPublicKey(privateKey).bytes);
  }

  /**
   * ### Extended Public Key
   * Gets the extended public key from a private key.
   * ## X𝑖 = x𝑖 ⋅ 𝐺
   * - __𝐺__ generatorPoint
   * - __x𝑖__ privateKey
   * - __X𝑖__ publicKey
   * @param {PrivKey} privateKey - The private key.
   * @returns {{scalar: bigint, bytes: Uint8Array}} The extended public key.
   */
  static getExtendedPublicKey(privateKey: PrivKey): {
    scalar: bigint;
    bytes: Uint8Array;
  } {
    const d = utils.secp256k1.utils.normPrivateKeyToScalar(privateKey);
    const X = Point.fromPrivateKey(d);
    return {
      scalar: X.hasEvenY() ? d : utils.modN(-d),
      bytes: utils.pointToBytes(X),
    };
  }

  /**
   *
   * ### Generate Key Pair
   * Generates a new private and public key pair in hexadecimal format.
   * @returns {{privateKey: PrivKey, publicKey: string, extended: {scalar: bigint, bytes: Uint8Array}}} The generated key pair.
   */
  static generateKeyPair(): {
    privateKey: PrivKey;
    publicKey: Hex;
    extended: { scalar: bigint; bytes: Uint8Array };
  } {
    const privateKey = this.createPrivateKey();
    return {
      privateKey,
      publicKey: this.getPublicKey(privateKey),
      extended: this.getExtendedPublicKey(privateKey),
    };
  }

  /**
   * ### Aggregate Public Keys
   * Aggregate multiple public keys Pi into P.
   * ### X = Σ X𝑖, for 𝑖 in [1,n]
   * - __X𝑖__ publicKeys
   * - __X__ aggregatedPublicKey
   * @param {Hex[]} publicKeys - An array of public keys.
   * @returns {Hex} The aggregated public key
   */
  //   static aggregatePublicKeys(publicKeys: string[]): Point<bigint> {
  static aggregatePublicKeys(publicKeys: Hex[]): Hex {
    return utils.bytesToHex(
      utils.pointToBytes(
        publicKeys
          .map((key, i) => utils.ensureBytes("pub_key_" + i, key))
          .reduce(
            (aggregatePublicKey, current) =>
              aggregatePublicKey.add(
                utils.lift_x(utils.bytesToNumberBE(current))
              ),
            Point.ZERO
          )
      )
    );
  }

  /**
   * ### Generate a Nonce
   * Generates a nonce ki and the corresponding commitment to Ri.
   * Choose 𝑘𝑖 ∈ Fq
   * ## 𝑅𝑖 = 𝑘𝑖 ⋅ 𝐺
   * - __𝐺__ generatorPoint
   * - __𝑘𝑖__ nonce
   * - __𝑅𝑖__ commitmentPoint
   * @param {PrivKey} x_i - The private key of the particiant.
   * @returns {{k_i: bigint, R_i: Point<bigint>, commitment: string}} The generated commitment.
   */
  static generateNonce(
    x_i: PrivKey,
    auxRand: Hex = utils.randomBytes(32)
  ): {
    k_i: bigint;
    R_i: Uint8Array;
    commitment: string;
  } {
    const a_i = utils.ensureBytes("auxRand", auxRand, 32);
    const d_i = this.getExtendedPublicKey(x_i).scalar;
    const t_i = utils.numTo32b(
      d_i ^ utils.bytesToNumberBE(utils.taggedHash("BIP0340/aux", a_i))
    );
    const rand_i = utils.taggedHash("BIP0340/nonce", t_i);
    const k_i_ = utils.modN(utils.bytesToNumberBE(rand_i));
    if (k_i_ === 0n) throw new Error("Nonce generation failed: k_i is zero");
    const { bytes: R_i, scalar: k_i } = this.getExtendedPublicKey(k_i_);
    return { k_i, R_i, commitment: utils.bytesToHex(utils.sha256(R_i)) };
    // const nonce = this.createPrivateKey(),
    //   d = secp256k1.utils.normPrivateKeyToScalar(nonce),
    //   Ri = Point.fromPrivateKey(nonce);
    // return {
    //   ki: Ri.hasEvenY() ? d : utils.modN(-d),
    //   Ri,
    //   commitment: utils.bytesToHex(sha256(utils.pointToBytes(Ri))),
    // };
  }

  /**
   * ### Aggregates Nonces
   * Aggregate multiple commitments Ri into R.
   * ### 𝑅 = Σ 𝑅𝑖, for 𝑖 in [1,n]
   * - __𝑅𝑖__ commitmentPoints
   * - __𝑅__ aggregatedCommitmentPoint
   * @param {Uint8Array[]} R_i_points - An array of Ri points.
   * @returns {Hex} aggregatedCommitment - The aggregated nonce point.
   */
  static aggregateCommitments(R_i_points: Uint8Array[]): Hex {
    return utils.bytesToHex(
      utils.pointToBytes(
        R_i_points.reduce(
          (agg, cur) => agg.add(utils.lift_x(utils.bytesToNumberBE(cur))),
          Point.ZERO
        )
      )
    ); // Convert the aggregated point back to bytes
  }

  /**
   * ### Generate Partial Signature
   * Generates a partial signature for a message m using an aggregatedCommitment point R and the chosen nonce ki
   * ### e = H (m ∣∣ 𝑅 ∣∣ X)
   * - __m__ message
   * - __𝑅__ aggregatedCommitmentPoint
   * - __X__ aggregatedPublicKey
   * - __e__ challenge
   * ### s𝑖 = k𝑖 + x𝑖 * e
   * - __x𝑖__ privateKey
   * - __e__ challenge
   * - __s𝑖__ partialSignature
   * @param {Hex} message - The message to be signed (m)
   * @param {PrivKey} x_i - The private key (d)
   * @param {bigint} k_i - Random private nonce key (k)
   * @param {Hex} R - Aggregated nonces point (R)
   * @param {Hex} X - Aggregated public Key (X)
   * @returns {Uint8Array} The partial signature (s)
   */
  static partialSign(
    message: Hex,
    x_i: PrivKey,
    k_i: bigint,
    R: Hex,
    X: Hex
  ): Uint8Array {
    const m = utils.ensureBytes("message", message);
    const pub = utils.ensureBytes("public_key", X);
    const d_i = this.getExtendedPublicKey(x_i).scalar;
    const e = utils.challenge(utils.hexToBytes(R as string), pub, m);
    return utils.numTo32b(utils.modN(k_i + e * d_i));
  }

  /**
   * ### Aggregate Partial Signatures
   * Aggregates partial signatures to the final signature
   * ### s = Σ s𝑖, for 𝑖 in [1,n]
   * - __s𝑖__ partialSignatures
   * - __s__ finalSignature
   * @param {Uint8Array[]} partialSigs - Array of partial signatures
   * @param {Hex} R - Aggregated nonces points R
   * @returns {Hex} The aggregated signature in hexadecimal format.
   */
  static aggregateSignatures(partialSigs: Uint8Array[], R: Hex): Hex {
    const combinedSig = new Uint8Array(64);
    combinedSig.set(utils.hexToBytes(R as string), 0);
    let s = 0n;
    for (const partialSig of partialSigs) {
      s = utils.modN(s + utils.bytesToNumberBE(partialSig));
    }
    combinedSig.set(utils.numTo32b(s), 32);
    return utils.bytesToHex(combinedSig);
  }

  /**
   * ### Verify a Signature
   * Verifies a signature using the original message and public key
   * ### e = H (m ∣∣ 𝑅 ∣∣ X)
   * - __m__ message
   * - __𝑅__ aggregatedCommitmentPoint
   * - __X__ aggregatedPublicKey
   * - __e__ challenge
   * ### s⋅𝐺 = R + e⋅X
   * - __s__ signature
   * - __𝐺__ generatorPoint
   * - __e__ challenge
   * - __𝑅__ aggregatedCommitmentPoint
   * - __X__ aggregatedPublicKey
   * @param {string} message - The signed message.
   * @param {Hex} signature - The signature in hexadecimal format.
   * @param {Hex} publicKey - The public key in hexadecimal format.
   * @returns {boolean} True if the signature is valid, false otherwise.
   */
  static verifySignature(
    message: Hex,
    signature: Hex,
    publicKey: Hex
  ): boolean {
    const m = utils.ensureBytes("message", message);
    const sig = utils.ensureBytes("signature", signature, 64);
    const pub = utils.ensureBytes("publicKey", publicKey, 32);
    try {
      const P = utils.lift_x(utils.bytesToNumberBE(pub)); // P = lift_x(int(pk)); fail if that fails
      const r = utils.bytesToNumberBE(sig.subarray(0, 32)); // Let r = int(sig[0:32]); fail if r ≥ p.
      if (!utils.fe(r)) return false;
      const s = utils.bytesToNumberBE(sig.subarray(32, 64)); // Let s = int(sig[32:64]); fail if s ≥ n.
      if (!utils.ge(s)) return false;
      const R = Point.BASE.multiply(r); // R = r⋅G
      const e = utils.challenge(
        m,
        utils.pointToBytes(R),
        utils.pointToBytes(P)
      ); // e = challenge(m, R, X)
      const check = utils.GmulAdd(P, s, utils.modN(-e)); // check = s⋅G - e⋅P
      console.log(R.x);
      console.log(check?.x);
      if (!check) return false;
      return R.equals(check); // Verify if R equals check
    } catch (error) {
      return false;
    }
  }
}

const numParticipants = 3;

// Step 1: Key Generation & Public Key
const participants = [];
for (let i = 0; i < numParticipants; i++) {
  participants.push(SchnorrSignatures.generateKeyPair());
}
const publicKey = SchnorrSignatures.aggregatePublicKeys(
  participants.map(({ publicKey }) => publicKey)
);
console.log("Aggregated Public Key:", publicKey);

// Step 2: Commitment Nonce Generation
const commitments = [];
for (let i = 0; i < numParticipants; i++) {
  commitments.push(SchnorrSignatures.generateNonce(participants[i].privateKey));
  console.log(
    "Commitments:",
    commitments.map((com) => com.commitment)
  );
}

// Step 3: Aggregate Nonce
const aggregateNoncePoint = SchnorrSignatures.aggregateCommitments(
  commitments.map((nonce) => nonce.R_i)
);

// console.log("Aggregated Nonce Point:", aggregateNoncePoint);

// // Step 4: Partial Signature
const message = new TextEncoder().encode("Hello, world!");
const partialSignatures = [];
for (let i = 0; i < numParticipants; i++) {
  partialSignatures.push(
    SchnorrSignatures.partialSign(
      message,
      participants[i].privateKey,
      commitments[i].k_i,
      aggregateNoncePoint,
      publicKey
    )
  );
}
console.log("Partials Signatures:", partialSignatures);

// // Step 5: Aggregate Signatures
const aggregateSignature = SchnorrSignatures.aggregateSignatures(
  partialSignatures,
  aggregateNoncePoint
);

// The aggregate signature now can be verified using the public keys and the message
console.log(
  "Aggregate Signature:",
  aggregateSignature,
  aggregateSignature.length
);
// console.log("Aggregate PublicKey:", publicKey, publicKey.length);

// // // Step 6: Verify Signatures
const verification = SchnorrSignatures.verifySignature(
  message,
  aggregateSignature,
  publicKey
);

console.log("Verification:", verification);

// Nobles library single point signature example
// import { schnorr } from "@noble/curves/secp256k1";
// const priv = schnorr.utils.randomPrivateKey();
// const pub = schnorr.getPublicKey(priv);
// const msg = new TextEncoder().encode(process.argv[2]);
// const sig = schnorr.sign(msg, priv);
// const isValid = schnorr.verify(sig, msg, pub);
// console.log(priv);
// console.log(pub);
// console.log(msg);
// console.log(sig);
// console.log(isValid);