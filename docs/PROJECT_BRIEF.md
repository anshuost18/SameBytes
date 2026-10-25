# SameBytes: project brief

> Working name, not final (see open question Q-005 in `DECISIONS.md`).
> Last updated: 2026-10-24. This file describes **what we're building and why**.
>
> Other docs:
> - `DECISIONS.md`: every choice, open question and blocker
> - `EXECUTION_GUARDRAILS.md`: how each feature earns judging points, plus session rituals
> - `BENCHMARK_PROTOCOL.md`: how the answers stay hidden during testing
> - `HACKATHON_CHECKLIST.md`: rules and submission checklist
> - `FEEDBACK_LOG.md`: running notes for the required feedback section
> - `TECH_REFERENCE.md`: endpoints, model IDs, SDKs, data-source URLs, tools, costs
> - `EXPLAINER.md`: plain-language explanation and glossary
> - `SOURCES.md`: citations for the write-up
> - `ORIGINAL_IDEA.md`: the first pitch, for reference
> - `../CLAUDE.md`: handoff and working agreements for coding sessions

## One sentence

An AI agent that finds out why a software package builds differently every time, fixes the cause, and verifies the fix by building it on two fresh, independent machines under varied conditions and showing byte-identical fingerprints (SHA-256 hashes).

## The problem in plain words

- **Source code is the recipe and the binary is the cake.** People download cakes, not recipes. To check that a cake wasn't tampered with, you bake the recipe yourself and compare fingerprints.
- **That check only works if the same recipe always gives the same cake.** This property is called a *reproducible build*.
- **Most builds aren't reproducible.** Build details leak into the output:
  - timestamps (for example, gzip headers);
  - the build folder path;
  - the username and hostname;
  - file listing order;
  - locale and timezone;
  - CPU count;
  - random hash seeds.
- **This is a security problem.** SolarWinds (2020) was a compromised build server. In the xz backdoor (2024), the malicious code was in the release files but not in the public source. Independent rebuild-and-compare catches both kinds of attack, but only for reproducible builds.

## Who has this problem

- **Debian.** Since 9 May 2026, Debian's migration software blocks new unreproducible packages and regressions from entering *testing*. Debian 14 "forky" is the first release under this mandate.
  - Live numbers on 2026-10-24 (tests.reproducible-builds.org, unstable/amd64): 1,148 unreproducible packages; 619 unreproducible with no identified cause.
  - Only 9 people committed to `reproducible-notes` in the last three months.
- **Package maintainers**, who get blocked and lack the expertise to diagnose the cause.
- **Other ecosystems.** Arch, Fedora, openSUSE, NixOS and F-Droid all have the problem. On PyPI, only 15.4–19.1% of rebuilds are byte-identical (2026 study, "No Snake Oil").
- **Companies shipping binaries and containers.** Under the EU Cyber Resilience Act, reporting duties started in September 2026 and full enforcement begins in December 2027.

## What exists vs. what we add

| Activity | Status today | Us |
|---|---|---|
| **Detecting** (is it reproducible?) | Solved: reprotest, diffoscope, Debian CI | We consume their published results |
| **Fixing** (why not, and what patch fixes it?) | Manual expert work; RepFix (ICSE 2022, non-LLM) fixed 64/116 | **Our core product** |
| **Verifying** (is the fix real?) | Manual | Automatic: two fresh sandbox builds, hash comparison, tests pass |

We **make** builds reproducible. Checking is our proof step, not the product.

## "Isn't this a one-time fix for ~620 packages?"

No. The answer for judges has three parts:

1. **It recurs.** New upstream versions and toolchain updates keep breaking reproducibility. That's why Debian blocks *regressions* specifically. 4,347 reproducibility bugs have been fixed over the years, yet about 1,100 unreproducible packages remain at any time. The monthly reports still list dozens of new fixes.
2. **Debian is the proving ground, not the market.** It gives us a public answer key. The same problem exists in other distributions, PyPI, npm, Maven, Rust, Go, containers, firmware, and most corporate build pipelines.
3. **Long-term product shape: a reproducibility guard**, Dependabot-style:
   - it runs on every change or release, builds twice, and compares;
   - on a regression, it diagnoses the cause and opens a pull request with a proven fix;
   - it fixes shared toolchain causes once, for many packages;
   - its verification receipts serve as audit evidence.

**Pitch order:** Debian backlog = proof it works. Reproducibility guard for any team = the product.

## How it works (pipeline)

1. **Gather evidence.** Download the published diffoscope result and both build logs from tests.reproducible-builds.org, plus the known-cause catalogue from `reproducible-notes`. No builds are needed at this stage.
2. **Rules pre-pass.** Deterministic checks catch easy cases cheaply: gzip mtime, build path strings, `date` calls in `debian/rules`, `.a` archive member order, and so on.
3. **Condense (Nemotron 3 Nano).** Shrink megabytes of diff to the few differences that matter.
4. **Diagnose (Nemotron 3 Ultra + Tavily).**
   - Ultra names the root cause (mapped to one of Debian's ~430 issue types) and the responsible file and line.
   - Tavily checks whether upstream already fixed it and finds the right upstream tracker.
5. **Patch (Nemotron 3 Super), as an agent loop (D-024).** Super works with tools (read file, search source, apply patch, run rebuild) under a hard per-package budget and proposes up to three candidate patches.
6. **Verify (Token Factory Sandboxes).**
   - For each candidate, on its own branch, build twice in fresh VMs from the same image while varying time, path, user, locale, timezone, umask and CPU count.
   - Success means identical SHA-256 hashes, build-time tests passing, and the smallest diff winning.
   - Staged (D-025): screen candidates with the failing variation only, stop at the first pass, then run the full variation set on the winner. The harness decides pass or fail, never the model.
   - If no candidate passes, the remaining diff goes back to step 4. Maximum 3 rounds.
7. **Receipt + human review.** Output a patch, a plain-English explanation, a ready-to-file bug report, and a JSON verification receipt (image UUID, operation IDs, variations, hashes, test result). A human reviews everything. Nothing is auto-filed.

**Campaign mode:** run the pipeline over many packages. Nano produces a signature per package, and similar signatures are clustered to find shared toolchain causes, so one fix covers N packages.

## Model roles

| Model | Job | Why this model |
|---|---|---|
| Nemotron 3 Nano 30B-A3B | Condense diffs, build cluster signatures | Cheapest (~$0.06/M input tokens), fast, good at summarizing |
| Nemotron 3 Ultra 550B-A55B | Root-cause diagnosis | Deepest reasoning (~$1/$3 per M tokens) |
| Nemotron 3 Super 120B-A12B | Write patches | Strong coder, ~1M token context |

We'll measure the split with an ablation (for example, Nano-only vs. Ultra for diagnosis: accuracy and cost). Confirm the exact model IDs from Token Factory's live model list.

## Tech stack

| Layer | Choice |
|---|---|
| Orchestrator | Python |
| LLM calls | `openai` Python SDK pointed at the Token Factory base URL |
| Build machines | Nebius Token Factory Sandboxes (Python SDK); fallback: local Docker (`--privileged` for disorderfs) |
| Build tools | Debian image with `dpkg-buildpackage`, `devscripts`, `reprotest`, `diffoscope` |
| Search | Tavily Python SDK |
| Data | tests.reproducible-builds.org (diffs, logs); `reproducible-notes` (`issues.yml`, `packages.yml`) |
| Storage | SQLite or JSON |
| Report UI | Static site on GitHub Pages: one card per package (hashes before and after, cause, patch, model per step, cost) |
| Repo | Public GitHub, MIT or Apache-2.0 license visible in About |
| Secrets | `.env` (gitignored); never commit keys |

## Evaluation (the benchmark)

> Full rules: `BENCHMARK_PROTOCOL.md`. The answers are sealed and the agent can't reach them. It works from pre-fix source versions, has no Debian notes, no network, and no Tavily for the headline numbers. There's a dev/test split with prompts frozen before the run, a memorization probe, and a single run with all failures published.

- **Diagnosis set (D-023).** Packages still unreproducible whose cause note was added after the models' training cutoffs. Their current source is pre-fix, so score cause and file against the note with no builds. Verified fix rate is measured on a subsample. Known-fix packages are optional.
- **Metrics:**
  - root-cause top-1 and top-3 accuracy;
  - file localization accuracy;
  - verified fix rate;
  - dollars per fix and minutes per fix.
- **Baseline:** RepFix's 64/116 (55%). State honestly that the datasets differ.
- **Unknown-cause set.** Run on a sample of the ~619 unexplained packages. Every success is new work.

## Success criteria for the hackathon

- **Must:**
  - Gate 1 passed by Mon 26: one package fixed end-to-end with a receipt (D-021);
  - at least 5 packages fixed end-to-end with byte-identical verification (D-025; report attempted vs verified);
  - a benchmark table;
  - the report site;
  - a video under 3 minutes;
  - a README and limitations section.
- **Should:**
  - the model ablation;
  - Tavily upstream check;
  - clustering on the unexplained set;
  - 2–3 human-reviewed fixes submitted with AI-assistance disclosure.
- **Stretch:**
  - 10 packages fixed end-to-end;
  - a minimal GitHub Action that runs the two-build check on a sample project (makes the "guard" story concrete);
  - batch-API campaign.

## Known limitations (publish these)

- We won't fix every package; the success rate on unexplained cases will be modest.
- Long-building packages are skipped.
- Reproducibility makes tampering detectable through independent rebuilds. It does not show that software is secure or free of malicious code. Our receipts show identical output under the tested variations only (D-022). Locally the user_group variation is excluded.
- A fix can be reproducible but not ideal, which is why a human reviews it.
- The file-ordering variation may not run in Sandboxes (FUSE).
- We focus on variation testing (tests.reproducible-builds.org), not every real-world rebuild failure (reproduce.debian.net).
- We do no auto-filing. This follows Debian's August 2026 general resolution: AI use is allowed, the human submitter is accountable, and disclosure is encouraged. The community is split roughly 64/36.

## Team split (proposed)

- **Person A, "the kitchen":**
  - sandbox setup and Debian build image;
  - two-build harness and variations;
  - hash comparison, tests, verification receipt.
- **Person B, "the brain":**
  - evidence download and rules pre-pass;
  - Nano, Ultra and Super prompts and the retry loop;
  - Tavily check;
  - benchmark scoring;
  - report site.
- **Both:** video, write-up, feedback section.

## Timeline (deadline Fri 30 Oct, 10:00 PDT = 22:30 IST)

| Day | Goal |
|---|---|
| Sat 24 | Accounts and credits; request Sandboxes access; package list; download evidence; test one sandbox build and `/dev/fuse` |
| Sun 25 | Verification harness working (build twice, compare, tests) |
| Mon 26 | **Gate 1 first (one full fix with receipt)**, then the agent loop: rules, Nano, Ultra (read tools), Super (edit tools), staged verification |
| Tue 27 | Gate 3 (about 5 fixes), then benchmark + ablation; Tavily; clustering and campaign only if Gate 3 is done; send 1-2 reviewed patches to users (D-026) |
| Wed 28 | **Feature freeze.** Report site, README, limitations, human review of top fixes |
| Thu 29 | Video, Devpost write-up, feedback; submit a draft |
| Fri 30 | Buffer only; final submit well before 22:30 IST |

**Cut first if behind:** CI regression check, batch campaign, file-order variation. **Never cut:** verified fixes, the benchmark table, the video.

## 30-second pitch

"Build the same code twice and you usually get different files, because things like the time and folder name sneak in. That breaks the main way to check software wasn't tampered with: rebuild and compare fingerprints. Debian now blocks packages with this problem, and only a handful of volunteers can fix them. SameBytes reads the evidence, finds the cause, writes the fix, and verifies it by building on two fresh Nebius sandboxes and showing identical fingerprints. Three NVIDIA Nemotron models share the work: Nano summarizes, Ultra diagnoses, Super writes the code."
