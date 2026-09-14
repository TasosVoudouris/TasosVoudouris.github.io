from Crypto.Util.number import long_to_bytes as l2b, bytes_to_long as b2l
from Crypto.Hash import SHA256, SHA512
import os

def sample():
    return randrange(2, q-1)

def encode_point(point):
    # compressed format
    x, y, _ = list(map(int, point))
    return (b'\x02' if y % 2 == 0 else b'\x03') + x.to_bytes(32, 'big')

def hash256(*args):
    H = SHA256.new()
    for arg in args:
        H.update(arg)
    return b2l(H.digest())

def H1(*args):
    return hash256(*args)

def H2(*args):
    H = SHA512.new()
    for arg in args:
        H.update(arg)
    return b2l(H.digest()[:256//8])

class Participant:
    def __init__(self, _id):
        self.id = _id
        self.shares = dict(zip(range(1, n+1), [() for _ in range(n)]))

    def generate_polynomial(self):
        self.poly = [Kq.random_element() for _ in range(t)]
        self.a0 = int(self.poly[0])

    def _f(self, x):
        return int(sum([coeff * x**i for i, coeff in enumerate(self.poly)]))

    def generate_share(self, x):
        return (x, self._f(x))

    def compute_lagrange_coefficient(self, signers):
        λ = 1
        for signer in signers:
            if self.id == signer.id:
                continue
            λ *= (Kq(signer.id) / Kq(signer.id - self.id))
        return int(λ)

    def compute_proof_of_knowledge(self):
        k = sample()
        self.R = G * k
        # c = H(id | Φ | G * a0 | R)
        c = hash256(l2b(self.id), 'Φ'.encode(), encode_point(G * self.a0), encode_point(self.R))
        self.μ = int(k + self.a0 * c)
        self.σ = (self.R, self.μ)

    def compute_public_commitment(self):
        self.C = [G * int(coeff) for coeff in self.poly]

    def verify_participants(self, parties):
        for l in range(1, n+1):
            if l == self.id:
                continue
            
            party = parties[l-1]

            Rl, μl = party.σ
            cl = hash256(l2b(party.id), 'Φ'.encode(), encode_point(party.C[0]), encode_point(Rl))
            verified = Rl == G * μl + party.C[0] * (-cl)
            if not verified:
                print(f"[-] Party{self.id} could not verify Party{party.id} :(")
            else:
                print(f'[+] Party{self.id} verified Party{party.id}')

    def send_share_to(self, parties):
        self.shares[self.id] = self.generate_share(self.id)

        for l in range(1, n+1):
            if l == self.id:
                continue

            party = parties[l-1]
            party.shares[self.id] = self.generate_share(party.id)

        self.poly = []

    def verify_shares(self, parties):
        for l in range(1, n+1):
            if l == self.id:
                continue

            party = parties[l-1]

            verified = G * self.shares[l][1] == sum(party.C[k] * (self.id**k) for k in range(t))

            if not verified:
                print(f"[-] Party{self.id} could not verify the share of Party{party.id} :(")
            else:
                print(f'[+] Party{self.id} verified the share of Party{party.id}')

    def compute_private_signing_share(self):
        self.si = 0
        for l in range(1, n+1):
            self.si += self.shares[l][1]
            if l != self.id:
                self.shares[l] = ()

    def compute_public_verification_share(self):
        self.Y = G * self.si

    def generate_nonce_commitment_share_pair_list(self, pi):
        # pi = number of signatures we want to generate
        # one nonce pair per signature
        # once a pair is used for a signature, discard it
        self.L = []
        self.nonce_commitment_pairs = []
        for j in range(1, pi+1):
            dj, ej = [sample() for _ in range(2)]   # private nonces
            Dj, Ej = G*dj, G*ej 
            self.L.append((Dj, Ej))
            self.nonce_commitment_pairs.append([(dj, Dj), (ej, Ej)])

    def compute_binding_group_commitment_and_challenge(self, tup, groupY, Bencoded):
        m, B = tup
        # SignProtocol . Step 3
        assert m and all(E.is_on_curve(Di[0], Di[1]) and E.is_on_curve(Ei[0], Ei[1]) for _, Di, Ei in B), "Either the message is not validated or Dl, El not in G*"

        self.binding_values = [H1(str(B[l][0]).encode(), m, Bencoded) for l in range(len(B))]
        R = sum(B[l][1] + B[l][2] * self.binding_values[l] for l in range(len(B)))
        self.challenge = H2(encode_point(R), encode_point(groupY), m)

    def compute_z(self, i, signers):
        (di, _), (ei, _) = self.nonce_commitment_pairs.pop(0)   # delete ((di, Di), (ei, Ei))
        self.λ = self.compute_lagrange_coefficient(signers)
        self.z = di + (ei * self.binding_values[i]) + self.λ * self.si * self.challenge




class FROST:
    def __init__(self, t, n, a):
        self.t = t
        self.n = n
        self.a = a
        self.parties = [Participant(i) for i in range(1, n+1)]
        self.groupY = 0
    
    def save_B_encoded(self, B):
        self.Bencoded = b''
        for _id, Di, Ei in B:
            self.Bencoded += str(_id).encode() + encode_point(Di) + encode_point(Ei)
    
    def sa_aggregation(self, m):
        binding_values = [H1(str(signer.id).encode(), m, self.Bencoded) for signer in self.signers]
        Ri = []
        for i, signer in enumerate(self.signers):
            Ri.append(signer.L[0][0] + signer.L[0][1] * binding_values[i])
            signer.L.pop(0)
        R = sum(Ri)
        challenge = H2(encode_point(R), encode_point(self.groupY), m)
        
        for i, signer in enumerate(self.signers):
            assert G * signer.z == Ri[i] + signer.Y * (challenge * signer.λ)
            print(f'[+] SA verified Party{i+1}')

        return R

    def FROSTKeyGen(self):
        ### Round 1 ###
        for party in self.parties:
            # 1.1
            party.generate_polynomial()
            # 1.2
            party.compute_proof_of_knowledge()
            # 1.3
            party.compute_public_commitment()
            # 1.4
            # print('[+] Broadcasting :', party.C, party.σ)

        # 1.5
        for party in self.parties: 
            party.verify_participants(self.parties)

        ### Round 2 ###

        # 2.1
        for party in self.parties:
            party.send_share_to(self.parties)
        
        # 2.2
        for party in self.parties:
            party.verify_shares(self.parties)
            # 2.3
            party.compute_private_signing_share()
            # 2.4
            party.compute_public_verification_share()
            # group's public key
            self.groupY += party.C[0]
    
    def FROSTPreprocess(self, π):
        for party in self.parties:
            # 1
            party.generate_nonce_commitment_share_pair_list(π)
            # 2
            # print(party.id, party.L)
    
    def FROSTSign(self, m):
        # 1
        self.signers = self.parties[:self.a]
        B = [(signer.id, signer.L[0][0], signer.L[0][1]) for signer in self.signers]

        # CUSTOM STEP
        self.save_B_encoded(B)  # precompute the encoded B to be used in the computation of the binding factors

        assert len(B) == a
        # 2
        for signer in self.signers:
            # send (m, B) to Pi
            # 3, 4
            signer.compute_binding_group_commitment_and_challenge((m, B), self.groupY, self.Bencoded)
        
        for i, signer in enumerate(self.signers):
            # 5
            signer.compute_z(i, self.signers)

        R = self.sa_aggregation(m)

        z = sum(signer.z for signer in self.signers)

        return (R, z)


# secp256k1 curve
p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
Kp = GF(p)
E = EllipticCurve(Kp, (0, 7))
G = E(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798, 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)
q = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
E.set_order(q)
Kq = GF(q)



messages = [os.urandom(20) for _ in range(20)]

### FROST parameters ###
t = 4
n = 5
π = len(messages)
a = n
########################

frost = FROST(t, n, a)

frost.FROSTKeyGen()
frost.FROSTPreprocess(π)
for i in range(π):
    print(f'message = {messages[i].hex()} | signature : {frost.FROSTSign(messages[i])}')