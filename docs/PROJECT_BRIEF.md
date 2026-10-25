# SameBytes: project brief

> **What** we're building and **why**. The **how** is in `BUILD_PLAN.md` (plan), `ARCHITECTURE.md`, `AGENT_DESIGN.md` and `VERIFICATION_HARNESS.md`. Every choice is logged in `DECISIONS.md`.
> Last updated: 2026-10-25 (after the build-plan research pass).

## One sentence
An AI agent that finds out why a software package builds differently every time, fixes the cause in the source, and proves the fix by building it twice in independent, deliberately different environments and showing byte-identical fingerprints (SHA-256).

## The problem in plain words
- **Source code is the recipe; the binary is the cake.** People download cakes. To check nobody tampered with one, you bake the recipe yourself and compare fingerprints.
- **That check only works if the same recipe always gives the same cake** (a *reproducible build*).
- **Most builds aren't reproducible.** Timestamps, paths, usernames, hostnames, file order, locale, timezone, CPU count and random seeds leak into the output.
- **It's a security problem.** SolarWinds (2020) was a compromised build server. In the xz backdoor (2024), the malicious code was in the release files but not in the public source. Rebuild-and-compare catches both, but only for reproducible builds.

## Who has it
- **Debian.**
  - Since May 2026, unreproducible packages and regressions are blocked from migrating to testing.
  - On Oct 25, unstable/amd64 had **1,140 unreproducible** (FTBR) packages, 429 of them with no notes at all.
  - About 9 people actively write notes.
- **Maintainers**, who get blocked without the expertise to diagnose the cause.
- **Every other ecosystem:** on PyPI only 15.4–19.1% of rebuilds are byte-identical. Also Arch, Fedora, NixOS, npm, Maven, containers and firmware.
- **Companies under the EU Cyber Resilience Act:** reporting since Sep 2026, full application Dec 2027.

## What exists vs. what we add
See `LANDSCAPE.md`. In short:
- **Detecting** is solved (Debian CI, rebuilderd, reprotest).
- **Explaining where** is solved (diffoscope).
- **Normalizing** differences away exists (strip-nondeterminism, Google OSS Rebuild "stabilizers").
- **Diagnosing why, fixing the cause, and proving it bit-for-bit** is manual expert work. **That's SameBytes.**

## Flagship result we're building toward (D-021, `FLAGSHIP_CASE.md`)
- One bug in a shared tool (argparse-manpage: an import that always fails, so dates come out in local time) makes **13 Debian packages** unreproducible.
- Debian's volunteers had **labelled** the cluster (`timezone_variant_in_argparse_manpage` on all 13, bug #1126092) but not fixed it: their patch is stuck (it doesn't build on Python 3.15), and upstream is still broken.
- SameBytes traces the bytes to the exact line, fixes the tool once, proves every dependent reproducible, and catches a 14th package (`hatchling`) that regressed on Oct 23 and has no label.
- **Because the label is public, the headline run is blind** (the catalogue entry is removed) and both runs are published (D-031).

## How it works (pipeline)
1. **Intake and evidence.** The package's CI status and build time; the published diffoscope JSON and logs from tests.reproducible-builds.org.
2. **Baseline twin build.** Reproduce the difference ourselves under Debian CI's exact variations, offline.
3. **Digest and rules.** Parse the diff, drop derived differences, and run deterministic detectors (timezone-shifted dates, clock, user, home, hostname, locale, PATH, flags, ordering, randomness, archive metadata).
4. **Investigate (Nemotron 3 Ultra, tools).** Search logs and source, attribute files to installed packages, and **run experiments** (`probe`: the same command under both environments) until the cause is confirmed. The output is a schema-validated diagnosis.
5. **Scout (Tavily, product mode).** Existing Debian bugs, upstream fixes, and the commits that introduced the problem. This changes the plan: reuse the human patch, backport upstream, or draft an upstream PR.
6. **Patch (Nemotron Super, tools).** Exact search-and-replace edits to the package or the toolchain package, 1 candidate per round on Docker, 2 on Sandboxes or Actions (D-037). A deterministic policy guard forbids test-skipping, file removal and hard-coded dates.
7. **Verify.** Twin build per candidate: identical SHA-256 for every `.deb`, unchanged file list, tests pass. A remaining diff feeds the next round (max 3).
8. **Critic (Nemotron 3 Ultra).** Root cause or workaround? It writes the maintainer explanation.
9. **Receipt and report.** An in-toto receipt, report, bug and PR drafts, and a site card. A human reviews; nothing is auto-filed.

**Campaign mode:** if the cause is in a toolchain package, fix it once, inject the fix into each dependent's environment (as a file overlay, or a rebuilt `.deb` when the tool is compiled) and twin-build them all, on the laptop or on GitHub runners with build A and build B on separate machines. The verified fix becomes a reusable rule.
**Map mode (Could, D-037):** a cheap Nemotron signature pass over all FTBR packages (Batch API) reveals other shared-cause clusters.

## Model roles (D-023, D-028)

| Role | Model | Why |
|---|---|---|
| Investigator | Nemotron 3 Ultra | Hardest reasoning: localize across packages, plan experiments |
| Patcher | Nemotron 3 Super or 3.5 Super VL (bake-off) | Strong tool-using coder at a third of Ultra's price |
| Critic | Nemotron 3 Ultra | Independent judgment and explanation |
| Fast roles (scout analysis, condense, signatures) | Nemotron 3.5 Lightning or 3 Nano (bake-off) | Cheap, schema-following |

An ablation justifies the split: Ultra with no tools is planned; Super or the fast model as investigator and no rule hints run only if time allows (D-037).

## Tech stack
- **Orchestrator:** Python 3.12, Typer, Rich, pydantic.
- **LLM client:** `openai` SDK pointed at Token Factory.
- **Build backends:** Docker (primary) and Sandboxes (accelerator, when granted).
- **Build tools:** dpkg-buildpackage, faketime, diffoscope, reprotest (strict and bisect only).
- **Search:** Tavily.
- **Storage:** JSON files in `runs/`, curated into `published/`.
- **Report:** a static site on GitHub Pages.
- **Repo:** public, MIT.

## Evaluation (`BENCHMARK_PROTOCOL.md` v2)
- **Track A: diagnosis.** Sealed set of packages tagged after the models' training cutoffs, plus an old-tag control, a memorization probe and the no-tools ablation.
- **Track B: verified fixes.** 4 fast packages (D-037), scored objectively by the twin build.
- **Track C: campaign.** Flagship cluster members proven, out of those attempted.

## Success criteria
- **Added by the review (D-031 to D-036), prioritised by D-037:** the blind flagship run (Should, first), keyless `samebytes replay` of a recorded run (Should), a GitHub Actions verification workflow (Should, after the campaign), the README "For judges" table (Must) and a `/judges` page (Could).
- **Must:**
  - flagship campaign with ≥ 9 verified receipts;
  - an end-to-end `samebytes fix` on the flagship;
  - report site, README with limitations, video ≤ 3:00, feedback section.
- **Should:** Track A and B tables; Tavily scout; batch map; upstream contribution (with your approval).
- **Could:** Sandboxes backend; strict profile; signed receipts; mini GitHub Action; hatchling verified.

## Known limitations (keep current; full list in `RISKS_AND_BLOCKERS.md`)
- Mirrors Debian CI's variations **except the kernel**, which CI varies on amd64 and a container can't. Build path and file order are not varied by CI today and only by our optional strict profile.
- Time variation via libfaketime; a few packages need it off, and their grade says so.
- Track A ground truth is volunteer tags, which may be stale or coarse.
- Not yet validated against reproduce.debian.net's real-archive rebuilds.
- Long builds are skipped; humans review everything before it goes upstream.

## Team split
- **Person A ("kitchen"):** harness, backends, receipts, campaign, site deploy.
- **Person B ("brain"):** LLM client, digest, rules, agents, scout, ledger, benchmark, site content.

Interfaces are frozen on Day 0 (`BUILD_PLAN.md` §3).

## Timeline
See `BUILD_PLAN.md` §4.
- **Gates:** G0 Sun 23:30, G1 Mon 23:30, G2 Tue 23:30.
- **Feature freeze:** Wed 23:59.
- **Draft submit:** Thu.
- **Final submit:** Fri 18:00 IST (deadline 22:30 IST).

## 30-second pitch
"Build the same code twice and you usually get different files, because things like the time and the timezone sneak in. That breaks the main way to check software wasn't tampered with. Debian now blocks packages with this problem, and over eleven hundred are failing. SameBytes finds the cause, fixes it, and proves it with byte-identical builds. On Debian it traced 13 broken packages to one silent bug in a shared tool, fixed it once and proved all 13. It runs on NVIDIA Nemotron through Nebius Token Factory: Ultra investigates, Super writes the fix."
