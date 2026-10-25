# Hackathon rules and submission checklist

> Nebius × NVIDIA Global AI Hackathon, Devpost: https://nebiusglobalaihackathon.devpost.com
> Track: **Coding and Agentic Engineering**
> Deadline: **Fri 30 Oct 2026, 10:00 PDT = 22:30 IST.** Judging runs 1–15 Dec 2026; winners are announced around 11 Jan 2027.

## Hard requirements (Stage 1 is pass/fail)

- [ ] The project makes a **runtime call to the Token Factory API** (or runs on Nebius AI Cloud compute). Calling the same models through other providers (HuggingFace, OpenRouter) does **not** count.
- [ ] It uses **at least one NVIDIA open model** (Nemotron).
- [ ] It's a genuine attempt at the track's goal ("agents that write, run, and test code"), not a rebrand.
- [ ] It's a working project that runs as shown in the video.

## Submission items

- [ ] Track selected: Coding and Agentic Engineering
- [ ] Project description: what, why, how
- [ ] Working demo URL / hosted app / test build, **kept reachable until 15 Dec**
- [ ] Public YouTube video **under 3 minutes**, with no copyrighted music
- [ ] Public GitHub repo with an **OSI license visible in the About section** (MIT or Apache-2.0)
- [ ] README containing:
  - [ ] setup and run instructions
  - [ ] how Nemotron is used (which model does what)
  - [ ] where Token Factory helped (inference + Sandboxes)
  - [ ] other Nebius tools used, plus Tavily
  - [ ] limitations
- [ ] **Feedback section** (required) on Token Factory, Sandboxes and each Nemotron model. Cover:
  - what we used each for
  - what worked
  - what didn't
  - onboarding experience (zero to hello world)
  - whether we'd use it again, and why

  Be specific. Ten $100 "Most Valuable Feedback" awards are given.
- [ ] "Built With" tags include Nebius Token Factory, the Nemotron models actually used (Ultra, Super / 3.5 Super, Lightning / Nano), Tavily, and Sandboxes if used
- [ ] No API keys in the repo (`.env` is gitignored; check git history)
- [ ] **Team members:** both people are added to the Devpost project as members (not just the submitter), and each has accepted the rules on `/rules`. Re-read the eligibility section once (age, residency, employer or sponsor restrictions) before submitting. *(added by the 2026-10-25 review)*
- [ ] **Evidence for Stage 1 is one click away:** the README "For judges" block (and the `/judges` page, if built) shows the Token Factory call counts, the models used, and the `samebytes replay` command, worded as a replay of a recorded run.
- [ ] The video shows the **blind** flagship run, or says in one sentence that Debian's own label was removed. The "we hid the label and it still found it" line is used **only** if the blind runs actually succeeded, with the real count.

## Judging (Stage 2): four equally weighted criteria, each scored 1–5

| Criterion | What it means | How we hit it |
|---|---|---|
| **Technological Implementation** (also the **tie-breaker**) | Build quality; effective use of Token Factory and Nemotron | Sandboxes as the proof engine; 3 models with distinct, measured roles; branches; receipts |
| **Design** | A complete, coherent product, not just a proof of concept | Report site: package card, before/after hashes, cause, patch, models, cost; clean CLI |
| **Potential Impact** | A credible, specific case for a real audience, shown working | Debian's blocking policy, volunteer shortage, CRA; benchmark numbers; real fixes |
| **Quality of the Idea** | Creative, non-obvious; real understanding of the problem | Fix + proof (not detection); contamination-aware benchmark; clustering; human-in-loop stance |

## What the judges said they want ("Will It Ship?" session)

- Solve a real problem for a real audience; talk to a few potential users. Consider asking on `#reproducible-builds` (OFTC IRC) or rb-general.
- The **aha moment within 30 seconds** of the video.
- One thing done well beats a big stack. Every integration must support the main story.
- Put the action first and **show which model is doing what**.
- **Publish limitations.** Judges read them as rigor.
- Budget extra time for packaging (write-up and video).
- Say Token Factory and Nemotron **out loud** in the video.
- Name the project like a human.

## Prizes we can win

- **Overall:** $20k / $10k / $6k, **or** the track winner prize (Jetson Orin Nano).
- **Plus one bonus:** Best Use of Tavily ($3k; requires a runtime Tavily call). Stackable with a track award.
- Most Valuable Feedback ($100 + swag).
- City awards are **not available** for India.

## Video plan (under 3:00)

> **Superseded by the second-by-second script in `DEMO_AND_SUBMISSION.md` §2** (built around the flagship case). The table below is the original outline.

| Time | Content |
|---|---|
| 0:00–0:30 | **Aha:** two builds of a package show different SHA-256 hashes. The agent runs and the hashes match. One line: "SameBytes makes builds reproducible and proves it." |
| 0:30–1:00 | Problem and audience: tampering checks need reproducible builds; Debian blocks unreproducible packages; few volunteers; CRA |
| 1:00–2:00 | How it works, live: evidence, Nano condenses, Ultra diagnoses, Tavily checks upstream, Super writes 3 patches, sandbox branches, receipt. Name each model and Token Factory aloud |
| 2:00–2:30 | Results: benchmark table, fixes on unexplained packages, cost per fix, a cluster example |
| 2:30–3:00 | Limitations, human review, and the bigger picture: a reproducibility guard for any team |

## Final-day checks

- [ ] Submit a **draft early** (Thu 29)
- [ ] Video is public, under 3:00, and the link works logged-out
- [ ] Repo is public, license shows in About, README renders
- [ ] Demo URL works logged-out
- [ ] Credit reserve left for judging (1–15 Dec)
- [ ] Final submit **before 22:30 IST, Fri 30 Oct**
