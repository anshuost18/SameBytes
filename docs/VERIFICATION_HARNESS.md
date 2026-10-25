# Verification harness ("twinbuild")

> The proof engine. It builds a Debian source package twice, in two independent containers or VMs, with exactly the variations Debian's own CI uses, then compares every `.deb` byte for byte.
> Owner: Person A. Interfaces: `ARCHITECTURE.md` §4–5.

## 1. What "verified reproducible" means (the acceptance rule)

For a package and a patch, verification **passes** only if all of these hold:
1. Build A and build B both exit 0.
2. Both produce the same set of `.deb` filenames.
3. Every `.deb` has the same SHA-256 in A and B.
4. A's file list (`dpkg-deb -c`, names only) equals the **baseline** (unpatched) A's file list for every `.deb`. Nothing was dropped or added.
5. Build A ran with tests enabled (`nocheck` absent; B uses `nocheck`, as Debian CI does) and exited 0. A failing test fails `dpkg-buildpackage`, so exit 0 is the evidence. `tests_ran` in `meta.json` is only a heuristic (`dh_auto_test` appears in every debhelper log even when a package has no tests); the receipt records `tests_enabled` plus the last summary-looking log line (`test_hint`), and the policy guard (P1) is what stops a patch from weakening tests.
6. The patch passed the policy guard (`AGENT_DESIGN.md` §7).

The **baseline** (unpatched) twin build must first show a difference. If it's identical locally, the package is `NOT_REPRODUCED` and we never claim a fix.

## 2. Why we mirror tests.reproducible-builds.org (and not "reprotest +all")

- The packages we fix are flagged by **tests.reproducible-builds.org**. To show we fixed *that* failure, our two builds must vary the same things.
- Its current variation table (`/debian/index_variations.html`, re-checked line by line on 2026-10-25; see `REVIEW_2026-10-25.md` §3):
  - does **not** vary the build path, which is fixed at `/build/reproducible-path/…`;
  - has file-order variation "temporarily not varied" (the build uses tmpfs);
  - **does vary the kernel on amd64** (`6.12.113+deb13-amd64` vs `…+deb13-cloud-amd64`). A Docker container shares the host kernel, so **we cannot reproduce this variation**. It is the one CI variation the default profile misses (see §3.1 and the limitations);
  - runs the second build **398 days plus 6 h 23 min** in the future, and sometimes the *first* build too (today or 2027-11-27).
- So the default profile needs **no FUSE, no disorderfs and no privileged containers**. That removes the biggest Docker and Sandboxes risk from the old plan.
- reprotest's broader variations stay available as an optional `strict` profile (§3.2) and as a diagnostic bisect tool (§12).

## 3. Variation profiles (`harness/profiles.py`)

### 3.1 `debian-ci` (default)

| Item | Build A | Build B | Implementation (Docker) | Implementation (Sandboxes) |
|---|---|---|---|---|
| Hostname | `sb-node-a` | `i-capture-the-hostname` | `--hostname` | `hostname …` as root in the VM (verify) |
| Domain name | `debian.net` | `i-capture-the-domainname` | `--domainname` | `domainname …` (verify) |
| `TZ` | `/usr/share/zoneinfo/Etc/GMT+12` | `/usr/share/zoneinfo/Etc/GMT-14` | env (needs `tzdata`) | same |
| `LANG` | `C.UTF-8` | `et_EE.UTF-8` | env (needs `locales-all`) | same |
| `LANGUAGE` | `en_US:en` | `et_EE:et` | env | same |
| `LC_ALL` | unset | `et_EE.UTF-8` | env | same |
| `PATH` | `/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:` (CI keeps the trailing colon) | `/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/i/capture/the/path` | env | same |
| `CAPTURE_ENVIRONMENT` | unset | `I capture the environment` | env | same |
| User / uid:gid | `pbuilder1` 1111:1111 | `pbuilder2` 2222:2222 | users created in the image; `setpriv` | same |
| `HOME` | `/nonexistent/first-build` | `/nonexistent/second-build` | env; the directory must not exist | same |
| GECOS | `first user,first room,first work-phone,first home-phone,first other` | `second user,…` | `useradd -c` | same |
| Login shell | `/bin/sh` | `/bin/bash` | `useradd -s` | same |
| `/bin/sh` | dash | bash | `ln -sf` in the container before the build | same |
| `DEB_BUILD_OPTIONS` | `parallel=N` | `nocheck parallel=N-1` | env (N = `SB_PARALLEL`, default 4) | same |
| umask | 0022 | 0002 | `umask` in the build shell | same |
| Niceness | 10 | 11 | `nice -n` | same |
| Clock | real time | +398 days +6 h 23 min (34,410,180 s) | `faketime -f "+34410180"` (libfaketime; `SB_TIME_OFFSET` overrides; the doctor check confirms the offset with `faketime -f +34410180 date`, and falls back to `+398d` if the plain-seconds form isn't accepted) | `date -s` as root if allowed, else faketime (verify) |
| UTS namespace | own | own | Docker default | separate VMs |
| Kernel version | host kernel | **CI varies it** (`deb13-amd64` ↔ `deb13-cloud-amd64`) | **cannot be reproduced** in a container. Option `--vary-kernel` uses `setarch --uname-2.6` in B, which only *approximates* "a different `uname -r`". Packages that capture the kernel string are caught by the `KERNEL_STRING` rule from CI evidence, then reported `NOT_REPRODUCED(kernel-only)` locally rather than claimed fixed | a Sandbox VM kernel is still one fixed kernel; not varied |
| Build path | `/build/reproducible-path/<src>-<upstream_ver>` | same | | |
| File ordering | not varied | not varied | | |
| Network | none | none | `--network none` | `networking.enabled=false` |
| `SOURCE_DATE_EPOCH` | not set by us | not set by us | dpkg derives it from `debian/changelog` | same |

### 3.2 `strict` (optional, flagship only, Could C2)
`debian-ci` plus:
- a different build path in B (`/build/other-path/…`);
- disorderfs file-order scrambling (needs `--privileged --device /dev/fuse`);
- `--vary-kernel`.

Implement it by calling reprotest with an explicit variation spec rather than re-implementing disorderfs. A pass earns a "strict-verified" badge on the site.

### 3.3 `none` (sanity check)
B uses A's settings. Both builds must be identical; if not, the package is nondeterministic regardless of environment (randomness or ordering). This runs only when the investigator asks for it.

## 4. Images

### 4.1 Builder image (`docker/Dockerfile`, in this pack)
- Base: `debian:unstable`. After the first pull, pin it with `FROM debian:unstable@sha256:<digest>` for the hackathon week and record the digest.
- Tools: build-essential, devscripts, dpkg-dev, fakeroot, quilt, equivs, faketime, locales-all, tzdata, diffoscope-minimal plus comparators, ripgrep, git, python3, disorderfs and reprotest (strict profile only).
- The users `pbuilder1` and `pbuilder2` are created at image build time (§3.1).
- `/usr/local/bin/sb-build` (§5) is copied in.
- Tag it with a date: `samebytes-builder:2026-10-25`. Record `docker image inspect --format '{{.Id}}'` in every receipt.

### 4.2 Env images (one per package and toolchain override set), made by `prepare_env`
This is the **only** step with network access.
```bash
CACHE=~/.cache/samebytes/src/autoflake_2.4.0-1      # host dir, persistent
mkdir -p "$CACHE"
docker run --name sb-prep-$$ -v "$CACHE":/srcpkg -v "$DEBS":/debs:ro samebytes-builder:2026-10-25 bash -euxc '
  apt-get update
  cd /srcpkg
  [ -d autoflake-2.4.0 ] || apt-get source --only-source "autoflake=2.4.0-1"
  apt-get build-dep -y --no-install-recommends ./autoflake-2.4.0
  if ls /debs/*.deb >/dev/null 2>&1; then apt-get install -y --allow-downgrades /debs/*.deb; fi
  dpkg-query -W -f "\${Package}=\${Version}\n" | sort > /etc/samebytes-env.lst
  apt-get clean'
docker commit sb-prep-$$ sb-env/autoflake:2.4.0-1-<key8>
docker rm sb-prep-$$
```
- `<key8>` is the first 8 hex digits of `sha256(pkg, version, sorted toolchain .deb sha256s)`. It is cached and reused.
- The unpacked source directory name is `<src>-<upstream_version>`. Parse it from `apt-get source` output or find the directory containing `debian/control`.
- **Version mismatch:** if the archive no longer has the exact version (a new upload since the CI run), fail with `VERSION_GONE`. Then either use the current version (and re-fetch its CI evidence) or fetch the old `.dsc` from snapshot.debian.org with `debsnap`/`dget`.
- `sha256(/etc/samebytes-env.lst)` is the **environment fingerprint** in the receipt.

### 4.3 Candidate source trees
- For each verification, the host makes a fresh copy: `runs/<run>/<pkg>/candidates/<id>/src`, which is pristine plus the patch.
- **Package target:** the patch is added as a quilt patch with a DEP-3 header (`debian/patches/samebytes-<slug>.patch` and `series`). For `3.0 (native)` or `1.0`, edits are applied directly.
- **Toolchain target:** the candidate tree is the pristine *dependent* package. The fix arrives through the env image (toolchain `.deb` installed). See §10.
- The tree is mounted **read-only** at `/src` in both containers. `sb-build` copies it into the build path.

## 5. `sb-build` entrypoint (reference implementation, `docker/sb-build`)

```bash
#!/bin/bash
# sb-build ROLE   — one variation build of /src into /out (run as root inside the env image)
set -euo pipefail
ROLE="${1:?usage: sb-build A|B}"
PROFILE="${SB_PROFILE:-debian-ci}"
PKGDIR="${SB_PKGDIR:?set SB_PKGDIR, e.g. autoflake-2.4.0}"
N="${SB_PARALLEL:-4}"
OUT=/out; BP=/build/reproducible-path
mkdir -p "$BP" "$OUT"

A_ENV=(TZ=/usr/share/zoneinfo/Etc/GMT+12 LANG=C.UTF-8 LANGUAGE=en_US:en
       PATH=/usr/sbin:/usr/bin:/sbin:/bin:/usr/games
       HOME=/nonexistent/first-build USER=pbuilder1 LOGNAME=pbuilder1
       DEB_BUILD_OPTIONS="parallel=$N")
B_ENV=(TZ=/usr/share/zoneinfo/Etc/GMT-14 LANG=et_EE.UTF-8 LANGUAGE=et_EE:et LC_ALL=et_EE.UTF-8
       PATH=/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/i/capture/the/path
       "CAPTURE_ENVIRONMENT=I capture the environment"
       HOME=/nonexistent/second-build USER=pbuilder2 LOGNAME=pbuilder2
       DEB_BUILD_OPTIONS="nocheck parallel=$(( N > 1 ? N - 1 : 1 ))"
       FAKETIME_DONT_FAKE_MONOTONIC=1)

if [ "$ROLE" = A ] || [ "$PROFILE" = none ]; then
  ID=1111; NICE=10; UM=0022; SH=dash; ENVV=("${A_ENV[@]}"); TW=()
else
  ID=2222; NICE=11; UM=0002; SH=bash; ENVV=("${B_ENV[@]}"); TW=(faketime -f "+398d")
  [ "${SB_DISABLE_TIME:-0}" = 1 ] && TW=()
  [ "${SB_VARY_KERNEL:-0}" = 1 ] && TW=(setarch x86_64 --uname-2.6 "${TW[@]}")
fi

ln -sf "$SH" /bin/sh
cp -a /src "$BP/$PKGDIR"
chown -R "$ID:$ID" "$BP"

start=$(date +%s)
set +e
setpriv --reuid="$ID" --regid="$ID" --init-groups \
  env -i "${ENVV[@]}" nice -n "$NICE" \
  bash -c 'umask "$0"; cd "$1"; shift 2; exec "$@"' "$UM" "$BP/$PKGDIR" _ \
  "${TW[@]}" dpkg-buildpackage -b --no-sign > "$OUT/build.log" 2>&1
rc=$?
set -e
end=$(date +%s)

cd "$BP"
cp -a ./*.deb ./*.buildinfo ./*.changes "$OUT"/ 2>/dev/null || true
cd "$OUT"
if ls ./*.deb >/dev/null 2>&1; then
  sha256sum ./*.deb | sed 's#  \./#  #' > sha256.txt
  for d in ./*.deb; do dpkg-deb -c "$d" | awk '{print $6}' | sort > "${d#./}.files"; done
fi
tests=$([ "$ROLE" = A ] && grep -q 'dh_auto_test' build.log && echo true || echo false)
printf '{"role":"%s","exit_code":%d,"wall_seconds":%d,"tests_ran":%s}\n' \
  "$ROLE" "$rc" "$((end-start))" "$tests" > meta.json
chown -R "${SB_HOST_UID:-0}:${SB_HOST_UID:-0}" "$OUT"
exit "$rc"
```

Notes:
- `dpkg-buildpackage` running as a normal user uses `fakeroot` automatically. faketime and fakeroot both use `LD_PRELOAD` and coexist, as in reprotest.
- `date` in `start`/`end` runs outside faketime, so the times are real.
- Some packages need a writable `$HOME`. The CI deliberately uses a nonexistent `HOME`, so a build that fails for that reason also fails on Debian CI. That's a real bug, not a harness bug.

## 6. Twin build procedure (Docker backend)

```bash
NONCE=$(python3 -c 'import uuid;print(uuid.uuid4())')
for R in A B; do
  H=$([ $R = A ] && echo "sb-node-a" || echo "i-capture-the-hostname")
  D=$([ $R = A ] && echo "debian.net" || echo "i-capture-the-domainname")
  docker run --rm --network none --hostname "$H" --domainname "$D" \
    --cpus 4 --memory 8g --pids-limit 4096 \
    --label samebytes.nonce="$NONCE" --label samebytes.role="$R" \
    -e SB_PKGDIR=autoflake-2.4.0 -e SB_PARALLEL=4 -e SB_HOST_UID="$(id -u)" \
    -v "$CAND_SRC":/src:ro -v "$OUTDIR/$R":/out \
    sb-env/autoflake:2.4.0-1-<key8> /usr/local/bin/sb-build "$R" &
done
wait
```
- A and B run in parallel when resources allow (`SAMEBYTES_PARALLEL_BUILDS`). Otherwise they run sequentially; the order doesn't matter.
- **If B fails and A passes:**
  - Check B's log tail for faketime symptoms: `Clock skew detected`, hangs, or `configure: error: newly created file is older than distributed files`.
  - If found, rerun B once with `SB_DISABLE_TIME=1`. Record `disabled_variations=["time"]`.
  - The receipt grade becomes `ci-minus-time`. It's still useful, but the site shows the badge honestly.
- **Grades:**
  - `ci-equivalent`: all `debian-ci` variations except kernel (which containers can't vary, §3.1). The site badge text must say "except kernel";
  - `ci-minus-time`;
  - `strict`: all of §3.2 as well.

## 7. Comparison (`harness/compare.py`)
1. Parse `A/sha256.txt` and `B/sha256.txt`. `reproducible = (names equal) and all(sha equal)`.
2. Manifest: compare `A/*.files` against the baseline A's `*.files` and record any difference.
3. On mismatch, run diffoscope **inside the builder image** (offline), on directories containing only the `.deb` files:
   ```bash
   docker run --rm --network none -v "$OUTDIR":/cmp samebytes-builder:2026-10-25 bash -c '
     mkdir -p /tmp/a /tmp/b && cp /cmp/A/*.deb /tmp/a/ && cp /cmp/B/*.deb /tmp/b/
     diffoscope --json /cmp/diffoscope.json --text /cmp/diffoscope.txt \
                --max-report-size 20000000 /tmp/a /tmp/b; true'
   ```
   Host-side timeout is 600 s. diffoscope exits 1 when files differ, which is expected.
4. The diffoscope JSON from our build goes to the same `DiffDigest` parser as CI evidence. The path prefixes differ (`/tmp/a/…` vs `/srv/reproducible-results/…/b1/…`), so the parser strips everything up to the first `.deb`/`.changes` name.

## 8. Receipt (`report/receipt.py`): an in-toto Statement v1

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {"name": "python3-autoflake_2.4.0-1_all.deb", "digest": {"sha256": "<after sha256>"}}
  ],
  "predicateType": "https://github.com/<you>/SameBytes/reproducible-fix/v0.1",
  "predicate": {
    "package": {"source": "autoflake", "version": "2.4.0-1", "suite": "unstable", "arch": "amd64"},
    "ci_evidence": {"status": "FTBR", "diffoscope": "<url>", "fetched_at": "2026-10-26T…Z"},
    "before": {"reproducible": false,
               "a": {"python3-autoflake_2.4.0-1_all.deb": "<sha A>"},
               "b": {"python3-autoflake_2.4.0-1_all.deb": "<sha B>"}},
    "fix": {"target": "toolchain:argparse-manpage", "strategy_class": "root_cause",
            "patch_sha256": "<sha of unified diff>", "files": ["argparse_manpage/compat.py"],
            "toolchain_overrides": [{"package": "python3-argparse-manpage",
                                     "version": "4.7-1.1+samebytes1", "deb_sha256": "<sha>"}]},
    "after": {"reproducible": true, "manifest_equal": true, "tests": "passed",
              "a": {"python3-autoflake_2.4.0-1_all.deb": "<sha>"},
              "b": {"python3-autoflake_2.4.0-1_all.deb": "<same sha>"}},
    "environment": {"backend": "docker", "builder_image": "sha256:…", "env_image": "sha256:…",
                    "env_fingerprint": "sha256 of /etc/samebytes-env.lst",
                    "host": {"kernel": "…", "cpus": 4}},
    "variations": {"profile": "debian-ci", "grade": "ci-equivalent", "disabled": ["kernel"],
                   "a": {"TZ": "Etc/GMT+12", "LANG": "C.UTF-8", "uid": 1111, "umask": "0022", "…": "…"},
                   "b": {"TZ": "Etc/GMT-14", "LANG": "et_EE.UTF-8", "uid": 2222, "umask": "0002", "clock": "+398d", "…": "…"}},
    "operations": [{"role": "after.A", "id": "<container id | sandbox op id>", "nonce": "…",
                    "started": "…", "wall_seconds": 212}],
    "agent": {"git_commit": "…", "mode": "product", "prompt_hashes": {"investigate_system.md": "…"},
              "models": [{"stage": "investigate", "model": "nvidia/Nemotron-3-Ultra-550b-a55b",
                          "prompt_tokens": 0, "cached_tokens": 0, "completion_tokens": 0, "usd": 0.0}],
              "total_usd": 0.0, "wall_seconds": 0},
    "review": {"status": "pending", "reviewer": null, "notes": null}
  }
}
```
- **Optional (Could C3):** sign the receipt in GitHub Actions with Sigstore keyless signing (`cosign sign-blob --bundle receipt.sigstore.json receipt.json`) when the site is published. The site links the bundle.

## 9. Day-0 manual recipe (tasks T03–T04): copy and paste in WSL
```bash
cd ~/src/SameBytes
docker build -t samebytes-builder:2026-10-25 -f docker/Dockerfile docker/
mkdir -p ~/sbtmp && cd ~/sbtmp

# 1) prepare env (network on)
docker run --name prep-af -v "$PWD/src":/srcpkg samebytes-builder:2026-10-25 bash -euxc '
  apt-get update && cd /srcpkg && apt-get source --only-source autoflake=2.4.0-1 &&
  apt-get build-dep -y --no-install-recommends ./autoflake-2.4.0'
docker commit prep-af sb-env/autoflake:manual && docker rm prep-af

# 2) baseline twin build (network off)
for R in A B; do
  H=$([ $R = A ] && echo sb-node-a || echo i-capture-the-hostname)
  docker run --rm --network none --hostname $H -e SB_PKGDIR=autoflake-2.4.0 -e SB_HOST_UID=$(id -u) \
    -v "$PWD/src/autoflake-2.4.0":/src:ro -v "$PWD/out-base/$R":/out \
    sb-env/autoflake:manual /usr/local/bin/sb-build $R
done
cat out-base/A/sha256.txt out-base/B/sha256.txt          # EXPECT: different hashes

# 3) manual toolchain fix (FLAGSHIP_CASE.md §5.3), new env image
docker run --name fix-af sb-env/autoflake:manual python3 -c "
import pathlib; p=pathlib.Path('/usr/lib/python3/dist-packages/argparse_manpage/compat.py'); s=p.read_text()
s=s.replace('import datetime.timezone\n    _TZ_ARGS = [datetime.timezone.utc]','from datetime import timezone\n    _TZ_ARGS = [timezone.utc]'); p.write_text(s)"
docker commit fix-af sb-env/autoflake:manual-fixed && docker rm fix-af

# 4) twin build again
for R in A B; do
  H=$([ $R = A ] && echo sb-node-a || echo i-capture-the-hostname)
  docker run --rm --network none --hostname $H -e SB_PKGDIR=autoflake-2.4.0 -e SB_HOST_UID=$(id -u) \
    -v "$PWD/src/autoflake-2.4.0":/src:ro -v "$PWD/out-fix/$R":/out \
    sb-env/autoflake:manual-fixed /usr/local/bin/sb-build $R
done
cat out-fix/A/sha256.txt out-fix/B/sha256.txt            # EXPECT: identical hashes
```
- If the Python path differs (for example `/usr/lib/python3/dist-packages/argparse_manpage/` doesn't exist), find it with `docker run --rm sb-env/autoflake:manual python3 -c 'import argparse_manpage,sys;print(argparse_manpage.__file__)'`.
- The source directory may be named differently; `ls src/` after step 1.

## 10. Toolchain injection (campaigns)

There are **two injection modes**. The receipt records which one was used (`toolchain_overrides[].kind = "overlay" | "deb"`).

- **`overlay` (default fast path, interpreted toolchains only: Python, Perl, shell, R, Lua, …).** `prepare_env(toolchain_overlays=[PatchSet])` applies the patch's edits *directly to the installed files* in the env image (for argparse-manpage, `/usr/lib/python3/dist-packages/argparse_manpage/compat.py`, which maps 1:1 to `argparse_manpage/compat.py` in the upstream tree). The receipt stores the SHA-256 of every file before and after, and the unified diff. This is exactly the Day-0 manual recipe (T04), so it is proven to work, needs no rebuild, and **cannot be broken by an unrelated Python 3.15 build failure of the toolchain package** (`RISKS_AND_BLOCKERS.md` R21/R24). Use it for the whole campaign.
  - **Bytecode caches:** Debian byte-compiles Python modules at install time (`py3compile` in the package's postinst), so `__pycache__/compat.cpython-3*.pyc` already exists next to the file. Normal timestamp-based `.pyc` files are re-validated against the source's mtime and size, but hash-based "unchecked" `.pyc` files are not. The overlay step therefore **deletes the `__pycache__` entries of every overlaid module** and records that in the receipt. Python then compiles in memory (the build user can't write there), which is slower by milliseconds and always uses the edited source.
  - **Sanity check after applying:** `python3 -c 'import argparse_manpage.compat as c; print(c._TZ_ARGS)'` must print a non-empty list in the env image; the receipt stores the output.
- **`deb` (the "proper artifact" path).** Build a patched toolchain `.deb` as below. Required when the toolchain is compiled (C, C++, Go, Rust…), and a nice-to-have for the flagship because a `.deb` is what Debian would actually ship. If the `.deb` build fails (R21), the campaign **does not wait**: it proceeds with `overlay`, and the `.deb` is reported separately as "toolchain package build: failed on Python 3.15 for an unrelated reason, backport attached".

Whichever mode is used, the verified result is the same claim: *with this change to this tool, every dependent builds byte-identically*.

### 10.1 Building the patched `.deb` (mode `deb`)
1. **Build the patched toolchain package once:**
   - `prepare_env(argparse-manpage 4.7-1.1)`;
   - copy the source;
   - apply the patch;
   - single build as A (tests on).
   - Output: `python3-argparse-manpage_4.7-1.1+samebytes1_all.deb`.
   - Set the local version with `dch --local +samebytes --distribution UNRELEASED "SameBytes local test build"` *inside the build copy only*. Don't include this change in the proposed patch.
2. **For each dependent:** `prepare_env(dep, toolchain_debs=[that .deb])` installs build-deps from the archive, then our `.deb` over the archive's 4.7-1 (`--allow-downgrades` isn't needed, since our version sorts higher).
3. **Twin build** each dependent with its *pristine* source. The receipt lists the override.
4. **Control:** also twin build one dependent *without* the override in the same session, to show the before state is still broken.

## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| Baseline A and B identical (no difference reproduced) | Check that B really got the variations: `docker run … sb-env/x bash -c 'env; id; umask; readlink /bin/sh'` with B's settings. Check that `tzdata` and `locales-all` are installed (`locale -a \| grep et_EE`). If all is correct, the CI failure may involve the kernel (try `SB_VARY_KERNEL=1`) or randomness: run `none` twice. |
| `et_EE.UTF-8: cannot change locale` warnings | `locales-all` is missing from the image |
| `TZ` ignored | `tzdata` is missing, so `/usr/share/zoneinfo/Etc/GMT+12` doesn't exist |
| B hangs | faketime and the monotonic clock. `FAKETIME_DONT_FAKE_MONOTONIC=1` is already set in B's environment; if it still hangs, use `SB_DISABLE_TIME=1` (recorded in the grade) |
| `dpkg-buildpackage: error: fakeroot not found` | Install `fakeroot` in the builder image |
| `Permission denied` writing to `/out` | Make `$OUTDIR` writable by Docker's root; `SB_HOST_UID` restores ownership afterwards |
| Very slow builds | The repo or `~/sbtmp` is on `/mnt/c`. Move it to the WSL ext4 home. Raise `.wslconfig` memory and processors. |
| `apt-get source` fails | `deb-src` isn't enabled. The Dockerfile enables it in `/etc/apt/sources.list.d/debian.sources`. |
| Out of disk | `docker system df`; `docker image prune`; `samebytes gc --older-than 2d` |

## 12. reprotest as a diagnostic (optional `samebytes bisect`)
When the investigator can't tell *which* variation matters, reprotest's `--auto-build` mode builds once per variation and reports which ones cause differences. It costs many builds (about one per variation), so use it only on fast packages and in the background.
```bash
docker run --rm --privileged --device /dev/fuse -v "$PWD/src/<dir>":/work samebytes-builder:2026-10-25 bash -c '
  cd /work && reprotest --auto-build --vary=-build_path,-fileordering,-domain_host \
     --store-dir /work/../reprotest-out . -- null'
```
Check the exact flags against `reprotest --help` in the image during Day 1. Its exit codes aren't documented: parse the summary text, not the exit code.

## 13. Sandboxes backend (`harness/sandbox_backend.py`), build it once access is granted

The design is identical to Docker's; only the transport differs.
- **Builder image:** push the same image to a public registry (`ghcr.io/<you>/samebytes-builder:2026-10-25`), then import it with `sdk.images.oci("docker://ghcr.io/<you>/samebytes-builder:2026-10-25")`. That guarantees the same toolchain in both backends.
- **`prepare_env`:** `img.run(shell="<prepare script>", disposable=False, tag=f"sb-env-{pkg}-{key8}")` with networking enabled. Keep `result_image_uuid` as `EnvImage.ref`.
- **`twinbuild`:**
  - two operations from the env image UUID, networking disabled;
  - command: `: sb-nonce=<uuid4>; SB_PKGDIR=… /usr/local/bin/sb-build A; cat /out/sha256.txt /out/meta.json; tail -c 200000 /out/build.log`.
  - The nonce is required: the SDK documents that the same command on the same image returns the same result UUID, which suggests results may be reused. A unique nonce forces a fresh build, and we record distinct operation IDs.
  - The candidate source tree is uploaded with the run's `files=` parameter, as a tarball unpacked to `/src`.
- **Proof needs only small outputs:** hashes, file lists and `meta.json` are under 1 MiB on stdout. For diffoscope on a mismatch, download both `.deb` sets (if the SDK supports downloading files from a result image), or rebuild the mismatching pair in Docker locally for diagnostics.
- **Branching for patch candidates:** all candidates start from the same env image UUID. With 2 candidates that's 4 concurrent operations; a campaign of 11 members is 22 concurrent operations, under the beta limit of 50. Show "22 fresh VMs in parallel" in the video.
- **Day-1 probe operation, once access is granted (answers Q-003):**
  `id; uname -a; nproc; free -m; hostname; date; ls -l /dev/fuse; ls /sys/class/net; cat /etc/os-release; timeout 5 date -s '+398 days' && date`
- **Verify:**
  - the SDK parameter name for networking (`networking.enabled=false` in REST);
  - the operation timeout (from `GET /v1/whoami`);
  - whether `SUCCESS` with a nonzero exit code is reported as `exit_code`. Treat `timed_out` as a failure.
- **Receipts:** `backend="sandbox"`, `env_image` is the image UUID, and `operations[].id` holds the Sandbox operation IDs.

## 14. GitHub Actions as a second, independent builder (D-033)

The Docker backend runs unchanged on a GitHub-hosted Linux runner (amd64, Docker preinstalled, free for public repositories). This gives us three things the laptop can't:

1. **Truly separate machines.** Build A runs in one job and build B in another (`sb-build A` and `sb-build B` are already separate role invocations), on different runners. The comparison job downloads the two `sha256.txt` files and compares them. That is the original "two independent machines" claim, with public logs anyone can open. Say it precisely: *same environment image (by digest), two separate hosts*. Same inputs on different machines is exactly what a reproducibility check needs.
2. **Parallelism and insurance.** The 14-member campaign becomes a matrix of jobs (about 10 minutes wall-clock instead of 1–1.5 hours on the laptop), and a slow or broken laptop (R4) no longer stops the Must items.
3. **The reproducibility *guard* made concrete (C4).** The same workflow is the "mini GitHub Action" from the product story.

**Scope (D-037):** flagship pair first (autoflake, baseline and overlay), then the other fast members if time allows. Build it only after the laptop campaign (T22) is green; budget 3–4 hours.

Shape of `.github/workflows/verify.yml` (Person A):
```yaml
on:
  workflow_dispatch:
    inputs:
      packages: {description: "space-separated source=version", required: true}
      patch:    {description: "path to patchset JSON (toolchain overlay)", required: false}
permissions: {contents: read}        # least privilege; only `env` gets packages: write
jobs:
  env:       # ONE job per package: prepare_env (network on: apt-get source + build-dep, overlay applied),
             # docker push ghcr.io/<owner>/samebytes-env:<pkg>-<run_id>; output: the image DIGEST.
    permissions: {contents: read, packages: write}
  build:
    needs: env
    permissions: {contents: read, packages: read}
    strategy:
      fail-fast: false
      matrix:
        pkg: ${{ fromJson(needs.env.outputs.pkgs) }}
        role: [A, B]
    runs-on: ubuntu-24.04
    steps:     # checkout; docker pull ghcr.io/…@sha256:<digest from env>   (by digest, never by tag);
               # samebytes ci-build --env-image <digest> --role ${{ matrix.role }}   (sb-build only, --network none);
               # upload-artifact: sha256.txt, meta.json, build.log, env digest
  compare:   # needs: build; downloads both roles per package; asserts A and B report the SAME env digest;
             # writes the receipt JSON; uploads it; fails the job if any hash differs
```
- **A and B must build in the same environment image, pulled by digest.** If each role job ran its own `prepare_env`, the two jobs could resolve build-dependencies against different archive states (unstable changes several times a day and the CDN backends can lag each other). A version difference in any build-dep would then show up as a fake "unreproducible" result, or hide a real one. The `env` job is the only one with network access; `compare` refuses to write a receipt if the two digests differ.
- **Workflow hygiene:** pass `workflow_dispatch` inputs to scripts through `env:` variables, never by `${{ inputs.* }}` inside `run:` (shell injection); pin third-party actions to a commit SHA; no repository secrets are referenced anywhere in this workflow.
- Builds still run with `--network none`. Only `prepare_env` (in the `env` job) has network (to `apt-get build-dep`), exactly as locally.
- No Nebius or Tavily secrets are needed or passed to these jobs. LLM calls stay on the laptop; the runners only verify.
- The receipt's `environment.backend` becomes `"github-actions"` with the run URL and job IDs in `operations[]`, and the site links the public run.
- **Limits to check on first use:** the 6-hour job limit (irrelevant), the free-runner disk (about 14 GB free: `prepare_env` for large build-dep sets can overflow; skip those packages), and artifact retention (90 days by default, so copy the receipts into `published/`).
