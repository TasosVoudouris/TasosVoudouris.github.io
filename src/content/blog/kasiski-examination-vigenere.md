---
title: "Classical Cryptanalysis III: The Kasiski Examination — Cryptanalysis of the Vigenère Cipher"
description: A complete ciphertext-only study of repeating-key Vigenère cryptanalysis
  using repeated n-grams, spacing divisors, Index of Coincidence, Friedman estimation,
  chi-squared column recovery, and end-to-end verification.
pubDate: '2026-08-12'
updatedDate: '2026-09-12'
topics:
- Classical Cryptography
- Cryptanalysis
- Mathematical Foundations
tags:
- kasiski
- vigenere
- classical-cryptography
- index-of-coincidence
- friedman-test
difficulty: Intermediate
sourcePath: experiments/cryptanalysis/kasiski
status: Validated
draft: false
series: Classical Cryptanalysis
seriesOrder: 3
---
> A complete, executable treatment of repeated-sequence analysis, period
> estimation, the Index of Coincidence, chi-squared key recovery, and the
> limitations of classical ciphertext-only cryptanalysis.

This chapter turns the original notebook and script into one coherent analysis.
It preserves the original progression—Vigenère encryption, Kasiski examination,
frequency analysis, and decryption—but makes every assumption explicit and
corrects the period-selection and frequency-analysis shortcuts that can produce
misleading results.

The complete implementation is in [`kasiski.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/kasiski/kasiski.py), the interactive
version is [`kasiski.ipynb`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/kasiski/kasiski.ipynb), and all numerical claims are checked
by [`test_kasiski.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/kasiski/test_kasiski.py).

## Contents

- [1. Scope and purpose](#1-scope-and-purpose)
- [2. Historical context](#2-historical-context)
- [3. The repeating-key Vigenère cipher](#3-the-repeating-key-vigenère-cipher)
- [4. Why ordinary frequency analysis is obscured](#4-why-ordinary-frequency-analysis-is-obscured)
- [5. The central Kasiski observation](#5-the-central-kasiski-observation)
- [6. Repeated n-grams, positions, and spacings](#6-repeated-n-grams-positions-and-spacings)
- [7. From spacings to period candidates](#7-from-spacings-to-period-candidates)
- [8. Accidental repetitions and dependent evidence](#8-accidental-repetitions-and-dependent-evidence)
- [9. The Index of Coincidence](#9-the-index-of-coincidence)
- [10. The Friedman estimate](#10-the-friedman-estimate)
- [11. Combining Kasiski and IC evidence](#11-combining-kasiski-and-ic-evidence)
- [12. Recovering the key by chi-squared analysis](#12-recovering-the-key-by-chi-squared-analysis)
- [13. Complete attack on the bundled sample](#13-complete-attack-on-the-bundled-sample)
- [14. Understanding each implementation component](#14-understanding-each-implementation-component)
- [15. Failure modes and diagnostic checks](#15-failure-modes-and-diagnostic-checks)
- [16. Which ciphers are and are not affected](#16-which-ciphers-are-and-are-not-affected)
- [17. Complexity and reproducible experimentation](#17-complexity-and-reproducible-experimentation)
- [18. Extensions and further study](#18-extensions-and-further-study)
- [19. Running the project](#19-running-the-project)
- [20. References](#20-references)

---

## 1. Scope and purpose

The Kasiski examination is a classical ciphertext-only technique for estimating
the period of a periodic polyalphabetic substitution cipher. Its best-known
application is the repeating-key Vigenère cipher.

The complete attack is not merely “find repeated letters.” It has two logically
separate phases:

1. **period discovery:** infer the length of the repeated key from periodic
   structure in the ciphertext; and
2. **column recovery:** after fixing a period, split the ciphertext into
   interleaved monoalphabetic streams and solve each as a Caesar cipher.

This distinction matters. Kasiski evidence normally produces **candidate
factors**, not a guaranteed key length. The Index of Coincidence can reinforce
the correct family of candidates, but it often scores multiples of the true
period highly. Finally, frequency analysis can fail when the resulting columns
are short or when the wrong language model is used.

The code therefore reports a ranking and retains intermediate evidence instead
of presenting one unexplained number as certain.

### Attack model

The demonstration assumes that the analyst:

- possesses only ciphertext;
- knows or suspects the repeating-key Vigenère construction;
- knows that the plaintext is approximately English;
- assumes the alphabet is the 26 letters `A` through `Z`; and
- has enough ciphertext for repeated sequences and letter statistics to become
  visible.

The implementation does **not** use the original plaintext's frequency table
when recovering the key. Doing so would leak information unavailable in a real
ciphertext-only attack.

---

## 2. Historical context

The construction now commonly called the Vigenère cipher belongs to a longer
development of polyalphabetic substitution. The repeating-key idea is commonly
traced to Giovan Battista Bellaso's 1553 work, while Blaise de Vigenère described
an autokey construction in 1586. The familiar repeating-key system was later
misattributed to Vigenère, and the name remained.

In 1863, the retired Prussian officer Friedrich Wilhelm Kasiski published
*Die Geheimschriften und die Dechiffrir-Kunst*. It contained the first published
systematic method for attacking periodic polyalphabetic ciphers by studying
repeated ciphertext sequences and their spacings. Historical accounts also
attribute earlier unpublished work on related attacks to Charles Babbage; the
details and dates differ among secondary sources, so Kasiski's unambiguous place
is as the first publisher of the general method.

William F. Friedman later developed the Index of Coincidence as a statistical
tool for cryptanalysis. IC provides evidence even when a message contains too
few useful literal repetitions for a decisive manual Kasiski examination.

These developments are historically important because they moved cryptanalysis
from guessing isolated words toward systematic exploitation of periodicity and
language statistics.

---

## 3. The repeating-key Vigenère cipher

Map the alphabet to integers:

$$
A\mapsto0,\ B\mapsto1,\ \ldots,\ Z\mapsto25.
$$

Let the normalized plaintext be

$$
P=P_0P_1\ldots P_{N-1}
$$

and let the key contain $\ell$ letters

$$
K=K_0K_1\ldots K_{\ell-1}.
$$

The key repeats periodically. Encryption is

$$
C_i=P_i+K_{i\bmod\ell}\pmod{26},
$$

and decryption is

$$
P_i=C_i-K_{i\bmod\ell}\pmod{26}.
$$

```python
from kasiski import vigenere_decrypt, vigenere_encrypt

ciphertext = vigenere_encrypt("ATTACK AT DAWN", "LEMON")
assert ciphertext == "LXFOPVEFRNHR"
assert vigenere_decrypt(ciphertext, "LEMON") == "ATTACKATDAWN"
```

The default implementation removes spaces, punctuation, digits, and non-ASCII
letters. This matches traditional cryptanalytic preprocessing. Formatting can
be retained for demonstrations:

```python
assert vigenere_encrypt(
    "ATTACK AT DAWN",
    "LEMON",
    preserve_nonletters=True,
) == "LXFOPV EF RNHR"
```

Nonletters do not consume key positions. Cryptanalysis is always performed on
the normalized `A`–`Z` stream, so reported sequence positions refer to that
stream rather than the original formatted document.

### Key length versus fundamental period

The cryptanalytic period is the shortest repeating unit. For example,
`MOUSEMOUSE` has ten written characters but fundamental period five. Encryption
with `MOUSEMOUSE` is identical to encryption with `MOUSE`.

Therefore a correct attack should prefer the minimal period and reduce an
obviously repeated recovered key to its shortest unit.

---

## 4. Why ordinary frequency analysis is obscured

A Caesar cipher maps each plaintext letter through one fixed shift. Its
ciphertext frequency distribution is merely a rotation of the plaintext
distribution, so a frequent ciphertext letter is likely to correspond to a
frequent plaintext letter.

Vigenère uses $\ell$ different shifts. The same plaintext letter can become
different ciphertext letters depending on its position modulo $\ell$. If the
entire ciphertext is counted as one stream, the shifted distributions are
mixed. This flattens and obscures the frequency pattern that defeats a Caesar
cipher.

The periodic key also creates the weakness that repairs the frequency attack.
If $\ell$ is known, form columns

$$
\mathcal{C}_j=C_j,C_{j+\ell},C_{j+2\ell},\ldots,
\qquad 0\le j<\ell.
$$

Every character in column $\mathcal{C}_j$ was encrypted by the same key letter
$K_j$. Each column is therefore one Caesar cipher. Period discovery turns one
polyalphabetic problem into $\ell$ monoalphabetic problems.

---

## 5. The central Kasiski observation

Suppose an $n$-letter plaintext fragment occurs at positions $a$ and $b$. The
two copies are encrypted by the same key segment when

$$
b-a\equiv0\pmod{\ell}.
$$

Under that alignment, equal plaintext fragments produce equal ciphertext
fragments. Their spacing

$$
d=b-a
$$

is therefore a multiple of the key period:

$$
\ell\mid d.
$$

Repeated ciphertext fragments are collected, their spacings are measured, and
common divisors of those spacings become period candidates.

### What this implication does not say

The observation is one-directional evidence, not an equivalence:

- equal plaintext fragments separated by a nonmultiple of $\ell$ are normally
  encrypted under different key segments and need not match in ciphertext;
- equal ciphertext fragments can occur accidentally even when the plaintext
  fragments differ; and
- an observed spacing may be a multiple of $2\ell$, $3\ell$, or another
  multiple, so one spacing does not reveal the minimal period by itself.

This is why several repetitions and a second statistical method are useful.

---

## 6. Repeated n-grams, positions, and spacings

An **n-gram** is a contiguous sequence of $n$ symbols. Kasiski analysis commonly
starts with trigrams and then includes longer sequences. Longer matches are less
likely to be accidental, but they also occur less often.

```python
from kasiski import find_repeated_ngrams_positions

repeated = find_repeated_ngrams_positions("ABCABCABC", 3)
assert repeated["ABC"] == [0, 3, 6]
```

For positions $[0,3,6]$, the consecutive spacings are $[3,3]$. All pairwise
spacings would be $[3,6,3]$.

```python
from kasiski import all_distances_from_positions

assert all_distances_from_positions([0, 3, 6]) == [3, 3]
assert all_distances_from_positions(
    [0, 3, 6],
    consecutive_only=False,
) == [3, 6, 3]
```

The implementation uses consecutive occurrences by default. With $r$
occurrences, this contributes $r-1$ spacings rather than $r(r-1)/2$, preventing
one highly repeated sequence from receiving quadratically more weight.

### Several n-gram lengths

```python
from kasiski import kasiski_distances

distance_counts, distances = kasiski_distances(
    ciphertext,
    min_n=3,
    max_n=5,
)
```

Using several lengths balances two goals:

- shorter n-grams provide more observations; and
- longer n-grams provide stronger individual evidence against coincidence.

However, a repeated 5-gram contains repeated 3-grams and 4-grams. These are not
independent observations. The code deliberately exposes the raw evidence and
does not assign it a false probabilistic interpretation.

---

## 7. From spacings to period candidates

For every spacing $d$, candidate $t$ receives a vote if $t$ divides $d$. A
simple score is

$$
V(t)=\sum_{d\in\mathcal{D}}\mathbf{1}[t\mid d],
$$

where $\mathcal{D}$ is the spacing multiset.

```python
from kasiski import factor_score

votes = factor_score(distances, max_period=20)
print(votes.most_common(10))
```

The code tests every bounded candidate directly. This avoids a subtle factoring
bug in which a loop ending below $\sqrt d$ can omit the square root, large
complementary factors, or the distance itself.

### Why divisors compete

If the true period is 8, many useful spacings are divisible by 8. They are also
divisible by 2 and 4. Consequently Kasiski votes often rank small factors highly:

$$
8\mid d\quad\Longrightarrow\quad2\mid d\ \text{and}\ 4\mid d.
$$

Kasiski evidence can reveal the factor structure of the period without uniquely
identifying the fundamental period.

### GCD reasoning

In a clean textbook example, the greatest common divisor of several genuine
spacings may equal the period:

$$
\gcd(d_1,d_2,\ldots)=\ell.
$$

A single accidental spacing can reduce the global GCD to 1, so real analysis is
usually more tolerant: inspect divisor votes, GCDs of subsets, or pairwise GCD
statistics. The module includes `gcd_score` as supplementary evidence but does
not let it replace the full ranking.

---

## 8. Accidental repetitions and dependent evidence

Repeated ciphertext n-grams arise for two reasons:

1. a repeated plaintext fragment is aligned under the same portion of the key;
2. unrelated fragments collide by chance.

Under the simplified model of independent uniformly random letters, two
specific $n$-grams match with probability $26^{-n}$. A length-$N$ ciphertext
contains approximately $N-n+1$ n-grams, so the expected number of matching
pairs is roughly

$$
\binom{N-n+1}{2}\frac{1}{26^n}.
$$

This is only an intuition:

- natural language is not uniform or independent;
- adjacent n-grams overlap;
- a Vigenère ciphertext is not an ideal random string;
- repeated phrases and document structure create correlated matches; and
- the same long repetition produces many nested shorter repetitions.

### Practical controls

- Use n-grams of at least three characters.
- Compare several lengths rather than relying on one trigram.
- Inspect how many distinct sequences support a period, not only how many raw
  spacings exist.
- Cross-check with IC or shift-coincidence evidence.
- Treat a candidate supported by one repeated fragment as weak.
- For very short ciphertexts, report that the evidence is insufficient rather
  than forcing a period.

---

## 9. The Index of Coincidence

For a string of length $N$ with letter counts $f_A,\ldots,f_Z$, the Index of
Coincidence is

$$
\operatorname{IC}
=\frac{\sum_{x\in\mathcal{A}}f_x(f_x-1)}{N(N-1)}.
$$

It is the probability that two distinct positions sampled uniformly without
replacement contain the same letter.

For uniformly random letters,

$$
\operatorname{IC}_{\mathrm{random}}=\frac1{26}\approx0.03846.
$$

For the English monogram model bundled with this project,

$$
\sum_x p_x^2\approx0.06550.
$$

Actual English samples vary with length and genre, so neither number is a hard
threshold.

```python
from kasiski import index_of_coincidence

assert index_of_coincidence("AAAA") == 1.0
assert index_of_coincidence("ABCD") == 0.0
```

### Average column IC

For candidate period $t$, split the ciphertext into $t$ columns and calculate

$$
\overline{\operatorname{IC}}(t)
=\frac1t\sum_{j=0}^{t-1}\operatorname{IC}(\mathcal{C}_j).
$$

If $t=\ell$, each column is a Caesar-shifted language sample and should retain
language-like IC. If $t$ is a wrong divisor, columns mix several shifts and IC
usually moves toward the random baseline.

```python
from kasiski import best_period_by_ic

for period, average_ic in best_period_by_ic(ciphertext, 20)[:10]:
    print(period, average_ic)
```

### The multiple-period trap

If $t=m\ell$ is a multiple of the true period, each column still uses one fixed
key shift. Multiples can therefore have IC as high as—or slightly higher than—
the true period. The columns are shorter, so sampling variation becomes larger.

Selecting `max(average_ic)` is not a reliable fundamental-period rule. In the
earlier demonstration, this selected period 16 for an 8-letter key. Key recovery
then produced the repeated string `LEMONADALEMONADA`; decryption succeeded, but
the claimed key length was not minimal.

This is an important diagnostic lesson: **correct plaintext does not prove that
the reported period is fundamental**.

---

## 10. The Friedman estimate

Friedman's method uses the IC of the full ciphertext to estimate a repeating-key
period. Let $\kappa_L$ be the expected language IC, $\kappa_R=1/26$, and $N$ the
ciphertext length. One common approximation is

$$
\widehat{\ell}
=\frac{(\kappa_L-\kappa_R)N}
{(N-1)\operatorname{IC}(C)-\kappa_RN+\kappa_L}.
$$

```python
from kasiski import friedman_period_estimate

print(friedman_period_estimate(ciphertext))
```

The result is a real-valued estimate, not a proof and not necessarily an
integer. It depends on the assumed language IC, the message length, and how well
the plaintext matches the language model. In the bundled experiment the true
period is 5 while the estimate is approximately 7.23. That discrepancy is not
a code failure; it demonstrates why Friedman, Kasiski, and column IC should be
used as complementary evidence.

When the denominator is close to zero, the estimate is unstable. The code
returns infinity when the modeled denominator is nonpositive.

---

## 11. Combining Kasiski and IC evidence

The project combines two normalized signals:

$$
K_t=\frac{V(t)}{\max_uV(u)}
$$

and

$$
I_t=
\frac{\max(0,\overline{\operatorname{IC}}(t)-1/26)}
{\max_u\max(0,\overline{\operatorname{IC}}(u)-1/26)}.
$$

The default teaching score is

$$
S_t=0.55K_t+0.45I_t.
$$

```python
from kasiski import rank_periods

ranking = rank_periods(
    ciphertext,
    max_period=20,
    min_n=3,
    max_n=5,
    kasiski_weight=0.55,
)
```

This combination addresses opposite tendencies:

- Kasiski divisor votes can overvalue small factors;
- average IC can overvalue multiples of the true period.

The formula is a transparent educational heuristic, not a universal optimum or
a formal maximum-likelihood estimator. Analysts should inspect both components,
change the range of candidate periods, and verify that the recovered key and
plaintext are plausible.

### Why the full ranking is retained

A single winning period hides ambiguity. `PeriodEvidence` records:

- candidate period;
- Kasiski vote count;
- average column IC;
- normalized Kasiski component;
- normalized IC component; and
- combined score.

This makes it possible to see harmonics, close candidates, and cases where one
method dominates the other.

---

## 12. Recovering the key by chi-squared analysis

After choosing period $\ell$, each column is attacked as a Caesar cipher. For a
candidate shift $s$, decrypt the column's counts and compare them with expected
English frequencies.

If $O_x(s)$ is the deciphered count of letter $x$ and $p_x$ is its modeled
English probability, the expected count is

$$
E_x=N_jp_x,
$$

and Pearson's statistic is

$$
\chi^2(s)=\sum_{x\in\mathcal{A}}
\frac{(O_x(s)-E_x)^2}{E_x}.
$$

The shift with the smallest statistic is the best monogram-model candidate.

```python
from kasiski import rank_shifts_for_column, split_columns

columns = split_columns(ciphertext, period)
for column in columns:
    best_shift, statistic = rank_shifts_for_column(column)[0]
    print(best_shift, statistic)
```

The recovered shifts are mapped back through `0 -> A`, ..., `25 -> Z`.

```python
from kasiski import recover_key

key = recover_key(ciphertext, period)
```

### Why this is stronger than “most common equals E”

The original notebook selected the most frequent ciphertext letter in each
column and aligned it with the most frequent letter of the **known original
plaintext**. That approach has two problems:

1. a ciphertext-only attacker does not possess the plaintext frequency table;
2. even in English, `E` is not guaranteed to be the most frequent letter in
   every finite column.

Chi-squared scoring uses the complete public language model and tests all 26
shifts. It is still imperfect, but it does not leak the answer and uses much
more information than one frequency maximum.

### Short-column uncertainty

If the ciphertext has length $N$ and candidate period $\ell$, each column has
only about $N/\ell$ letters. Large candidate periods make the columns short and
shift rankings noisy. Useful improvements include:

- retaining the top several shifts per column;
- using bigram, trigram, or tetragram language scores;
- applying beam search over key combinations;
- using dictionary or word-segmentation scores; and
- combining multiple ciphertexts encrypted under the same key.

---

## 13. Complete attack on the bundled sample

The supplied file [`input-1-50.txt`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/kasiski/input-1-50.txt) is normalized to 2,634
letters and encrypted with the demonstration key `MOUSE`. The attack receives
only the ciphertext and the English frequency model.

```python
from pathlib import Path
from kasiski import break_vigenere, clean_text, vigenere_encrypt

plaintext = clean_text(Path("input-1-50.txt").read_text(encoding="utf-8"))
ciphertext = vigenere_encrypt(plaintext, "MOUSE")
result = break_vigenere(ciphertext, max_period=20)

assert result.period == 5
assert result.key == "MOUSE"
assert result.plaintext == plaintext
```

### Observed period evidence

| Rank | Period | Kasiski votes | Average IC | Combined score | Interpretation |
|---:|---:|---:|---:|---:|---|
| 1 | 5 | 1116 | 0.0677 | 0.987 | fundamental period |
| 2 | 15 | 571 | 0.0685 | 0.731 | multiple $3\ell$ |
| 3 | 10 | 572 | 0.0678 | 0.721 | multiple $2\ell$ |
| 4 | 20 | 216 | 0.0677 | 0.545 | multiple $4\ell$ |
| 5 | 2 | 618 | 0.0423 | 0.362 | divisor noise; IC is weak |

The table illustrates both central ambiguities:

- period 2 receives many divisor votes but its column IC is not language-like;
- periods 10, 15, and 20 have language-like IC but weaker Kasiski support than
  the fundamental period 5.

Some of the most frequent distances are 75, 225, 670, 660, 295, and 1050. Each
is divisible by 5. Accidental and correlated repeats still exist, so the attack
uses the aggregate pattern rather than one spacing.

### End-to-end result

```text
True key:          MOUSE
Recovered period:  5
Recovered key:     MOUSE
Decryption correct: True
```

The deterministic result is a regression example, not a claim that every
2,634-letter English text is equally easy. Different genres and keys should be
tested in a broader experimental study.

---

## 14. Understanding each implementation component

### `clean_text`

Normalizes to uppercase ASCII `A`–`Z`. This defines the alphabet and the
positions used throughout the attack.

### `vigenere_encrypt` and `vigenere_decrypt`

Implement modular addition and subtraction. They reject an empty normalized key
instead of failing later with division by zero.

### `find_repeated_ngrams_positions`

Uses a dictionary from each n-gram to its start positions. Overlapping
occurrences are included because they are legitimate occurrences, but their
evidence is not independent.

### `all_distances_from_positions`

Uses consecutive distances by default, with an option for all pairs. It checks
that positions are distinct and sorts them before subtraction.

### `kasiski_distances`

Combines repeated-sequence distances across a configurable range of n-gram
lengths. It returns both a histogram and the flat spacing list.

### `factor_score` and `gcd_score`

`factor_score` tests every candidate period against every spacing. `gcd_score`
offers a supplementary outlier-tolerant view based on pairwise GCDs.

### `index_of_coincidence` and `average_column_ic`

Compute full-stream or column-wise coincidence probabilities. Empty and
one-letter strings return zero because no pair of distinct positions exists.

### `friedman_period_estimate`

Provides an independent approximate scalar estimate and clearly handles an
unstable denominator.

### `rank_periods`

Keeps the Kasiski and IC evidence separately, normalizes them, and applies an
explicit weight. It returns every candidate rather than only the winner.

### `rank_shifts_for_column`

Tests all 26 Caesar shifts and retains the full chi-squared ranking. The code
rotates ciphertext counts so that plaintext index $p$ receives ciphertext count
$(p+s)\bmod26$ under candidate key shift $s$.

### `minimal_repeating_unit`

Reduces candidates such as `MOUSEMOUSE` to `MOUSE`, ensuring the final period is
fundamental when the recovered key is exactly repetitive.

### `break_vigenere`

Connects period ranking, key recovery, decryption, and evidence retention in one
reproducible function.

---

## 15. Failure modes and diagnostic checks

### Insufficient ciphertext

Short messages may contain no useful repeated trigrams, and their columns may be
too small for stable monogram statistics. A failed Kasiski examination is not
evidence of a long key; it can simply mean there is too little data.

### Period search bound is too small

If `max_period` is below the true period, the algorithm can only select a
divisor, an alias, or noise. Always report the searched range.

### Period search bound is too large

Very large periods create tiny columns. Their average IC can fluctuate upward,
and chi-squared recovery becomes unreliable. The upper bound should be
reasonable relative to the ciphertext length.

### Repetitive or artificial plaintext

Repeating a whole paragraph produces many unusually strong Kasiski repetitions
and makes an experiment easier than ordinary prose. The final demonstration
uses the supplied long sample without duplicating it.

### Key has internal repetition

A written key such as `ABCABC` has fundamental period 3. The attack should
report `ABC`, because both strings generate the same keystream.

### Coincidental n-grams

One accidental spacing may inject unrelated factors. Inspect several n-grams,
use longer matches, and compare Kasiski evidence with IC.

### Wrong language model

English frequencies are unsuitable for Greek, French, source code, compressed
data, or arbitrary identifiers. Supply the proper alphabet and probability
model or use a more suitable plaintext-scoring method.

### Normalization mismatch

If encryption advances the key over spaces but analysis removes spaces, the
assumed periodic positions are wrong. Sender and analyst must use the same rule
for which symbols consume a key character.

### Correct decryption under a repeated key

If period 10 yields `MOUSEMOUSE`, the plaintext will be correct but the minimal
period is 5. Always reduce exact repetitions and compare harmonic candidates.

### Plausible but incorrect plaintext

Monogram scoring can select locally plausible shifts that combine into poor
text. Check n-gram language likelihood, word structure, key rank gaps, and
whether alternative period candidates improve the global score.

---

## 16. Which ciphers are and are not affected

### Directly relevant

The reasoning applies to repeating-key Vigenère and, with adjusted arithmetic,
to other periodic polyalphabetic substitutions. Periodic rotor or stream-like
systems can also leak spacing or coincidence structure, although their exact
attack equations differ.

### Variants requiring modification

- **Beaufort and variant Beaufort:** the period search remains relevant, but
  encryption and Caesar-shift recovery use different subtraction conventions.
- **Generalized Vigenère:** a different alphabet size changes modular arithmetic,
  random IC, frequency models, and collision rates.
- **Mixed alphabets:** column recovery is monoalphabetic but not necessarily a
  simple Caesar rotation.

### Cases where the short-period attack fails

- **Autokey:** the keystream continues with plaintext-derived symbols rather
  than repeating a short word.
- **Running key:** a long nonrepeating text is used as keystream.
- **One-time pad:** a uniformly random key as long as the message has no repeated
  short period; with correct one-time use it has information-theoretic secrecy.
- **Modern block and stream ciphers:** they are designed to avoid exploitable
  short periodic substitution structure. Kasiski analysis is not a meaningful
  attack on AES, ChaCha20, or properly used authenticated encryption.

The historical lesson remains modern: repeating structured keystream material
can convert local statistical regularities into global cryptanalytic evidence.

---

## 17. Complexity and reproducible experimentation

Let $N$ be ciphertext length, $q$ the number of tested n-gram lengths, $P$ the
largest candidate period, and $D$ the number of collected spacings.

| Stage | Teaching implementation cost |
|---|---:|
| n-gram dictionary construction | $O(qN)$ expected time |
| consecutive spacing collection | $O(D)$ |
| divisor voting | $O(DP)$ |
| IC ranking for all periods | $O(PN)$ |
| chi-squared key recovery | $O(26N)$ after period selection |

The direct implementation is more than sufficient for classroom-sized texts.
Large-scale tools can use suffix arrays, suffix automata, rolling hashes,
divisor precomputation, and vectorized scoring.

### Experimental reporting checklist

1. state the plaintext language and source;
2. report normalization and alphabet rules;
3. state the true fundamental key period;
4. do not repeat a paragraph merely to inflate the sample without disclosure;
5. report ciphertext length and searched period range;
6. report n-gram lengths and consecutive/all-pair spacing choice;
7. retain several period and shift candidates;
8. separate period accuracy, key accuracy, and plaintext accuracy;
9. repeat evaluation over several keys and texts; and
10. use deterministic fixtures for regression tests but varied data for
    performance claims.

---

## 18. Extensions and further study

The current implementation is a sound foundation for more advanced classical
cryptanalysis.

### Weighted Kasiski evidence

Longer n-grams can receive larger weights because accidental matches are less
likely. Evidence should be grouped by the maximal repeated sequence so nested
substrings do not receive independent weight.

### Shift autocorrelation

Compare the ciphertext with shifted copies and count equal symbols. Peaks often
appear at multiples of the key period, offering another periodicity diagnostic.

### Mutual Index of Coincidence

Columns can be shifted against one another to estimate relative key-letter
differences. Once one shift is anchored, the others follow. This uses
cross-column relations rather than solving every column independently.

### Better language scoring

Monograms ignore letter order. Tetragram log-likelihoods are often much more
discriminating. A practical solver can retain the top shifts for each column and
use beam search or hill climbing to maximize global n-gram likelihood.

### Confidence and model selection

Rather than a fixed weighted sum, periods can be compared using likelihood,
Bayesian evidence, bootstrap intervals, permutation tests, or held-out language
scores. Such methods should still account for harmonic periods and multiple
testing.

### Multilingual support

Generalize the alphabet, cleaning rules, expected IC, and frequency model.
Greek text, for example, requires a decision about tonos, final sigma, spaces,
and whether all characters consume a key position.

---

## 19. Running the project

Python 3.10 or newer is recommended. No third-party dependency is required.

```bash
python kasiski.py
python -m unittest -v test_kasiski.py
```

Expected checkpoints are:

- the `ATTACK AT DAWN` / `LEMON` known-answer vector passes;
- all 17 regression tests pass;
- the bundled sample has 2,634 normalized letters;
- combined evidence selects fundamental period 5;
- chi-squared column recovery produces `MOUSE`; and
- the recovered normalized plaintext equals the original normalized sample.

The notebook imports the same checked module rather than keeping a second,
divergent implementation.

---

## 20. References

Machine-readable entries are provided in [`references.bib`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/blob/main/experiments/cryptanalysis/kasiski/references.bib).

1. F. W. Kasiski, *Die Geheimschriften und die Dechiffrir-Kunst*, Berlin:
   E. S. Mittler und Sohn, 1863.
2. W. F. Friedman, *The Index of Coincidence and Its Applications in
   Cryptanalysis*, Riverbank Publication No. 22, 1922. A later official
   reproduction is preserved in the NSA Friedman collection.
3. F. L. Bauer, *Decrypted Secrets: Methods and Maxims of Cryptology*, 4th ed.,
   Springer, 2007. <https://doi.org/10.1007/978-3-540-48121-8>
4. D. Kahn, *The Codebreakers: The Comprehensive History of Secret
   Communication from Ancient Times to the Internet*, revised ed., Scribner,
   1996.
5. C. Shene, “Kasiski's Method” and “Index of Coincidence,” Michigan
   Technological University cryptography tutorials.

### Ethical use

Use cryptanalytic techniques only on educational material or systems you own or
are explicitly authorized to test. This project concerns obsolete classical
ciphers and must not be presented as protection for real data.
