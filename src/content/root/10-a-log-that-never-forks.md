---
title: 'A log that never forks'
description: 'The one rule a transparency log must never break, and the engineering that keeps it under crashes, storage rollbacks, a second copy of the service and a reused key. Five commit protocols for a tiled log, crashed before every step and judged by a referee and a witness: two of them fork, one gets stuck, and two recover by themselves. With the Sunlight CT log design, its known crash scenarios, and what it all means for an MTC CA.'
part: 10
pubDate: 2026-11-24
tags:
  - transparency-logs
  - tlog-tiles
  - merkle-tree-certificates
  - fault-tolerance
  - witnesses
companion: experiments/root-of-trust
---

Everything in this series rests on one promise. A log signs checkpoints, and every checkpoint it ever signs describes a prefix of the same history. Part 04 turned that promise into consistency proofs, Part 05 into witnesses who check it, and Parts 07 and 08 into certificates and landmarks that inherit it. If a log ever signs two checkpoints that disagree about the past, it has **forked**. Witnesses will refuse to cosign anything after the fork, monitors will flag it, and for an MTC CA the draft is blunt: a CA that has signed inconsistent subtree hashes should move to a new issuance log (draft -07, §12.2.1). The old log is finished.

Part 09 wrote tiles in a world where nothing fails. This part puts the writer on real infrastructure, where processes crash between two writes, storage requests time out and succeed later, operators restore backups, and someone starts a second copy of the service by mistake. The question is the engineering one: **in what order must a log write its files so that no failure can make it fork?**

The method is a fault injection experiment. The script builds five commit protocols for a tiled log. Each uses the same steps in a different order. It crashes each protocol before every step, rolls its storage back, starts a twin on the same storage, and starts a fresh log with an old key. A referee that sees every checkpoint ever signed counts the results.

By the end you should be able to:

1. say precisely what a fork is, and why a crash can cause one even though the log never "lies";
2. explain why a log needs a record of its last signed checkpoint that is separate from its storage, and why that record needs compare-and-swap;
3. read a commit protocol and find its dangerous window;
4. explain the Sunlight CT log's commit order and its one known weakness with write-once storage;
5. design a commit order that recovers by itself from any crash, on any storage.

The code is [`experiments/root-of-trust/10_never_fork.py`](https://github.com/TasosVoudouris/TasosVoudouris.github.io/tree/main/experiments/root-of-trust), with tests in `test_10_never_fork.py`. It writes Part 09's tiles and signs Part 05's checkpoints. It takes about half a minute to run.

## How an honest log forks

<img src="/images/root/10-fork.svg" alt="The naive log publishes checkpoint 587, then crashes before uploading that round of tiles. On restart it rebuilds from storage, which ends at entry 315, and in-flight clients retry in a new order. Checkpoint 640 has certificate 359 at position 315 where 587 had certificate 316. Two signed checkpoints disagree about the past." width="1000" height="560" loading="lazy" />

Nobody in this story is malicious. A log batches submissions every second or so, as Sunlight does: it drains its pool of pending submissions, appends them to the tree, writes the new tiles, signs a checkpoint and answers the submitters. The **naive** protocol does it in this order:

1. drain the pool;
2. sign the new checkpoint;
3. publish the checkpoint to storage, where witnesses and clients read it;
4. upload the new tiles;
5. acknowledge the submitters (return their SCTs, or for MTC, let their certificates be issued).

Now crash the process between steps 3 and 4. The checkpoint for 587 entries is public, and witnesses may already have cosigned it. The tiles for entries 315 to 586 exist only in memory, which is gone. On restart, the log rebuilds its tree from storage, which ends at 315 entries. The clients whose submissions were in that batch never got an answer, so they retry, in whatever order the retries happen to arrive. The log appends them, signs and publishes:

```text
== one crash, told step by step: the naive protocol ==
  witnesses saw checkpoint size    96  root 4868a8083d720f63
  witnesses saw checkpoint size   315  root 627262ce5d60ff1b
  witnesses saw checkpoint size   587  root 987f84e8894dd637
  witnesses saw checkpoint size   640  root 357b5a46a2b94f57
  witnesses saw checkpoint size   687  root 4150f6f563a3b074
  witnesses saw checkpoint size   979  root aeedd561613393ac
  -> 3 pair(s) of published checkpoints disagree about the past
  checkpoints 587 and 640 first differ at entry 315: 'cert 316 seed 3' vs 'cert 359 seed 3'
```

Checkpoint 640 is not an extension of 587: position 315 holds a different certificate. No consistency proof from 587 to 640 can exist. The log signed both. From the outside this is indistinguishable from a log that shows different histories to different people, which is exactly the attack transparency exists to catch.

Two lessons generalize. First, **a fork does not need a lie, only a forgotten signature**: the log forgot that it had signed 587. Second, **order is not deterministic across a crash**: if the retried batch came back in exactly the same order, the new tree would match, but nothing guarantees that. Retries race, new submissions arrive in between, and the pool is rebuilt from scratch.

So the rule has two parts. **Never publish a checkpoint whose tiles are not durable**, and **never forget a checkpoint you have signed**.

## Five orders

<img src="/images/root/10-orders.svg" alt="Five commit orders. Naive: sign, publish, tiles; a crash between publish and tiles forks. Tiles first: tiles, sign, publish; forks on rollback and twins. Lock first: sign, lock, tiles, publish; a crash between lock and tiles leaves it stuck. Sunlight: tiles, sign, lock, publish; recovers alone. Staged: stage, sign, lock, copy, publish; recovers alone on any storage." width="1000" height="600" loading="lazy" />

The script builds five protocols from the same steps. Two new ingredients appear in the later ones.

The **lock** is a tiny, strongly consistent database that stores one value per log: the last checkpoint ever signed. It supports a single operation, **compare-and-swap**: replace the value with a new one only if it still equals the value I read before. The Sunlight design document describes exactly this: a private global table, keyed by log, holding the latest checkpoint of every log, updated with a compare-and-swap before the checkpoint goes to object storage. DynamoDB is its example. The lock is the log's memory of what it has signed, kept outside both the process and the public storage.

**Staging** writes new tiles under a private name that only one exact tree can have, `staging/<size>/<root>/`, and copies them to their public paths only after the commit.

| protocol | order | idea |
|---|---|---|
| naive | sign, publish, tiles | publish first, write data after |
| tiles first | tiles, sign, publish | never publish without data; storage is the only memory |
| lock first | sign, lock, tiles, publish | remember the signature first |
| sunlight | tiles, sign, lock, publish | data first, then remember, then publish |
| staged | stage, sign, lock, copy, publish | data in a private place, remember, then make it public |

Recovery differs too. The naive log takes whatever entries it finds. Tiles first trusts the checkpoint in storage and checks the tiles against it. The three lock protocols trust the lock. They read the locked checkpoint, rebuild the tree from the tiles up to that size, check the root, and refuse to start if anything disagrees. The staged protocol first looks for staged files matching the locked size and root, and if it finds them it finishes the copy: it **rolls forward**.

## The verdict

```text
== every protocol, every failure (runs out of 20, reused key: 1 run; faults injected before the named step) ==
                                     naive              tiles first               lock first                 sunlight                   staged
  crash:sign                          safe                     safe                     safe                     safe                     safe
  crash:tiles                      FORK 20                     safe                 stuck 20                     safe                        -
  crash:stage                            -                        -                        -                        -                     safe
  crash:lock                             -                        -                     safe                     safe                     safe
  crash:copy                             -                        -                        -                        -                     safe
  crash:publish                       safe                     safe                     safe                     safe                     safe
  crash:ack                           safe                     safe                     safe                     safe                     safe
  rollback                 FORK 20 lost 20          FORK 20 lost 20                 stuck 20                 stuck 20                 stuck 20
  twin                     FORK 20 lost 20          FORK 20 lost 20                 stuck 20                 stuck 20                 stuck 20
  reused key                        FORK 1                   FORK 1                  stuck 1                  stuck 1                  stuck 1
```

How to read it. A fault "before tiles" means the process dies just before the tiles step, so everything earlier in that protocol's order has happened. **FORK** counts runs in which two published checkpoints disagree. **stuck** counts runs in which recovery refused to continue. **lost** counts runs in which a submission that had been acknowledged is missing from the log's final history: a broken promise. The referee also checks for **hidden forks**: two disagreeing checkpoints that both left the process, even if only into the private lock. None of the lock protocols produced one, in any run.

<img src="/images/root/10-grid.svg" alt="Results grid. Naive forks on a crash, rollback, twin and reused key. Tiles first forks on the last three. Lock first gets stuck after a crash. Sunlight and staged recover from every crash. All three lock protocols stop safely on rollback, twin and reused key. With conditional writes, Sunlight gets stuck after some crashes; staged never does." width="1000" height="560" loading="lazy" />

Read it row by row.

**Crashes.** The naive protocol forks every time it crashes in its window, as in the story above. Every other protocol survives a crash before any step, because none of them publishes a checkpoint before its tiles are durable. A crash before signing loses nothing durable. A crash after publishing but before acknowledging leaves submitters without an answer; they retry and the log gets a few duplicates, which a real log removes with a deduplication cache. Lock first is the exception: a crash between the lock and the tiles leaves a locked checkpoint that storage cannot support, and recovery stops. That is safe, but someone must now decide whether to roll the lock back, which means discarding a checkpoint that was signed. It was never published, but it was signed. That discussion happened in Sunlight's issue tracker, and Filippo Valsorda was not comfortable with it: rolling back the lock would mean an inconsistent tree had been signed, even if it was never published.

**Rollback.** An operator restores storage from yesterday's backup. Or a storage request that timed out succeeds late and puts back an old checkpoint. Tiles first has no memory beyond storage, so it continues from yesterday, re-sequences, forks, and loses everything acknowledged since the backup. The lock protocols read the lock, see a checkpoint storage cannot support, and stop. The Sunlight design document names both causes, hedged requests that succeed late and backup restores, as the reason the lock exists.

**Twin.** Two instances of the service run against the same storage, a classic deployment mistake. Without a lock each happily extends its own tree. With a lock, the first compare-and-swap after the twin moved the log fails: the value is no longer what that instance read. It stops. The other can continue. Sunlight lists two instances on the same storage as one of the two problems the lock guards against.

**Reused key.** An operator creates a new bucket for a new log, but reuses an old configuration and key. Without a lock the new log starts at size zero and signs a tree that disagrees with everything the old one signed. With a lock keyed by log, the lock already holds a checkpoint while storage is empty, and recovery refuses. Sunlight's code has an error for exactly this case: "checkpoint already exist, refusing to initialize log".

So the lock turns every fork in the table into a stop. That trade is right. A stuck log is an availability incident that an operator can fix. A forked log cannot be fixed by anyone.

## The witness makes it loud

<img src="/images/root/10-witness.svg" alt="A tiles-first log restored from a backup. The witness cosigns 62, 222, 312 and 595, refuses 322 and 593 as older than what it cosigned, then refuses 817, 954, 1032 and 1311 because no consistency proof from 595 can exist." width="1000" height="520" loading="lazy" />

What happens to a log that forks anyway? Run the tiles-first log through a backup restore and show its checkpoints to a witness that behaves as in Part 05:

```text
== what a witness does with a fork (Part 05): tiles first, storage restored from a backup ==
  checkpoint    62: consistent with what it cosigned before, cosigns
  checkpoint   222: consistent with what it cosigned before, cosigns
  checkpoint   312: consistent with what it cosigned before, cosigns
  checkpoint   595: consistent with what it cosigned before, cosigns
  checkpoint   322: older than the 595 it already cosigned, refuses (the backup)
  checkpoint   593: older than the 595 it already cosigned, refuses (the backup)
  checkpoint   817: no consistency proof from 595 can exist, refuses: the log has forked
  checkpoint   954: no consistency proof from 595 can exist, refuses: the log has forked
  checkpoint  1032: no consistency proof from 595 can exist, refuses: the log has forked
  checkpoint  1311: no consistency proof from 595 can exist, refuses: the log has forked
```

The witness never cosigns again. Every client that requires its cosignature stops accepting the log's checkpoints, and for MTC every new certificate from that log, standalone or landmark-relative, fails verification. The design is doing its job: a fork cannot stay silent. But for the operator the log is lost, which is why the commit protocol matters so much.

## Sunlight's order, and its one sharp edge

The Sunlight CT log, designed by Filippo Valsorda and run by Let's Encrypt, sequences once a second in this order: drain the pool, produce the new tiles, upload them to object storage in parallel, sign the new checkpoint and store it in the lock with a compare-and-swap, upload it to object storage, then answer the submitters. Its design document walks through the two crash points:

- A crash after the tile upload but before the lock leaves tiles that extend past every checkpoint, possibly with data that will never be part of the log. That is harmless, because no checkpoint commits to those hashes.
- A crash after the lock but before the checkpoint upload is resolved on recovery: the node trusts the lock and ignores the older checkpoint in storage.

Recovery downloads and verifies the checkpoint from the lock, compares it with the one in storage, reads the right edge of the tree from the tiles, and checks that it matches. That is our `sunlight` column, and it recovers from every crash in the table.

The sharp edge is the first bullet. After that crash, the next round writes **different** content to some of the same tile paths, because the retried batch arrives in a different order. On storage with last-writer-wins semantics, like plain S3, the new write simply replaces the bogus one. But some operators make tile writes conditional, refusing to overwrite a file that exists, because full tiles are supposed to be immutable. The script models that:

```text
== the same, with storage that refuses to overwrite a full tile (conditional writes) ==
                                     naive              tiles first               lock first                 sunlight                   staged
  crash:lock                             -                        -                     safe                 stuck 10                     safe
  crash:copy                             -                        -                        -                        -                     safe
  crash:publish                       safe                 stuck 10                     safe                     safe                     safe
  twin            FORK 20 stuck 10 lost 20 FORK 10 stuck 10 lost 10                 stuck 20                 stuck 20                 stuck 20
```

Sunlight gets stuck in 10 of 20 runs: exactly those in which the lost batch had completed a full tile that the retried batch now wants to write differently. This is not hypothetical. It is Sunlight issue #12, reported in March 2024 by a contributor testing conditional writes: a sequencing failure after uploading a tile but before updating the lock, a restart, an attempt to write the same tile, and a failure because it already exists, so the log gets stuck. The commit that followed notes that conditional writes can lock up the log in this way. The same thread discusses a subtler hazard, a timed-out upload that lands seconds later and overwrites newer data. Sunlight's position is that last-writer-wins and never sending two requests for the same step at once make that impossible or extremely rare, and manual recovery is acceptable if it happens. My toy does not model delayed writes; I mention it because it is the kind of failure that a protocol with a lock still has to think about.

## Staging: commit, then make public

<img src="/images/root/10-staged.svg" alt="The staged protocol writes tiles under staging/size/root/, signs, compare-and-swaps the lock, then copies the tiles to public paths and publishes. A crash before the lock leaves staged files of an uncommitted tree, ignored. A crash after the lock is recovered by rolling the copy forward. Public paths only ever hold tiles of committed trees." width="1000" height="560" loading="lazy" />

The staged protocol removes the sharp edge by never writing an uncommitted tile to a public path:

1. **stage**: write the new tiles under `staging/<size>/<root>/`. Two different trees have different roots, so they can never write the same staged path;
2. **sign** the checkpoint;
3. **lock**: compare-and-swap it into the lock. This is the commit point;
4. **copy** the staged tiles to their public paths;
5. **publish** the checkpoint to storage, then acknowledge.

If the process crashes before the lock, the staged files belong to a tree that nobody committed to. They are ignored, and the next round stages under a different root. If it crashes after the lock, recovery finds `staging/<size>/<root>/` for exactly the locked checkpoint and finishes the copy. Public paths only ever receive tiles of committed trees, so a public full tile is written with the same bytes every time, and write-once storage never refuses. The table shows it: staged recovers by itself from every crash, with or without conditional writes, and still stops safely on rollback, twin and reused key.

The cost is one extra copy of each round's tiles, which on object storage is a server-side copy. I did not invent this shape. Let's Encrypt's tile code for MTC logs has a `Stage` step that writes dirty tiles under a prefix derived from the tree size and root hash, and a separate `Publish` step. Its documentation does not describe a lock, so I do not claim that the rest of its protocol matches mine.

## What this means for an MTC CA

For an MTC CA the stakes are higher than for a CT log, for three reasons:

- **Acknowledging is issuing.** In CT, an acknowledgment is an SCT, a promise to include. In MTC, the certificate is only built after the entry is in a cosigned subtree (Part 07). An entry that is acknowledged and then lost means a certificate in the wild that its own log does not contain. In the table, "lost" happens only to protocols without a lock.
- **Cosigners hold the CA to every signature.** The CA's own cosigner and its witnesses sign subtrees and checkpoints. A forgotten signature is a fork, and the draft's remedy is to abandon the log.
- **Landmarks freeze history into browsers.** Landmark subtrees are distributed to relying parties (Part 08). A CA that forks after a landmark has disagreed with a value in millions of browsers.

So an MTC issuance log needs a durable record of its last signed checkpoint, updated with compare-and-swap before anything is published or any certificate is built, and a recovery that trusts that record over storage. The cosigning order follows the same rule: the CA's cosigner signs subtrees only of a tree that is already committed in the lock.

## The limits of this experiment

The fault model is simple: a crash before a step, a whole-storage rollback, a twin that runs one round, a new bucket. It does not model partial uploads of a single file, delayed writes, eventual consistency, a lock that is itself rolled back, or Byzantine storage. The referee knows every signed checkpoint, which no real party does. The tiles are rebuilt from entry bundles on recovery, where a real log reads only the right edge of the tree. And 20 runs per cell prove nothing. They demonstrate mechanisms that the reasoning above explains. A proof that a protocol can never fork under a stated fault model is a job for a model checker or a proof assistant, not a simulation.

## Try it

From the `experiments\root-of-trust` folder:

```text
python 10_never_fork.py
python -m unittest test_10_never_fork
```

Exercises:

1. Change the naive protocol so the retried batch arrives in its original order. Does it still fork? Then add one new submission that arrives before the retries, and run it again.
2. Add a "crash during tiles" fault that uploads only half of the round's files. Which protocols are affected?
3. Model a lock that is itself restored from a backup. Which protocols still never fork, and what would you add to detect it?
4. Give the staged protocol a cleanup step that deletes staging directories older than the locked checkpoint. Where in the order is it safe?
5. Make the twin run several rounds. In the lock protocols, does the twin's history ever end up inconsistent with what the original published?
6. Write the invariant "every published checkpoint is a prefix of the locked one" as a check inside `Sequencer.recover`, and find the protocols in which it can fail.

## Reader checkpoint

<details>
<summary><strong>1.</strong> The naive log never signed anything false. Why is the result a fork?</summary>

It forgot that it had signed checkpoint 587. After the crash it rebuilt from storage, which ended at 315, and the retried submissions came back in a different order, so its next checkpoint put different entries in the same positions. Both signatures are real and they disagree.

</details>

<details>
<summary><strong>2.</strong> Why is storage alone not enough as the log's memory?</summary>

Storage can be rolled back (a backup restore, a late write) or shared by mistake (two instances, a reused key), and the log cannot tell from storage alone that it is behind what it already signed. A separate record of the last signed checkpoint, updated with compare-and-swap, can tell.

</details>

<details>
<summary><strong>3.</strong> Why compare-and-swap, not a plain write?</summary>

A plain write lets two writers overwrite each other without noticing. Compare-and-swap only succeeds if the value is still the one the writer last saw, so a second instance, or an instance that is behind, fails instead of extending a different history.

</details>

<details>
<summary><strong>4.</strong> In Sunlight's order, why are tiles beyond the locked checkpoint harmless, and when do they cause trouble?</summary>

No signed checkpoint commits to them, so no client will rely on them. They cause trouble on storage that refuses to overwrite: the next round needs to write different bytes at the same full-tile path, and the log gets stuck (Sunlight issue #12).

</details>

<details>
<summary><strong>5.</strong> What makes the staged protocol safe on write-once storage?</summary>

Uncommitted tiles go only to private paths named by size and root, which no other tree can share. Public paths are written only after the lock commits, always with the committed tree's bytes, so a rewrite is always identical.

</details>

<details>
<summary><strong>6.</strong> Why is "stuck" an acceptable outcome and "fork" not?</summary>

A stuck log is an availability incident: an operator can restore storage, retire a twin, or fix a configuration, and the log continues with its history intact. A fork is permanent: witnesses refuse the log forever, and for MTC the CA must move to a new log.

</details>

## What comes next

Ten parts have built the whole stack in Python, from the bytes of a certificate to a crash-safe tiled log of Merkle Tree Certificates. The [last part](/root/11-from-toy-to-qcert/) maps each experiment to the module it becomes in the QCERT implementation, and carries the test vectors over, so the code starts where the series ends.

## References

- F. Valsorda, [*The Sunlight CT log*](https://filippo.io/a-different-CT-log), design document, 2023 to 2024: sequencing order, the compare-and-swap lock, crash points, recovery.
- [Sunlight issue #11](https://github.com/FiloSottile/sunlight/issues/11) and [pull request #12](https://github.com/FiloSottile/sunlight/pull/12): crash scenarios, conditional writes, and the stuck log.
- [Sunlight internal/ctlog](https://pkg.go.dev/filippo.io/sunlight/internal/ctlog): the `LockBackend` interface and the "refusing to initialize log" error.
- Let's Encrypt, [*Introducing Sunlight*](https://letsencrypt.org/2024/03/14/introducing-sunlight), March 2024.
- Let's Encrypt, [*Boulder trees/tiles*](https://pkg.go.dev/github.com/letsencrypt/boulder/trees/tiles): `Stage` and `Publish` for MTC tile storage.
- D. Benjamin et al., [*Merkle Tree Certificates*](https://www.ietf.org/archive/id/draft-ietf-plants-merkle-tree-certs-07.html), draft-ietf-plants-merkle-tree-certs-07, §12.2: split views and moving to a new log.
