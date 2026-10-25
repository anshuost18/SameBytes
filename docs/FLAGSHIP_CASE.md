# Flagship case: one silent bug, 13 unreproducible Debian packages

> Every fact here was verified live on 2026-10-25, with the source of each check listed. Re-verify §2 on Thu 29 Oct before recording the video; humans could fix it any day (`RISKS_AND_BLOCKERS.md` R11).
> **Benchmark note:** the team now knows this answer, so this case is a **demo and dev case**. It must never be in the sealed test set (`BENCHMARK_PROTOCOL.md` L8).

## 1. The story in four sentences

1. Thirteen Debian packages fail Debian's reproducibility test only because the date printed in their man pages differs between the two builds.
2. They all generate man pages with the same tool, **argparse-manpage**. Its code tries `import datetime.timezone`, which *always* raises ImportError (`datetime` is a module, not a package). The tool then silently formats `SOURCE_DATE_EPOCH` in **local time**, and Debian's two builds run in timezones 26 hours apart (GMT+12 and GMT-14).
3. Debian's fix (4.7-1.1, January 2026) is stuck because that version fails to build on Python 3.15 for an unrelated reason. Unstable still ships the buggy 4.7-1, and upstream's latest release (v4.8, Oct 14 2026) still has the broken import.
4. SameBytes traces the dates to the tool, fixes the tool once, and proves all affected packages reproducible. It also attaches a 14th package that regressed on Oct 23 and that nobody has connected yet.

### 1.1 What is new and what Debian already knew (verified 2026-10-25, read this before pitching)
- **Debian already knows the symptom.** `reproducible-notes` tags **all 13 members** with `timezone_variant_in_argparse_manpage` ("argparse manpage >= 4.7 will use SOURCE_DATE_EPOCH but will vary on the timezone", bug #1126092). Only `hatchling` is untagged. Debian also has a patch (NMU 4.7-1.1).
- **What nobody had done:**
  - pinned the exact line (`import datetime.timezone` always fails, so `_TZ_ARGS` is always empty) and shown by experiment that this is the *mechanism*;
  - noticed that the Debian patch (`utcfromtimestamp`) is deprecated and that 4.7-1.1 **cannot build on Python 3.15**, so the fix never shipped (unstable binaries are still 4.7-1);
  - proved that fixing the tool makes **every** dependent byte-identical in Debian CI's own variations;
  - connected the 14th package, `hatchling` (regressed 2026-10-23, untagged);
  - sent upstream a correct fix with a regression test (checked 2026-10-25: upstream has **no** open issue or PR about this; issue #26 and PRs #48 and #76 are the old closed "reproducible man page" work, and PR #119 introduced the regression).
- **Pitch wording that stays true:** "Debian's volunteers had *labelled* this cluster but not *fixed* it. SameBytes found the exact line, proved the fix across all 13 dependents, and caught a 14th." Never say "nobody knew" or "no one had explained it".
- **Because the label is in the catalogue, the headline run is blind** (`AGENT_DESIGN.md` §3.1.1, D-031): the catalogue entry is removed and the agent still has to find the cause by experiment.

## 2. Verified evidence (with how it was checked)

### 2.1 The symptom (autoflake 2.4.0-1, unstable/amd64)
From `https://tests.reproducible-builds.org/debian/dbdjson/unstable/amd64/autoflake_2.4.0-1.diffoscope.json.gz`:
```
python3-autoflake_2.4.0-1_all.deb ▸ data.tar.xz ▸ ./usr/share/man/man1/autoflake.1.gz ▸ autoflake.1
-.TH AUTOFLAKE "1" "2026\-08\-24" ...
+.TH AUTOFLAKE "1" "2026\-08\-25" ...
```
The rest of the diff (md5sums, `.changes` Files line, sizes) is derived from this one line.

### 2.2 The root cause (upstream `praiskup/argparse-manpage`, `argparse_manpage/compat.py`, main @ v4.8)
```python
import datetime
try:
    import datetime.timezone          # always ImportError: 'datetime' is not a package
    _TZ_ARGS = [datetime.timezone.utc]
except ImportError:
    _TZ_ARGS = []                     # always taken
...
def get_reproducible_date():
    return datetime.datetime.fromtimestamp(
        int(os.environ.get('SOURCE_DATE_EPOCH', time.time())),
        *_TZ_ARGS).strftime('%Y-%m-%d')   # local time → TZ-dependent date
```
Reproduced locally:
- `import datetime.timezone` raises `ImportError: No module named 'datetime.timezone'; 'datetime' is not a package`.
- With the same epoch, `TZ=Etc/GMT+12` prints `2025-08-24` and `TZ=Etc/GMT-14` prints `2025-08-25`.

The regression came in with upstream PR #119, "Fix deprecation warnings for datetime and setuptools" (Aug 2025), which swapped `utcfromtimestamp` for `fromtimestamp(..., *_TZ_ARGS)`.

### 2.3 Why Debian's fix never reached users
- **Bug report:** Debian bug **#1126092** "argparse-manpage: please make the output reproducible", reported by Chris Lamb on 2026-01-21, tagged `patch`.
  - It is marked "Fixed in 4.7-1.1" (an NMU by Vagrant Cascadian).
  - The patch (`debian/patches/0001-argparse_manpage-compat.py-Use-utcfromtimestamp-for-.patch`) switches back to `utcfromtimestamp`. That works, but it's deprecated since Python 3.12, and it only works because `_TZ_ARGS` is always empty.
- **The 4.7-1.1 build fails on unstable.** tests.reproducible-builds.org history shows FTBFS twice on 2026-10-24. The build log (`/debian/rbuild/unstable/amd64/argparse-manpage_4.7-1.1.rbuild.log.gz`) shows:
  ```
  AttributeError: '_ManpageFormatter' object has no attribute '_cached_theme'. ...
  E: pybuild pybuild:485: build: plugin distutils failed with: exit code=1: /usr/bin/python3.15 setup.py build
  ```
  Python 3.15's argparse expects `HelpFormatter.__init__` to have run. argparse-manpage 4.7's formatter skipped it. Upstream fixed this in commits `05f8260` and `412123f` (2026-05-27), released in v4.8.
- **Migration is blocked.** The tracker excuses for 4.7-1 → 4.7-1.1 say "Missing build on all", and the reproducibility check is deferred because builds are missing.
- **What users actually get:** unstable's binary is `python3-argparse-manpage 4.7-1`, which still has the bug (checked against `dists/unstable/main/binary-all/Packages.xz`).

### 2.4 Cluster members (all build-depend on argparse-manpage; checked against `Sources.xz` and each `debian/control`)

| Package | Version (unstable) | Status | CI build time (both builds) | Note version |
|---|---|---|---|---|
| autoflake | 2.4.0-1 | FTBR | 1m58s | 2.3.1-2 (stale) |
| psutils | 3.3.14-1 | FTBR | 2m15s | current |
| svtplay-dl | 4.97.1-0.1 | FTBR | 2m26s | current |
| osc | 1.15.1-1 | FTBR | 2m27s | current |
| virtme-ng | 1.41-1 | FTBR | 2m31s | 1.40-1 (stale) |
| autotiling | 1.9.3-2 | FTBR | 3m24s | 1.9.3-1 (stale) |
| python-stone | 3.5.5-1 | FTBR | 3m36s | current |
| python-pipx | 1.15.0-1 | FTBR | 3m37s | 1.8.0-1 (stale) |
| cmake-format | 0.6.13-7 | FTBR | 3m48s | current |
| power-profiles-daemon | 0.30-2 | FTBR | 4m24s | current |
| telegram-send | 0.39.2-1 | FTBR | 4m27s | current |
| openqa | 5.1790164836.5c04ab047-1 | FTBR | 8m00s | stale |
| python-salib | 1.6.0-1 | FTBR | 17m09s | 1.5.2-2 (stale) |
| **hatchling** | 1.32.4-1 | FTBR, **no note** | ≈25m | — |

- **hatchling:**
  - Its man page header is `.TH HATCHLING "1" "2026\-10\-22"` versus `"2026\-10\-24"`.
  - Version 1.30.1-2 was reproducible on 2026-10-22; 1.32.4-1 regressed on 2026-10-23.
  - It isn't tagged in reproducible-notes; finding it is new work.
- **Raw evidence for all 14 members is committed** in `tests/fixtures/evidence/` (see its `MANIFEST.md`): every file shows the same single `.TH` date leaf. Three pairs are **2 days apart** (osc, autotiling, hatchling), so detectors must allow a 2-day gap. `psutils` and `cmake-format` carry extra derived `file list` leaves, which makes them the best tests for derivative filtering.
- **Controls, which must stay reproducible:**
  - `crazy-complete` (build-depends on argparse-manpage, currently reproducible; find out why, as it is a good agent question);
  - `389-ds-base` (FTBR for a different reason, `usr_lib_debug_dotdwz_dir_inherits_build_user`; it's not in this cluster).
- **In total, 20 source packages build-depend on argparse-manpage:** 15 FTBR, 3 reproducible, 2 FTBFS.

## 3. Why this is the right flagship
- **Aha in one screen:** two hashes differ, the agent's one-line explanation appears, then 13 hashes match.
- **Non-obvious root cause.** A human looking at the diff sees "dates differ" and would likely add `export TZ=UTC` to each package's `debian/rules`: 13 workarounds. The real cause is a silent ImportError in a different package. The agent finds it by *running code* (`probe`) and *attributing files to packages* (`which_package`).
- **Real impact:**
  - It unblocks a stuck Debian fix.
  - It gives upstream a correct 2-line patch.
  - It shows the "regressions keep coming" point with hatchling.
- **Tavily has real work to do (S3).** It finds bug #1126092, upstream PR #119, the v4.8 status, and the Python 3.15 incompatibility fix commits. That changes the agent's plan: backport, don't reinvent.
- **Builds are fast.** Most members take 2–4 minutes on CI.

## 4. Expected agent trajectory (use as the end-to-end acceptance test)
1. **Intake:** autoflake 2.4.0-1, FTBR, CI build time 1m58s, so within the time limit.
2. **Evidence and digest:** one meaningful leaf (`autoflake.1`, the `.TH` line); everything else is derived.
3. **Rules:**
   - The −/+ lines contain roff-escaped dates (`2026\-08\-24`) one day apart (up to two days for some members), both within ±2 days of the `SOURCE_DATE_EPOCH` date.
   - Signal `TZ_SHIFTED_SDE_DATE` (varying factor `timezone`, confidence 0.9). In a **product run** the catalogue hints include `timezone_variant_in_argparse_manpage` (it exists and names the tool, see §1.1). In the **blind run** that entry is redacted and the nearest remaining hints are generic timezone/manpage labels (`manpages_generated_by_node_marked_man_vary_on_build_timezone`, `timezones_manpages_podman`), which point at the wrong tools. The agent must not trust them. Never write a catalogue name in a test unless it exists in `issues.yml`.
4. **Investigator (Ultra):**
   - `grep_build_log("autoflake.1")` finds the man page generated during `setup.py build`, by argparse-manpage's `build_manpages` command or the `argparse-manpage` CLI, depending on the package.
   - `search_source("manpage")` finds `pyproject.toml`/`setup.cfg` config for `build_manpages`, with no date logic in the package itself.
   - `which_package("argparse_manpage")` resolves `/usr/lib/python3/dist-packages/argparse_manpage/` to `python3-argparse-manpage 4.7-1`, a toolchain package.
   - `read_file("sys:/usr/lib/python3/dist-packages/argparse_manpage/compat.py")` shows `get_reproducible_date()` and `_TZ_ARGS`.
   - `probe("python3 -c 'from argparse_manpage.compat import get_reproducible_date as g; print(g())'")` prints different dates under A and B. Hypothesis confirmed.
   - `probe("python3 -c 'import argparse_manpage.compat as c; print(c._TZ_ARGS)'")` prints `[]` in both, which shows the timezone import never succeeds.
   - `submit_diagnosis`:
     - `responsible.kind=toolchain`, `package=argparse-manpage`, `file=argparse_manpage/compat.py`, `symbol=get_reproducible_date`, `varying_factor=timezone`;
     - causal chain: TZ → `fromtimestamp` local time → `.TH` date;
     - `fix_strategy=toolchain_fix`.
5. **Scout (Tavily, product mode):** Debian #1126092 (patch, fixed in 4.7-1.1); tracker shows "Missing build on all"; upstream main still has the import; upstream PR #119 introduced it.
   - **Plan change:** fix both the timezone bug and the Python 3.15 incompatibility in the toolchain package (backport `05f8260`/`412123f`), and draft an upstream PR for the import bug.
6. **Patcher (Super), target `toolchain:argparse-manpage`:**
   - Candidate 1, the root-cause fix: `from datetime import timezone` plus `_TZ_ARGS = [timezone.utc]`.
   - Candidate 2, a minimal fix: `fromtimestamp(epoch, tz=datetime.timezone.utc)` directly.
   - Both also carry the Python 3.15 backport so the toolchain package can build.
7. **Verify:**
   - **Overlay first (default, D-034):** apply the two-line edit to the installed `compat.py` in autoflake's env image, twin-build. Hashes identical, file list unchanged, tests pass, so the result is **reproducible**. This is the Day-0 recipe in code and does not depend on the toolchain package building.
   - **Then the proper artifact:** build the patched `python3-argparse-manpage` `.deb` (it needs the Python 3.15 backport to build at all) and repeat. If that build fails, report it and keep the overlay result; the claim "fixing the tool fixes the dependents" already stands.
8. **Campaign:** repeat step 7 for every cluster member. The diagnosis isn't re-run: the cluster signature matches, so the verified fix is reused as a rule (D-027, RELAY-style).
9. **Outputs:** receipts, the upstream PR draft, the Debian bug follow-up draft, and the site cards.

## 5. The fix

### 5.1 Upstream patch (for `praiskup/argparse-manpage` main)
```diff
--- a/argparse_manpage/compat.py
+++ b/argparse_manpage/compat.py
@@
 import datetime
 try:
-    import datetime.timezone
-    _TZ_ARGS = [datetime.timezone.utc]
+    from datetime import timezone
+    _TZ_ARGS = [timezone.utc]
 except ImportError:
     _TZ_ARGS = []
```
Add a regression test to `tests/`:
- set `SOURCE_DATE_EPOCH=1756080000`, which is 2025-08-25 00:00 UTC;
- for `TZ` in `Etc/GMT+12` and `Etc/GMT-14`, call `time.tzset()` and assert `get_reproducible_date() == "2025-08-25"`.

The test fails on current main and passes after the fix. Verify the epoch-to-date mapping in the test before committing.

### 5.2 Debian toolchain patch (the proper `.deb`; the campaign itself uses the overlay, D-034)
Start from source `argparse-manpage 4.7-1.1`.
- Replace `debian/patches/0001-…utcfromtimestamp….patch` with the §5.1 fix, which removes the deprecated call.
- Add a backport of upstream `05f8260` and `412123f`: the formatter calls `super().__init__(prog)`, so Python 3.15's argparse attributes exist.
- Version it locally as `4.7-1.1+samebytes1`. This is never uploaded; it exists only to prove the dependents.

### 5.3 Manual reproduction for Day 0 (task T04)
Inside autoflake's env image, before building:
```bash
python3 - <<'EOF'
import pathlib, re
p = pathlib.Path('/usr/lib/python3/dist-packages/argparse_manpage/compat.py')
s = p.read_text()
s = s.replace("import datetime.timezone\n    _TZ_ARGS = [datetime.timezone.utc]",
              "from datetime import timezone\n    _TZ_ARGS = [timezone.utc]")
p.write_text(s)
EOF
python3 -c 'import argparse_manpage.compat as c; print(c._TZ_ARGS)'   # expect [datetime.timezone.utc]
```
Then run the twin build. Expect identical SHA-256 for `python3-autoflake_2.4.0-1_all.deb`. For the real run, inject a properly built `.deb` (§5.2), not an in-place edit; the receipt records the override.

## 6. What could make this case weaker, and the answer
- **"Debian's notes already tag all of these."** True (§1.1). Tags are labels, not fixes: the tag text doesn't say which line is wrong, Debian's patch never shipped, and nobody had verified the dependents. We run the agent with the label removed to show it doesn't need it.
- **"Debian already had a fix."** True, and we say so. The agent *finds* it via Tavily, credits it, and explains why it never shipped. Our contribution is the correct upstream fix, the unblocked Debian package, and proof across all dependents.
- **"Someone fixes it before the 30th."** It's still a fully validated, end-to-end case on the published evidence. Say "as of Oct 25". Keep the receipts dated.
- **"The agent only matched a known pattern."** The benchmark (Track A on the sealed post-cutoff set) answers the "does it generalize" question; the flagship answers "does it go end-to-end".

## 7. Contribution drafts (your approval is required before sending; see working agreement 7)
- **Upstream:** a PR to `praiskup/argparse-manpage` titled "compat: fix timezone import so SOURCE_DATE_EPOCH dates are UTC".
  - Body: root cause, a 2-line reproduction, a link to Debian #1126092, the list of affected Debian packages, and the test.
  - Footer: "Assisted-by: SameBytes (NVIDIA Nemotron via Nebius Token Factory); reviewed and tested by <your name>."
- **Debian:** a follow-up on #1126092 explaining that 4.7-1.1 fails to build on Python 3.15 (`_cached_theme`), plus the backport and the import fix, and the hatchling regression. CC `reproducible-builds@lists.alioth.debian.org`. Same disclosure line.
- **Timing:** send by Wed 28 morning IST so a reply can land before the video. Quote replies only with permission.
