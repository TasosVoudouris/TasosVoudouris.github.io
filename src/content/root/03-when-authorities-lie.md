---
title: 'When authorities lie'
description: 'Why the web demands two extra signatures on every certificate. Fifteen years of certificate authorities that were breached, careless or coerced; how each failure was found (often by luck); and how Certificate Transparency turned silent misissuance into public evidence. Then a toy CT ecosystem that replays the attacks, and the one gap it cannot close on its own.'
part: 3
pubDate: 2026-11-19
tags:
  - certificate-transparency
  - certificates
  - pki
  - incidents
  - history
companion: experiments/root-of-trust
---

Part 02 ended with an awkward fact. Of the 15,802 bytes an ML-DSA-44 server sends to authenticate itself, 4,840 are two signatures that have nothing to do with the CA or the server: they come from **Certificate Transparency logs**, in the form of SCTs. A CA's signature is supposed to mean "we checked, this key belongs to this name". Why would anyone need two more signatures saying, in effect, "and we wrote it down"?

Because CAs have lied. Not usually on purpose, but the effect is the same: a certificate saying "this is google.com" with a key Google never saw, signed by a CA every browser trusted. This part tells that story through real incidents, each with how it was discovered, because the *discovery* is the point. Then it builds a small CT ecosystem in code, replays the attacks against it, and finds the one hole that CT cannot close by itself. That hole is why the next two parts are about Merkle trees.

By the end you should be able to:

1. explain why the security of every site is the security of the *weakest* trusted CA;
2. tell the story of five real CA failures and say how each one came to light;
3. describe Certificate Transparency's moving parts: logs, SCTs, precertificates, monitors, and the browser policy that ties them together;
4. say precisely what CT guarantees (detection) and what it does not (prevention);
5. name the assumption CT still makes about logs, and what it takes to remove it.

The companion code is [`experiments/root-of-trust/03_ct_toy.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust), with its tests in `test_03_ct_toy.py`.

## The weakest link

Recall Part 00: a browser carries a store of root certificates, and accepts any chain that ends at one of them. What Part 00 did not stress is the next sentence: **by default, any of those roots may vouch for any name.** There is no rule that only "Google's CA" may issue for google.com. And every root may delegate its power to intermediates, which may in turn be operated by other companies.

<figure class="plate">
<img src="/images/root/03-any-ca.svg" alt="Six certificate authorities, A to F, all with arrows to example.com. example.com chose and pays CA B. CA F is breached, careless or coerced, and one signature from F is as good as one from B." width="1000" height="520" loading="lazy" />
<figcaption>example.com chose one CA. Every other CA in the store can still sign for it.</figcaption>
</figure>

So the security of example.com is not the security of the CA example.com chose. It is the security of **the worst CA in the browser's store**, and of every intermediate below it, and of every company those intermediates trusted with an account. A website owner has no say in any of that.

Two mechanisms narrow this a little. **CAA records** (RFC 8659) let a domain publish in DNS which CAs may issue for it, and CAs must check them before issuing. **Name constraints** let a parent CA restrict an intermediate to certain domains. Both help against honest mistakes. Neither helps when the CA itself is breached, because a CA whose signing system is in an attacker's hands does not check anything.

## Fifteen years of authorities that lied

<figure class="plate">
<img src="/images/root/03-timeline.svg" alt="Timeline 2011 to 2025. Red: Comodo RA account breached, 9 certs (2011); DigiNotar, 531+ certs, *.google.com used against Iran (2011); TURKTRUST stray intermediate signs *.google.com (2012); CNNIC / MCS MITM box signs Google names (2015). Amber: Symantec test cert for google.com found in CT (2015); Chrome distrusts Entrust, cutoff by SCT time (2024); 12 Fina certs for 1.1.1.1 found in CT (2025). Green: RFC 6962 (2013); Chrome requires CT and distrusts Symantec (2018); Firefox 135 enforces CT (2025)." width="1000" height="640" loading="lazy" />
<figcaption>Red: a CA issued what it should not. Amber: caught or punished through CT. Green: the system changing.</figcaption>
</figure>

For each incident, read three things: what went wrong, **how anyone found out**, and what it taught.

### Comodo, March 2011: the front door was an account

On 15 March 2011 an attacker obtained the username and password of a Comodo **registration authority**, a partner company in southern Europe allowed to approve certificate requests on Comodo's behalf. Using that account, the attacker had Comodo issue **nine certificates for seven domains**: `login.live.com`, `mail.google.com`, `www.google.com`, `login.yahoo.com` (three), `login.skype.com`, `addons.mozilla.org`, and one for "Global Trustee". The attack came from an Iranian IP address.

*How it was found:* by Comodo itself, quickly, and it revoked the certificates. But revocation checking on the web was (and is) unreliable, so browser makers shipped updates that hard-coded the nine certificates as blocked, about a week later. Mozilla's patch blocked ten: the nine, plus a test certificate Comodo had issued to Mozilla.

*What it taught:* a CA's root key can be perfectly safe in its vault while its *process* is the weak point. Every partner with an issuing account is part of the attack surface.

### DigiNotar, summer 2011: the CA itself

DigiNotar was a Dutch CA, trusted by every browser and also used for Dutch government certificates. According to the investigation by Fox-IT, the attacker was inside DigiNotar's network by **17 June 2011**, and on **10 July** issued the first rogue certificate: a wildcard for `*.google.com`. Fox-IT's list of rogue certificates, explicitly not exhaustive, ran to **531**, for names including Google, Microsoft, Skype, Twitter, the Tor project, Mozilla, and the CIA, MI6 and Mossad. The final report concluded that **all** of DigiNotar's CA servers had been compromised. DigiNotar detected an intrusion on 19 July, and did not tell anyone.

The `*.google.com` certificate was used for interception at national scale. It only became public on **29 August**, when it was being presented to users in Iran. Fox-IT reconstructed the scale from an unexpected source: the certificate's **OCSP requests**. Every browser that saw the rogue certificate asked DigiNotar's revocation server whether it was still valid, and those queries came from about **300,000 unique IP addresses, more than 99% of them in Iran**. The certificate meant to stay invisible had left a trace only because browsers asked about it.

*How it was found:* by users who saw a warning, in part because Chrome shipped with Google's own keys pinned and rejected a google.com certificate with any other key. Pinning only protected the handful of sites built into the browser.

*What it taught:* the browser makers removed DigiNotar from their trust stores, the Dutch government took over its operations, and the company was declared bankrupt in September 2011. More importantly, for six weeks a CA had been forging certificates for the most important sites on the internet and **nobody outside the attacker and the CA could have known**.

### TURKTRUST, 2011 to 2012: a mistake that minted a CA

In **August 2011**, during a software migration, the Turkish CA TURKTRUST issued two certificates that should have been ordinary site certificates as **intermediate CA certificates**: certificates with the power to sign other certificates. One went to EGO, a public agency in Ankara. Nobody noticed. Sixteen months later, on **24 December 2012**, Chrome detected and blocked an unauthorized `*.google.com` certificate issued by an intermediate chaining to TURKTRUST. The intermediate had apparently ended up in a firewall that inspects encrypted traffic by forging certificates on the fly. Chrome blocked the first intermediate on 25 December and the second on 26 December; Microsoft and Mozilla followed.

*How it was found:* Chrome's pinning again, again for Google only.

*What it taught:* one wrong bit (Part 01's `cA` flag in basicConstraints) turns a customer into a certificate authority, and nothing in the system would ever have reported it.

### CNNIC and MCS Holdings, 2015: delegation without control

CNNIC, the Chinese domain registry and a trusted CA, gave an Egyptian company, MCS Holdings, an **unconstrained intermediate certificate**, labelled as a test with a two-week validity, on the understanding that MCS would only issue for domains it had registered. MCS installed it in a man-in-the-middle proxy, which then generated certificates for Google domains as its employees browsed. Google found out on **20 March 2015** and blocked the intermediate in Chrome. On 1 April, Google and Mozilla announced they would no longer trust new certificates from CNNIC.

*How it was found:* Chrome reported the certificates to Google. Pinning, once more.

*What it taught:* the pattern was now hard to deny. Three of these four incidents were found because the victim happened to be Google, whose keys Chrome knew in advance. For everyone else, there was no detector at all.

### Symantec, 2015 to 2018: the first catch by CT

On **14 September 2015**, Symantec's Thawte brand issued an **Extended Validation precertificate** for `google.com` and `www.google.com`, which Google had neither requested nor authorized. This time no pinning was involved. Since 1 January 2015, Chrome had required EV certificates to be published in **Certificate Transparency logs**, and Google found the precertificate by reading the logs. It had been recorded in logs run by Google and by DigiCert.

Symantec said the certificate was issued during internal testing and fired the employees involved. The audit that followed found more: first 23 test certificates for domains of Google, Opera and others, then **more than 2,400** certificates for domains that had never been registered. Google's response was to require Symantec to log **every** certificate it issued from 1 June 2016. Problems continued to surface, and in 2017 Chrome announced a full distrust: Chrome 66 (April 2018) stopped trusting Symantec certificates issued before June 2016, and Chrome 70 (October 2018) stopped trusting the whole old Symantec infrastructure. Symantec sold its certificate business to DigiCert.

*What it taught:* for the first time a misissued certificate was found **not by luck, not by pinning, but because issuance was public**. Anyone could have found it.

### Since then: Entrust and Fina

Two recent cases show both CT's power and its limit.

In June 2024 Chrome announced it would stop trusting new certificates from **Entrust**, citing a six-year pattern of compliance failures and unmet commitments; Mozilla followed. The interesting detail is *how* "new" was defined: Chrome distrusted certificates whose **earliest SCT** was dated after the cutoff (in the end, 11 November 2024). A CA can write any date it likes into a certificate's notBefore field; it cannot make a log sign an earlier timestamp. CT had become the clock of the Web PKI.

In September 2025 someone noticed on a CT mailing list that **Fina**, a Croatian CA trusted by Microsoft's root program (but not by Chrome, Firefox, Apple or Android), had issued certificates containing **1.1.1.1**, the IP address of Cloudflare's public DNS resolver. Cloudflare's investigation found **twelve** such certificates issued between February 2024 and August 2025. Fina said they were test certificates, issued because IP addresses were entered incorrectly, and that they were logged to CT as part of standard procedure. Cloudflare, itself an operator of CT logs, acknowledged it should have caught them earlier.

*What it taught:* the certificates were public the whole time. For over a year, nobody looked. CT makes detection *possible*; it does not make anyone watch.

## The pattern

Put the cases side by side and the problem is plain:

| incident | who issued | found by | when |
|---|---|---|---|
| Comodo 2011 | breached RA account | the CA | same day |
| DigiNotar 2011 | breached CA | users, Chrome pinning | ~7 weeks |
| TURKTRUST 2012 | mistaken intermediate | Chrome pinning | ~16 months |
| CNNIC/MCS 2015 | delegated intermediate | Chrome reporting | days |
| Symantec 2015 | the CA, "testing" | **CT logs** | days |
| Fina 2024–25 | the CA, "testing" | **CT logs** (late) | up to ~19 months |

Before CT, misissuance was invisible by default. It was found when the victim was one of the few sites pinned in a browser, or when the CA itself noticed and chose to say so. A rogue certificate for a bank, a news site or an activist's mail server could be used quietly, and it would never appear anywhere. Pinning for ordinary sites (HPKP) was tried and abandoned: a mistake in a pin could lock a site out of its own users for months.

What was missing was not better cryptography. The signatures were all valid. What was missing was **a public record of what CAs sign**.

## Certificate Transparency

Ben Laurie, Adam Langley and Emilia Kasper at Google proposed it; the IETF published it as **RFC 6962** in 2013. The idea fits in one sentence: *a browser should only accept a certificate that has been published where everyone can see it.*

<figure class="plate">
<img src="/images/root/03-ct-flow.svg" alt="The CA sends a precertificate to log 1 (operator X) and log 2 (operator Y). The logs return SCTs, promises to publish within 24 hours. The CA embeds them in the certificate and signs it. The server sends it to the browser, which checks the chain and at least 2 valid SCTs from at least 2 log operators. A monitor reads every log entry and alerts the domain owner." width="1000" height="640" loading="lazy" />
<figcaption>The parts of CT, and the path a certificate takes through them.</figcaption>
</figure>

The moving parts:

**Logs.** Public, append-only lists of certificates, run by independent operators (Google, Cloudflare, Let's Encrypt and others). A log accepts any certificate that chains to a root it recognizes. It does **not** judge whether the certificate should have been issued: it only makes it public.

**SCTs.** When a log accepts a certificate it immediately returns a *signed certificate timestamp*: a signature over the certificate and the time, which is a promise to include it in the public log within the **maximum merge delay (MMD)**, 24 hours for the logs browsers accept. Part 02 built real ones, byte by byte.

**Precertificates.** There is a chicken-and-egg problem: the SCTs should be *inside* the certificate, but the logs must sign the certificate first. The solution is the precertificate: the exact certificate, plus a **critical "poison" extension** (OID `1.3.6.1.4.1.11129.2.4.3`). Remember Part 01: a verifier must reject a certificate with a critical extension it does not understand. So a precertificate can never be used as a real one, but it commits the CA to every byte of the final certificate. The CA logs the precertificate, collects the SCTs, then issues the real certificate with the SCT list where the poison was. A browser checking an SCT removes the SCT list and verifies the log's signature over what remains, exactly as `02_handshake.py` does.

**Monitors.** Programs that read every new log entry, looking for certificates for the names they care about. Big sites run their own; services like crt.sh, Cert Spotter and Cloudflare's offer it to everyone. A monitor is what turns "public" into "noticed".

**Browser policy.** This is what gives the system teeth. Chrome has required CT for EV certificates since January 2015, and for **every** publicly trusted certificate issued after 30 April 2018. Firefox enforces CT on desktop since version 135 (February 2025). The current Chrome policy, which Firefox's mirrors, asks for SCTs from distinct logs that it recognizes:

| certificate lifetime | SCTs required (embedded) |
|---|---|
| 180 days or less | 2 |
| more than 180 days | 3 |

and, in every case, **at least two different log operators**. That last rule matters: two logs run by the same company are, for trust purposes, one witness.

## A CT ecosystem in a hundred lines

The companion script adds CT to Part 00's toy PKI. A log signs a promise and, if honest, publishes by the deadline:

```python
@dataclass
class Log:
    name: str
    operator: str
    sk: Ed25519PrivateKey
    honest: bool = True

    def submit(self, cert, at):
        """Sign a promise to publish `cert` within MMD. A dishonest log signs and forgets."""
        sct = SCT(self.name, at, b"")
        sct.signature = self.sk.sign(sct.signed_bytes(cert))
        if self.honest:
            self.pending.append((at + MMD, cert))
        return sct
```

The browser checks the chain exactly as in Part 00, then the CT policy:

```python
good = []
for s in scts:
    if s.log not in self.logs:
        continue                      # an SCT from an unknown log counts for nothing
    operator, pub = self.logs[s.log]
    pub.verify(s.signature, s.signed_bytes(chain[0]))   # forged SCT -> reject
    good.append((s, operator))
if len({s.log for s, _ in good}) < self.min_scts:
    return False, "not enough SCTs"
if len({op for _, op in good}) < 2:
    return False, "SCTs all come from one log operator"
```

And a monitor reads the published entries and flags any certificate for its domain carrying a key the owner does not know. There are four logs: two run by "Google", one by "Let's Encrypt", one by "Cloudflare". Then the script replays the attacks:

```text
scenario                               browser  owner sees       reason
1. honest certificate, 2 SCTs          ACCEPT   nothing          chain ok, CT policy met
2. rogue cert, browser without CT      ACCEPT   nothing          chain ok (no CT check)
3. rogue cert, CT browser, no SCTs     REJECT   nothing          only 0 valid SCT(s), policy needs 2
4. rogue cert, logged honestly         ACCEPT   ALERT (2 log(s)) chain ok, CT policy met
5. two SCTs, same operator             REJECT   ALERT (2 log(s)) SCTs all come from one log operator
6. one SCT forged                      REJECT   ALERT (1 log(s)) SCT claiming to be from oak has a bad signature
7. one log lies, one is honest         ACCEPT   ALERT (1 log(s)) chain ok, CT policy met
8. both logs lie                       ACCEPT   nothing          chain ok, CT policy met
9. backdated cert from distrusted CA   REJECT   nothing          Toy Issuing CA is distrusted for certificates logged after the cutoff
```

Read them in order; each is a lesson.

**1** is the normal case: accepted, and the owner's monitor sees a certificate with the owner's own key, so it stays quiet.

**2 is DigiNotar.** The intermediate signs a certificate for example.com with Mallory's key. A browser that does not check CT accepts it, and the owner sees *nothing*: there is nowhere to see it. Every pre-2013 incident above was this row.

**3** is the same certificate meeting a CT-enforcing browser: rejected, because it was never logged. The attacker now has a choice: stay hidden and be rejected, or log it.

**4** is that choice. The attacker submits the rogue certificate to two logs, gets two valid SCTs, and the browser **accepts** it. CT did not stop the attack. But within the MMD the logs publish the certificate, and the owner's monitor raises an alert. The certificate gets revoked, the CA gets investigated, and its trust may be removed: the Symantec story.

<figure class="plate">
<img src="/images/root/03-detection.svg" alt="Timeline: rogue cert issued, logged and SCTs signed; a window of use up to the 24-hour MMD; the log publishes it by the deadline; the monitor raises an alert about an unknown key; the certificate is revoked and the CA investigated." width="1000" height="420" loading="lazy" />
<figcaption>CT cannot stop the first use. It guarantees there is a second act.</figcaption>
</figure>

**5** shows why the policy counts *operators*. Two SCTs from two logs of the same company are rejected. If one company could vouch twice, then compromising (or pressuring) that one company would be enough. The owner still gets an alert here, because those logs were honest and published the attempt.

**6**: the attacker signs an SCT with their own key and writes a real log's name on it. The log's public key is in the browser, the signature does not verify, rejected. SCTs are not decorations; they are checked.

**7**: one of the two logs is dishonest. It signs the SCT and never publishes. But the other log is honest, publishes, and the owner is alerted. **One honest log among the SCT signers is enough** for detection.

**8 is the hole.** Both logs that signed SCTs are dishonest: two different operators, compromised or coerced. The browser accepts (both SCTs are perfectly valid signatures), and the owner's monitor, reading every log, sees **nothing**, even a month later. Nothing in the SCT itself can reveal that the promise inside it was broken.

**9 is Entrust.** A CA that browsers distrusted for new certificates issues one anyway and backdates its notBefore by two months. A browser that judged by notBefore would be fooled. But the cutoff is checked against the SCT timestamps, which the logs signed, and the logs wrote today's date. Rejected.

## What CT guarantees, and what it assumes

Look again at the shape of the attacks.

<figure class="plate">
<img src="/images/root/03-who-must-lie.svg" alt="Three panels. Before CT: one CA lying is enough to stay secret. CT today: the CA and the logs of operators X and Y must all lie, and then the certificate is still secret, which is the toy's scenario 8. With proofs: the CA and logs may lie, but witnesses see and everyone gets one view, so a broken promise becomes evidence." width="1000" height="470" loading="lazy" />
<figcaption>CT raises the number of parties who must lie. Proofs make the lie itself visible.</figcaption>
</figure>

Before CT, one dishonest or breached party (a CA, or anyone with an issuing account) was enough for a rogue certificate to work **and** stay secret. With CT, the CA **and every log that signed an SCT** must lie, and those logs must belong to at least two different operators. That is a real improvement: logs are few, run by large and well-known organizations, and a log caught breaking a promise is removed from the browsers' lists. In practice, this is most of what keeps CT honest today.

But it is still trust, not proof. Scenario 8 shows the remaining assumption precisely: **an SCT is a promise, and a promise proves nothing about whether it was kept.** A dishonest log has an even subtler option, called a **split view**: it can show the monitors one version of the log (without the rogue certificate) and show anyone who asks about the rogue certificate another version (with it). Each audience sees a consistent story; nobody sees both.

Closing that hole needs three things the toy does not have:

1. **A small commitment to the whole log.** One short value that changes if any entry changes, so a log can sign "this is my entire log at size *n*" in 32 bytes plus a signature. That is the root of a **Merkle tree**.
2. **Proofs against that commitment.** An *inclusion proof* that a given certificate is in the log at a given size, and a *consistency proof* that the log at size *n* is a prefix of the log at size *m*: nothing removed, nothing rewritten. Each is a few hundred bytes of hashes.
3. **One view for everyone.** Some way to make sure every client and every monitor sees the same signed commitments, so a split view is caught. That is the job of **gossip** and, in modern designs, **witnesses** that cosign each log state they have checked.

Real CT logs already are Merkle trees: RFC 6962 specifies them, and everything above exists in some form. [Part 04](/root/04-merkle-trees-from-zero/) builds the trees and the proofs from zero. Part 05 builds the signed checkpoints and the witnesses.

## Back to the bill

Now the two SCTs in Part 02's bill make sense. They exist because the web learned, from DigiNotar onwards, that a CA's signature alone is not enough: issuance must be public and checkable. They are, today, the price of that lesson: 142 bytes with ECDSA, **4,840 bytes with ML-DSA-44**.

And now a sharper question can be asked. The CA signs the certificate, then two logs sign a promise to publish it. Three offline signatures, all about the same fact: *this certificate was issued and is public.* What if the CA's log **were** the publication, and the certificate carried a proof of inclusion in it instead of three signatures? That is the idea of Merkle Tree Certificates, and the reason this series spends the next two parts on trees and checkpoints.

## Try it

From the `experiments\root-of-trust` folder:

```text
python 03_ct_toy.py
python -m unittest test_03_ct_toy
```

Exercises:

1. Change scenario 8 so that only the *Google* logs lie, and get SCTs from argon and xenon. What does the browser say, and why does that rule protect against exactly this?
2. Give the monitor a window: alert only if a rogue certificate appears more than MMD after its SCT timestamp. Which scenario starts to look different, and what real-world failure does that model?
3. Add a CAA check to the toy CA (a dict of domain to allowed CAs). Which scenarios does it prevent, and which can it not touch? (Hint: think about DigiNotar.)
4. Implement a split view: a dishonest log with two lists and a `view_for(who)` method. Can the toy's monitor ever detect it? What would it need?

## Reader checkpoint

<details>
<summary><strong>1.</strong> Why is a site's security bounded by the weakest CA in the store, and not by the CA it chose?</summary>

Because any trusted root, and any intermediate below it, may issue for any name by default. An attacker does not need the site's CA: any breached or careless CA in the store can produce a certificate the browser will accept.

</details>

<details>
<summary><strong>2.</strong> Three of the four pre-CT incidents were found the same way. How, and why does that not scale?</summary>

Chrome had Google's keys pinned (or reported unexpected Google certificates), so forged google.com certificates stood out. That protects only the few sites built into the browser; a rogue certificate for anyone else had nothing to trip over.

</details>

<details>
<summary><strong>3.</strong> What is a precertificate's poison extension for?</summary>

It is a critical extension no browser recognizes, so the precertificate can never be accepted as a real certificate. Yet the precertificate commits to every byte of the final certificate except the SCTs, so the logs can sign it before the SCTs exist.

</details>

<details>
<summary><strong>4.</strong> In scenario 4 the browser accepts the rogue certificate. In what sense did CT still work?</summary>

The attacker could only get SCTs by publishing the certificate. Within the MMD it appears in the logs, the owner's monitor alerts, and the CA can be investigated and distrusted. CT turned a silent attack into a public, attributable one. It never promised prevention.

</details>

<details>
<summary><strong>5.</strong> Why did Chrome key the Entrust distrust on SCT timestamps rather than notBefore?</summary>

The CA writes notBefore and could backdate it. SCT timestamps are written and signed by the logs, which the CA does not control, so they give a date the CA cannot forge.

</details>

<details>
<summary><strong>6.</strong> What exactly does scenario 8 show, and what three things are needed to close it?</summary>

That an SCT is only a promise: if every log that signed one lies, nobody can tell. Closing it needs a compact commitment to the whole log (a Merkle tree head), proofs of inclusion and consistency against it, and a way for everyone to see the same commitments (gossip or witnesses).

</details>

## References

- Fox-IT, *DigiNotar Certificate Authority breach: "Operation Black Tulip"*, interim report, 5 September 2011, and the final report of 2012.
- Comodo, incident report of 23 March 2011; Mozilla Security Blog, *Comodo Certificate Issue – Follow Up*, March 2011.
- A. Langley, [*Enhancing digital certificate security*](https://security.googleblog.com/2013/01/enhancing-digital-certificate-security.html), Google Security Blog, 3 January 2013 (TURKTRUST).
- A. Langley, [*Maintaining digital certificate security*](https://security.googleblog.com/2015/03/maintaining-digital-certificate-security.html), Google Security Blog, March 2015 (CNNIC / MCS Holdings).
- S. Somogyi and A. Eijdenberg, [*Improved Digital Certificate Security*](https://security.googleblog.com/2015/09/improved-digital-certificate-security.html), Google Security Blog, 18 September 2015 (Symantec/Thawte, found in CT).
- Chrome Security Team, [*Chrome's Plan to Distrust Symantec*](https://security.googleblog.com/2017/09/chromes-plan-to-distrust-symantec.html), September 2017.
- Chrome Root Program, [*Sustaining Digital Certificate Security: Entrust Certificate Distrust*](https://security.googleblog.com/2024/06/sustaining-digital-certificate-security.html), June 2024.
- Cloudflare, [*Addressing the unauthorized issuance of multiple TLS certificates for 1.1.1.1*](https://blog.cloudflare.com/unauthorized-issuance-of-certificates-for-1-1-1-1), September 2025; and [Mozilla bug 1986968](https://bugzilla.mozilla.org/show_bug.cgi?id=1986968) (Fina).
- SSLMate, [*Timeline of Certificate Authority Failures*](https://sslmate.com/certspotter/failures): a long, sourced list beyond the cases above.
- RFC 6962, *Certificate Transparency* (2013); RFC 9162, *Certificate Transparency Version 2.0* (2021).
- [Chrome Certificate Transparency Policy](https://googlechrome.github.io/CertificateTransparency/ct_policy.html); [Mozilla: Certificate Transparency](https://wiki.mozilla.org/SecurityEngineering/Certificate_Transparency) (enforced from Firefox 135).
- RFC 8659, *DNS Certification Authority Authorization (CAA) Resource Record*.
