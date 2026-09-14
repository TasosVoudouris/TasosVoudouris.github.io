---
title: "The RSA Cryptosystem: Extended Reference"
description: "A detailed RSA reference covering the protocol, message representation, encryption/decryption mechanics, multiplicative structure, and implementation examples."
pubDate: "2025-05-27"
updatedDate: '2026-09-12'
topics:
- "Public-Key Cryptography"
- "Number Theory"
- "Cryptographic Engineering"
tags:
- "rsa"
- "modular-exponentiation"
- "euler-phi"
- "public-key-encryption"
difficulty: "Intermediate"
sourcePath: "experiments/ready-material/rsa-reference"
draft: false
---
We have already discussed Diffie-Hellman key exchange, whose security rests on the difficulty of the discrete logarithm problem.

Although this represents progress towards secure communication, it is particularly vulnerable to problems of authentication, like we saw with the "man-in-the-middle attack". To avoid such an attack, we need some type of authentication.  We need something *asymmetric* -- something one person can do that no other person can do, like a verifiable signature, so that we can be sure we're communicating with the intended person.  For such a purpose, we introduce the RSA cryptosystem.  Computationally based on modular exponentiation, its security rests on the difficulty of factoring large numbers.


## The RSA protocol
Like Diffie-Hellman, the RSA protocol involves a series of computations in modular arithmetic, taking care to keep some numbers private while making others public.  RSA was published two years after Diffie-Hellman, in 1978 by Rivest, Shamir, and Adelman (hence its name).  The great advance of the RSA protocol was its *asymmetry*.  While Diffie-Hellman is used for symmetric key cryptography (using the same key to encrypt and decrypt), the RSA protocol has two keys:  a *public key** that can be used by anyone for encryption and a *private key* that can be used by its owner for decryption.  

In this way, if Alice publishes her public key online, anyone can send her an encrypted message.  But as long as she keeps her private key private, *only* Alice can decrypt the messages sent to her.  Such an asymmetry allows RSA to be used for authentication -- if the owner of a private key has an ability nobody else has, then this ability can be used to prove the owner's identity.  In practice, this is one of the most common applications of RSA, guaranteeing that we are communicating with the intended person.
In the RSA protocol, the *private key* is a pair of large (e.g. 512 bit) prime numbers, called $p$ and $q$.  The *public key* is the pair $(N, e)$, where $N$ is defined to be the product $N = pq$ and $e$ is an auxiliary number called the exponent.  The number $e$ is often (for computational efficiency and other reasons) taken to be 65537 -- the same number $e$ can be used over and over by different people.  But it is absolutely crucial that the same private keys $p$ and $q$ are not used by different individuals.  Individuals must create and safely keep their own private key.
We begin with the creation of a private key $(p,q)$.  We use the `SystemRandom` function to "cook up" cryptographically secure random numbers, and the Miller-Rabin test to certify primality.


#### Key Generation  
1. Pick two distinct large primes $ p, q $.  
2. Compute $ N = p \cdot q $.  
3. Compute Euler's totient function:  
   $$ \phi(N) = (p-1)(q-1) $$
4. Pick a number $ e $ such that $ \gcd(e, \phi(N)) = 1 $ (usually $ e = 65537 $).  
5. Compute the modular inverse:  
   $$ d = e^{-1} \mod \phi(N) $$
6. **Public key**: $ \{N, e\} $  
7. **Private key**: $ \{d\} $ (values $ p, q, \phi(N) $ should be kept secret). 

```python
from random import SystemRandom, randint

def Miller_Rabin(p, base):
    '''
    Tests whether p is prime, using the given base.
    The result False implies that p is definitely not prime.
    The result True implies that p **might** be prime.
    It is not a perfect test!
    '''
    result = 1
    exponent = p-1
    modulus = p
    bitstring = bin(exponent)[2:] # Chop off the '0b' part of the binary expansion of exponent
    for bit in bitstring: # Iterates through the "letters" of the string.  Here the letters are '0' or '1'.
        sq_result = result*result % modulus  # We need to compute this in any case.
        if sq_result == 1:
            if (result != 1) and (result != exponent):  # Note that exponent is congruent to -1, mod p.
                return False  # a ROO violation occurred, so p is not prime
        if bit == '0':
            result = sq_result 
        if bit == '1':
            result = (sq_result * base) % modulus
    if result != 1:
        return False  # a FLT violation occurred, so p is not prime.
    
    return True  # If we made it this far, no violation occurred and p might be prime.

def is_prime(p, witnesses=50):  # witnesses is a parameter with a default value.
    '''
    Tests whether a positive integer p is prime.
    For p < 2^64, the test is deterministic, using known good witnesses.
    Good witnesses come from a table at Wikipedia's article on the Miller-Rabin test,
    based on research by Pomerance, Selfridge and Wagstaff, Jaeschke, Jiang and Deng.
    For larger p, a number (by default, 50) of witnesses are chosen at random.
    '''
    if (p%2 == 0): # Might as well take care of even numbers at the outset!
        if p == 2:
            return True
        else:
            return False 
    
    if p > 2**64:  # We use the probabilistic test for large p.
        trial = 0
        while trial < witnesses:
            trial = trial + 1
            witness = randint(2,p-2) # A good range for possible witnesses
            if Miller_Rabin(p,witness) == False:
                return False
        return True
    
    else:  # We use a determinisic test for p <= 2**64.
        verdict = Miller_Rabin(p,2)
        if p < 2047:
            return verdict # The witness 2 suffices.
        verdict = verdict and Miller_Rabin(p,3)
        if p < 1373653:
            return verdict # The witnesses 2 and 3 suffice.
        verdict = verdict and Miller_Rabin(p,5)
        if p < 25326001:
            return verdict # The witnesses 2,3,5 suffice.
        verdict = verdict and Miller_Rabin(p,7)
        if p < 3215031751:
            return verdict # The witnesses 2,3,5,7 suffice.
        verdict = verdict and Miller_Rabin(p,11)
        if p < 2152302898747:
            return verdict # The witnesses 2,3,5,7,11 suffice.
        verdict = verdict and Miller_Rabin(p,13)
        if p < 3474749660383:
            return verdict # The witnesses 2,3,5,7,11,13 suffice.
        verdict = verdict and Miller_Rabin(p,17)
        if p < 341550071728321:
            return verdict # The witnesses 2,3,5,7,11,17 suffice.
        verdict = verdict and Miller_Rabin(p,19) and Miller_Rabin(p,23)
        if p < 3825123056546413051:
            return verdict # The witnesses 2,3,5,7,11,17,19,23 suffice.
        verdict = verdict and Miller_Rabin(p,29) and Miller_Rabin(p,31) and Miller_Rabin(p,37)
        return verdict # The witnesses 2,3,5,7,11,17,19,23,29,31,37 suffice for testing up to 2^64. 
    

def random_prime(bitlength):
    while True:
        p = SystemRandom().getrandbits(bitlength)  # A cryptographically secure random number.
        if is_prime(p):
            return p
random_prime(100) # A random 100-bit prime
random_prime(512) # A random 512-bit prime.  Should be quick, thanks to Miller-Rabin!
%timeit random_prime(1024)  # Even 1024-bit primes should be quick!
def RSA_privatekey(bitlength):
    '''
    Create private key for RSA, with given bitlength.
    Just a pair of big primes!
    '''
    p = random_prime(bitlength)
    q = random_prime(bitlength)
    return p,q # Returns both values, as a "tuple"
type(RSA_privatekey(8))  # When a function returns multiple values, the type is "tuple".
p,q = RSA_privatekey(512)  # If a function outputs two values, you can assign them to two variables.
print("Private key p = {}".format(p))
print("Private key q = {}".format(q))
def RSA_publickey(p,q, e = 65537):
    '''
    Makes the RSA public key out of 
    two prime numbers p,q (the private key), 
    and an auxiliary exponent e.  
    By default, e = 65537.
    '''
    N = p*q
    return N,e
N,e = RSA_publickey(p,q) # No value of e is input, so it will default to 65537

print("Public key N = {}".format(N)) # A big number!
print("Public key e = {}".format(e))
```

Now we explain how the public key $(N,e)$ and the private key $(p,q)$ are used to encrypt and decrypt a (numerical) message $m$.  If you wish to encrypt/decrypt a text message, one case use a numerical scheme like ASCII, of course.  The message should be significantly shorter than the modulus, $m < N$ (ideally, shorter than the private key primes), but big enough so that $m^e$ is much bigger than $N$ (not usually a problem if $e = 65537$).  

#### Encryption  
The encryption procedure is simple. The ciphertext $c$ is given by the formula

$$c = m^e \text{ mod } N$$

where here we mean the "natural representative" of $m^e$ modulo $N$.  

```python
def RSA_encrypt(message, N, e):
    '''
    Encrypts message, using the public keys N,e.
    '''
    return pow(message, e, N)
c = RSA_encrypt(17,N,e) # c is the ciphertext.
print("The ciphertext is {}".format(c)) # A very long number!
```
#### Decryption 
To decrypt the ciphertext, we need to "undo" the operation of raising to the $e$-th power modulo $N$.  We must, effectively, take the $e$-th root of the ciphertext, modulo $N$.  This is what we studied earlier in this notebook.  Namely, if $c \equiv m^e \text{ mod } N$ is the ciphertext, and $ef \equiv 1$ modulo $\phi(N)$, then
$$c^f \equiv m^{ef} \equiv m \text{ mod } N.$$

So we must raise the ciphertext to the $f$ power, where $f$ is the multiplicative inverse of $e$ modulo $\phi(N)$.  Given a giant number $N$, it is difficult to compute the totient $\phi(N)$.  But, with the **private key** $p$ and $q$ (primes), the fact that $N = pq$ implies

$$\phi(N) = (p-1) \cdot (q-1) = pq - p - q + 1 = N - p - q + 1.$$



Armed with the private key (and the public key, which everyone has), we can decrypt a message like below:
```python

def RSA_decrypt(ciphertext, p,q,N,e):
    '''
    Decrypts message, using the private key (p,q) 
    and the public key (N,e).  We allow the public key N as
    an input parameter, to avoid recomputing it.
    '''
    tot = N - (p+q) + 1
    f = mult_inverse(e,tot)  # This uses the Euclidean algorithm... very quick!
    return pow(ciphertext,f,N)
RSA_decrypt(c,p,q,N,e)  # We decrypt the ciphertext... what is the result?
```

That's the entire process of encryption and decryption.  Encryption requires just the public key $(N,e)$ and decryption requires the private key $(p,q)$ too.  Everything else is modular arithmetic, using Euler's theorem and the Euclidean algorithm to find modular multiplicative inverses.

### Challenges 
From a practical standpoint, there are many challenges, and we just mention a few here.

**Key generation:**  The person who constructs the private key $(p,q)$ needs to be careful.  The primes $p$ and $q$ need to be pretty large (512 bits, or 1024 bits perhaps), which is not so difficult.  They also need to be constructed **randomly**.  For imagine that Alice comes up with her private key $(p,q)$ and Anne comes up with her private key $(q,r)$, with the same prime $q$ in common.  Their public keys will include the numbers $N = pq$ and $M = qr$.  If someone like Arjen comes along and starts taking GCDs of all the public keys in a database, that person will stumble upon the fact that $GCD(N,M) = q$, from which the private keys $(p,q)$ and $(q,r)$ can be derived.  And this sort of disaster has happened!  Poorly generated keys were stored in a database, and [discovered by Arjen Lenstra et al.](https://eprint.iacr.org/2012/064.pdf).

**Security by difficulty of factoring:**  The security of RSA is based on the difficulty of obtaining the private key $(p,q)$ from the public key $(N,e)$.  Since $N = pq$, this is precisely the difficulty of factoring a large number $N$ into two primes (given the knowledge that it is the product of two primes).  Currently it seems very difficult to factor large numbers.  The RSA factoring challenges give monetary rewards for factoring such large $N$.  The record (2017) is factoring a [768-bit (232 digit) number, RSA-768](https://en.wikipedia.org/wiki/RSA_numbers#RSA-768).  For this reason, we may consider a 1024-bit number secure for now (i.e. $p$ and $q$ are 512-bit primes), or use a 2048-bit number if we are paranoid.  If quantum computers develop sufficiently, they could make factoring large numbers easy, and RSA will have to be replaced by a quantum-secure protocol. 

**Web of Trust:**  Trust needs to begin somewhere.  Every time Alice and Bob communicate, Alice should not come up with a new private key, and give Bob the new public key.  For if they are far apart, how does Bob know he's receiving Alice's public key and not talking to an eavesdropper Eve?  Instead, it is better for Alice to register (in person, perhaps) her public key at some time.  She can create her private key $(p,q)$ and register the resulting public key $(N,e)$ with some "key authority" who checks her identity at the time.  The key authority then stores everyone's public keys -- effectively they say "if you want to send a secure message to Alice, use the following public key:  (..., ...)"  Then Bob can consult the key authority when he wishes to communicate securely to Alice, and this private/public key combination can be used for years.

But, as one might guess, this kicks the trust question to another layer.  How does Bob know he's communicating with the key authority?  The key authorities need to have their own authentication mechanism, etc..  One way to avoid going down a rabbithole of mistrust is to *distribute* trust across a network of persons.  Instead of a centralized "key authority", one can distribute one's public keys across an entire network of communicators (read about [openPGP](https://en.wikipedia.org/wiki/Pretty_Good_Privacy#OpenPGP)).  Then Bob, if he wishes, can double-check Alice's public keys against the records of numerous members of the network -- assuming that hackers haven't gotten to all of them!  

In practice, some implementations of RSA use a more centralized authority and others rely on a web of trust.  Cryptography requires a clever application of modular arithmetic (in Diffie-Hellman, RSA, and many other systems), but also a meticulous approach to implementation.  Often the challenges of implementation introduce new problems in number theory.


Why might the exponent $e = 65537$ be a computationally convenient choice?

### Notice: RSA Works Only with Numbers  
RSA encryption and decryption operate on numbers. However, as humans, we usually want to encrypt and decrypt normal text (e.g., *"Hello, World!"*). To apply RSA to text, we must first *convert text into a number* before encryption and convert it back after decryption. This is commonly done using *ASCII encoding*, *UTF-8*, or other encoding schemes.  


#### Example: Encoding Text for RSA  
- *Text:* `"HELLO"`  
- *ASCII Representation:* `72 69 76 76 79`  
- *Concatenated as a Single Number:* `7269767679`  
- This number can now be encrypted using RSA.  

⚠️Note: In real applications, padding schemes like *PKCS#1* are used to prevent attacks and ensure security.  


Let's return to Joseph and Helen like in our Diffie-Hellman example. Before encrypting and decrypting messages with RSA, both Joseph and Helen must generate their own key pairs.

#### **Joseph's Key Generation**
1. Choose two random large prime numbers:
   $$ p = 28932697, \quad q = 33479519 $$
2. Compute $ N_J = p \cdot q $:
   $$ N_J = 28932697 \times 33479519 = 968652778932743 $$
3. Compute Euler’s totient function:
   $$ \phi(N_J) = (p - 1) \times (q - 1) = 968652716520528 $$
4. Choose public exponent $ e_J = 65537 $ (a commonly used value, coprime to $ \phi(N_J) $).
5. Compute the private exponent:
   $$ d_J = e_J^{-1} \mod \phi(N_J) = 662716488446945 $$
6. **Public Key (Joseph):** $ \{N_J, e_J\} $
7. **Private Key (Joseph):** $ \{d_J\} $

#### **Helen's Key Generation**
1. Choose two random large prime numbers:
   $$ p = 19402601, \quad q = 29394899 $$
2. Compute $ N_H = p \cdot q $:
   $$ N_H = 19402601 \times 29394899 = 570337496732299 $$
3. Compute Euler’s totient function:
   $$ \phi(N_H) = (p - 1) \times (q - 1) = 570337447934800 $$
4. Choose public exponent $ e_H = 65537 $ (a commonly used value, coprime to $ \phi(N_H) $).
5. Compute the private exponent:
   $$ d_H = e_H^{-1} \mod \phi(N_H) = 295807562029873 $$
6. **Public Key (Helen):** $ \{N_H, e_H\} $
7. **Private Key (Helen):** $ \{d_H\} $

Joseph wants to encrypt the message **"Hello"** using Helen’s public key and send it to her.

The given Public Key of (Helen): 
- **Public Modulus:** $ N = 570337496732299 $
- **Public Exponent:** $ e = 65537 $

#### **Encryption Process**
1. Compute the ciphertext:
   $$ C = M^e \mod N $$  
   But **"Hello"** is text and must be converted to an integer first.

2. Convert **"Hello"** to an integer representation:  
   - Trust that **"Hello"** corresponds to:
     $$ M = 79600447942433 $$

3. Encrypt the integer representation:  
   $$ C = 79600447942433^{65537} \mod 570337496732299 $$  
   $$ C = 287307116472560 $$

4. **Encrypted Ciphertext:**  
   $$ C = 287307116472560 $$

5. **Joseph sends $ C $ to Helen.** 

#### **Decrypting Joseph’s Encrypted Message**
Helen receives the encrypted message $ C $ from Joseph and uses her private key to decrypt it. She has the following: 

- **Private Key (Helen):**  
  $$ d = 295807562029873 $$
- **Encrypted Message (Ciphertext):**  
  $$ C = 287307116472560 $$
- **Public Modulus:**  
  $$ N = 570337496732299 $$

So she does the following steps: 

1. Compute the original message:  
   $$ M = C^d \mod N $$
   $$ M = 287307116472560^{295807562029873} \mod 570337496732299 $$
   $$ M = 79600447942433 $$

2. Convert the integer **$ M = 79600447942433 $** back to text. Helen successfully decrypts Joseph’s message using her private key and retrieves the original text *"Hello!"*. This confirms that the RSA encryption and decryption process works as expected!

Now let's look behind the scenes, what actually happened between Joseph and Helen with some coding: 

```python
#### Joseph key Generation:

>>> from Crypto.Util.number import getPrime, GCD
>>> p = getPrime(25) ; p
28932697
>>> q = getPrime(25) ; q
33479519
>>> Nj = p * q
>>> phi = (p-1)*(q-1) ; phi
968652716520528
>>> ej = 65537
>>> GCD(ej, phi) == 1
True
>>> dj = pow(ej, -1, phi)
>>> pubj = (Nj, ej) ; pubj
(968652778932743, 65537)
>>> privj = (dj) ; privj
662716488446945

#### Helen key generation:
>>> from Crypto.Util.number import getPrime, GCD
>>> p = getPrime(25) ; p
19402601
>>> q = getPrime(25) ; q
29394899
>>> Nh = p * q
>>> phi = (p-1)*(q-1) ; phi
570337447934800
>>> eh = 65537
>>> GCD(eh, phi) == 1
True
>>> dh = pow(eh, -1, phi)
>>> pubh = (Nh, eh) ; pubh
(570337496732299, 65537)
>>> privh = (dh) ; privh
295807562029873

###### Encryption

>>> from Crypto.Util.number import bytes_to_long
>>> Nh = 570337496732299
>>> eh = 65537
>>> msg = b‘Hello!’
>>> m = bytes_to_long(msg) ; m
79600447942433
>>> c = pow(m, eh, nh) ; c
287307116472560

#### Decryption

>>> from Crypto.Util.number import long_to_bytes
>>> c = 287307116472560
>>> dh = 295807562029873
>>> m = pow(c, dh, nh) ; m
79600447942433
>>> msg = long_to_bytes(m) ; msg
b’Hello!’
```
---

Before we end our RSA analysis let's make some questions and answers for a wholesome overview of the RSA cryptosystem. 

#### Why Must $ e $ and $ \phi(N) $ Be Coprime?
In RSA, the public exponent $ e $ and Euler's totient function $ \phi(N) $ must be coprime (i.e., $ \gcd(e, \phi(N)) = 1 $). This ensures that the modular inverse of $ e $ exists, allowing us to compute the private key $ d $:
$$ d = e^{-1} \mod \phi(N) $$
If $ e $ and $ \phi(N) $ are not coprime, then $ e $ has no modular inverse, making decryption impossible.
Let's see an example where $ e $ and $ \phi(N) $ are not coprime:

- $ p = 7 $, $ q = 11 $
- Compute $ N = p \times q = 7 \times 11 = 77 $
- Compute $ \phi(N) = (p - 1) \times (q - 1) = 6 \times 10 = 60 $
- Choose $ e = 30 $ (which **is not coprime** with $ \phi(N) = 60 $, since $ \gcd(30, 60) = 30 $)

Since $ \gcd(e, \phi(N)) \neq 1 $, $ e^{-1} \mod 60 $ **does not exist**, and RSA encryption/decryption **fails**.


#### Encrypt and Decrypt $ M = N + 5 $ When Given $ p, q, e $

- $ p = 181738122577234101964418424964488593581 $
- $ q = 296349521830896499719611812070065036783 $
- Compute $ N = p \times q $
- Public exponent $ e = 65537 $
- Message:  
  $$ M = N + 5 $$

RSA encryption follows:
$$ C = M^e \mod N $$  
Since $ M = N + 5 $, we get:
$$ C = (N + 5)^{65537} \mod N $$  
Using modular arithmetic:
$$ (N + 5) \mod N = 5 $$
Thus:
$$ C = 5^{65537} \mod N $$

To decrypt:
$$ M' = C^d \mod N $$
$$ M' = 5^d \mod N $$  
However, **$ M' \neq N + 5 $** because RSA encrypts numbers *modulo $ N $*. The decryption process only gives us the *reduced form of the message* mod $ N $, meaning that we *lose information if $ M > N $*.

To correctly decrypt $ M $, we need *message padding* (e.g., OAEP) to ensure the message size fits within the modulus range. If padding is missing, and $ M \geq N $, we **cannot** recover the original message.

## RSA key files, PEM, and what is *not* an RSA attack

The recovered Part1 notes contained a page called `PEMattack.md`. The useful material is really about **key handling**, not a new mathematical attack on RSA.

PEM is a textual container/encoding convention commonly used to store DER-encoded keys and certificates. A PEM block can contain public information or private-key material. The presence of `-----BEGIN ...-----` headers does not by itself tell us whether the private key is adequately protected.

If an attacker obtains an unencrypted RSA private key, RSA has not been factored—the key has simply been compromised. The relevant engineering controls are file permissions, encrypted private-key formats when appropriate, KDF/password policy, hardware-backed key storage, backup protection, and minimizing key export.

This distinction matters throughout CryptoCave: **key compromise, serialization mistakes, and mathematical cryptanalysis are different failure classes**, even when all three ultimately expose the same secret key.

## * RSA and Multiplicative Homomorphism

One last and very important property that we should remember about RSA. 

>RSA is *multiplicatively homomorphic*, meaning it supports **multiplicative homomorphic encryption**.

But first, as always, some maths. 
#### What is a Homomorphism?
A **homomorphism** is a map:
$$ f: A \to B $$
between two sets **A** and **B**, which preserves the same structure and operations.  
If **$ \cdot $** is an operation (e.g., **addition or multiplication**), then:
$$ f(x \cdot y) = f(x) \cdot f(y) $$

#### **Homomorphic Property in RSA**
In RSA, this property is translated as:

1. *$ f $ is the RSA encryption function $ E $ or decryption function $ D $*.
2. *$ x, y $ are messages ($ M_1, M_2 $) being encrypted or decrypted*.

Thus, *RSA encryption preserves multiplication*:
$$ E(M_1 \cdot M_2) = E(M_1) \cdot E(M_2) \mod N $$

This means that multiplying *two ciphertexts* results in a *ciphertext of the product* of the original plaintexts, without needing to decrypt them first.

Let's see why *RSA encryption preserves multiplication*. Suppose we have:

- **Message:**  
  $$ M = M_1 \cdot M_2 $$
- **Ciphertexts:**  
  $$ C_1 = M_1^e \mod N $$  
  $$ C_2 = M_2^e \mod N $$  

Then, encrypting $ M $:
$$ C = M^e = (M_1 \cdot M_2)^e = M_1^e \cdot M_2^e = C_1 \cdot C_2 \mod N $$

By multiplying the ciphertexts of $ M_1 $ and $ M_2 $, we obtain the ciphertext of their product. Don'r rush to be excited... This can be useful but also dangerous...

* **Bypass Blacklisted Words:**  
   - Encrypted content *cannot be easily filtered* based on blacklists.  
   - Attackers can use *multiplicative manipulation* to hide flagged words.  

* **Sign or Encrypt Unauthorized Data:**  
   - A malicious entity can *modify encrypted data* without knowing the plaintext.  
   - This can lead to *unauthorized signatures* or *tampered encrypted messages*.  

* **Forge Messages:**  
   - If an adversary has encrypted messages *$ C_1 = E(M_1) $** and **$ C_2 = E(M_2) $*,  
     they can create *a valid ciphertext for $ M_1 \cdot M_2 $ without decrypting*.
   - This can lead to *forging authenticated messages** in systems that rely on RSA encryption.


So to wrap up, never use raw textbook RSA for encryption! Always use proper padding! And dont roll your own crypto! Some bacic implementations in Python and SageMath can be found in `src/` folder.
