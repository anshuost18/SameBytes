# Original idea (as first written, ~22 Oct 2026)

> Kept for reference. Several points were corrected or upgraded after research. See `DECISIONS.md`, especially:
> - D-003: Sandboxes instead of GitHub Actions;
> - D-008: no mass filing;
> - D-009 and D-017: sealed benchmark;
> - D-013: positioning.
>
> The timeline below has been replaced by the one in `PROJECT_BRIEF.md`.

---

Hackathon idea: an AI agent that makes software builds reproducible, and proves it (Nebius × NVIDIA hackathon, deadline Oct 30, 10:00am PDT = 10:30pm IST, about 8 days)

## The problem

If you build the same source code twice, you'd expect the exact same output file. Usually you don't get it. Small things leak into the binary:

- the current date and time;
- the folder it was built in;
- the username;
- the order files are listed;
- language settings, CPU count, random hash ordering.

Why it matters: if builds are bit-for-bit reproducible, anyone can rebuild a released binary from source and check it matches. That's how you catch tampering. In the 2024 xz backdoor, the release files didn't match the public source; rebuilding releases from source is meant to catch exactly that. If builds aren't reproducible, every rebuild differs anyway, so the check is useless.

How big it is:

- Debian: about 1,100 non-reproducible packages today, 622 with no known cause. Debian's release team is moving to require reproducible builds starting in 2026.
- Arch Linux: about 11% non-reproducible. Nix: 69–91% reproducible.
- Fixing it is skilled manual work: Debian's notes list 431 distinct root-cause types across about 6,400 package issues, maintained by a handful of volunteers.
- Regulation: the EU Cyber Resilience Act's reporting duties started in Sept 2026, with full enforcement in Dec 2027. Supply-chain teams are adopting "build twice independently and compare" as an integrity check.

What exists: reprotest (builds twice with variations, finds which variation causes the difference) and diffoscope (shows exactly where two outputs differ). Both detect; neither fixes. There's no product or published AI agent that diagnoses and repairs these end to end with proof.

## The solution

An agent that takes a non-reproducible package and:

1. **Reproduces it:** builds twice with reprotest, varying time, path, user, locale, file order and CPU count, and finds which variation causes the difference.
2. **Condenses the evidence:** diffoscope output can be megabytes. Nemotron Nano shrinks it to the few differences that matter, e.g. "a build path is inside the debug info" or "a timestamp is in a gzip header."
3. **Diagnoses:** Nemotron Ultra combines the diff, the build log and Debian's 431-type cause catalogue to name the root cause and the responsible file.
4. **Fixes:** Nemotron Super writes the patch. Typical fixes:
   - use the standard fixed build timestamp (SOURCE_DATE_EPOCH);
   - strip build paths from debug info;
   - sort file lists;
   - stop gzip storing a timestamp (gzip -n);
   - fix hash seeds.
5. **Proves it:** rebuilds under every variation. Success means the output hashes are byte-for-byte identical and the package's tests still pass. If it fails, the remaining diff loops back to step 3, up to 3 tries.
6. **Ships:** a report, a ready-to-file Debian bug or upstream patch, and a CI check against regressions.

**Campaign mode:** run across hundreds of packages, with Nano triaging all the diffs through Token Factory's batch API. Rebuilds run in parallel on free GitHub Actions runners.

**Built-in benchmark:** about 6,400 Debian issues already have known causes. Hide the answer, run the agent, measure accuracy. Then attack the 622 unexplained packages, where every success is new, verified work.

## Why it can win

- The proof is undeniable: two hashes become identical.
- Measurable, real-world impact: accuracy on known cases, plus verified fixes for packages nobody had explained, filed as real bug reports.
- A security story judges get instantly: xz and supply-chain integrity.
- Real systems depth: compilers, linkers, ELF/debug info, archive formats, filesystem ordering, environment leaks.
- Each Nemotron model has a distinct job, plus batch-API campaigns.
- Runs on any laptop: Linux, Windows with WSL2, or a cloud VM, with Docker. No GPU, no special hardware. Costs nothing beyond the free $25 Token Factory credit.
- Track: Coding & Agentic Engineering.

## Drawbacks

- **Moderate business:** Linux distributions don't pay. The buyers would be companies shipping containers or binaries under the CRA or government rules, security-sensitive software, and hardened-image vendors. Bigger than a niche, smaller than GPU tools.
- **Unexplained cases are hard,** so the success rate there may be modest. The known-cause benchmark carries the demo.
- **Some packages build slowly.** Pick short ones.
- **About a day of learning:** Debian packaging basics and reading diffoscope output.
- **Setup detail:** the file-order variation needs FUSE (a Linux filesystem feature), so the Docker container must run `--privileged`.

## Plan (about 70 hours)

| Day | Plan |
|---|---|
| Oct 22–23 | Docker test environment, a test runner (reprotest plus diffoscope), and the package list split into known-cause and unknown-cause |
| Oct 24–25 | The Nano diff condenser, Ultra diagnosis, Super patching, and the verification loop |
| Oct 26 | End-to-end on 10 known-cause packages; measure accuracy; report web page |
| Oct 27 | Campaign on 30–50 packages; write up the best new fixes |
| Oct 28 | Feature freeze, README, record the demo |
| Oct 29 | Video and submit. Oct 30 is buffer only |
