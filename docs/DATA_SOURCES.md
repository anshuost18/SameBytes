# Data sources

> Every external input SameBytes uses: exact URL patterns, formats, parsing notes and gotchas. URLs marked ✓ were fetched successfully on 2026-10-25.
> Cache everything under `~/.cache/samebytes/` with the URL as key and the ETag/Last-Modified stored, so reruns don't hammer Debian's servers.

## 1. Package status: `reproducible.json` ✓
- URL: `https://tests.reproducible-builds.org/debian/reproducible.json` (≈105 MB, one array).
- Row: `{"package": "autoflake", "version": "2.4.0-1", "suite": "unstable", "architecture": "amd64", "status": "FTBR", "build_date": "2026-10-09 08:50"}`. There are 475,259 rows across suites and architectures.
- Status values: `reproducible`, `FTBR` (unreproducible), `FTBFS`, `timeout`, `depwait`, `E404`, `NFU`, `blacklisted`.
- unstable/amd64 on Oct 25: reproducible 39,326; FTBR 1,140; FTBFS 746; timeout 130; depwait 74; E404 69; NFU 53; blacklisted 30.
- Download once a day at most. Parse it with `json.load` (it fits in memory; about 1.5 GB peak in Python, so consider `ijson` if WSL memory is tight).

## 2. Per-package build history (build durations) ✓
- URL: `https://tests.reproducible-builds.org/debian/history/amd64/<pkg>.html`
- Table columns: build date, version, suite, architecture, status, **build duration** (both builds combined, e.g. `1m 58s`), node1, node2, job.
- Parse by stripping tags and normalizing whitespace, then match rows:
  ```python
  import re, html
  t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(page)))
  rows = re.findall(r"(\d{4}-\d\d-\d\d \d\d:\d\d(?::\d\d)?) (\S+) (unstable|forky|trixie|experimental) amd64 "
                    r"(\w+) ((?:\d+h )?(?:\d+m )?\d+s) (\S+) (\S+)", t)
  # → (date, version, suite, status, duration, node1, node2)
  ```
- Use the newest `unstable` row for `ci_build_seconds`. Intake skips packages slower than `SAMEBYTES_MAX_CI_BUILD_S` (default 600 s).

## 3. Per-package evidence (unstable/amd64) ✓
`<ver>` is the version **without epoch** (`1:2.3-1` → `2.3-1`).

| Artifact | URL pattern |
|---|---|
| diffoscope JSON (preferred) | `https://tests.reproducible-builds.org/debian/dbdjson/unstable/amd64/<pkg>_<ver>.diffoscope.json.gz` |
| diffoscope text | `…/debian/dbdtxt/unstable/amd64/<pkg>_<ver>.diffoscope.txt.gz` |
| Build 1 log | `…/debian/rbuild/unstable/amd64/<pkg>_<ver>.rbuild.log.gz` |
| Build 2 log | `…/debian/logs/unstable/amd64/<pkg>_<ver>.build2.log.gz` |
| Diff of the two logs | `…/debian/logdiffs/unstable/amd64/<pkg>_<ver>.diff.gz` |
| buildinfo | `…/debian/buildinfo/unstable/amd64/<pkg>_<ver>_amd64.buildinfo` (for arch:all-only packages the suffix is still `_amd64`) |
| Package page (**contains notes, never feed it to the agent**) | `…/debian/rb-pkg/unstable/amd64/<pkg>.html` |
| Notes page (**never feed to agent**) | `…/debian/notes/<pkg>_note.html` |
| Issue page | `…/debian/issues/unstable/<issue>_issue.html` |
| Variation table | `…/debian/index_variations.html` |

- **Sizes:** diffoscope JSON is mostly 2–30 KB, but the tail is huge (largest seen: 1.37 GB, `infernal`).
  - Rule: stream-download with a size cap of 20 MB (`httpx.stream`, abort past the cap).
  - If capped, fetch the text version with the same cap and keep the first 2 MB.
  - Mark `Evidence.truncated=true`.
- **diffoscope JSON shape:**
  ```json
  {"diffoscope-json-version": 1,
   "source1": "/srv/reproducible-results/rbuild-debian/r-b-build.X/b1/autoflake_2.4.0-1_amd64.changes",
   "source2": "…/b2/autoflake_2.4.0-1_amd64.changes",
   "unified_diff": null,
   "details": [ {"source1": "Files", "source2": "Files", "unified_diff": "@@ … @@\n- …\n+ …\n"},
                {"source1": "python3-autoflake_2.4.0-1_all.deb", "source2": "…", "details": [ … recursive … ]} ],
   "comments": ["optional notes, e.g. 'Files similar despite different names'"]}
  ```
  A **leaf** is any node whose `unified_diff` is non-null. Its path is the chain of `source1` values from the root, with the CI prefix stripped up to the first `.changes` or `.deb` name.
- **Text fallback format (checked 2026-10-25):** `dbdtxt` is a box-drawing tree, not a unified diff: lines look like `│ │ │ │ │ -.TH AUTOFLAKE "1" "2026\-08\-24" …` under `├── ./usr/share/man/man1/autoflake.1.gz`. It needs its own small parser (strip the `[│├└─ ]*` prefix; a leaf is a run of `@@` hunks under a `├──` path). Real JSON samples for all 14 flagship members are in `tests/fixtures/evidence/`; write the parser against them first.
- **SOURCE_DATE_EPOCH:** in the buildinfo, look at the `Environment:` field for `SOURCE_DATE_EPOCH="…"`. Fallback: `dpkg-parsechangelog -l debian/changelog -STimestamp` in the env image.

## 4. Issue catalogue and notes (reproducible-notes) ✓
- Clone: `git clone https://salsa.debian.org/reproducible-builds/reproducible-notes.git`. Record the commit SHA in the run manifest.
- `issues.yml` (441 entries): `name: {description: str, url?: str, deterministic: bool}`. The agent gets this with leaks stripped (`AGENT_DESIGN.md` §3.1). It renders to about 23K tokens.
- `packages.yml` (7,694 entries): `pkg: {version: str, issues: [names], bugs?: [ints], comments?: str}`.
  - **This is the answer key.** Only `src/samebytes/bench/` may read it, and a test enforces this.
- **Tag history** (how the post-cutoff set was built):
  ```bash
  cd reproducible-notes
  C=$(git rev-list -1 --before="2025-10-01" HEAD); git show "$C:packages.yml" > /tmp/packages_2025-10-01.yml
  # compare with current packages.yml: tags present now but absent then = added after the cutoff
  ```
- **The notes tag all 13 flagship packages** with `timezone_variant_in_argparse_manpage` and not `hatchling` (verified 2026-10-25 for the review; this is answer-key knowledge, so only `bench/` may read it, and the flagship is excluded from sealed sets).
- Facts from Oct 25:
  - 574 FTBR packages have issue-tagged notes, of which only 40 match the current version; 429 FTBR packages have no notes at all.
  - Since 2025-10-01: 136 FTBR packages got new tags (92 of them `haskell_abi_hash_differences`), and 168 packages had notes removed (likely fixed).

## 5. Debian archive metadata ✓
- **Sources** (reverse build-deps, versions): `https://deb.debian.org/debian/dists/unstable/main/source/Sources.xz` (≈12 MB). Parse stanzas split by blank lines; join `Build-Depends`, `Build-Depends-Indep` and `Build-Depends-Arch` including continuation lines.
- **Binary packages:**
  - `…/dists/unstable/main/binary-all/Packages.xz` and `…/binary-amd64/Packages.xz`;
  - these show which binary version users actually get (e.g. `python3-argparse-manpage 4.7-1`).
- **sources.debian.org:**
  - versions: `https://sources.debian.org/api/src/<pkg>/` → `{"versions":[{"version","suites"}]}`;
  - raw files: `https://sources.debian.org/data/main/<prefix>/<pkg>/<ver>/<path>`, where `<prefix>` is the first letter, or the first 4 letters for `lib*` packages;
  - **product mode only.** In benchmark mode the agent reads source only from its env image.
- **Tracker:**
  - `https://tracker.debian.org/pkg/<pkg>` (HTML) shows the versions per suite and the migration excuses (e.g. "Missing build on all");
  - product mode only.
- **BTS:**
  - `https://bugs.debian.org/cgi-bin/pkgreport.cgi?src=<pkg>;archive=both` (HTML list);
  - a single bug at `https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=<n>`; plain-text mbox via `;mbox=yes`.
  - Product mode only.
- **snapshot.debian.org machine-readable API** (old versions):
  - `https://snapshot.debian.org/mr/package/<src>/` lists versions;
  - `…/mr/package/<src>/<ver>/srcfiles?fileinfo=1` gives file hashes and names;
  - download from `https://snapshot.debian.org/file/<sha1>`;
  - or use `debsnap <src> <ver>` from devscripts. It is slow, so cache aggressively. Needed only if `VERSION_GONE` (`VERIFICATION_HARNESS.md` §4.2).

## 6. Upstream (product mode only)
- Tavily search and extract (`AGENT_DESIGN.md` §8).
- GitHub REST API without a token is limited to 60 requests per hour (fine for a few lookups):
  - `https://api.github.com/repos/<o>/<r>/compare/<a>...<b>`;
  - `…/search/issues?q=repo:<o>/<r>+<terms>`;
  - raw files: `https://raw.githubusercontent.com/<o>/<r>/<ref>/<path>`.

## 7. Candidate lists (verified Oct 25; regenerate with `samebytes bench build` on Day 3)

### 7.1 Flagship cluster
See `FLAGSHIP_CASE.md` §2.4 (13 tagged FTBR members plus `hatchling`).

### 7.2 Track B candidates (fast, diverse, outside the flagship cluster)
These need a local baseline twin build first (T13). Keep the ones that reproduce.

| Package | Version at selection | CI time | Known tag (notes) | Why include |
|---|---|---|---|---|
| frozenlist | (current) | 3m01 | Cython temp-dir path | Path capture through a code generator |
| python-tld | (current) | 3m02 | **no notes** | Unexplained, so new work |
| samhain | (current) | 3m18 | **no notes** | Unexplained, C/autotools |
| node-uplot | (current) | 3m32 | **no notes** | Unexplained, JS |
| r-cran-laplacesdemon | (current) | 3m45 | `randomness_in_r_rdb_rds_databases` | R toolchain cluster (31 packages); likely hard |
| python-webvtt | (current) | 4m24 | **no notes** | Unexplained |
| mdbtools | (current) | 4m37 | libtool-related | autotools |
| painintheapt | (current) | 4m41 | org-mode timestamps | Doc generator dates |
| python-trx-python | (current) | 5m03 | **no notes** | Unexplained |
| fortran-shlex | (current) | 5m30 | (check notes) | Fortran |
| python-gfloat | (current) | 5m48 | `sphinx_reading_durations` | Sphinx cluster (7 packages), a second campaign candidate |
| node-webpack-stats-plugin | (current) | ≈6m | pkgjs lock-file issue | JS toolchain |
| pyuvm | (current) | 6m13 | (check notes) | Python |

Write the final list to `bench/trackB_candidates.txt`, one `source=version` per line. **Exclude** every Track B package from Track A's sealed test set: the team will look at their results.

### 7.3 Selection script outline (`bench/dataset.py`)
1. Load `reproducible.json` and keep `suite == unstable and architecture == amd64 and status == FTBR`.
2. For each package, get the CI build time (history page, cached) and the diffoscope JSON size (HTTP HEAD `Content-Length`).
3. Join with notes. The scorer side may read `packages.yml`; the agent side must not.
4. Write candidate tables as CSV under `bench/candidates/` (no answers in these files: package, version, CI time, diff size only).
