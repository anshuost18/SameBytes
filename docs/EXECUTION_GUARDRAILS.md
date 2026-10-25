# Execution guardrails

> **Purpose.** Make sure every hour of building earns points with the judges, and that the small things that matter don't slip. Read this at the start of each session; run the end-of-session ritual before stopping.
> Related decisions: D-016, D-017, D-018, D-019, D-020 in `DECISIONS.md`. Last updated: 2026-10-24.

## 1. What the judges score, and the features that earn each point

Four criteria, equally weighted, each scored 1–5. Technological Implementation breaks ties, so it gets the most care.

### Technological Implementation (tie-breaker)
*"How well is it built, and how effectively does it use Token Factory and Nemotron?"*
- Token Factory used for **both** thinking (inference) **and** doing (Sandboxes). This is the core differentiator.
- Each Nemotron model has one clear, measured job, backed by an ablation table showing the split pays off.
- Sandbox features used for real reasons:
  - fresh VM per build means independent builders;
  - immutable image UUID becomes the environment record;
  - branches let us test 3 patches in parallel;
  - `networking.enabled=false` gives hermetic builds and a benchmark that can't leak.
- Reliability: retries, timeouts, caching, logs for every call and operation.
- Clean repo with tests for the leakguard, the scorer and the rules.

### Design
*"A complete, coherent product, not a proof of concept."*
- One command runs the full flow: `samebytes fix <package>`.
- The report site is the product face. For each package it shows:
  - before/after hashes;
  - cause in plain English;
  - the patch;
  - **which model did which step**, with cost;
  - a receipt download;
  - review status.
- A little onboarding: a short "what you're looking at" panel on the report site and a quick start under 5 minutes in the README.
- Action first: the landing view opens on a finished fix, not on a settings form.

### Potential Impact
*"A credible, specific case for a real audience, and the demo actually shows it."*
- A specific audience with current pain:
  - Debian maintainers blocked since May 2026;
  - a volunteer team of about 9 active note-writers;
  - companies facing the CRA (December 2027).
- Proof in numbers: test-set results, fixes on previously unexplained packages, $ and minutes per fix.
- **Talk to real users** (D-020): one or two quotes from Reproducible Builds people or a Debian maintainer.
- The "isn't this one-time?" answer: it recurs, it's a bigger market, and the product becomes a guard (D-013).

### Quality of the Idea
*"Creative, non-obvious use of Token Factory and Nemotron; genuine understanding of the problem."*
- We fix and prove, rather than detect.
- Contamination-aware benchmark with a sealed answer key (`BENCHMARK_PROTOCOL.md`).
- Clustering finds one-fix-many-packages causes.
- Respect for Debian's AI policy: human review, disclosure, no spam.
- Published limitations and failure analysis.

## 2. Token Factory and partner resources: what we use and why

We use a resource only when it supports the main story. Judges said "one thing done well beats a big stack."

| Resource | Use | Status |
|---|---|---|
| Inference API (Nemotron 3 Nano / Super / Ultra) | The three agent roles | Core |
| **Sandboxes** | Independent builds, patch branches, hermetic verification, receipts | Core (beta access: Q-002) |
| Structured output / JSON | Diagnosis returns a strict schema: cause type, file, line, confidence, evidence | Use; check support for Nemotron (Q-010) |
| Function calling / tools | Agent tools: read file, grep source, run a build, query the catalogue | Use if Nemotron supports it well; otherwise JSON actions |
| Context caching | The long static prefix (system prompt + ~430-type catalogue) is reused on every diagnosis, which cuts cost | Use if it applies automatically; mention in feedback |
| `-fast` model flavor | Nano in the interactive demo, for snappy responses | Optional, check cost |
| Batch inference | Campaign mode: Nano condenses hundreds of diffs cheaply | Should, if it supports Nemotron (Q-010) |
| Inference observability | Screenshots for the video and README to show real usage | Nice to have |
| **Tavily** | Upstream-fix lookup; Best Use of Tavily bonus ($3k) | Should; disabled in benchmark mode |
| Fine-tuning | Not used: no Nemotron models are on the fine-tune list | Rejected (D-006) |
| Serverless Endpoints/Jobs, NemoClaw, OpenShell, Hermes | Not needed for this track's story | Not used (avoid stack padding) |

## 3. Things that silently cost points: check continuously

- [ ] Models and Token Factory are named in the README, the Devpost description, "Built With", **and spoken aloud** in the video.
- [ ] Every model call is logged with model, tokens, cost and latency. The report shows them.
- [ ] No API keys in code or git history (`.env` gitignored; scan before every push).
- [ ] License visible in the repo's About section.
- [ ] Benchmark mode enforced in code, not by memory (see `BENCHMARK_PROTOCOL.md` section 5).
- [ ] Limitations section kept up to date as we discover new ones.
- [ ] **Feedback log** updated whenever something with Nebius or NVIDIA tools is good or painful (`FEEDBACK_LOG.md`). It's required, there's a $100 prize, and specifics are forgotten by Thursday.
- [ ] Credit spend tracked against the budget (Q-008); keep a reserve for judging, 1–15 December.
- [ ] Demo artifacts (report site, receipts, test build) will still work on 15 December without our laptops.
- [ ] Human review recorded before anything is filed upstream; AI assistance disclosed.

## 4. Start-of-session ritual (5 minutes)

1. Read the open questions and blockers in `DECISIONS.md`. Is anything blocking today's goal?
2. Check today's goal in the `PROJECT_BRIEF.md` timeline. Is the plan still realistic, or do we cut something now?
3. Pick the one thing that most moves the judging score today.

## 5. End-of-session ritual (10 minutes)

1. New decision or scope change? Add a `D-0NN` entry in `DECISIONS.md` and update the brief if needed.
2. New blocker or question? Add a `Q-0NN` row.
3. Anything worth telling Nebius or NVIDIA? Add a line to `FEEDBACK_LOG.md`.
4. New limitation discovered? Add it to the brief's limitations list.
5. Record credit spend so far.
6. Commit code and docs together.
