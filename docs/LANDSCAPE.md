# Landscape: who else works on reproducible builds, and where SameBytes fits

> Researched 2026-10-24/25. Use this for the "Quality of Idea" argument, the README "Related work" section, and judge Q&A. Claims about others are kept conservative. If unsure, say "as far as we found".

## 1. The workflow and who covers each step

| Step | What it means | Existing tools | SameBytes |
|---|---|---|---|
| **Detect** | Is the build reproducible? | tests.reproducible-builds.org (Debian variation CI), reproduce.debian.net / rebuilderd (real-archive rebuilds), reprotest, NixOS r13y, Guix `challenge`, Arch rebuilderd, Reproducible Central (Maven), F-Droid verification | **Consumes** their results |
| **Explain** | *Where* do the outputs differ? | diffoscope | **Consumes** it |
| **Diagnose** | *Why*, and what produces the bytes? | Human experts (about 9 active note-writers per 3 months); research: RepLoc, RepTrace | **Core:** Nemotron investigator with experiments (`probe`) and toolchain attribution |
| **Fix** | Change the source so the output is deterministic | Humans; research: RepFix (non-LLM); generic coding agents | **Core:** patcher with a policy guard |
| **Prove** | Show the fix works | Humans rerun CI and wait days | **Core:** twin build with byte-identical SHA-256 and a receipt |
| **Normalize instead** | Scrub differences after the build | strip-nondeterminism (in debhelper), Fedora add-determinism, OSS Rebuild "stabilizers" | Last resort only, labelled `normalization` |

## 2. Closest competitor: Google OSS Rebuild
- **What it does:**
  - Rebuilds open-source packages (npm, PyPI, crates.io, Debian, …) from source and checks them against the published artifacts.
  - Publishes SLSA provenance attestations.
  - Build definitions are inferred per ecosystem (strategy types include `debian_package` and `debrebuild`).
- **How it handles differences:** **stabilizers**, pure functions that normalize timestamps, file order and archive metadata. Equivalence is defined as `stabilize(rebuild) == stabilize(upstream)`.
- **Its AI agent** helps *infer build definitions* when a rebuild fails. It has tools like `read_repo_file`, `list_repo_files` and `read_logs_end`, and its tooling can "generate stabilizers from a diff".
- **Difference:**
  - OSS Rebuild asks "is the published artifact *equivalent* to source, after normalization?"
  - SameBytes asks "*why* do bytes differ, and how do we *change the source* so they don't?", then proves it **bit-for-bit with no normalization**.
  - They're complementary: OSS Rebuild verifies supply chains; SameBytes removes the nondeterminism so verification no longer needs stabilizers.
- **What we borrow:** small, read-only investigation tools (log tail, file read, list) and an attestation format (we use in-toto Statements).

## 3. Debian's own infrastructure
- **tests.reproducible-builds.org:**
  - builds every package twice with deliberate variations (`VERIFICATION_HARNESS.md` §3);
  - publishes diffoscope output, logs and notes;
  - it is our evidence source and our acceptance definition.
- **reproduce.debian.net (rebuilderd):**
  - rebuilds the *actual archive binaries* from `.buildinfo` (debrebuild → debootsnap/mmdebstrap/sbuild) and compares them to what Debian shipped;
  - since May 2026, unreproducible packages and regressions are blocked from migrating to testing, and tracker excuses show "Reproducibility check".
  - It's the next target after the hackathon (D-012).
- **reprotest:** the standard twin-build tool with many variations and `--auto-build` bisection. We use it for the strict profile and diagnostics, not as the core harness, because Debian CI's exact variation set is easier to mirror directly.
- **strip-nondeterminism / dh_strip_nondeterminism:** normalizes known formats (zip, jar, gzip, png, …) inside debhelper. It's legitimate Debian practice; our policy treats new normalization as a lower class than a root-cause fix.
- **disorderfs, faketime, dettrace:**
  - disorderfs and faketime are environment perturbation tools;
  - dettrace is a container that makes builds deterministic by intercepting syscalls, and it now supports PGO and Lisp dumps. It's an alternative philosophy: make the *environment* deterministic rather than the *package*.

## 4. Research prior art

| Work | Year / venue | What | Result | Relation |
|---|---|---|---|---|
| RepLoc | ICSE 2018 | Localize the files responsible, using heuristics (14 rules) and IR over diff, log and source | 47.09% top-1, 79.28% top-10 (671 Debian packages) | Our rules engine plays a similar "hint" role; we localize to file and symbol and confirm with probes |
| RepTrace | ASE 2019 | Syscall tracing for causality | ~90% top-10 | Our `probe` is a lightweight, targeted alternative |
| RepFix | ICSE 2022 | Tracing plus history-based patch retrieval | 64/116 fixed | Closest "auto-fix" baseline (not LLM) |
| EvidenT | ISSTA 2026 | Evidence-preserving agent for system-level package build *failures* (RISC-V) | 53.88% vs 20.55% for agentic baselines vs 1.83% for direct LLM; 72% of fixes are build-config, dependency or environment changes | We adopt evidence preservation across rounds (remaining-diff feedback) |
| Build-bench | 2025–26 | Architecture-migration build repair (OBS) | — | Shows agentic build repair is an active area; not reproducibility |
| RELAY | arXiv 2610.27784 | LLM-derived deterministic rules reused first; unresolved cases go to an agent | — | Our "verified fix becomes a rule" campaign design (`AGENT_DESIGN.md` §10.3) |
| SANER 2026 (dependency build repair agent) | 2026 | Agent repairs dependency-caused build breaks | — | Adjacent |
| "No Snake Oil" (PyPI reproducibility) | arXiv 2607.21888 | Only 15.4–19.1% of PyPI rebuilds byte-identical | — | Market-size evidence for "next ecosystem" |

**As far as we found (Oct 25 searches), there is no LLM agent that diagnoses *and fixes* reproducibility bugs and proves the fix with independent builds.** Say "as far as we found" in the write-up.

## 5. Generic AI coding agents (SWE-agent, OpenHands, Copilot coding agent, Cursor/Claude Code)
- They can edit code, but they have no domain tools (diffoscope digests, variation-aware probes, toolchain attribution) and no built-in proof.
- Judges' "push past the obvious" maps here. The obvious hackathon build is "LLM reads a diff and suggests a patch". Our non-obvious parts:
  1. the agent runs controlled experiments under Debian's exact variation environments;
  2. it attributes causes across package boundaries and fixes the toolchain once for N packages;
  3. it proves the result bit-for-bit, with receipts;
  4. it is measured on a sealed, contamination-aware benchmark.

## 6. Positioning lines (for the video and write-up)
- "Detection is solved. Debian already tells you *that* a build isn't reproducible. SameBytes tells you *why*, fixes it, and proves it."
- "Other tools scrub the differences away. We remove the cause, so the bytes are identical without any scrubbing."
- "One bug in one shared tool broke 13 packages. Fixing it once and proving all 13 is the kind of leverage a small volunteer team needs."
