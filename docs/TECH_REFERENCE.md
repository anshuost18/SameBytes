# Technical reference

> Collected during research on 2026-10-24. Items marked **(verify)** came from third-party pages or memory. Confirm them against the live service before relying on them.

## Nebius Token Factory: inference

- Docs index (machine-readable list of every page): https://docs.tokenfactory.nebius.com/llms.txt
- API style: **OpenAI-compatible.** Use the `openai` Python SDK with a custom `base_url`.
- Base URL as shown in the docs:
  - `https://api.tokenfactory.nebius.com/v1/`
  - Nebius' Nemotron page also shows the regional `https://api.tokenfactory.us-central1.nebius.com/v1/`
  - Confirmed 2026-10-25: our account works with the first (global) URL.
- Fast flavor: append `-fast` to a model name for lower latency (pricing differs) **(verify per model)**.
- Features listed in the docs:
  - function calling / tools;
  - structured output / JSON;
  - batch inference;
  - context caching;
  - observability;
  - prompt presets.
- Confirmed 2026-10-25 on Nano, Super and Ultra: JSON mode (`response_format={"type": "json_object"}`), function calling, and automatic prefix caching (4,224 of 4,520 prompt tokens cached on the second identical call). Batch inference untested.
- Reasoning models return thinking in a separate `reasoning` field and the answer in `content` (which may start with a newline: strip it). With a low `max_tokens`, `content` is `None` because thinking uses the budget. Use `max_tokens` of 1500 or more.
- Caching is prefix-based: put the static system prompt and catalogue first, and per-package evidence last.
- **Fine-tuning:** no Nemotron models on the fine-tune list, so not used (D-006).

### Nemotron models (IDs confirmed on the live model list 2026-10-25; prices from benchlm.ai, check the console)

| Role | Model ID | $ per 1M input / output | Context |
|---|---|---|---|
| Condense, signatures | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | $0.06 / $0.24 | 262K |
| Patch writing | `nvidia/nemotron-3-super-120b-a12b` | $0.30 / $0.90 | 262K listed (model card says up to 1M) |
| Diagnosis | `nvidia/Nemotron-3-Ultra-550b-a55b` | $1.00 / $3.00 | ~1.05M |
| (not planned) | `nvidia/Nemotron-3.5-Super-VL` | $0.30 / $0.90 | ~1.05M |
| (not planned) | `nvidia/Nemotron-3-Nano-Omni` | $0.06 / $0.24 | 64K |

### Minimal call

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ["NEBIUS_API_KEY"],
)
r = client.chat.completions.create(
    model="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
    messages=[{"role": "user", "content": "hello"}],
)
print(r.choices[0].message.content, r.usage)
```

## Nebius Token Factory: Sandboxes (beta, product name "Contree")

- Overview: https://docs.tokenfactory.nebius.com/sandboxes/overview.md
- Request access: https://tokenfactory.nebius.com/sandboxes/about
- Feedback contact: contree@nebius.com, or the Nebius Discord Sandboxes channel
- Interfaces:
  - Python SDK (`contree-sdk`);
  - REST API;
  - CLI;
  - MCP server.
- REST base: `https://api.tokenfactory.nebius.com/sandboxes`
  - Headers: `Authorization: Bearer $NEBIUS_API_KEY` and `Project: $NEBIUS_PROJECT_ID`
  - Check limits: `GET /v1/whoami`
  - Inspect a run: `GET /v1/operations/{id}`
- Concepts:
  - **Operation:** fresh VM, one command, returns output.
  - **Image:** immutable filesystem state, identified by UUID.
  - **Tag:** mutable name pointing to an image.
  - **Branching:** start several runs from one image.
  - You choose save or discard *before* each run.
- **Limits (beta):**
  - 50 simultaneous operations;
  - stdout/stderr capped at 1 MiB per stream by default (10 MiB max), so write big logs to files and download them;
  - images retained for 180 days;
  - execution timeout per account (check `whoami`);
  - networking on by default; `networking.enabled=false` starts the VM with no network interface.
- Recipes that match our pipeline:
  - "Try two coding fixes and keep the passing branch"
  - "Generate and download a binary artifact" (verify exact bytes)
  - "Prepare inputs, then verify with networking disabled"
  - "Build and refresh a reusable custom environment" (Dockerfile subset or OCI import)
  - "Run a bounded evaluation batch"
- **Unknowns (Q-003):** `/dev/fuse` for disorderfs; root access for the `user_group` and `domain_host` variations; pricing.

## Tavily

- Python SDK `tavily-python`. Credits come with the Nebius Builders Program (https://dev.nebius.com/builders).
- Use: search for existing upstream fixes and upstream trackers. Supports excluding domains, which we need for the benchmark ablation.
- **Disabled in `MODE=benchmark`** (D-017).
- Best Use of Tavily ($3k) requires a functional runtime call.

## Debian / Reproducible Builds data sources

- Dashboard: https://tests.reproducible-builds.org/debian/reproducible.html
- Unreproducible packages with no notes (unstable/amd64): https://tests.reproducible-builds.org/debian/unstable/amd64/index_no_notes.html
- Issue catalogue: https://tests.reproducible-builds.org/debian/index_issues.html
  - per-issue page pattern: `…/debian/issues/<issue_name>_issue.html`
- Per-package diffoscope result, pattern seen: `https://tests.reproducible-builds.org/debian/rb-pkg/unstable/amd64/diffoscope-results/<pkg>.html`
- Per-package page: `…/debian/rb-pkg/<suite>/<arch>/<pkg>.html`. It links the buildinfo, the first build log ("rbuild"), the second build log, and the diff. **(verify exact log URLs)**
- Machine-readable status JSON may exist at `…/debian/reproducible.json` **(verify)**
- Notes repo, with the issue catalogue and per-package causes: https://salsa.debian.org/reproducible-builds/reproducible-notes
  - `issues.yml`: the catalogue of cause types. **The agent may use this, with package names stripped.**
  - `packages.yml`: maps packages to causes. **The agent must never see this; it's for the answer key and scorer only.**
- Old source versions: https://snapshot.debian.org (pre-fix versions for the benchmark, Q-011)
- Real-world rebuilds of archive binaries (the source of migration blocking): https://reproduce.debian.net
- Monthly reports, with recent human fixes for the benchmark: https://reproducible-builds.org/reports/2026-07/ (change the month)
- Debian bug tracker: https://bugs.debian.org. Reproducibility bugs are usually tagged or usertagged `reproducible-builds` **(verify the tag)**.

## Build tools (inside the Debian build image)

- `dpkg-buildpackage`, `devscripts`, `build-essential`, plus the package's build dependencies (`apt-get build-dep` or `mk-build-deps`)
- `reprotest`: builds twice with variations. Variations include:
  - environment, build_path, user_group, fileordering, domain_host, home;
  - kernel, locales, exec_path, time, timezone, umask, num_cpus, aslr.
  - Disable one with syntax like `--variations=+all,-fileordering`. **(verify against `reprotest --help`)**
- `diffoscope`: deep diff of two outputs. Add `--text` for plain-text output.
- `disorderfs`: a FUSE filesystem for the file-ordering variation. Needs `/dev/fuse`; in Docker, use `--privileged` or `--device /dev/fuse`.
- `sha256sum` for the fingerprints.
- **Typical fix mechanisms:**
  - honor `SOURCE_DATE_EPOCH`;
  - `gzip -n`;
  - strip or map build paths (e.g. `-ffile-prefix-map`);
  - sort file lists and archive members;
  - fix hash seeds;
  - use Debian helpers (`dh_compress`, `dh_strip_nondeterminism`).

## Local fallback (user's Mac)

- Docker Desktop with a `debian:unstable` image.
- On Apple Silicon, builds are **arm64**. Use the arm64 pages on tests.reproducible-builds.org for comparison, or build amd64 in Sandboxes.

## Cost estimate

- Per package, including retries: roughly **$0.05–0.25** of model usage.
  - Nano condensing a ~1 MB diff: ~250K tokens, about $0.015.
  - Ultra diagnosis: ~30K in / 4K out, about $0.04.
  - Super, 3 patches: about $0.02.
  - Up to 3 rounds.
- 100 packages comes to about $5–25. Credits are $50 total.
- Sandbox pricing: unknown (Q-002).
- Keep a reserve for judging, 1–15 December (Q-008).

## Hackathon links

- Devpost: https://nebiusglobalaihackathon.devpost.com (rules: `/rules`, FAQ: `/details/faqs`, updates: `/updates`)
- Credits form (code `NEBIUS-DEVPOST-GLOBAL26`): linked from the Devpost Resources page
- Nebius Discord (questions for judges and staff): https://discord.gg/eXYTGhgnhK
- Judges' "Will It Ship?" recording: https://youtu.be/LjCh-ZIyjx4
