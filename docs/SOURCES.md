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

## Rejected alternatives (why not kernel crash fixing)

- syzbot's AI-assisted patch workflow (Google, LPC 2026; 9 patches merged by Aug 2026): https://lpc.events/event/20/contributions/2597/
- kAgent (repairs up to 54.5% of KBenchSyz crashes): https://www.cs.columbia.edu/~junfeng/papers/kagent/

## Background facts used in the pitch (well known; cite if asked)

- SolarWinds (2020): compromised build system injected code into shipped binaries.
- xz-utils backdoor (2024): malicious build code present in release tarballs, not in the git repository.
- EU Cyber Resilience Act: reporting obligations from 11 Sep 2026; full application from 11 Dec 2027.
