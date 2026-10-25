# Benchmark protocol: keeping the answers hidden

> **Why this file exists.** A benchmark is only worth something if the agent can't see the answer. Judges read rigor as a strength, so we design the test like an exam: sealed answer key, no peeking, one honest run, and every failure published.
> Related decision: D-017 in `DECISIONS.md`. Last updated: 2026-10-25.
> **Update 2026-10-25 (D-023):** the diagnosis set is now packages still unreproducible with a recent cause note, not pre-fix versions from snapshot.debian.org. Leak path L3 and the dataset construction below are superseded where they conflict.

## 1. What we're measuring

For each benchmark package (one with a known human fix), we measure:

| Metric | Question it answers | How it's scored |
|---|---|---|
| Cause top-1 / top-3 | Did the agent name the right root cause? | The predicted issue type matches any ground-truth tag |
| Localization | Did it find the right file? | The predicted file is among the files touched by the human fix |
| Verified fix rate | Did its patch actually work? | Byte-identical SHA-256 hashes across two varied sandbox builds, and build-time tests pass. This is objective and needs no answer key |
| Same fix as human? | Is it the fix an expert would make? | Same file, same mechanism. Judged manually for small n and recorded per package |
| Cost and time | Is it practical? | $ per package and minutes per package, from the call and operation logs |

## 2. Every way the answer could leak, and how we block it

| # | Leak path | Block |
|---|---|---|
| L1 | **Debian's notes** (`packages.yml` maps each package to its cause) | The agent receives only `issues.yml` (the catalogue of cause types), with all package names stripped from the descriptions. `packages.yml` is never loaded. |
| L2 | **tests.reproducible-builds.org package pages** show the notes next to the diff | The scraper keeps only the diffoscope output and build logs and drops the notes and issue sections. For benchmark packages we generate our own evidence anyway (see L3). |
| L3 | **The current source already contains the fix.** The package was fixed in May–Oct, so today's version is reproducible. | We use the **pre-fix version** from snapshot.debian.org and build it twice ourselves in Sandboxes to produce the evidence. The agent never sees any later version, changelog or diff. |
| L4 | **Web search** finds the bug report or fix commit | Headline numbers come from a run with **Tavily switched off**. A second ablation run has Tavily on, with `bugs.debian.org`, `salsa.debian.org`, `tracker.debian.org`, `reproducible-builds.org`, `snapshot.debian.org` and the upstream repo excluded. Any search result containing the bug number, fix commit or patch text is auto-flagged, and that package is reported separately. |
| L5 | **Network access from inside the sandbox** (`apt-get source` of a newer version, git fetch) | Benchmark builds and agent tool runs use `networking.enabled=false`. All inputs are uploaded beforehand. |
| L6 | **The model memorized the fix during training** | Prefer fixes newer than the models' training cutoff (Q-009). We also run a **memorization probe**: ask the model with no evidence, "what is the reproducibility problem in package X version Y?" A correct answer marks the item as possibly memorized. We report accuracy with and without those items, plus an "old fixes vs new fixes" comparison to show the size of the effect. |
| L7 | **We tune prompts or rules on the test set** (accidental human leakage) | Dev/test split (section 3). Prompts, rules and few-shot examples come only from the dev set and the public catalogue. Prompts are **frozen** (git commit hash recorded) before the test run. |
| L8 | **We see the answers while building** | The person who builds the answer key does not write prompts or rules for those items. The answer key lives in `bench/answer_key/` and is read **only** by the scorer, never by agent code. Its SHA-256 is committed **before** the test run, which proves it wasn't edited afterwards. |
| L9 | **The bug number or fix text sits in some file we pass in** | `leakguard` scans every input artifact (logs, diffs, source tree, prompts) for the bug number, fix commit hash, patch hunks and ground-truth tag names in package context. A hit aborts that item with an error. |
| L10 | **Cherry-picking runs** | Run the test set **once** with frozen settings. If we must re-run (for example, after an infrastructure crash), we report every run, not the best. |

## 3. Dataset construction

> **Replaced by D-023 (2026-10-25).** Diagnosis set: packages still unreproducible in unstable/amd64 whose cause note was added after the models' training cutoffs (date from the reproducible-notes git history, read only by the key builder). Evidence is the current published diffoscope output plus our own build logs. Score cause top-1/top-3 (and file where the note names one) with no builds. Confirm each package is still unreproducible in our harness. Measure verified fix rate on a subsample of the same set. Known-fix packages are optional, and only they can score same fix as human. The original plan below is kept for reference.

1. **Collect candidates.** Gather packages fixed for reproducibility between **May and October 2026**:
   - sources: monthly reports, bugs.debian.org bugs tagged `reproducible-builds` with patches, `reproducible-notes` history;
   - for each: pre-fix version, fixed version, bug number, fix commit or patch, ground-truth issue tags.
2. **Filter.** Keep packages that build in under about 10 minutes and whose pre-fix version is actually unreproducible when we build it twice in Sandboxes. Discard any we can't reproduce, and log why.
3. **Split, stratified by issue type:**
   - **dev set** (about 1/3): used freely to build prompts and rules;
   - **test set** (about 2/3): sealed;
   - **old-fix control set** (about 15 packages fixed before 2025): only for the memorization comparison (L6).
4. **Seal.** The answer key is written to `bench/answer_key/test.jsonl`. Its hash goes into `bench/SEAL.txt`, which is committed before the run.

Target sizes are a dev set of about 15–20 and a test set of about 30–40. Small n is fine if we're honest: report raw counts (e.g. "23/36"), not just percentages.

## 4. Run procedure (test set)

1. Freeze prompts, rules and model configuration. Record the git commit in the run manifest.
2. Set `MODE=benchmark`. This turns off Tavily and disables sandbox networking.
3. `leakguard` pre-scans all inputs; aborted items are logged.
4. The agent runs on each item and writes predictions plus patches to `bench/runs/<run_id>/`.
5. Verification builds run in Sandboxes. Hashes and tests are recorded in receipts.
6. **Only now** the scorer reads the answer key and produces `bench/runs/<run_id>/scores.json` and a report table.
7. Run the ablations: Tavily-on (filtered), Nano-only diagnosis, Super-only diagnosis.
8. Run the memorization probe and produce the old-vs-new comparison.
9. Publish everything: per-package results, **all failures with reasons**, costs, and the manifest.

## 5. What the code must enforce (not just us remembering)

- [ ] `MODE=benchmark` flag: Tavily client refuses calls; sandbox spawn forces `networking.enabled=false`
- [ ] The agent's file loader can't read `bench/answer_key/` (path denylist, plus a test that proves it)
- [ ] `leakguard` scanner with a unit test that plants a fake bug number and checks the item aborts
- [ ] Run manifest: git commit, prompt hashes, model IDs, answer-key hash, date, mode
- [ ] Scorer is a separate script run after predictions are written
- [ ] Every model call logged (model, tokens, cost, latency) and every sandbox operation logged (ID, image UUID, duration)

## 6. How we report it (README, video, Devpost)

- One honest table: dev and test results kept separate, raw counts, ablations, and the memorization-flagged split.
- A sentence on method: "Answers were sealed before the run; the agent had no network access and no access to Debian's notes or newer versions; Tavily was disabled for headline numbers."
- RepFix (ICSE 2022: 64/116) as context, noting that the datasets differ.
- Failure analysis: the 3–5 most common reasons the agent failed.
