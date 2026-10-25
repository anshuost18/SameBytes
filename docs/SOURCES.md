# Sources (for README, Devpost write-up and video claims)

> Researched 2026-10-24. Re-check live numbers (dashboards) right before submission and quote them with a date.

## Hackathon

- Overview, tracks, judging criteria, prizes: https://nebiusglobalaihackathon.devpost.com
- Official rules covering Stage 1 pass/fail, equal weighting, tie-break order, the "runtime call" definition, prizes and multiple-prize rules, and judging dates (1–15 Dec): https://nebiusglobalaihackathon.devpost.com/rules
- FAQ, including that other providers don't count: https://nebiusglobalaihackathon.devpost.com/details/faqs
- Judges' advice (scored 1–5; "push past the obvious"): https://nebiusglobalaihackathon.devpost.com/updates/46204-here-s-how-judging-works
- "Will It Ship?" takeaways (aha in 30 s, one thing done well, show which model does what, publish limitations): https://nebiusglobalaihackathon.devpost.com/updates/47163-recording-will-your-project-ship
- Submission tips (name the tools aloud, hide keys, video as pitch): https://nebiusglobalaihackathon.devpost.com/updates/46205-how-to-build-a-winning-project
- India RuPay activation issue (forum): https://nebiusglobalaihackathon.devpost.com/forum_topics/45627-token-factory-needs-a-visa-mastercard-participants-in-india-with-only-rupay-cards-can-t-activate

## Nebius

- Token Factory docs index (including Sandboxes): https://docs.tokenfactory.nebius.com/llms.txt
- Sandboxes overview (beta, fresh VM per operation, image UUIDs): https://docs.tokenfactory.nebius.com/sandboxes/overview.md
- Sandboxes limits (50 concurrent, output caps, networking off option): https://docs.tokenfactory.nebius.com/sandboxes/operate/limits-retention-and-usage.md
- Sandboxes for SWE agents (branching): https://docs.tokenfactory.nebius.com/sandboxes/swe-agents.md
- Fine-tunable models (no Nemotron): https://docs.tokenfactory.nebius.com/post-training/models.md
- Model prices snapshot: https://benchlm.ai/hosts/nebius
- Nebius to acquire Tavily (Feb 2026): https://nebius.com/newsroom/nebius-announces-agreement-to-acquire-tavily-to-add-agentic-search-to-its-ai-cloud-platform

## Debian / Reproducible Builds

- Debian release team: "Debian must ship reproducible packages"; migration blocking since May 2026:
  - https://reproducible-builds.org/reports/2026-05/
  - https://www.phoronix.com/news/Debian-Must-Ship-Reproducible
- Holger Levsen's MiniDebConf Hamburg talk (9 May 2026): reproduce.debian.net, forky amd64 at 97.2% good / 512 bad, 4,347 reproducibility bugs fixed and 262 patches pending, and reproduce.debian.net vs. tests.reproducible-builds.org: https://reproducible-builds.org/_lfs/presentations/2026-05-09-Reproducing-Debian-in-the-real-world/
- Live dashboard (24 Oct 2026: unstable/amd64 has 1,148 unreproducible, 619 unreproducible with no notes, 9 notes.git committers in 3 months): https://tests.reproducible-builds.org/debian/reproducible.html
- July 2026 report (human fix throughput; PyPI study at 15.4% / 19.1% byte-identical; F-Droid study): https://reproducible-builds.org/reports/2026-07/
- PyPI paper "No Snake Oil: Verifying Python Package Builds": https://arxiv.org/pdf/2607.21888

## Debian AI policy

- GR 2026-002 "LLM usage in Debian", ballot: https://www.debian.org/vote/2026/vote_002
- Result, choice 5 "Responsible Use of Generative AI": https://lwn.net/Articles/1091231/
- Disclosure encouraged but not required: https://www.helpnetsecurity.com/2026/08/31/debian-linux-llm-policy/
- Community split of about 64/36: https://www.linuxcompatible.org/story/debian-developers-vote-to-allow-llmassisted-contributions-under-responsible-use-framework

## Prior work (baselines and related)

- RepFix, "Automated Patching for Unreproducible Builds", ICSE 2022 (64/116 fixed): https://conf.researchr.org/details/icse-2022/icse-2022-papers/66/Automated-Patching-for-Unreproducible-Builds
- RepLoc, "Automated Localization for Unreproducible Builds", ICSE 2018 (671 packages): https://arxiv.org/abs/1803.06766

## Added 2026-10-25 (build-plan research)

### Flagship evidence
- **Debian side:**
  - Bug #1126092 (argparse-manpage reproducibility, patch, NMU 4.7-1.1): https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1126092
  - Tracker (4.7-1.1 blocked: "Missing build on all"): https://tracker.debian.org/pkg/argparse-manpage
  - 4.7-1.1 FTBFS log (Python 3.15 `_cached_theme`): https://tests.reproducible-builds.org/debian/rbuild/unstable/amd64/argparse-manpage_4.7-1.1.rbuild.log.gz
  - autoflake diff: https://tests.reproducible-builds.org/debian/dbdtxt/unstable/amd64/autoflake_2.4.0-1.diffoscope.txt.gz
  - hatchling diff: https://tests.reproducible-builds.org/debian/dbdtxt/unstable/amd64/hatchling_1.32.4-1.diffoscope.txt.gz
- **Upstream:**
  - `compat.py` (broken import): https://github.com/praiskup/argparse-manpage/blob/main/argparse_manpage/compat.py
  - Compare v4.7…main (`05f8260`, `412123f` super-init fix; v4.8 release): https://github.com/praiskup/argparse-manpage/compare/v4.7...main
  - PR #119 (introduced `fromtimestamp` + `_TZ_ARGS`): https://github.com/praiskup/argparse-manpage/pull/119
- **Debian CI variations table:** https://tests.reproducible-builds.org/debian/index_variations.html

### Data
- Status JSON: https://tests.reproducible-builds.org/debian/reproducible.json
- Notes repo: https://salsa.debian.org/reproducible-builds/reproducible-notes
- reprotest man page (0.7.33): https://manpages.debian.org/unstable/reprotest/reprotest.1.en.html

### Prior art and competitors (see `LANDSCAPE.md`)
- **Google OSS Rebuild** (stabilizers, AI agent, SLSA): https://github.com/google/oss-rebuild
- **RepTrace** (ASE 2019): search "RepTrace unreproducible builds ASE 2019"
- **EvidenT** (ISSTA 2026): system-level package build repair (RISC-V), 53.88%
- **RELAY:** arXiv 2610.27784 (LLM-derived deterministic rules, then agent escalation)
- **dettrace:** https://github.com/dettrace/dettrace
- **in-toto Statement v1:** https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md

### Nebius / NVIDIA / Tavily
- Token Factory model catalog with prices (cached input column): Token Factory console → Models
- Nemotron 3.5 Super technical report (2026-10-21): from the NVIDIA Nemotron model card page
- NeMo Agent Toolkit deprecation notice (Oct 2026): NVIDIA NeMo docs
- Tavily API reference (search, extract): https://docs.tavily.com

## Rejected alternatives (why not kernel crash fixing)

- syzbot's AI-assisted patch workflow (Google, LPC 2026; 9 patches merged by Aug 2026): https://lpc.events/event/20/contributions/2597/
- kAgent (repairs up to 54.5% of KBenchSyz crashes): https://www.cs.columbia.edu/~junfeng/papers/kagent/

## Background facts used in the pitch (well known; cite if asked)

- SolarWinds (2020): compromised build system injected code into shipped binaries.
- xz-utils backdoor (2024): malicious build code present in release tarballs, not in the git repository.
- EU Cyber Resilience Act: reporting obligations from 11 Sep 2026; full application from 11 Dec 2027.
