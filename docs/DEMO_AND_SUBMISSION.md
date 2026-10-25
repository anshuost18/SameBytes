# Demo, video and submission

> Everything judges see: the video script, report site, README, Devpost text, feedback section, and the "above and beyond" checklist. Rules are in `HACKATHON_CHECKLIST.md`.

## 1. What judges must take away (in this order)
1. **Aha (≤ 30 s):** two builds of the same source give different bytes. SameBytes explains why in one sentence and turns 13 packages green.
2. **It's a real agent**, not a prompt: it runs experiments, crosses package boundaries, and proves results.
3. **Each Nemotron model has a clear, measured job,** and Token Factory features are used for real reasons.
4. **Real impact:** a Debian backlog with policy pressure, a real upstream fix, measured cost per fix.
5. **Rigor:** sealed benchmark, published failures and limitations.

## 2. Video script (target 2:50; hard limit 3:00)
Record the terminal and site segments separately at 1080p. Use the voice-over on top. Speed up long runs ×8–×20 with an on-screen "⏩ 4 min build". No copyrighted music.

| Time | Screen | Voice-over (read naturally) |
|---|---|---|
| 0:00–0:08 | Split terminal: `sha256sum` of autoflake build A and build B, hashes highlighted red | "Debian built this package twice from the same source and got different files." |
| 0:08–0:22 | `samebytes fix autoflake` live view, sped up; it ends with the diagnosis line, then a grid of 13 packages flipping red → green | "We hid Debian's own label for this bug, and SameBytes still found it: one silent bug in a shared tool that stamps man pages with local time. One fix, and all 13 affected packages now build byte-for-byte identical." **Use this line only if the blind runs succeeded; say the real count ("in 3 of 3 runs") and the N of 13.** If they didn't, use: "SameBytes traced it to one silent bug in a shared tool…" and show the blind result honestly on the results page. |
| 0:22–0:45 | Site landing page: Debian stats with sources, "blocked since May 2026" | "Why it matters: reproducible builds are how you check nobody tampered with software between source and binary. Debian now blocks packages that aren't reproducible. Over eleven hundred are failing, and only a handful of volunteers fix them by hand." |
| 0:45–1:05 | Live view, investigator phase. Highlight each tool call: `grep_build_log`, `which_package → python3-argparse-manpage`, `read_file compat.py`, `probe` printing `2025-08-24` vs `2025-08-25` | "The diagnosis runs on NVIDIA Nemotron 3 Ultra through Nebius Token Factory. It doesn't guess. It searches the build log, traces the man page to an installed tool, reads that tool's code, and runs an experiment under Debian's two test environments. Different dates, hypothesis confirmed." |
| 1:05–1:20 | Scout panel: Tavily results showing Debian bug #1126092, tracker "Missing build on all", upstream PR #119. **On-screen caption: "product run (Tavily on)"**, because the blind run has Tavily off and the 0:45 shots come from it | "Tavily search checks what humans already know. Debian had a patch, but it's stuck: that version doesn't build on Python 3.15. So the agent plans to fix both." |
| 1:20–1:40 | Patcher (Nemotron Super) applying two edits; the policy guard passes; two builds on **two separate GitHub runners** (or Nebius Sandbox VMs) running in parallel, the public Actions page visible | "Nemotron Super writes the smallest root-cause patch. A policy guard blocks cheats like skipping tests or hard-coding dates. Then two builds on separate machines vary timezone, locale, user, clock and more, the way Debian's CI does." (Say "on separate machines" only if `verify.yml` or Sandboxes ran it; otherwise show the two laptop containers and drop those three words.) |
| 1:40–1:55 | Identical hashes; receipt JSON; critic explanation | "Identical hashes, tests passing, and a receipt anyone can check. Nemotron Ultra reviews the fix and writes the explanation for maintainers." |
| 1:55–2:20 | Results page: campaign 13/13 (actual numbers), hatchling "found by SameBytes", Track A table with the probe split, Track B table, cost per fix, the cache savings line, the map of 1,140 packages | "Across the cluster: N of 13 proven. It also caught a fourteenth package that regressed two days ago and nobody had linked yet. On a sealed benchmark of cases tagged after the models' training cutoff, it named the right cause in X of Y. A full fix costs about thirty cents, and prompt caching cut input cost by Z percent." |
| 2:20–2:38 | Upstream PR page and the Debian bug follow-up (with disclosure line); limitations slide | "We submitted the upstream fix ourselves, reviewed and disclosed as AI-assisted. Nothing is filed automatically. Limitations are on the site: we mirror Debian's CI variations except the kernel, not every real-world rebuild yet. You can replay this whole run without a key." |
| 2:38–2:50 | End card: name, URL, "Built with Nebius Token Factory · NVIDIA Nemotron 3 Ultra / Super / Lightning · Tavily" | "SameBytes: we don't just detect unreproducible builds, we fix them and prove it. Next, a reproducibility guard for every CI pipeline." |

**Rules for the recording:**
- Say "Nebius Token Factory" and the Nemotron model names out loud.
- Never show keys or `.env`.
- Every number on screen must match the README and site exactly. Pull them from the same `published/*.json`.

## 3. Shot list to capture as you build (don't leave this for Thursday)
- [ ] T03 baseline hashes differing (terminal, large font). **Capture on Day 0.**
- [ ] T04 identical hashes after the manual fix (backup shot).
- [ ] First full `samebytes fix autoflake` live view (Tue), **recorded with `SAMEBYTES_LLM_MODE=record`** so it replays later.
- [ ] The **blind** run (`--blind`) live view, and the public GitHub Actions page with A and B on two runners.
- [ ] `samebytes replay published/flagship-blind` running with no `.env` (proof for the "keyless" claim).
- [ ] The campaign grid filling in (Tue/Wed).
- [ ] The Sandboxes console or operations list, if access is granted.
- [ ] Token Factory console: usage or observability page showing the calls (for the "used for real" proof).
- [ ] Upstream PR page.

## 4. Report site (static, GitHub Pages)

- **Source of truth:** curated results copied from `runs/` into `published/` (committed, small JSON: cards, receipts, benchmark scores, map). The site is generated only from `published/`. `runs/` stays gitignored.
- **Stack:** Jinja2 templates rendered by `samebytes site build`. Plain HTML plus a small vanilla JS file; diffs rendered with diff2html from a CDN; no build toolchain.
- **Deploy:** `.github/workflows/pages.yml` runs on push to `main`: `pip install -e . && samebytes site build --from published --out site`, then `actions/upload-pages-artifact` and `actions/deploy-pages`. Optionally sign receipts with cosign keyless (Could C3).

**Scope (D-037):** the **Must** site is two templates: the landing page (items 1, 2, 4 and 6 below as sections of one page) and the `/pkg/<name>/` card (item 3). `/map/` exists only if the batch map (now Could) ran. `/judges/` (item 7) is **Could**; the README "For judges" table (§5) carries the same links and is Must.

**Pages:**
1. **`/` landing.** It opens on the flagship result.
   - Hero: "1 root cause → 13 packages reproducible".
   - Before and after hash pair; the "how it works" strip of 7 icons, with the model name under each step.
   - The three headline numbers: packages fixed, benchmark score, $ per fix.
2. **`/cluster/argparse-manpage/`:**
   - the root-cause explanation (critic's `explanation_md`) and the two-line code view;
   - a member grid (package, before/after, grade, receipt link), with hatchling marked "found by SameBytes";
   - the upstream and Debian links.
3. **`/pkg/<name>/` card:**
   - status badge and grade;
   - before and after hashes per `.deb`;
   - cause in plain English; causal chain; patch (diff2html);
   - **model timeline**: each stage with model, tokens (cached), $ and seconds;
   - tool-call transcript (collapsible); receipt download; review status.
4. **`/benchmark/`:** Track A, B and C tables, ablation rows, probe-flagged split, failure analysis, and the method sentence.
5. **`/map/`:** the batch signature map, with clusters by size, example hunks and "suspected shared tool".
6. **`/about/`:** what you're looking at, limitations, the AI-disclosure stance, and the team.
7. **`/judges/`** (D-036, **Could** per D-037, generated from `published/`): one page that answers "did they follow the rules, and where is the evidence?"
   - **Stage 1 requirements, each with a link:** runtime Token Factory calls (count, models, tokens, $, cached %, first and last timestamp from the ledger); NVIDIA open models used (names); track fit ("agent that writes, runs and tests code": link to one tool-call transcript with a `probe` and a twin build); working project (the keyless replay command).
   - **Criterion map:** the four criteria, each with 3–4 links (Technological Implementation: model-role table with bake-off numbers, Sandboxes/Actions usage, tests, ledger; Design: the card page and live view; Impact: the flagship, the upstream PR, cost per fix; Idea: blind run, sealed benchmark, limitations).
   - **Counts that match the README and the video:** packages verified, builds run, receipts, Token Factory calls, Tavily calls, total $.
   - **Rigor links:** `SEAL.txt` and its commit, the leakguard tests, all failures.
   - **Honesty block:** what Debian already knew (label, patch), what we added, the kernel limitation.

## 5. README template (repository root; fill it on Wed/Thu)
```markdown
# SameBytes — make builds reproducible, and prove it

SameBytes is an AI agent that finds why a Debian package builds differently every time, fixes the
cause in the source, and proves the fix with two independent builds that produce byte-identical
packages. Built for the Nebius × NVIDIA Global AI Hackathon (Coding & Agentic Engineering).

**Demo:** <GitHub Pages URL> · **Video:** <YouTube URL> · **License:** MIT

## For judges (60 seconds)
| You want to check | Where |
|---|---|
| It calls Nebius Token Factory at runtime, with NVIDIA Nemotron | Ledger totals below (N calls, models, tokens, $, cached %); raw `published/*/ledger.jsonl` |
| It is an agent that writes, runs and tests code | `/pkg/autoflake/` tool-call transcript: `probe` (experiment), patch, twin build, receipt |
| You can watch the recorded run **without keys** | `samebytes replay published/flagship-blind` plays back the recorded session (no network, no `.env`; labelled REPLAY) |
| The proof is real | Receipts with both hashes per `.deb`; if `verify.yml` ran: public Actions run with build A and build B on two runners <link> |
| Technological Implementation | Model roles + bake-off table; structured output, tool calling, prefix caching (measured); tests (`pytest`), leakguard |
| Design | `/` landing, `/pkg/<name>/` cards, the live terminal view |
| Potential Impact | Flagship (13 packages, one fix), upstream PR <link>, cost per fix, Debian policy since May 2026 |
| Quality of the Idea | Fix-and-prove (not detect), **blind run** (Debian's own label removed), sealed benchmark |
| Honest limits | Limitations section; failures table; what Debian already knew (label + stuck patch) |

## Results (as of <date>)
- Flagship: one bug in `argparse-manpage` made 13 Debian packages unreproducible. SameBytes fixed it once
  and proved N/13 (+ hatchling) reproducible. Upstream PR: <link>. Debian bug: #1126092 follow-up <link>.
- Benchmark (sealed, post-training-cutoff tags): tag@1 X/Y, tag@3 …, family@1 … (table below).
- Verified fixes outside the cluster: K/M. Median cost $…, median time … min.

## How it works
<diagram from docs/ARCHITECTURE.md §2> + 7-step list with the model per step.

## Which model does what, and why
| Role | Model | Why (bake-off numbers) |
| Investigator | NVIDIA Nemotron 3 Ultra | … |
| Patcher | NVIDIA Nemotron 3 Super / 3.5 Super | … |
| Critic | Nemotron 3 Ultra | … |
| Fast roles (scout, signatures, condense) | Nemotron 3.5 Lightning / Nano | … |

## Where Nebius Token Factory helped
- Inference for all roles (OpenAI-compatible API) — structured outputs (strict JSON schema), function
  calling, automatic prefix caching (measured: Z% of input tokens cached, $ saved), Batch API (map of
  1,140 packages), [Sandboxes: N VMs, branches, offline verification — if used].
## Other tools: Tavily (how it changes the agent's plan), Debian reproducible-builds data.

## Quickstart
(5 steps: clone → .env → docker build → samebytes doctor → samebytes fix autoflake)

## Benchmark method and results
(method sentence from BENCHMARK_PROTOCOL.md §8, tables, failure analysis)

## Limitations
(from docs/RISKS_AND_BLOCKERS.md)

## Responsible use
Human review before anything is sent upstream; AI assistance disclosed (Debian GR 2026-002).

## Feedback on Nebius Token Factory, Sandboxes and NVIDIA Nemotron
(see §7 below — required)

## Related work
(docs/LANDSCAPE.md short version)
```

## 6. Devpost write-up (fields)
- **Inspiration:** the xz backdoor and SolarWinds; Debian's May 2026 policy; volunteers fixing by hand.
- **What it does:** the 3-sentence version plus the flagship.
- **How we built it:** architecture; model roles; Token Factory features; harness that mirrors Debian CI; benchmark integrity.
- **Challenges:** honest ones, e.g. faketime quirks, reasoning-token budgets (`content=None`), Python 3.15 toolchain breakage, Sandboxes access timing.
- **Accomplishments:** the flagship, the upstream fix, the sealed benchmark.
- **What we learned:** e.g. "experiments beat reading: the probe tool turned guesses into proof".
- **What's next:** reproduce.debian.net real-archive rebuilds; the Sphinx and R clusters; PyPI wheels; a GitHub Action guard.
- **Built with:** nebius-token-factory, nvidia-nemotron, nemotron-3-ultra, nemotron-3-super, nemotron-3.5-lightning (or nano), tavily, python, docker, debian, diffoscope, github-pages, [nebius-sandboxes].

## 7. Feedback section (required; ten $100 prizes)
Use `FEEDBACK_LOG.md` entries. For **each** tool (Token Factory inference, Batch API, Sandboxes, Nemotron Ultra, Super/3.5 Super, Lightning/Nano, Tavily), give:
- what we used it for;
- what worked (with numbers);
- what didn't (exact error or behaviour, and what we expected);
- onboarding (time from zero to the first call);
- whether we'd use it again, and why.

**Specific, verifiable items already collected:**
- `content=None` when `max_tokens` is small, because reasoning consumes the budget. Suggest a docs note or a server-side minimum.
- Prefix caching worked out of the box (4,224 of 4,520 tokens cached).
- Model-ID inconsistencies (`Nemotron-3_5-Lightning` has an underscore; mixed case across IDs).
- Whether `chat_template_kwargs` reasoning controls are honoured (T06 result).
- Sandboxes access process and timing.
- Batch API turnaround.

## 8. "Above and beyond" checklist (bonus points)
- [ ] **Three-plus Nemotron models with measured roles,** with the bake-off table in the README.
- [ ] **Structured outputs, function calling, prefix caching with measured savings, and the Batch API,** each used for a real reason and named in the README.
- [ ] **Sandboxes** if granted (fresh VM per build, branches, `networking=false`, image UUIDs in receipts). If not granted, the designed backend plus a feedback entry.
- [ ] **Tavily changes decisions** (reuse the human patch, backport upstream, upstream PR draft), shown in the video. A $3k prize, stackable.
- [ ] **A real upstream contribution,** with disclosure.
- [ ] **A user signal:** a reply from a maintainer or the RB team, quoted with permission (D-020).
- [ ] **Sealed benchmark,** memorization probe, failure analysis, limitations.
- [ ] **Receipts** in in-toto format (signed if C3 is done).
- [ ] **Tests:** rules, policy, leakguard, scorer, compare. CI on GitHub Actions running `pytest` on pull requests.
- [ ] **Feedback section** that is detailed and specific.
- [ ] **Demo works logged out until Dec 15** with no server.
- [ ] **Keyless replay** works from a fresh clone (D-032).
- [ ] **Blind flagship run** published next to the product run, with the no-tools memory probe (D-031).
- [ ] **Independent builders** (if time): a public GitHub Actions run with A and B on different runners from one env digest (D-033), plus Sandboxes if granted.
- [ ] **README "For judges" table** with every claim linked; the `/judges` page only if ahead (D-036, D-037).
- [ ] **Honest provenance:** the write-up says Debian had labelled the cluster and had a stuck patch, and says exactly what we added.
