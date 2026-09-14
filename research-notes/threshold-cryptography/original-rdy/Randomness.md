Verifiable randomness is essential for ensuring trust in various institutional decision-making processes such as elections and lotteries. There are also cryptographic applications that require verifiable randomness. In the land of decentralized consensus mechanisms, the DFINITY approach uses random seeds to decide the outcome of leadership elections. In this setting, it is essential that the randomness is publicly verifiable so that the outcome of the leadership election is trustworthy. Such a situation arises more generally in Sortitions: an election where leaders are selected as a random individual (or subset of individuals) from a larger set.

In this blog post, we will give a technical overview behind the cryptography used in the distributed randomness beacon, and how it can be used to generate publicly verifiable randomness. We believe that distributed randomness beacons have a huge amount of utility in realizing the Internet of the Future; where we will be able to rely on distributed, decentralized solutions to problems of a global-scale.

A source of randomness is measured in terms of the amount of entropy it provides. Think about the entropy provided by a random output as a score to indicate how “random” the output actually is. The notion of information entropy was concretised by the famous scientist Claude Shannon in his paper A Mathematical Theory of Communication, and is sometimes known as Shannon Entropy.

A common way to think about random outputs is: a sequence of bits derived from some random outcome. For the sake of an argument, consider a fair 8-sided dice roll with sides marked 0-7. The outputs of the dice can be written as the bit-strings 000,001,010,...,111. Since the dice is fair, any of these outputs is equally likely. This is means that each of the bits is equally likely to be 0 or 1. Consequently, interpreting the output of the dice roll as a random output then derives randomness with 3 bits of entropy.

More generally, if a perfect source of randomness guarantees strings with n bits of entropy, then it generates bit-strings where each bit is equally likely to be 0 or 1. This allows us to predict the value of any bit with maximum probability 1/2. If the outputs are sampled from such a perfect source, we consider them uniformly distributed. If we sample the outputs from a source where one bit is predictable with higher probability, then the string has n-1 bits of entropy. To go back to the dice analogy, rolling a 6-sided dice provides less than 3 bits of entropy because the possible outputs are 000,001,010,011,100,101 and so the 2nd and 3rd bits are more likely to be to set to 0 than to 1.

It is possible to mix entropy sources using specifically designed mixing functions to retrieve something with even greater entropy. The maximum resulting entropy is the sum of the entropy taken from the number of entropic sources used as input.

Sampling randomness
To sample randomness, let’s first identify the appropriate sources. There are many natural phenomena that one can use:

atmospheric noise;

radioactive decay;

Unfortunately, these phenomena require very specific measuring tools, which are prohibitively expensive to install in mainstream consumer electronics. As such, most personal computing devices usually use external usage characteristics for seeding specific generator functions that output randomness as and when the system requires it. These characteristics include keyboard typing patterns and speed and mouse movement – since such usage patterns are based on the human user, it is assumed they provide sufficient entropy as a randomness source. 


Naturally, it is difficult to tell whether a system is actually returning random outputs by only inspecting the outputs. There are statistical tests that detect whether a series of outputs is not uniformly distributed, but these tests cannot ensure that they are unpredictable. This means that it is hard to detect if a given system has had its randomness generation compromised.


Distributed randomness
It’s clear we need alternative methods for sampling randomness so that we can provide guarantees that trusted mechanisms, such as elections and lotteries, take place in secure tamper-resistant environments. The drand project was started by researchers at EPFL to address this problem. The drand charter is to provide an easily configurable randomness beacon running at geographically distributed locations around the world. The intention is for each of these beacons to generate portions of randomness that can be combined into a single random string that is publicly verifiable.

This functionality is achieved using threshold cryptography. Threshold cryptography seeks to derive solutions for standard cryptographic problems by combining information from multiple distributed entities. The notion of the threshold means that if there are n entities, then any t of the entities can combine to construct some cryptographic object (like a ciphertext, or a digital signature). These threshold systems are characterised by a setup phase, where each entity learns a share of data. They will later use this share of data to create a combined cryptographic object with a subset of the other entities.

Threshold randomness
In the case of a distributed randomness protocol, there are n randomness beacons that broadcast random values sampled from their initial data share, and the current state of the system. This data share is created during a trusted setup phase, and also takes in some internal random value that is generated by the beacon itself.

When a user needs randomness, they send requests to some number t of beacons, where t < n, and combine these values using a specific procedure. The result is a random value that can be verified and used for public auditing mechanisms.

Consider what happens if some proportion c/n of the randomness beacons are corrupted at any one time. The nature of a threshold cryptographic system is that, as long as c < t, then the end result still remains random.

If c exceeds t then the random values produced by the system become predictable and the notion of randomness is lost. In summary, the distributed randomness procedure provides verifiably random outputs with sufficient entropy only when c < t.

By distributing the beacons independent of each other and in geographically disparate locations, the probability that t locations can be corrupted at any one time is extremely low. The minimum choice of t is equal to n/2.

How does it actually work?
What we described above sounds a bit like magictm. Even if c = t-1, then we can ensure that the output is indeed random and unpredictable! To make it clearer how this works, let’s dive a bit deeper into the underlying cryptography.

Two core components of drand are: a distributed key generation (DKG) procedure, and a threshold signature scheme. These core components are used in setup and randomness generation procedures, respectively.


Distributed key generation
At a high-level, the DKG procedure creates a distributed secret key that is formed of n different key pairs (vk_i, sk_i), each one being held by the entity i in the system. These key pairs will eventually be used to instantiate a (t,n)-threshold signature scheme (we will discuss this more later). In essence, t of the entities will be able to combine to construct a valid signature on any message.

To think about how this might work, consider a distributed key generation scheme that creates n distributed keys that are going to be represented by pizzas. Each pizza is split into n slices and one slice from each is secretly passed to one of the participants. Each entity receives one slice from each of the different pizzas (n in total) and combines these slices to form their own pizza. Each combined pizza is unique and secret for each entity, representing their own key pair.

Going back to pizzas temporarily, it will become clear in the next section how this Lagrange interpolation procedure essentially describes the dissemination of one slice (corresponding to (x,y) coordinates) taken from a single pizza (the entire n-1 degree polynomial) among n participants. Running this procedure n times in parallel allows each entity to construct their entire pizza (or the eventual key pair).


Back to key generation
Intuitively, in the DKG procedure we want to distribute n key pairs among n participants. This effectively means running n parallel instances of a t-out-of-n Shamir Secret Sharing scheme. This secret sharing scheme is built entirely upon the polynomial interpolation technique that we described above.

In a single instance, we take the secret key to be the first coefficient of a polynomial of degree t-1 and the public key is a published value that depends on this secret key, but does not reveal the actual coefficient. Think of RSA, where we have a number N = pq for secret large prime numbers p,q, where N is public but does not reveal the actual factorisation. Notice that if the polynomial is reconstructed using the interpolation technique above, then we immediately learn the secret key, because the first coefficient will be made explicit.

Each secret sharing scheme publishes shares, where each share is a different evaluation of the polynomial (dependent on the entity i receiving the key share). These evaluations are essentially coordinates on the (x,y) plane.

By running n parallel instances of the secret sharing scheme, each entity receives n shares and then combines all of these to form their overall key pair (vk_i, sk_i).

The DKG procedure uses n parallel secret sharing procedures along with Pedersen commitments to distribute the key pairs. We explain in the next section how this procedure is part of the procedure for provisioning randomness beacons.

In summary, it is important to remember that each party in the DKG protocol generates a random secret key from the n shares that they receive, and they compute the corresponding public key from this. We will now explain how each entity uses this key pair to perform the cryptographic procedure that is used by the drand protocol.

Threshold signature scheme
Remember: a standard signature scheme considers a key-pair (vk,sk), where vk is a public verification key and sk is a private signing key. So, messages m signed with sk can be verified with vk. The security of the scheme ensures that it is difficult for anybody who does not hold sk to compute a valid signature for any message m.

A threshold signature scheme allows a set of users holding distributed key-pairs (vk_i,sk_i) to compute intermediate signatures u_i on a given message m.

Given knowledge of some number t of intermediate signatures u_i, a valid signature u on the message m can be reconstructed under the combined secret key sk. The public key vk can also be inferred using knowledge of the public keys vk_i, and then this public key can be used to verify u.

Again, think back to reconstructing the degree t-1 curves on graphs with t known coordinates. In this case, the coordinates correspond to the intermediate signatures u_i, and the signature u corresponds to the entire curve. For the actual signature schemes, the mathematics are much more involved than in the DKG procedure, but the principal is the same.

The n beacons that will take part in the drand project are identified. In the trusted setup phase, the DKG protocol from above is run, and each beacon effectively creates a key pair (vk_i, sk_i) for a threshold signature scheme. In other words, this key pair will be able to generate intermediate signatures that can be combined to create an entire signature for the system.

For each round (occurring once a minute, for example), the beacons agree on a signature u evaluated over a message containing the previous round’s signature and the current round’s number. This signature u is the result of combining the intermediate signatures u_i over the same message. Each intermediate signature u_i is created by each of the beacons using their secret sk_i.

Once this aggregation completes, each beacon displays the signature for the current round, along with the previous signature and round number. This allows any client to publicly verify the signature over this data to verify that the beacons honestly aggregate. This provides a chain of verifiable signatures, extending back to the first round of output. In addition, there are threshold signature schemes that output signatures that are indistinguishable from random sequences of bytes. Therefore, these signatures can be used directly as verifiable randomness for the applications we discussed previously.

To instantiate the required threshold signature scheme, drand uses the (t,n)-BLS signature scheme of Boneh, Lynn and Shacham. In particular, we can instantiate this scheme in the elliptic curve setting using  Barreto-Naehrig curves. Moreover, the BLS signature scheme outputs sufficiently large signatures that are randomly distributed, giving them enough entropy to be sources of randomness. Specifically the signatures are randomly distributed over 64 bytes.

BLS signatures use a specific form of mathematical operation known as a cryptographic pairing. Pairings can be computed in certain elliptic curves, including the Barreto-Naehrig curve configurations.


The randomness beacons are synchronised in rounds. At each round, a beacon produces a new signature u_i using its private key sk_i on the previous signature generated and the round ID. These signatures are usually broadcast on the URL drand.<host>.com/api/public. These signatures can be verified using the keys vk_i and over the same data that is signed. By signing the previous signature and the current round identifier, this establishes a chain of trust for the randomness beacon that can be traced back to the original signature value.

The randomness can be retrieved by combining the signatures from each of the beacons using the threshold property of the scheme. This reconstruction of the signature u from each intermediate signature u_i is done internally by the League of Entropy nodes. Each beacon broadcasts the entire signature u, that can be accessed over the HTTP endpoint above.


As we’ve discussed in the past, cryptography relies on the ability to generate random numbers that are both unpredictable and kept secret from any adversary. In this post, we’re going to go into fairly deep technical detail, so there is some background that we’ll need to ensure that everybody is on the same page.


True Randomness vs Pseudorandomness
In cryptography, the term random means unpredictable. That is, a process for generating random bits is secure if an attacker is unable to predict the next bit with greater than 50% accuracy (in other words, no better than random chance).

We can obtain randomness that is unpredictable using one of two approaches. The first produces true randomness, while the second produces pseudorandomness.

True randomness is any information learned through the measurement of a physical process. Its unpredictability relies either on the inherent unpredictability of the physical process being measured (e.g., the unpredictability of radioactive decay), or on the inaccuracy inherent in taking precise physical measurements (e.g., the inaccuracy of the least significant digits of some physical measurement such as the measurement of a CPU’s temperature or the timing of keystrokes on a keyboard). Random values obtained in this manner are unpredictable even to the person measuring them (the person performing the measurement can’t predict what the value will be before they have performed the measurement), and thus are just as unpredictable to an external attacker. All randomness used in cryptographic algorithms begins life as true randomness obtained through physical measurements.

However, obtaining true random values is usually expensive and slow, so using them directly in cryptographic algorithms is impractical. Instead, we use pseudorandomness. Pseudorandomness is generated through the use of a deterministic algorithm that takes as input some other random value called a seed and produces a larger amount of random output (these algorithms are called cryptographically secure pseudorandom number generators, or CSPRNGs). A CSPRNG has two key properties: First, if an attacker is unable to predict the value of the seed, then that attacker will be similarly unable to predict the output of the CSPRNG (and even if the attacker is shown the output up to a certain point - say the first 10 bits - the rest of the output - bits 11, 12, etc - will still be completely unpredictable). Second, since the algorithm is deterministic, running the algorithm twice with the same seed as input will produce identical output.

The CSPRNGs used in modern cryptography are both very fast and also capable of securely producing an effectively infinite amount of output1 given a relatively small seed (on the order of a few hundred bits). Thus, in order to efficiently generate a lot of secure randomness, true randomness is obtained from some physical process (this is slow), and fed into a CSPRNG which in turn produces as much randomness as is required by the application (this is fast). In this way, randomness can be obtained which is both secure (since it comes from a truly random source that cannot be predicted by an attacker) and cheap (since a CSPRNG is used to turn the truly random seed into a much larger stream of pseudorandom output).

Running Out of Randomness
A common misconception is that a CSPRNG, if used for long enough, can “run out” of randomness. This is an understandable belief since, as we’ll discuss in the next section, operating systems often re-seed their CSPRNGs with new randomness to hedge against attackers discovering internal state, broken CSPRNGs, and other maladies.

But if an algorithm is a true CSPRNG in the technical sense, then the only way for it to run out of randomness is for somebody to consume far more values from it than could ever be consumed in practice (think consuming values from a CSPRNG as fast as possible for thousands of years or more).2

However, none of the fast CSPRNGs that we use in practice are proven to be true CSPRNGs. They’re just strongly believed to be true CSPRNGs, or something close to it. They’ve withstood the test of academic analysis, years of being used in production, attacks by resourced adversaries, and so on. But that doesn’t mean that they are without flaws. For example, SHA-1, long considered to be a cryptographically-secure collision-resistant hash function (a building block that can be used to construct a CSPRNG) was eventually discovered to be insecure. Today, it can be broken for $110,000’s worth of cloud computing resources.3

Thus, even though we aren’t concerned with running out of randomness in a true CSPRNG, we also aren’t sure that what we’re using in practice are true CSPRNGs. As a result, to hedge against the possibility that an attacker has figured out how to break our CSPRNGs, designers of cryptographic systems often choose to re-seed CSPRNGs with fresh, newly-acquired true randomness just in case.

Randomness in the Operating System
In most computer systems, one of the responsibilities of the operating system is to provide cryptographically-secure pseudorandomness for use in various security applications. Since the operating system cannot know ahead of time which applications will require pseudorandomness (or how much they will require), most systems simply keep an _entropy pool_4 - a collection of randomness that is believed to be secure - that is used to seed a CSPRNG (e.g., /dev/urandom on Linux) which serves requests for randomness. The system then takes on the responsibility of not only seeding this entropy pool when the system first boots, but also of periodically updating the pool (and re-seeding the CSPRNG) with new randomness from whatever sources of true randomness are available to the system in order to hedge against broken CSPRNGs or attackers having compromised the entropy pool through other non-cryptographic attacks.

For brevity, and since Cloudflare’s production system’s run Linux, we will refer to the system’s pseudorandomness provider simply as /dev/urandom, although note that everything in this discussion is true of other operating systems as well.

Given this setup of an entropy pool and CSPRNG, there are a few situations that could compromise the security of /dev/urandom:

The sources of true randomness used to seed theentropy pool could be too predictable, allowing an attacker to guess the values obtained from these sources, and thus to predict the output of /dev/urandom.

An attacker could have access to the sources of true randomness, thus being able to observe their values and thus predict the output of /dev/urandom.

An attacker could have the ability to modify the sources of true randomness, thus being able to influence the values obtained from these sources and thus predict the output of /dev/urandom.

Randomness Mixing
A common approach to addressing these security issues is to mix multiple sources of randomness together in the system’s entropy pool, the idea being that so long as some of the sources remain uncompromised, the system remains secure. For example, if sources X, Y, and Z, when queried for random outputs, provide values x, y, and z, we might seed our entropy pool with H(x, y, z), where H is a cryptographically-secure collision-resistant hash function. Even if we assume that two of these sources - say, X and Y - are malicious, so long as the attackers in control of them are not able to observe Z’s output,5 then no matter what values of x and y they produce, H(x, y, z) will still be unpredictable to them.

The flow of the “lava” in a lava lamp is very unpredictable,6 and so the entropy in those lamps is incredibly high. Even if we conservatively assume that the camera has a resolution of 100x100 pixels (of course it’s actually much higher) and that an attacker can guess the value of any pixel of that image to within one bit of precision (e.g., they know that a particular pixel has a red value of either 123 or 124, but they aren’t sure which it is), then the total amount of entropy produced by the image is 100x100x3 = 30,000 bits (the x3 is because each pixel comprises three values - a red, a green, and a blue channel). This is orders of magnitude more entropy than we need.

The goal of LavaRand is to ensure that our production machines have access to secure randomness even if their local entropy sources are compromised. Just after boot, each of our production machines contacts LavaRand over TLS to obtain a fixed-size chunk of fresh entropy called a “beacon.” It mixes this beacon into the entropy system (on Linux, by writing the beacon to /dev/random). After this point, in order to predict or control the output of /dev/urandom, an attacker would need to compromise both the machine’s local entropy sources and the LavaRand beacon.

Bootstrapping TLS
Unfortunately, the reality isn’t quite that simple. We’ve gotten ourselves into something of a chicken-and-egg problem here: we’re trying to hedge against bad entropy from our local entropy sources, so we have to assume those might be compromised. But TLS, like many cryptographic protocols, requires secure entropy in order to operate. And we require TLS to request a LavaRand beacon. So in order to ensure secure entropy, we have to have secure entropy…

We solve this problem by introducing a second special-purpose CSPRNG, and seeding it in a very particular way. Every machine in Cloudflare’s production fleet has its own permanent store of secrets that it uses just after boot to prove its identity to the rest of the fleet in order to bootstrap the rest of the boot process. We piggyback on that system by storing an extra random seed - unique for each machine - that we use for that first TLS connection to LavaRand.

There’s a simple but very useful result from cryptography theory that says that an HMAC - a hash-based message authentication code - when combined with a random, unpredictable seed, behaves (from the perspective of an attacker) like a random oracle. That’s a lot of crypto jargon, but it basically means that if you have a secret, randomly-generated seed, s, then an attacker will be completely unable to guess the output of HMAC(s, x) regardless of the value of x - even if x is completely predictable! Thus, you can use HMAC(s, x) as the seed to a CSPRNG, and the output of the CSPRNG will be unpredictable. Note, though, that if you need to do this multiple times, you will have to pick different values for x! Remember that while CSPRNGs are secure if used with unpredictable seeds, they’re also deterministic. Thus, if the same value is used for x more than once, then the CSPRNG will end up producing the same stream of “random” values more than once, which in cryptography is often very insecure!


The obvious question to ask is... why mess with random number generation?

The answer is rather simple: good random numbers are fundemental to almost all secure computer systems. Without them everything from Second World War ciphers like Lorenz to the SSL your browser uses to secure web traffic are in serious trouble.

To understand why, and the threat that bad random numbers pose, it's necessary to understand a little about random numbers themselves (such as "what is a good random number anyway?") and how they are used in secure systems.


When you log into a web site you are typically assigned a unique ID for that session (the period you are logged in). That unique ID needs to be unique to you and not guessable by someone else. If someone else can guess it they can impersonate you.


Pseudo-randomness
The IDs are generated internally using a pseudo-random numbergenerator. That's a mathematical function that can be calledrepeatedly to get apparently random numbers. I say apparently because, as the great mathematician John von Neumann said: "Anyone who considers arithmetical methods of producing random digits is, of course, in a state of sin." The computer scientist Donald Knuth tells a story of inventing a pseudo-random number generator himself only to be shocked at how poor it was.

Although pseudo-random number generators can generate a sequence of apparently random numbers they have weaknesses.

von Neumann used a simple pseudo-random number generator called themiddle square that works as follows. You start with some number (called a seed) and square it. You take the four middle digits as your random number and square them to get the next random number, and so on.

For example, if you chose 4181 as a seed the sequence 4807, 1072,1491, 2230, 9279, ... would be generated as follows:

 Random number        Its Square    Middle digits
 4181                 17480761      4807
 4807                 23107249      1072
 1072                  1149184      1491
 1491                  2223081      2230
 2230                  4972900      9729
 9279                 94653441      6534
 and so on
This particular pseudo-random number has long since been replaced by better ones such as the Mersenne Twister whose output is harder to predict. The middle square method is trivial to predict: the next number it generates is entirely determined by the number it last produced. The Mersenne Twister on the other hand is much harder to predict because it has internal state that it uses to produce random numbers.

In the world of cryptography there are cryptographically secure pseudo-random number generators which are designed to be unpredictable no matter how many random cnumbers you ask it to generate. (The Mersenne Twister isn't cryptographically secure because it can be predicted if enough of the random numbers it generates are observed.)

For secure systems it's vital that the random number generator be unpredictable.

For example, any HTTPS session starts as follows:

The web browser sends information to the server about which version of SSL it wants to use and other information.

The web server replies with similar information about SSL versions and its SSL certificate.

The web browser checks that the certificate is valid. If it is, it generates a random 'pre-main secret' that will be used to secure the connection.

After that further exchanges occur all based on the randomly chosen pre-main secret. It needs to be unpredictable for the connection to be secure.

Here's part of how a computer using WiFi establishes a secure connection to an access point using the popular WPA2 protocol:

The access point generates a random nonce and sends it to the computer.

The computer generates a random nonce and sends it to the access point.

The access point and the computer continue on from there using thoserandom nonce values to secure the connection.

Similarly, random numbers turn up when logging into web sites (and other systems), creating secure connections to servers using SSH, holding Skype video chats, sending encrypted email and more.

And the Achilles' Heel of the only completely secure cryptosystem, the one-time pad is that the pad itself must be completely randomly generated. Any predictability or non-uniformity in the random numbers used can lead to breaking of a one-time pad. (The other problem with one-time pads is reuse: they must be used only once.)


We currently obtain most of our random numbers from either OpenSSL's random number generation system or from the Linux kernel. Both seed their random number generators from a variety of sources to make them as unpredictable as possible. Sources include things like network data, or the seek time of disks. But we think we can improve on them by adding some truly random data into the system, and, as a result, improve security for our customers.