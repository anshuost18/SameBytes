# Decisions, open questions and blockers

> A living log. Every time we choose a direction, change scope, or hit a blocker, add an entry here, update `PROJECT_BRIEF.md` if the brief changes, and link the code or commit that implements it.
> Statuses: **Accepted** (decided, to implement) · **Implemented** (done, link it) · **Superseded** (replaced; link the new entry) · **Proposed** (not yet agreed).

## How to add an entry

```
### D-0NN: <short title>
**Date:** YYYY-MM-DD · **Status:** Accepted
**Context:** why this came up
**Decision:** what we chose
**Alternatives:** what we rejected and why
**Consequences / to do:** what this means for the build (checkboxes)
**Implemented in:** <file / commit / PR>
```

---

## Decisions

### D-001: Build the reproducible-builds repair agent
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** We researched alternatives before committing.
**Decision:** Keep the original idea, upgraded as described in D-003 to D-015.
**Alternatives:**
- **Linux kernel syzbot crash fixing:** Google already runs an AI patch workflow in syzbot, and academic agents such as kAgent and CrashFixer exist; it's also too heavy for 6 days.
- **CUDA/Triton kernel optimizer:** crowded field, needs GPUs, not Token Factory–native.
- **Fuzz harness generation:** OSS-Fuzz-gen already exists.
- **PyPI wheel reproducibility:** interesting, but the ground truth is murky. It becomes our "next ecosystem" mention instead.
**Consequences / to do:** Submit to the **Coding and Agentic Engineering** track.

### D-002: We fix; we don't just detect
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Detection is already solved by reprotest, diffoscope and Debian CI.
**Decision:** The product is diagnosis + fix + proof. Detection results are inputs.
**Consequences / to do:** All messaging says "makes builds reproducible and proves it."

### D-003: Token Factory Sandboxes are the build and proof engine
**Date:** 2026-10-24 · **Status:** Superseded in part by D-022 (2026-10-25). Sandboxes become an accelerator behind the same backend interface; Docker is the primary backend until access is granted.
**Context:** The track wording is "agents that write, run, and test code in Token Factory." Two judging criteria score effective and non-obvious use of Token Factory. Sandboxes give us:
- a fresh VM per operation;
- immutable image UUIDs;
- branching;
- runs with networking disabled;
- 50 concurrent operations (beta).
**Decision:** Run all verification builds in Sandboxes. Replace the earlier plan of free GitHub Actions runners.
**Alternatives:** GitHub Actions (no Token Factory credit); local Docker only (weaker story). Local Docker stays as a **fallback**.
**Consequences / to do:**
- [ ] Request Sandboxes access
- [ ] Import a Debian unstable image with the build toolchain
- [ ] Record image UUID and operation IDs in each receipt
- [ ] Keep a Docker backend behind the same interface

### D-004: Start from published evidence, build only to verify
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** tests.reproducible-builds.org already publishes diffoscope results and both build logs for each unreproducible package.
**Decision:** Download that evidence for diagnosis. Spend compute only on verifying patches.
**Consequences / to do:** [ ] Write a scraper/downloader with local caching.

### D-005: Deterministic rules run before any LLM
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Many causes are pattern-matchable, which saves money and adds certainty. Judges reward using LLMs only where they add value.
**Decision:** The rules pre-pass covers gzip mtime, build path strings, `date` in `debian/rules`, `.a` member order, and similar patterns. Rule hits are passed to the models as hints.
**Consequences / to do:** [ ] Rules module; [ ] report which cases rules alone solved.

### D-006: Model roles are Nano (condense), Ultra (diagnose), Super (patch); no fine-tuning
**Date:** 2026-10-24 · **Status:** Superseded by D-023 and D-028 (2026-10-25). Ultra stays the investigator. The patcher and fast roles are decided by bake-off, and Nemotron 3.5 Super VL and 3.5 Lightning are added as candidates. No fine-tuning still holds.
**Context:** Judges want to see which model does what. Token Factory's fine-tuning list contains no Nemotron models.
**Decision:** Fixed roles as above, plus an ablation to justify them. No fine-tuning.
**Consequences / to do:** [ ] Log the model, tokens and cost for every call; [ ] show this per package in the report.

### D-007: Three candidate patches on parallel branches, max 3 rounds
**Date:** 2026-10-24 · **Status:** Amended 2026-10-25: up to **2** candidates per round on Docker (laptop capacity), 3 on Sandboxes; still max 3 rounds. **Amended again by D-037: 1 candidate per round on Docker, 2 on Sandboxes or Actions.** Ranking: root cause, then workaround, then normalization, then smaller diff (`AGENT_DESIGN.md` §7).
**Decision:** Super proposes 3 patches, each verified on its own sandbox branch. The winner is the smallest passing diff. If none pass, the remaining diff goes back to diagnosis, for up to 3 rounds.

### D-008: Human in the loop; no auto-filing; disclose AI help
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Debian's GR 2026-002 (August 2026) chose "Responsible Use of Generative AI": AI is allowed, the submitter is fully accountable, and disclosure is encouraged. The community is split roughly 64/36.
**Decision:** Campaign output is a review queue. Any bug or merge request we file is human-reviewed and carries an `Assisted-By:` disclosure. We file only a handful.
**Consequences / to do:** [ ] Add "approve / reject" state to the report; [ ] include a disclosure line in the bug template.

### D-009: Benchmark on recent human fixes; RepFix as baseline
**Date:** 2026-10-24 · **Status:** Superseded by D-026 (2026-10-25)
**Context:** Older Debian notes and patches are likely in the models' training data.
**Decision:** The held-out set is fixes from May–October 2026 (monthly reports, bugs.debian.org). Metrics: cause top-1/top-3 accuracy, file localization, verified fix rate, $/fix, min/fix. Report RepFix's 64/116 alongside, with a dataset caveat.

### D-010: Tavily for upstream intelligence
**Date:** 2026-10-24 · **Status:** Accepted
**Decision:** Before patching, search for existing upstream fixes, issues and the upstream tracker. This is a runtime Tavily call, which makes us eligible for Best Use of Tavily ($3k, stackable with a track award).
**Consequences / to do:** [ ] If upstream already fixed it, the agent says so and links it instead of duplicating work.

### D-011: Cluster the unexplained packages
**Date:** 2026-10-24 · **Status:** Expanded by D-024 (toolchain campaigns) and D-027 (batch map), 2026-10-25
**Decision:** Nano produces a diff signature per package. We cluster the signatures to find shared toolchain causes, so one fix covers N packages.

### D-012: Demo focuses on variation testing, not real-world rebuilds
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** tests.reproducible-builds.org varies the environment deliberately, giving clean cause and effect. reproduce.debian.net rebuilds the published archive packages and is what blocks migration.
**Decision:** Target the variation-testing failures. Explain the distinction and name reproduce.debian.net as next.

### D-013: Positioning is "Debian = proof, guard = product"
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Objection raised: "Isn't this one-time for ~620 packages?"
**Decision:** The pitch has three parts:
1. **It recurs.** Regressions and new packages keep appearing; Debian blocks regressions specifically. 4,347 bugs have been fixed, yet about 1,100 unreproducible packages remain.
2. **The market is much bigger.** Other distros, PyPI (15–19% byte-identical), npm, Maven, containers, firmware, corporate pipelines.
3. **The product form is a Dependabot-style reproducibility guard** for CI, with receipts as audit evidence. CRA enforcement begins December 2027.
**Consequences / to do:** [ ] Put this in the video (2 sentences) and in the write-up; [ ] stretch goal: a minimal GitHub Action demo.

### D-014: File-ordering variation depends on FUSE
**Date:** 2026-10-24 · **Status:** Superseded by D-022 (2026-10-25). Debian CI doesn't currently vary file ordering or build path, so the default profile needs no FUSE. disorderfs is used only in the optional strict profile.
**Decision:** Test for `/dev/fuse` in Sandboxes on day 1. If it's unavailable, run reprotest with that variation disabled in Sandboxes, run disorderfs locally in privileged Docker, and list this as a limitation.

### D-015: Demo hosting
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Judging runs 1–15 December, and the project must stay available until then. Judges may judge from the video alone.
**Decision:** A static report site on GitHub Pages plus a CLI test build. Any live mode is rate- and credit-capped so it survives to December 15.

### D-016: Optimize every feature against the judging rubric
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Goal is to maximize the score. There are four equal criteria, scored 1–5, and Technological Implementation breaks ties. The judges asked for:
- a real problem for a real audience;
- an aha moment within 30 seconds;
- one thing done well;
- showing which model does what;
- published limitations.
**Decision:** Each feature must map to a criterion in `EXECUTION_GUARDRAILS.md` section 1, or it gets cut. Sessions start and end with the rituals in that file.
**Consequences / to do:** [ ] Review the map at the feature freeze (Wed 28).

### D-017: Benchmark answers are sealed and hidden from the agent
**Date:** 2026-10-24 · **Status:** Accepted; procedure updated by D-026 (protocol v2). No pre-fix snapshot builds; three tracks.
**Context:** Testing on known fixes is worthless if the agent can see or remember the answer. Ten leak paths were identified (L1–L10).
**Decision:** Follow `BENCHMARK_PROTOCOL.md`:
- pre-fix source versions, with evidence built by us;
- `packages.yml` never loaded; package names stripped from the catalogue;
- Tavily off and sandbox networking off for headline numbers;
- dev/test split, with prompts frozen before the test run;
- answer key readable only by the scorer, with its hash committed before the run;
- `leakguard` scanner;
- memorization probe plus an old-vs-new comparison;
- one run, with all failures published.
**Alternatives:** Hiding the issue label only (the original plan). Rejected: leaks through newer sources, the web, notes pages and model memory.
**Consequences / to do:**
- [ ] Implement `MODE=benchmark` enforcement in code
- [ ] Assign separate people to building the answer key and writing prompts
- [ ] Find pre-fix versions on snapshot.debian.org (Q-011)

### D-018: Use Token Factory features only where they serve the story
**Date:** 2026-10-24 · **Status:** Accepted
**Decision:**
- **Core:** inference and Sandboxes.
- **Use if supported for Nemotron:** structured JSON output, function calling, context caching, batch inference for campaigns.
- **Optional:** `-fast` flavor, observability screenshots.
- **Not used:** fine-tuning, Serverless, NemoClaw/OpenShell. See the table in `EXECUTION_GUARDRAILS.md` section 2.

### D-019: Keep a live feedback log
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Feedback is a required part of the submission, there's a $100 prize, and details are forgotten quickly.
**Decision:** Log entries in `FEEDBACK_LOG.md` as they happen.

### D-020: Validate with real users
**Date:** 2026-10-24 · **Status:** Proposed
**Context:** Judges said to talk to potential users. That strengthens Potential Impact.
**Decision:** Post a short, honest note to `#reproducible-builds` (OFTC IRC) or the rb-general list, and/or contact a maintainer whose package we fixed. Ask whether the patch and explanation are useful. Quote replies in the write-up, with permission.
**Consequences / to do:** [ ] Draft the message once we have 2–3 verified fixes (Tue 27).

### D-021: Flagship case is the argparse-manpage cluster
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** Research found one root cause behind 13 FTBR packages, verified live.
- `import datetime.timezone` always fails in argparse-manpage, which then uses local time for `SOURCE_DATE_EPOCH`.
- Debian's fix 4.7-1.1 is stuck because it fails to build on Python 3.15.
- Upstream v4.8 is still broken.
- `hatchling` regressed on Oct 23 with no note.
**Decision:** The video, site landing and Track C are built around this case (`FLAGSHIP_CASE.md`). It is excluded from sealed benchmark sets (we know the answer).
**Consequences / to do:**
- [ ] T03/T04 manual proof on Day 0
- [ ] Campaign (T22)
- [ ] Upstream and Debian drafts for your approval (T26)

### D-022: Docker-first harness that mirrors Debian CI exactly; Sandboxes as an accelerator
**Date:** 2026-10-25 · **Status:** Accepted. **Amended 2026-10-25 by D-035:** "exactly" holds for everything except the kernel (CI varies it, containers can't) and the clock is +398 d **+6 h 23 min**.
**Context:**
- Sandboxes access isn't granted yet.
- Debian CI's current variation table doesn't vary build path or file ordering, so no FUSE is needed.
- Mirroring CI (all but the kernel) is what "fixing the CI failure" means.
**Decision:**
- `debian-ci` profile (`VERIFICATION_HARNESS.md` §3.1) on Docker, with `--network none`.
- The same `Backend` interface for Sandboxes (`ARCHITECTURE.md` §4).
- Strict profile (reprotest/disorderfs) is optional.
**Alternatives:** reprotest `+all` as the core (needs privileged FUSE; varies more than CI does); waiting for Sandboxes (a blocker).
**Consequences / to do:**
- [ ] `docker/Dockerfile` + `docker/sb-build`
- [ ] `docker_backend.py`
- [ ] `sandbox_backend.py` when access arrives (decide by Tue 22:00)

### D-023: Tool-using investigator with a `probe` experiment tool
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** One-shot "read the diff, guess the cause" can't localize causes that live in other packages, and can't confirm hypotheses. The track asks for agents that write, run and test code.
**Decision:** The Ultra investigator uses function-calling tools: read, search, `grep_build_log`, `which_package`, `probe` (runs a command under the A and B environments, offline) and `catalogue_lookup`. It must confirm with a probe before high confidence (`AGENT_DESIGN.md` §5.1, §6.2).
**Consequences / to do:** [ ] `Backend.probe` (T12); [ ] investigator loop (T15)

### D-024: Toolchain attribution and campaigns
**Date:** 2026-10-25 · **Status:** Accepted
**Decision:**
- If the producing file is in an installed package (`dpkg -S`), the diagnosis targets that package.
- The fix is built once as a local `.deb`, injected into each dependent's env image, and every dependent is twin-built.
- Receipts list the toolchain override.
**Consequences / to do:** [ ] `build_toolchain_deb`, `prepare_env(toolchain_debs=…)` (T20); [ ] `samebytes campaign` (T22)

### D-025: Patches are exact search-and-replace edits; the harness computes the diff
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** LLM-written unified diffs often have bad hunk headers and context.
**Decision:**
- The patcher uses `edit_file(path, old, new)` on a git-tracked scratch copy.
- `view_diff` and `submit_candidate` snapshot `git diff`.
- The harness wraps non-`debian/` changes as quilt patches with DEP-3 headers.
**Consequences / to do:** [ ] patcher tools (T23)

### D-026: Benchmark protocol v2, three tracks
**Date:** 2026-10-25 · **Status:** Accepted (supersedes D-009)
**Context:** Only 10 FTBR packages were tagged after June 2026, so there are too few recent human fixes. Pre-fix snapshot builds would take too long.
**Decision:**
- **Track A:** diagnosis-only on CI evidence. The test set is tags added after 2025-10-01 (after every model's pretraining cutoff); old-tag control; memorization probe; ablations.
- **Track B:** verified fixes on 6–10 fast packages (4 per D-037).
- **Track C:** the flagship campaign.

Full rules in `BENCHMARK_PROTOCOL.md`.
**Consequences / to do:** [ ] `bench build|seal|run|score|probe` (T30)

### D-027: Batch signature map plus rule learning
**Date:** 2026-10-25 · **Status:** Accepted (Should)
**Decision:**
- A Nano/Lightning signature pass over all ~1,140 FTBR packages through the Batch API (estimated under $1), published as a map of clusters.
- Verified fixes become reusable deterministic rules (RELAY-style); members that match skip the LLMs.
**Consequences / to do:** [ ] submit the batch by Tue 23:00 IST (24-hour window risk); [ ] `rules/verified/*.yml`

### D-028: Model bake-offs decide the patcher and fast roles
**Date:** 2026-10-25 · **Status:** Proposed (fill in the results after T25)
**Decision:**
- **Patcher:** Nemotron 3 Super vs Nemotron 3.5 Super VL.
- **Fast roles:** Nemotron 3.5 Lightning vs Nemotron 3 Nano.
- **Metrics:** schema-valid submit rate, tool-call errors, verified candidates, $, latency (`AGENT_DESIGN.md` §13).
**Results:** _TBD_

### D-029: Upstream contribution for the flagship
**Date:** 2026-10-25 · **Status:** Proposed (needs your approval before sending)
**Decision:**
- **Upstream:** a PR to `praiskup/argparse-manpage` fixing the import, plus a regression test.
- **Debian:** a follow-up on bug #1126092 with the Python 3.15 build fix backport and the hatchling regression.
- Human-reviewed and sent by you, with the AI-assistance disclosure line (D-008).
**Consequences / to do:** [ ] drafts (T26); [ ] send by Wed 28 morning IST

### D-030: Report site is generated from committed `published/` JSON
**Date:** 2026-10-25 · **Status:** Accepted
**Decision:** `runs/` stays gitignored. Curated cards, receipts and scores are copied into `published/`. The GitHub Pages workflow builds the static site from `published/` only. The same files feed the README numbers and the video, so the numbers always match.

### D-031: Flagship headline run is blind (catalogue label removed); both runs published
**Date:** 2026-10-25 (review pass) · **Status:** Accepted
**Context:** `issues.yml` contains `timezone_variant_in_argparse_manpage` ("argparse manpage >= 4.7 will use SOURCE_DATE_EPOCH but will vary on the timezone", bug #1126092), and the notes tag all 13 flagship packages with it. In a normal run the investigator's cached prompt therefore names the tool and the factor. A judge who reads the transcript could conclude the demo was handed its answer.
**Decision:** Add `--blind` / `SAMEBYTES_REDACT_ISSUES`. Run the flagship blind (Tavily off during investigation) as the **headline**, and run it normally as the realistic product case. Publish both, with the redaction list in the manifest (`AGENT_DESIGN.md` §3.1.1, `BENCHMARK_PROTOCOL.md` L11). Reword the pitch: Debian had *labelled* the cluster; SameBytes found the line, fixed it, proved 13 and found a 14th (`FLAGSHIP_CASE.md` §1.1).
**Alternatives:** keep the demo as is (leaves an avoidable credibility gap); pick another flagship (the verified cluster is still the best case we found, and the label doesn't say *where* the bug is).
**Consequences / to do:** [ ] `--blind` flag (T23b); [ ] record both runs; [ ] README table "with label / label removed"; [ ] video line (done in `DEMO_AND_SUBMISSION.md` §2).
**Amended 2026-10-25 (v3 review):** redaction covers all three catalogue paths (system prompt, rule-signal hints, `catalogue_lookup`) from one redacted object; a blind leakguard checks inputs for the label, `1126092` and "vary on the timezone"; a no-tools memory probe on Ultra is published with the blind result, because the bug has been public since January 2026 and the model may simply remember it. The video's "we hid the label" line is used only if the blind runs succeeded.

### D-032: Record/replay layer for model calls (keyless demo, deterministic tests)
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** Judges and the teammate can't run the agent without a Nebius key and credits; the end-to-end test would otherwise cost money and vary run to run; the demo must still work on 15 December.
**Decision:** `SAMEBYTES_LLM_MODE=live|record|replay` in `llm/client.py`, keyed by a hash of the full request (superseded by the amendment below); `samebytes replay <dir>` reruns a recorded session with no network (`AGENT_DESIGN.md` §2.1.1).
**Alternatives:** a screen recording only (not interactive, not testable); mocking with hand-written fixtures (drifts from real behaviour).
**Consequences / to do:** [ ] build with T06; [ ] `published/flagship-blind` and `published/flagship-product`; [ ] CI test replays the flagship.
**Amended 2026-10-25 (v3 review):** replay is keyed by `(stage, call index)`, with a hash of the *normalized* request kept only as a drift check. A raw full-request hash would miss on almost every replay (run IDs, paths, timestamps, fresh tool outputs). Wording everywhere: "replay of a recorded run", never "run the agent without a key".

### D-033: GitHub Actions is a second, independent builder (A and B on separate runners)
**Date:** 2026-10-25 · **Status:** Accepted (Should S8)
**Context:** All verification currently runs on one laptop, so "two independent machines" is two containers on one host, speed depends on the laptop (R4), and judges can't inspect the builds. The repo is public, so runners are free.
**Decision:** `verify.yml` runs the same Docker backend on hosted amd64 runners: build A and build B as separate matrix jobs, a compare job, receipts uploaded, public logs linked from the site (`VERIFICATION_HARNESS.md` §14). It needs no Nebius or Tavily secret.
**Alternatives:** Sandboxes only (access not granted; stays the Nebius-native variant behind the same interface); laptop only (single point of failure).
**Consequences / to do:** [ ] workflow (T22b); [ ] Pages/Actions settings (`SETUP.md` §7b); [ ] receipts carry run URL and job IDs.
**Amended 2026-10-25 (v3 review):** (1) one `env` job per package runs `prepare_env` and pushes the env image; build A and build B pull it **by digest**, and `compare` refuses a receipt if the digests differ. Separate `prepare_env` per role could resolve build-deps against different archive states and fake a result. (2) Least-privilege `permissions:`, inputs via `env:`, actions pinned by SHA. (3) **Status → Should, flagship-first, after T22 is green** (D-037); it is insurance and evidence, not the critical path.

### D-034: Toolchain fixes are verified by file overlay first; the rebuilt `.deb` is a separate deliverable
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** A patched `python3-argparse-manpage` `.deb` can't build today because 4.7 fails on Python 3.15 (`_cached_theme`), the same reason Debian's fix is stuck. Making the Must-have campaign (M7) wait on that is an avoidable risk, and the Day-0 recipe (T04) already proves the overlay path works.
**Decision:** For interpreted toolchains the harness applies the patch's edits to the installed files in each dependent's env image (`toolchain_overrides[].kind="overlay"`, file hashes in the receipt). Compiled toolchains use a rebuilt `.deb`. For the flagship the `.deb` build is attempted afterwards and reported separately (`VERIFICATION_HARNESS.md` §10).
**Consequences / to do:** [ ] `prepare_env(toolchain_overlays=…)` (T20); [ ] overlay mapping via `dpkg -L`; [ ] receipt field.
**Amended 2026-10-25 (v3 review):** the overlay also deletes the overlaid modules' `__pycache__` entries (Debian byte-compiles at install; hash-based "unchecked" `.pyc` files would ignore the edited source) and records an import check (`_TZ_ARGS` non-empty) in the receipt. T20's "done when" now uses the overlay, not the `.deb`.

### D-035: Harness fidelity corrections after reading Debian CI's variation table line by line
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** Re-reading `index_variations.html` found: the kernel **is** varied on amd64; the future clock adds **+6 h 23 min** to +398 d (and the first build may also run in the future); CI's first `PATH` ends with a colon; `tests_ran` as implemented (`dh_auto_test` in the log) is true for every debhelper package.
**Decision:** `sb-build` uses `+34410180` s (override `SB_TIME_OFFSET`), keeps the trailing colon, and records `tests_enabled` plus `test_hint`; acceptance rule 5 is "build A exits 0 with tests enabled". Documentation says "all variations except the kernel", never "exactly". Kernel-string leaks are detected from CI evidence and reported `NOT_REPRODUCED(kernel-only)`, never claimed fixed.
**Consequences / to do:** [ ] doctor check for the faketime offset (T02); [ ] site badge text; [ ] limitations updated (done).

### D-036: A `/judges` evidence page and a "For judges" README block
**Date:** 2026-10-25 · **Status:** Accepted (was Should S7; the page is Could per D-037)
**Context:** The judging brief asks for visible rigor, model roles, and limitations. Evidence scattered across files costs scorers time.
**Decision:** Generate `/judges/` from `published/` and open the README with a 60-second table mapping each Stage 1 requirement and each criterion to a link (`DEMO_AND_SUBMISSION.md` §4–5). Numbers come from the same JSON as the README and video.
**Consequences / to do:** [ ] T35; [ ] a test that fails the site build if a number on `/judges/` disagrees with `published/`.
**Amended 2026-10-25 (v3 review, D-037):** the README "For judges" table is **Must** (part of T34, about 30 minutes). The `/judges/` page is **Could**: it repeats the same links and costs about 2 hours that the Musts need.

### D-037: Scope trimmed to fit 20–30 focused hours per person
**Date:** 2026-10-25 (v3 review) · **Status:** Accepted
**Context:** Each person has about 20–30 focused hours until Friday (asked on Oct 25). The Must list alone is estimated at about 50 person-hours (`BUILD_PLAN.md` §2.1). The v2 review added roughly 10 hours of new work (S6–S9) and marked three of them never-cut, without removing anything.
**Decision:**
- **Patcher:** 1 candidate per round on Docker (2 only on Sandboxes or Actions), still max 3 rounds. **Critic:** one Ultra call that writes the explanation and labels root cause vs workaround; the "revise once" loop is Could.
- **Rules engine:** a core set first (`TZ_SHIFTED_SDE_DATE`, `CLOCK_DATE`, `CLOCK_TIME`, `EPOCH_NUMBER`, `LOCALE_TEXT`, and one table-driven marker detector for user, home, host, domain, environment, PATH, build flags and kernel strings). `ORDERING_ONLY`, `RANDOM_TOKEN`, `ARCHIVE_MTIME`, `UMASK_PERMS` and `BINARY_CODE` only if ahead. `SIZE_ONLY` stays, because the digest needs it.
- **Track A:** headline config plus `ultra-oneshot` only; other ablations optional. **Track B:** 4 packages.
- **Batch API map (S4) → Could.** **`/judges/` page (S7) → Could;** README "For judges" table → Must.
- **GitHub Actions (S8):** flagship-first, after T22 is green.
- **Site:** two templates (landing page and package card).
- **Kept as Should, in this order of value per hour:** S9 blind run, S5 upstream PR, S3 Tavily scout, S6 replay, S1 Track A (trimmed), S2 Track B (4), S8 Actions. Recording model calls starts in T06 (it costs nothing); only the replay command waits.
**Alternatives:** keep v2's scope (likely to finish with half-done Shoulds and a rushed video); cut the blind run (it's the cheapest credibility gain we have).
**Consequences:** the budget drops from about $22 to about $16 planned (`BUILD_PLAN.md` §6). The pitch loses nothing a judge would score.

---

## Open questions and blockers

| ID | Question / blocker | Owner | Due | Status |
|---|---|---|---|---|
| Q-001 | Token Factory activation needs a Visa or Mastercard (RuPay rejected). Get the account active and claim both $25 credits (code `NEBIUS-DEVPOST-GLOBAL26` + Builders Program) | You | Sat 24 | Mostly resolved 2026-10-25: account active and API calls work. Confirm both $25 credits show in billing. |
| Q-002 | Sandboxes beta access granted? What's the pricing, and does it use our credits? | You | Sat 24 | Open, **blocker** for D-003 |
| Q-003 | Inside Sandboxes: is `/dev/fuse` available? Root for the `user_group` and `domain_host` variations? Max execution timeout? | Person A | Sat 24 | Open |
| Q-004 | Exact Nemotron model IDs on Token Factory; does batch inference support Nemotron? | Person B | Sat 24 | Partly resolved 2026-10-25: model IDs and base URL confirmed; batch inference untested (test a 3-request batch on Tue, D-027) |
| Q-005 | Final project name (SameBytes / Twinbuild / other) | Both | Wed 28 | Open |
| Q-006 | Confirm team split (A = kitchen, B = brain) | Both | Sat 24 | Proposed in `BUILD_PLAN.md` §3; confirm who is A and who is B |
| Q-007 | Tavily API key (Builders Program credits) | You | Sat 24 | Open |
| Q-008 | Credit budget: target ≤ $35 of $50, leaving a reserve for the live demo through December 15 | Person B | Ongoing | Open |
| Q-009 | Training-data cutoffs of Nemotron 3 Nano, Super and Ultra (from the model cards), to pick benchmark fixes newer than the cutoff | Person B | Sun 25 | **Resolved 2026-10-25 → D-026.** Pretraining: Ultra Sep 2025, Super Jun 2025, Lightning Sep 2025; boundary 2025-10-01 |
| Q-010 | Does Token Factory support structured JSON output, function calling, context caching and batch inference for the Nemotron models? | Person B | Sun 25 | Mostly resolved 2026-10-25: JSON mode, function calling and caching confirmed on Nano, Super and Ultra; batch untested |
| Q-011 | Can we fetch pre-fix source versions from snapshot.debian.org and upload them into sandboxes? How long do they take to build? | Person A | Sun 25 | **Resolved 2026-10-25 → D-026:** no longer needed; snapshot is used only for `VERSION_GONE` |
| Q-012 | **Employer IP check.** The user works on a NetApp machine with NetApp OneDrive. The hackathon rules require the submission to be the entrant's original work, solely owned by them. Check NetApp's policy on side projects, open-source contributions and IP ownership. Preferably build on a personal machine or account. | You | Sat 24 | Resolved 2026-10-25: building on a personal laptop. Still check the side-project policy before sending upstream contributions under your name. |
| Q-013 | Where the project folder lives (Downloads vs. other) and the GitHub repo name. The Claude Desktop Filesystem connector couldn't reach Downloads. | You | Sat 24 | Resolved 2026-10-25: repo `github.com/anshuost18/SameBytes`; working copy goes in WSL at `~/src/SameBytes` (`SETUP.md` §4) |
| Q-014 | Arch (~11% unreproducible) and Nix (69–91%) figures from the original idea weren't re-verified. Check them before quoting, or drop them. | Person B | Thu 29 | Open |
| Q-015 | Which reasoning controls does Token Factory honour per model? (`TECH_REFERENCE.md` §2.4) | Person B | Sun 25 | Open (T06) |
| Q-016 | Does the autoflake twin build reproduce locally, and does the manual toolchain fix make it identical? | Person A | Sun 25 | Open (T03/T04, gate G0) |
| Q-017 | Exact Batch API request shape (operations API vs OpenAI-style batches) and turnaround | Person B | Tue 27 | Open |
| Q-018 | Rotate the Nebius and Tavily keys (they were in a shared zip) | You | Sun 25 | Open, **security** |
| Q-019 | Why is `crazy-complete` reproducible despite build-depending on argparse-manpage? (A control; a good agent question) | Person B | Wed 28 | Open. Note (review): the notes tag it with the same label, so the tag is stale. |
| Q-020 | Does `faketime -f +34410180` (plain seconds) give +398 d 6 h 23 min in the builder image, or is a unit suffix needed? | Person A | Sun 25 (T02) | Open |
| Q-021 | Can the `env` job of `verify.yml` push the per-package env image to `ghcr.io` with the default token (`packages: write`), can the build jobs pull it by digest from a public package, and do the runners have enough disk for `prepare_env` on the flagship members? | Person A | Tue 27 | Open |
| Q-022 | Devpost eligibility and team membership: are both people eligible, added as members, and have both accepted the rules? | Both | Wed 28 | Open |
| Q-023 | Which `published/` runs become the keyless replay (`flagship-blind`, `flagship-product`) and are the recorded requests free of secrets and of your local paths? | Person B | Thu 29 | Open |

When a question is resolved, move it into a decision entry (D-0NN) and mark it **Resolved → D-0NN** here.

---

## Changelog

- 2026-10-24: Initial log created from research and planning discussion (D-001 to D-015, Q-001 to Q-008).
- 2026-10-24: Added rubric optimization, sealed benchmark protocol, Token Factory feature policy, feedback log and user validation (D-016 to D-020, Q-009 to Q-011). New docs: `BENCHMARK_PROTOCOL.md`, `EXECUTION_GUARDRAILS.md`, `FEEDBACK_LOG.md`.
- 2026-10-24: Handoff pack completed for the code session. Added `CLAUDE.md` (root), `TECH_REFERENCE.md`, `EXPLAINER.md`, `SOURCES.md` and `ORIGINAL_IDEA.md`. Added Q-012 to Q-014.
- 2026-10-25: API smoke tests passed (Q-004 partly, Q-010 mostly resolved). Q-012 resolved. Repo pushed with MIT license and secret scan.
- 2026-10-25: Build-plan research pass. Added D-021 to D-030 and Q-015 to Q-019. D-003, D-006, D-009 and D-014 superseded; D-007 and D-017 amended. New docs: `BUILD_PLAN.md`, `FLAGSHIP_CASE.md`, `AGENT_DESIGN.md`, `VERIFICATION_HARNESS.md`, `DATA_SOURCES.md`, `LANDSCAPE.md`, `RISKS_AND_BLOCKERS.md`, `DEMO_AND_SUBMISSION.md`, `SETUP.md`. Rewritten: `ARCHITECTURE.md`, `BENCHMARK_PROTOCOL.md` (v2), `TECH_REFERENCE.md`. New `docker/Dockerfile` and `docker/sb-build`.
- 2026-10-25 (evening): Review pass (`REVIEW_2026-10-25.md`). Verified flagship facts live; found that Debian's notes already tag all 13 packages and the catalogue entry names the cause; found the CI kernel and clock variations were mis-stated. Added D-031 to D-036 and Q-020 to Q-023; amended D-022. New fixtures: `tests/fixtures/evidence/` (14 real diffoscope JSON files).
- 2026-10-25 (night, v3): Senior review of the review pass (`REVIEW_2026-10-25.md` §10). Amended D-007, D-031 to D-034 and D-036; added D-037 (scope trim for 20–30 h per person). Fixed `sb-build` `meta.json` escaping, the Actions env-digest design, the `KERNEL_STRING` regex, the leakguard/rule-hint conflict (L9) and T20's stale `.deb` dependency.
