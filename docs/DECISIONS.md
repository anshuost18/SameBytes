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
**Date:** 2026-10-24 · **Status:** Accepted (pending beta access, see Q-002)
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
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Judges want to see which model does what. Token Factory's fine-tuning list contains no Nemotron models.
**Decision:** Fixed roles as above, plus an ablation to justify them. No fine-tuning.
**Consequences / to do:** [ ] Log the model, tokens and cost for every call; [ ] show this per package in the report.

### D-007: Three candidate patches on parallel branches, max 3 rounds
**Date:** 2026-10-24 · **Status:** Accepted (refined by D-024 and D-025)
**Decision:** Super proposes 3 patches, each verified on its own sandbox branch. The winner is the smallest passing diff. If none pass, the remaining diff goes back to diagnosis, for up to 3 rounds.

### D-008: Human in the loop; no auto-filing; disclose AI help
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Debian's GR 2026-002 (August 2026) chose "Responsible Use of Generative AI": AI is allowed, the submitter is fully accountable, and disclosure is encouraged. The community is split roughly 64/36.
**Decision:** Campaign output is a review queue. Any bug or merge request we file is human-reviewed and carries an `Assisted-By:` disclosure. We file only a handful.
**Consequences / to do:** [ ] Add "approve / reject" state to the report; [ ] include a disclosure line in the bug template.

### D-009: Benchmark on recent human fixes; RepFix as baseline
**Date:** 2026-10-24 · **Status:** Accepted
**Context:** Older Debian notes and patches are likely in the models' training data.
**Decision:** The held-out set is fixes from May–October 2026 (monthly reports, bugs.debian.org). Metrics: cause top-1/top-3 accuracy, file localization, verified fix rate, $/fix, min/fix. Report RepFix's 64/116 alongside, with a dataset caveat.

### D-010: Tavily for upstream intelligence
**Date:** 2026-10-24 · **Status:** Accepted
**Decision:** Before patching, search for existing upstream fixes, issues and the upstream tracker. This is a runtime Tavily call, which makes us eligible for Best Use of Tavily ($3k, stackable with a track award).
**Consequences / to do:** [ ] If upstream already fixed it, the agent says so and links it instead of duplicating work.

### D-011: Cluster the unexplained packages
**Date:** 2026-10-24 · **Status:** Accepted (Should)
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
**Date:** 2026-10-24 · **Status:** Accepted
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
**Date:** 2026-10-24 · **Status:** Accepted
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
**Date:** 2026-10-24 · **Status:** Superseded by D-026
**Context:** Judges said to talk to potential users. That strengthens Potential Impact.
**Decision:** Post a short, honest note to `#reproducible-builds` (OFTC IRC) or the rb-general list, and/or contact a maintainer whose package we fixed. Ask whether the patch and explanation are useful. Quote replies in the write-up, with permission.
**Consequences / to do:** [ ] Draft the message once we have 2–3 verified fixes (Tue 27).

### D-023: Benchmark on still-unreproducible packages with recent notes
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** The original protocol (D-017) built pre-fix versions from snapshot.debian.org for 60-75 packages. Old sources often fail with today's toolchain, and the builds would consume the week.
**Decision:**
- Diagnosis set: packages still unreproducible in unstable/amd64 whose cause note was added after the models' training cutoffs (Q-009). The note date comes from the git history of reproducible-notes, read only by the answer-key builder.
- Their current source is pre-fix by definition. Evidence is the published diffoscope output plus our own build logs. Cause top-1/top-3 (and file localization where the note names a file) are scored against the note, with no builds.
- Confirm each package is still unreproducible in our harness. Drop it otherwise and log why.
- Verified fix rate is measured on a subsample of the same set (no answer key needed).
- Known-fix packages (a human fix exists) are optional, only if time allows. "Same fix as human" is scored only on those.
- Everything else in BENCHMARK_PROTOCOL stays: sealed key, frozen prompts, leakguard, Tavily off, networking off, one run, all failures published.
**Supersedes:** leak path L3 and dataset construction in the protocol, Q-011, and the dataset part of D-009.
**Consequences / to do:**
- [ ] Build the answer key from the notes and their git dates (key builder only).
- [ ] Find the models' training cutoffs (Q-009).

### D-024: Agent loop with tools (refines D-007)
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** The track is "agents that write, run, and test code". A fixed pipeline that writes three blind patches is weaker than a model that can inspect and test. Function calling works on Nano, Super and Ultra (2026-10-25).
**Decision:**
- Ultra gets read-only tools: read_file, grep_source, list_dir.
- Super gets edit tools: apply_patch, show_diff, run_build (calls our harness).
- Super may propose up to 3 candidate patches inside the loop.
- Hard budget per package: max tool steps, tokens, minutes and builds. Running out is a logged failure with a reason.
- The harness decides pass or fail. A model's claim of success counts for nothing.
- Every tool call is logged. In benchmark mode networking is off and the answer-key path is denied.
- The rules pre-pass (D-005) and the Nano condense step stay in front.
**Consequences / to do:**
- [ ] Define tool schemas and the budget config.
- [ ] Log tool calls in the report.

### D-025: Staged verification, lower Must, demo package criteria
**Date:** 2026-10-25 · **Status:** Accepted
**Context:** Three candidates over three rounds could mean up to 18 full builds per package, which a laptop can't sustain.
**Decision:**
- Screen candidates with the failing variation only and stop at the first pass. Run the full variation set only on the winning patch. Cache the unpatched baseline build. Run containers in parallel.
- The Must is 5 verified fixes. 10 is a stretch. Always report attempted vs verified, and failures by reason.
- Demo package: both builds under 2 minutes, a clear cause, a visible hash mismatch before the fix and a match after. Choose it at Gate 1 and pre-record the run as a fallback.
- Receipts list the variations actually tested, including that user_group is excluded locally (D-022).
**Consequences / to do:**
- [ ] Implement staged verification in the harness.

### D-026: Contact real users by Tue 27 (replaces D-020 as Proposed)
**Date:** 2026-10-25 · **Status:** Accepted
**Decision:**
- Send 1-2 human-reviewed patches by Tue 27 Oct, with an Assisted-By disclosure (D-008), so a reply can arrive before 30 Oct.
- Pick packages with no existing bug or patch.
- Ask a short question on #reproducible-builds or rb-general: "is this patch and explanation useful?"
- File only what we have reviewed and understood, under our own name.
- Do not make the video depend on a reply.

---

## Open questions and blockers

| ID | Question / blocker | Owner | Due | Status |
|---|---|---|---|---|
| Q-001 | Token Factory activation needs a Visa or Mastercard (RuPay rejected). Get the account active and claim both $25 credits (code `NEBIUS-DEVPOST-GLOBAL26` + Builders Program) | You | Sat 24 | Open, **blocker** |
| Q-002 | Sandboxes beta access granted? What's the pricing, and does it use our credits? | You | Sat 24 | Open, **blocker** for D-003 |
| Q-003 | Inside Sandboxes: is `/dev/fuse` available? Root for the `user_group` and `domain_host` variations? Max execution timeout? | Person A | Sat 24 | Open |
| Q-004 | Exact Nemotron model IDs on Token Factory; does batch inference support Nemotron? | Person B | Sat 24 | Partly resolved 2026-10-25: model IDs and base URL confirmed; batch inference untested |
| Q-005 | Final project name (SameBytes / Twinbuild / other) | Both | Wed 28 | Open |
| Q-006 | Confirm team split (A = kitchen, B = brain) | Both | Sat 24 | Open |
| Q-007 | Tavily API key (Builders Program credits) | You | Sat 24 | Open |
| Q-008 | Credit budget: target ≤ $35 of $50, leaving a reserve for the live demo through December 15 | Person B | Ongoing | Open |
| Q-009 | Training-data cutoffs of Nemotron 3 Nano, Super and Ultra (from the model cards), to pick benchmark fixes newer than the cutoff | Person B | Sun 25 | Open |
| Q-010 | Does Token Factory support structured JSON output, function calling, context caching and batch inference for the Nemotron models? | Person B | Sun 25 | Mostly resolved 2026-10-25: JSON mode, function calling and caching confirmed on Nano, Super and Ultra; batch untested |
| Q-011 | Can we fetch pre-fix source versions from snapshot.debian.org and upload them into sandboxes? How long do they take to build? | Person A | Sun 25 | Superseded by D-023 |
| Q-012 | **Employer IP check.** The user works on a NetApp machine with NetApp OneDrive. The hackathon rules require the submission to be the entrant's original work, solely owned by them. Check NetApp's policy on side projects, open-source contributions and IP ownership. Preferably build on a personal machine or account. | You | Sat 24 | Resolved 2026-10-25: building on a personal laptop |
| Q-013 | Where the project folder lives (Downloads vs. other) and the GitHub repo name. The Claude Desktop Filesystem connector couldn't reach Downloads. | You | Sat 24 | Open |
| Q-014 | Arch (~11% unreproducible) and Nix (69–91%) figures from the original idea weren't re-verified. Check them before quoting, or drop them. | Person B | Thu 29 | Open |

When a question is resolved, move it into a decision entry (D-0NN) and mark it **Resolved → D-0NN** here.

---

## Changelog

- 2026-10-24: Initial log created from research and planning discussion (D-001 to D-015, Q-001 to Q-008).
- 2026-10-24: Added rubric optimization, sealed benchmark protocol, Token Factory feature policy, feedback log and user validation (D-016 to D-020, Q-009 to Q-011). New docs: `BENCHMARK_PROTOCOL.md`, `EXECUTION_GUARDRAILS.md`, `FEEDBACK_LOG.md`.
- 2026-10-24: Handoff pack completed for the code session. Added `CLAUDE.md` (root), `TECH_REFERENCE.md`, `EXPLAINER.md`, `SOURCES.md` and `ORIGINAL_IDEA.md`. Added Q-012 to Q-014.
- 2026-10-25: API smoke tests passed (Q-004 partly, Q-010 mostly resolved). Q-012 resolved. Repo pushed with MIT license and secret scan.
- 2026-10-25: Added D-023 (benchmark on still-unreproducible packages), D-024 (agent loop with tools), D-025 (staged verification, Must lowered to 5), D-026 (contact real users by Tue 27). D-020 superseded.
