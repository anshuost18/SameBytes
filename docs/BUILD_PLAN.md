# SameBytes build plan (Oct 25 → Oct 30, 2026)

> **This is the master plan.** It tells you what to build, in what order, who builds it, how you know it's done, and what to cut if you fall behind. Details live in the linked docs; this file links to them by section.
>
> Deadline: **Fri 30 Oct 2026, 10:00 PDT = 22:30 IST.** Internal submit target: **Fri 30 Oct, 18:00 IST.**
> Written 2026-10-25 15:30 IST, after a full research pass. All numbers marked *verified* were checked live on 2026-10-25.

---

## 0. What changed versus the plan from Oct 24 (read this first)

The research produced seven upgrades (items 1–7), and the Oct 25 review pass added item 8. Each has a decision entry in `DECISIONS.md`.

1. **We have a real, verified flagship case** (`FLAGSHIP_CASE.md`, D-021).
   - Thirteen Debian packages are unreproducible for one reason: a bug in a shared tool, `argparse-manpage`.
     - Its `import datetime.timezone` line *always* fails, because `datetime` is a module, not a package.
     - The tool then silently formats `SOURCE_DATE_EPOCH` in local time.
     - Debian's two builds use timezones 26 hours apart, so man pages get different dates.
   - Debian's fix (4.7-1.1, Jan 2026) never reached users: that version fails to build on Python 3.15 for an unrelated reason. Upstream's newest release, v4.8 from Oct 14, still has the bug.
   - A 14th package, `hatchling`, regressed on Oct 23 with no note yet. Nobody has connected it to the cluster.
   - **The demo:** one root cause, one toolchain fix, 13–14 packages proven reproducible.
2. **The build harness mirrors Debian's own CI (all variations except the kernel), on Docker first** (`VERIFICATION_HARNESS.md`, D-022).
   - Debian's CI no longer varies file ordering or build path, so we don't need FUSE or privileged containers for the default profile.
   - Sandboxes become an accelerator behind the same interface, not a blocker.
3. **The agent is a tool-using investigator, not a one-shot prompt** (`AGENT_DESIGN.md`, D-023).
   - Its key tool is `probe`: run any command twice under the two Debian variation environments and compare the outputs, in seconds rather than a 5-minute rebuild.
   - This is how it *tests hypotheses*, the "write, run, and test code" the track asks for.
4. **Toolchain attribution is built in** (D-024). When the responsible file lives in an installed package (`dpkg -S`), the agent fixes that package, injects the patched `.deb` into every affected build environment, and verifies all dependents. One fix, N receipts.
5. **Patches are made with exact search-and-replace edits, not raw diffs written by the model** (D-025). The harness computes the real diff. This removes the most common failure of LLM patching: malformed hunks.
6. **The benchmark is restructured into three tracks** (`BENCHMARK_PROTOCOL.md` v2, D-026). Track A (diagnosis) needs no builds and no snapshot.debian.org archaeology, so it can't eat our week.
7. **Scale story with the Batch API** (D-027). We run a cheap Nemotron signature pass over all ~1,140 unreproducible Debian packages and publish a "map of Debian unreproducibility".
   - Estimated cost: under $1.
   - It also finds other one-fix-many-packages clusters.

8. **Review pass of 2026-10-25 (`REVIEW_2026-10-25.md`): six changes, D-031 to D-036.** Verified against live Debian data; none of them changes the architecture.
   - **Blind flagship run** (D-031): Debian's notes already tag all 13 packages, and the catalogue entry names the tool, so the headline run removes it.
   - **Keyless record/replay** (D-032): anyone can watch the real agent session without a key; also makes the end-to-end test free and deterministic.
   - **GitHub Actions as a second builder** (D-033): A and B on separate public runners, 14 packages in parallel, laptop-independent.
   - **Overlay injection** (D-034): the campaign no longer depends on the toolchain package building on Python 3.15.
   - **Harness fidelity fixes** (D-035): Debian CI also varies the kernel and adds 6 h 23 min to the clock; our docs said otherwise.
   - **`/judges` page and README "For judges" section** (D-036): every guideline and criterion linked to evidence.
9. **Scope trim, v3 (D-037).** With about 20–30 focused hours per person, the Musts alone take most of the time (§2.1). So: 1 patch candidate per round, a core set of rule detectors, Track A with one ablation, Track B with 4 packages, the batch map and the `/judges` page moved to Could, the Actions workflow after the campaign is green, and a two-template site. Technical fixes to the v2 additions are in `REVIEW_2026-10-25.md` §10.

---

## 1. The winning thesis (what every hour serves)

**One sentence for judges:**
> "SameBytes is an agent that finds why software builds differently every time, fixes the cause in the source (not by scrubbing the output), and proves it with byte-identical builds. On Debian it traced 13 unreproducible packages to one silent bug in a shared tool, fixed it once, and proved all 13 reproducible."

The four judging criteria and what wins each (full map in `EXECUTION_GUARDRAILS.md` §1):

| Criterion | What wins it for us |
|---|---|
| Technological Implementation (tie-breaker) | Tool-using Nemotron agent that runs real experiments (`probe`, twin builds). Each model has a role chosen by a bake-off. Token Factory structured output, function calling, prefix caching (with measured savings), Batch API and, if granted, Sandboxes. Every call and build is logged. Tests for the rules, policy, leakguard and scorer. |
| Design | One command (`samebytes fix autoflake`) with a live terminal view of which model is doing what. A static report site that opens on the finished flagship fix: before and after hashes, cause in plain English, patch, receipt, cost. |
| Potential Impact | Debian has blocked unreproducible packages since May 2026. 1,140 packages are unreproducible on unstable. A real upstream fix (argparse-manpage) and a Debian follow-up, submitted with your approval. Maintainer or RB-team quote if we get one. |
| Quality of Idea | Fix the cause, then prove it, versus Google OSS Rebuild, which normalizes differences away. Toolchain clustering. Sealed, contamination-aware benchmark. Published limitations. |

---

## 2. Scope (MoSCoW): frozen today, revisited only at the gates in §5

### Must (the submission fails without these)
- **M1. `twinbuild` harness on Docker** with the `debian-ci` profile.
  - Before and after builds; SHA-256 comparison; diffoscope on mismatch; package file-list check.
  - Builds run offline. (`VERIFICATION_HARNESS.md`)
- **M2. Evidence fetcher and diff digest.** Published diffoscope JSON and logs, digested into a compact `DiffDigest`. (`DATA_SOURCES.md`, `ARCHITECTURE.md` §5)
- **M3. Rules engine, core set (D-037).** `TZ_SHIFTED_SDE_DATE`, `CLOCK_DATE`, `CLOCK_TIME`, `EPOCH_NUMBER`, `LOCALE_TEXT`, `SIZE_ONLY` (derivative marking) and one table-driven marker detector (user, home, host, domain, environment, PATH, build flags, kernel string). Ordering, randomness, archive mtime, umask and binary-code detectors only if ahead. (`AGENT_DESIGN.md` §4)
- **M4. Investigator agent** (Nemotron 3 Ultra, tools including `probe`) that returns a schema-valid `Diagnosis` naming the responsible file. Toolchain attribution included.
- **M5. Patcher agent** (Nemotron Super, chosen by bake-off) with edit tools, the patch policy guard, 1 candidate per round (2 on Sandboxes or Actions) and up to 3 rounds. The critic is a single Ultra call (explanation plus root-cause/workaround label); its "revise once" loop is Could (D-037).
- **M6. Verification loop.** Patched twin build; success means identical hashes for every `.deb`, an unchanged file list, and tests passing in build A. A receipt is produced.
- **M7. Flagship campaign.** argparse-manpage fixed once; the 11 fast cluster members verified (the 13 minus `openqa` and `python-salib`, which build slowly; run those overnight if time allows).
- **M8. Cost ledger and budget guard.** Every model call is logged with tokens, cached tokens, $ and latency, with a hard dollar cap.
- **M9. Report site** (static, GitHub Pages; two templates: landing page and package card) plus a `README` with the required sections and the "For judges" table.
- **M10. Video ≤ 3:00, Devpost submission, feedback section.**

### Should (big score gains, do after the Musts are green). Listed in priority order: value per hour (D-037)
1. **S9. Blind flagship run** (D-031). A flag, the redaction in three places, the blind leakguard, the memory probe and 3 recorded runs (T23b). About 2 hours. It is the headline.
2. **S5. Real contribution.** An upstream PR to `praiskup/argparse-manpage` and a follow-up on Debian bug #1126092, after your explicit approval, with AI-assistance disclosure. About 1 hour of agent and team time, plus your review.
3. **S3. UpstreamScout with Tavily**, in product mode only: finds the Debian bug, the upstream PR that introduced the regression, and the upstream release status. It changes what the agent does next (see `AGENT_DESIGN.md` §8). This is our entry for the Best Use of Tavily prize. About 3 hours.
4. **S6. Keyless replay** (D-032). Recording is free from T06 onwards (the `llm/*.json` files already exist); `samebytes replay` by `(stage, index)` is about 2 hours, any day before Thursday.
5. **S1. Benchmark Track A** (diagnosis, no builds) on a sealed set with the memorization probe and **one** ablation (`ultra-oneshot`); others only if ahead. About 3 hours plus unattended runtime.
6. **S2. Benchmark Track B.** **4** diverse fast packages outside the flagship cluster through the full fix loop, scored objectively. About 2 attended hours; builds run overnight.
7. **S8. GitHub Actions verification workflow** (D-033), flagship first, **only after T22 is green**. About 3–4 hours for Person A (T22b).

### Could (only if ahead of schedule)
- **C0a. Batch API signature map** of all FTBR packages, with cluster discovery (was S4; `AGENT_DESIGN.md` §10).
- **C0b. `/judges` page** (was S7; D-036). The README "For judges" table carries the same links and is Must.
- **C0c. Critic "revise once" loop, extra rule detectors, extra Track A ablations, Track B beyond 4 packages** (D-037).
- **C1. Sandboxes backend**: same interface, parallel candidate branches, offline verification. Promote it to Should the moment access is granted. (With S8 in place, the "independent machines" claim no longer depends on it; Sandboxes remain the Nebius-native version of the same idea.)
- **C2. Strict profile** (reprotest with build-path and file-order variation via disorderfs) for the flagship only: a "strict-verified" badge.
- **C3. Signed receipts.** Sigstore keyless signing in GitHub Actions when the site is published.
- **C4. Mini GitHub Action** that runs the twin-build check on *any* repo: promoted to **S8** for our own repo; packaging it as a reusable action for other repos stays Could.
- **C5. `hatchling`** (a 25-minute CI build) verified as the 14th cluster member. With S8 this becomes feasible: two parallel runner jobs (A and B), roughly 40 minutes wall-clock, no laptop time.

### Won't (explicitly out of scope this week)
- Fine-tuning; NeMo Agent Toolkit (deprecated Oct 2026); a web backend or database server.
- reproduce.debian.net-style real-archive rebuilds; non-Debian ecosystems (mention as "next").
- Auto-filing anything upstream.

### 2.1 Hours check (D-037; rough estimates of focused hours with AI-assisted coding)
Capacity: about 20–30 focused hours per person until Friday morning, so 40–60 in total.

| Work | Person A | Person B |
|---|---|---|
| Day 0: setup, image, manual twin build and fix (T01–T04) / skeleton, client with recording, digest on fixtures (T05–T07) | 4 | 5 |
| M1 harness and probe (T10–T12), baselines (T13) / M3 core rules, M4 investigator, M8 ledger (T14–T16) | 9 | 10 |
| M5 policy guard (T21), M6 verify and receipt, M7 overlay and campaign (T20, T22) / M5 patcher, orchestrator, one-call critic (T23) | 9 | 6 |
| M9 site, two templates (T33) / M10 README, video and Devpost, shared (T34, T40–T43) | 3 + 3 | 3 |
| **Musts** | **≈ 28** | **≈ 24** |
| Shoulds in priority order | S2 (2), S8 (3–4) | S9 (2), S5 (1), S3 (3), S6 (2), S1 (3) |

What this means, stated plainly:
- **The Musts fill most of the capacity.** At 20 hours each, the Musts don't all fit; you'd ship the flagship fix, campaign, site and video, and nothing else. At 30 hours each, B fits S9, S5 and S3 and probably S6; A fits S2 and maybe S8.
- **Person A is the bottleneck** (the harness is on the critical path and has the most Must hours). B takes any shared work (README, video edit) so A can finish M6–M7 by Tuesday.
- **Gate rule:** a person starts a Should only when their Must tasks for that day are done. B's first Should (S9, then T24) waits until `samebytes fix autoflake` runs end to end (T23); A's S8 waits until T22 is green.
- If Day 0 or Day 1 slips by more than half a day, drop S1 and S8 immediately rather than at the freeze.

---

## 3. Team split and the contract between you

- **Person A, "the kitchen":** harness, builds, Docker or Sandboxes, receipts, campaign runner, site deploy.
- **Person B, "the brain":** LLM client, digest, rules, agents, scout, ledger, benchmark, site content.

You meet at **three frozen interfaces**, written down in `ARCHITECTURE.md` §4 and §5. Freeze them by the end of Day 0. After that, change them only together.

1. `Backend.twinbuild(request: TwinBuildRequest) -> TwinBuildResult`, plus `Backend.probe(...)`.
2. Pydantic models in `src/samebytes/models.py`: `PackageRef`, `DiffDigest`, `Diagnosis`, `PatchCandidate`, `TwinBuildResult`, `Receipt`, `LedgerEntry`.
3. The run directory layout `runs/<run_id>/<pkg>/…` (`ARCHITECTURE.md` §7).

**Fixtures unblock B before A is done.** On Day 0, A commits a recorded `TwinBuildResult` and diffoscope JSON for `autoflake` (unpatched) under `tests/fixtures/autoflake/`. B builds the agent against a `FakeBackend` that replays the fixtures.

---

## 4. Day-by-day plan

Times are IST, estimated at about 5 focused hours per person on weekdays and more on Sunday. Each task has an ID; mention it in commit messages (`T07: ...`).

### Day 0: Sun 25 Oct (today, evening). Prove the flagship end-to-end by hand

| ID | Owner | Task | Done when |
|---|---|---|---|
| T01 | A | Follow `SETUP.md` §1–6 on the personal laptop. Repo inside WSL ext4 (`~/src/SameBytes`), not on NTFS or `/mnt/c`. | `docker run --rm hello-world` works inside WSL; `git status` clean |
| T02 | A | Build `samebytes-builder` from `docker/Dockerfile` (fixed version in this pack). Record the image digest. Also run the faketime offset check: `docker run --rm samebytes-builder:2026-10-25 faketime -f +34410180 date` must print a date 398 days 6 h 23 min ahead of `date`; if it doesn't, set `SB_TIME_OFFSET=+398d`. | `docker image inspect samebytes-builder:2026-10-25` shows a digest; offset check passes |
| T03 | A | **Manual twin build of `autoflake` 2.4.0-1**, using the shell recipe in `VERIFICATION_HARNESS.md` §9. | SHA-256 of `python3-autoflake_*.deb` differs between A and B, and diffoscope shows the `.TH` date line differing |
| T04 | A | **Manual fix test.** Inside the env image, patch `/usr/lib/python3/dist-packages/argparse_manpage/compat.py` as in `FLAGSHIP_CASE.md` §5 and rebuild both. | Hashes identical. **This single result de-risks the whole project.** |
| T05 | B | Project skeleton: `pyproject.toml` (`ARCHITECTURE.md` §3), `src/samebytes/` layout, `ruff`, `pytest`, pre-commit with detect-secrets (keep your existing baseline). | `pytest` runs (0 tests OK); pre-commit passes |
| T06 | B | `llm/client.py` plus `samebytes doctor --llm`: probe which reasoning controls Token Factory honours (`TECH_REFERENCE.md` §2.4). **Record from the start** (`SAMEBYTES_LLM_MODE=record` writes each request/response keyed by `(stage, index)`, `AGENT_DESIGN.md` §2.1.1); the `replay` mode and command come later (S6). | A table of supported params for Ultra, Super, Lightning and Nano, saved to `docs/TECH_REFERENCE.md` §2.4; recorded calls appear under `runs/<id>/llm/` |
| T07 | B | `evidence/debian.py`: fetch `reproducible.json` (cached), the dbdjson, both logs and the buildinfo for `autoflake`. `digest/diffoscope.py` v0. **Real fixtures for all 14 cluster members are already in `tests/fixtures/evidence/`** (with `MANIFEST.md`): write the parser against them. | `samebytes fetch autoflake` writes `evidence/` and a `digest.json` showing the `.TH` leaf; the parser passes on all 14 fixtures |
| T08 | You | Email contree@nebius.com about Sandboxes access, including your project ID, use case, and the request for 50 concurrent operations. Ask in Discord too. | Sent; logged in `FEEDBACK_LOG.md` |

**Gate G0 (Sun 23:30 IST):**
- Did T03 reproduce the difference and T04 make it vanish?
  - **Yes:** proceed as planned.
  - **T03 shows no difference:** check the variation env with `VERIFICATION_HARNESS.md` §11, the troubleshooting section.
  - **T03 still fails after an hour:** switch the flagship to the next cluster candidate (`psutils`, then `osc`). The fix is the same, so only the demo package changes.

### Day 1: Mon 26 Oct. Harness in code; investigator finds the cause

| ID | Owner | Task | Done when |
|---|---|---|---|
| T10 | A | `harness/docker_backend.py`: env-image creation (source download and build-deps, committed image), the `sb-build` entrypoint with the `debian-ci` profile, twin build, collection of outputs. | `samebytes twinbuild autoflake` reproduces T03 in code |
| T11 | A | `harness/compare.py`: per-`.deb` SHA-256, file-list manifest, diffoscope JSON and text on mismatch. | Unit tests on two fixture `.deb` pairs, identical and different |
| T12 | A | `Backend.probe()`: run a command twice under the A and B environments in the env image, offline, with a 120 s timeout. | `samebytes probe autoflake -- python3 -c 'from argparse_manpage.compat import get_reproducible_date as g; print(g())'` shows two different dates |
| T13 | A | Start **baseline twin builds** of the 11 fast cluster members plus 8 Track B candidates in the background (`samebytes twinbuild --batch bench/trackB_candidates.txt`). | A table of reproduced vs not reproduced, with wall times, in `runs/baseline/` |
| T14 | B | `digest/rules.py` with the **core detector set** (M3, D-037) from `AGENT_DESIGN.md` §4, plus a unit test per detector using the real hunks from §4.3 and the 14 evidence fixtures (2-day gaps included). | `pytest tests/test_rules.py` green; autoflake yields a `TZ_SHIFTED_SDE_DATE` signal |
| T15 | B | `agent/tools.py` and `agent/investigator.py`: the Ultra tool loop, `submit_diagnosis` schema, step and budget caps. | On the autoflake fixture, with `probe` from T12 or a fake, the diagnosis names `argparse_manpage/compat.py`, `responsible.kind=toolchain`, `varying_factor=timezone` |
| T16 | B | `ledger.py` and budget guard; `samebytes cost` summary. | Every call in T15 appears in `runs/.../ledger.jsonl` with `cached_tokens` |

**Gate G1 (Mon 23:30 IST):**
- Does `samebytes diagnose autoflake` find the toolchain file without any notes?
  - **No:** look at the transcript first, before changing prompts. The usual causes are a missing tool result or truncated evidence (`AGENT_DESIGN.md` §12).

### Day 2: Tue 27 Oct. Patch, verify, campaign

| ID | Owner | Task | Done when |
|---|---|---|---|
| T20 | A | Patch application: package target (quilt patch with DEP-3 header) and toolchain target by **overlay** (D-034: apply the edits to the installed files, delete their `__pycache__` entries, record before/after hashes; `VERIFICATION_HARNESS.md` §10). The `.deb` mode is a later, non-blocking task. | `samebytes twinbuild autoflake --toolchain-overlay runs/<id>/patch.json` gives identical hashes |
| T21 | A | `agent/policy.py` (deterministic patch policy, `AGENT_DESIGN.md` §7) and the manifest check after the build. | Unit tests: test-disabling, hardcoded-date and file-deleting patches are all rejected |
| T22 | A | `samebytes campaign argparse-manpage` runs the dependents' twin builds with the patched toolchain, 2 in parallel. | ≥ 9 of the 11 fast members reproducible, with receipts |
| T23 | B | `agent/patcher.py`: Super tool loop with edit tools and `submit_candidate`; `agent/orchestrator.py` state machine; refine loop on a remaining diff. | `samebytes fix autoflake` runs end-to-end: diagnosis, toolchain patch, verified, receipt |
| T23b | B | **Blind run** (S9; `--blind`, `SAMEBYTES_REDACT_ISSUES`, `AGENT_DESIGN.md` §3.1.1): one redacted catalogue feeding the system prompt, the rule hints and `catalogue_lookup`; the blind leakguard; the no-tools memory probe (3 samples). Then 3 blind runs and 1 product run, recorded, copied to `published/`. | Leakguard test green; the memory probe and all 3 blind results are recorded whatever they show (target: `argparse_manpage/compat.py`, `responsible.kind=toolchain`) |
| T22b | A | **Only after T22 is green** (S8). `.github/workflows/verify.yml` (`VERIFICATION_HARNESS.md` §14): one `env` job per package (prepare_env, push by digest), `build` A and B as separate jobs pulling that digest, `compare` checking the digests match; `samebytes ci-build --env-image`. Flagship pair first. | A public Actions run shows autoflake baseline different and overlay identical, with A and B on different runners and one env digest; receipts uploaded |
| T24 | B | `agent/scout.py`: Tavily search and extract, BTS lookup, `UpstreamIntel` schema, citation check. | For autoflake it reports Debian #1126092 (patch, NMU 4.7-1.1), that 4.7-1.1 is not built for `all` because of the Python 3.15 failure, and that upstream v4.8 still uses the broken import |
| T25 | B | Model bake-off on the dev set (5 packages): Super 3 vs 3.5 Super VL as patcher; Lightning vs Nano as condenser. Record results in `DECISIONS.md` D-028. | Table with JSON validity, tool-call errors, success and $ |
| T26 | You | Review the upstream patch and Debian follow-up drafts the agent produced (`FLAGSHIP_CASE.md` §7). Approve or edit, then **you** submit them under your name with the disclosure line. | PR URL and bug mail sent, logged in `DECISIONS.md` |

**Gate G2 (Tue 23:30 IST): the most important gate.**
- Is there at least one end-to-end agent fix with a receipt, and has the campaign started?
  - **Yes:** Wednesday goes to benchmark, site and Should items.
  - **No:** cut every Could, S8 and S1 now. Wednesday morning goes to finishing M5–M7.
- **Sandboxes decision:** if access isn't granted by now, the Docker backend is final (D-022). Mention Sandboxes only as "designed for, pending beta access" (`RISKS_AND_BLOCKERS.md` R1).

### Day 3: Wed 28 Oct. Evidence of quality. Feature freeze at 23:59

| ID | Owner | Task | Done when |
|---|---|---|---|
| T30 | B | Build and **seal** Track A (`BENCHMARK_PROTOCOL.md` §3); run it once; run the `ultra-oneshot` ablation and the memorization probe (other ablations only if ahead, D-037). | `bench/runs/<id>/scores.json` and a table; seal hash committed *before* the run |
| T31 | A | Track B: **4** diverse packages through `samebytes fix` in the background (`BENCHMARK_PROTOCOL.md` §4), chosen before the run. | Results table with failures and reasons |
| T32 | B | **Could (C0a):** Batch API signature pass over all FTBR packages; cluster table. | `site/data/map.json` with cluster sizes |
| T33 | A | `report/site.py`: static site generated from the runs data (`DEMO_AND_SUBMISSION.md` §4), deployed by a GitHub Pages workflow. | A public URL that works when logged out |
| T34 | Both | README v1 (`DEMO_AND_SUBMISSION.md` §5) including the **"For judges" table**, limitations, feedback section draft from `FEEDBACK_LOG.md`. | README renders on GitHub; every row of the judges table links to a real file or run |
| T35 | B | **Could (C0b):** `/judges` page from the same data as the README "For judges" block (`DEMO_AND_SUBMISSION.md` §4 and §5): requirement checklist with evidence links, criterion map, ledger totals, 60-second keyless check (`samebytes replay`). | Page live; every claim on it links to a file in `published/` or a public Actions run |

**Feature freeze, Wed 23:59 IST.** After this point, only bug fixes, docs, video and packaging.

### Day 4: Thu 29 Oct. Packaging

| ID | Owner | Task | Done when |
|---|---|---|---|
| T40 | Both | Record the video per the script in `DEMO_AND_SUBMISSION.md` §2. Pre-record terminal runs; never demo live builds in one take. | Final cut ≤ 2:55; uploaded to YouTube as public; link works when logged out |
| T41 | B | Final benchmark tables, failure analysis, costs on the site and in the README. | Numbers in README = numbers on site = numbers in video |
| T42 | A | Fresh-clone test: follow the README quickstart on a clean WSL user. | Quickstart works in ≤ 10 minutes up to `samebytes doctor` |
| T43 | Both | **Submit a Devpost draft** with all fields, even if imperfect. | Draft saved |

### Day 5: Fri 30 Oct. Buffer and submit
- Morning: fix only what Thursday's checks found. Final `git push`; tag `v1.0-hackathon`.
- Run the final checklist in `HACKATHON_CHECKLIST.md`.
- **Submit by 18:00 IST.** The hard deadline is 22:30 IST.

---

## 5. Gates, cut lines and "if behind" rules

- **Cut order if behind:** all Coulds → S8 → S2 → S1 → S6 → S3. Never cut M1–M10 (including the README "For judges" table), S9, S5, or the flagship. If even the Musts are at risk on Wednesday, shrink M7 to the ≥ 9 fast members already built and M9 to the landing page plus the autoflake card.
- **The 90-minute rule:** if any task is stuck for 90 minutes, write it in `RISKS_AND_BLOCKERS.md` with what you tried, then take its fallback.
- **No new features after the freeze.** Ideas go to `DECISIONS.md` as "Proposed (post-hackathon)". They are good material for the write-up's "what's next" section.

---

## 6. Budgets

### Money (Token Factory credits)
Estimates use the live prices in `TECH_REFERENCE.md` §2.2; the derivation is in `AGENT_DESIGN.md` §11.

| Item | Estimate |
|---|---|
| Development and debugging over the week (mostly on cheap models) | ≈ $4 |
| Flagship agent runs: 1 product run, 3 blind runs, the memory probe (verification is compute) | ≈ $1.50 |
| Track B, 4 packages × ≈ $0.30, plus reruns | ≈ $1.50 |
| Track A: headline Ultra agentic on 84 items (≈ $0.09 each, ≈ $7.60); `ultra-oneshot` ablation on the 54 test items (≈ $1.20); memorization probe (≈ $0.50) | ≈ $9.30 |
| Optional (Could): batch signature map ≈ $1; other ablations ≈ $4 | (≈ $5) |
| **Total planned** | **≈ $16** (≈ $21 with every optional item) |
| Hard cap (`SAMEBYTES_MAX_USD`) | $30 (assumes both $25 credits; Q-001) |
| Reserve for judges, Dec 1–15 | ≥ $5 |

If only $25 of credit is available, set the cap to $18. Run Track A's headline on the 54 test items only (≈ $4.90), which brings the plan to about $12, and skip the optional ablations.

### Machine time (Docker on the laptop)
- One twin build of a 2–4-minute package takes about 5–10 minutes locally. Laptop builds run 1.5–2× slower than CI, and A and B run in parallel only if you have ≥ 8 cores and ≥ 12 GB RAM for WSL.
- Campaign of 11 members: about 1–1.5 hours, unattended. Track B, 4 packages × up to 4 twin builds (baseline plus up to 3 rounds of 1 candidate): about 1.5–2.5 hours, overnight.
- **Rule:** long runs start before you go to sleep and before work. Never wait on a build while awake.

---

## 7. Rituals (from `EXECUTION_GUARDRAILS.md` §4–5, condensed)

- **Start of session:** read `DECISIONS.md` open questions; check today's gate; pick the one task that moves the score most.
- **End of session:** decisions and questions logged; feedback entry if anything was good or painful; credit spend recorded; commit code and docs together; push.
- **Daily at 22:00 IST (15 min):** A and B sync on the gate question for the day. Write the answer in `DECISIONS.md` (changelog).

---

## 8. Definition of done for the submission
- [ ] Every Must is green, and `samebytes fix autoflake` works from a fresh clone (with keys).
- [ ] The flagship campaign has ≥ 9 verified receipts published on the site, **and the blind-run recordings** (catalogue entry removed; all 3 attempts and the memory probe) of the diagnosis.
- [ ] If S6 is done: `samebytes replay published/flagship-blind` plays back from a fresh clone with **no** `.env`.
- [ ] The README "For judges" table exists and every row links to evidence (the `/judges` page only if C0b was done).
- [ ] README has setup, Nemotron usage per role, where Token Factory helped, Tavily use, limitations, benchmark tables, feedback.
- [ ] Video ≤ 3:00, public, names Token Factory, Nemotron Ultra, Super and Lightning or Nano, and Tavily out loud.
- [ ] Repo is public with an MIT license visible in About; no secrets in the history (`detect-secrets scan` clean).
- [ ] Demo URL (GitHub Pages) works when logged out and needs no running server until Dec 15.
- [ ] Every upstream submission is approved by you and carries an AI-assistance disclosure.
