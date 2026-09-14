def keygen(bits):
	p = random_prime(2^bits)
	q = random_prime(2^bits)
	Lambda = (p - 1) * (q - 1)
	n = p * q
	Zn = IntegerModRing(n)
	Zn2 = IntegerModRing(n^2)
	g = Zn2(n + 1)
	mu = Zn(Lambda)^-1
	return ((n, g), (Lambda, mu))

def encrypt(m, pub):
	(n, g) = pub
	Zn2 = IntegerModRing(n^2)
	r = Zn2(randint(0, n))
	c = g^m * r^n
	return c

def decrypt(c, priv):
	((n, g), (Lambda, mu)) = priv
	Zn = IntegerModRing(n)
	c = Zn((Integer(c^Lambda) - 1) / n) * mu
	return c

def encrypt_add(cipher_1, cipher_2, pub):
	(n, g) = pub
	Zn2 = IntegerModRing(n^2)
	r = Zn2(randint(0, n))
	return cipher_1 * cipher_2 * r^n

def encrypt_sub(cipher_1, cipher_2, pub):
	(n, g) = pub
	Zn2 = IntegerModRing(n^2)
	r = Zn2(randint(0, n))
	inv_cipher_2 =Zn2(cipher_2)^-1
	return cipher_1 * inv_cipher_2 * r^n

def decrypt_signed_sub(cipher_sub, priv):
    n, g = priv[0]
    # decrypt to get the result in [0, n-1]
    diff_mod_n = decrypt(cipher_sub, priv)
    # interpret as signed in (-n/2, +n/2)
    if diff_mod_n > n//2:
        return diff_mod_n - n
    else:
        return diff_mod_n


def encrypt_scalar_mul(a, c, pub):
	return c^a;

def encrypt_linear(a, cipher_1, b, cipher_2, pub):
	(n, g) = pub
	Zn2 = IntegerModRing(n^2)
	r = Zn2(randint(0, n))
	return (cipher_1^a) * (cipher_2^b) * r^n

priv = keygen(512)
pub = priv[0]


message_1 = randint(0, 1000)
cipher_1 = encrypt(message_1, pub)

message_2 = randint(0, 1000)
cipher_2 = encrypt(message_2, pub)


sum = encrypt_add(cipher_1, cipher_2, pub)
diff =encrypt_sub(cipher_1, cipher_2, pub)


ret = encrypt_linear(5, cipher_1, 4, cipher_2, pub)


print (f"Public key (n,g):  {priv[0]}")
print (f"Private (Lambda, mu):  {priv[1]}")

print ("Message 1 = %d" %message_1)
print ("Ciphertext 1 = %d" %cipher_1)
print ("Message 2 = ", message_2)
print ("Ciphertext 2 = ", cipher_2)
print ("Message addition = ", message_1 + message_2)
print ("Message addition (after decrypt) = ", decrypt(sum, priv))
print ("Message substraction = ", message_1 - message_2)
print ("Message substraction (after decrypt) = ", decrypt(diff, priv))
print("Message subtraction (signed)        = ", decrypt_signed_sub(diff, priv))
print ("5 * message_1 + 4 * message_2 = ", 5*message_1 + 4*message_2)
print ("5 * message_1 + 4 * message_2 (after decrypt)= ", decrypt(ret, priv))