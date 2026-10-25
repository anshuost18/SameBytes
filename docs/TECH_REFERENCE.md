# Technical reference

> Facts we rely on, each marked with how sure we are: ✓ verified by us, 📄 from official docs (2026-10-24/25), ⚠ needs verification on Day 0/1.
> Debian data URLs are in `DATA_SOURCES.md`; harness commands are in `VERIFICATION_HARNESS.md`.

## 1. Accounts and links
- Devpost: https://nebiusglobalaihackathon.devpost.com (`/rules`, `/details/faqs`, `/updates`)
- Token Factory docs index: https://docs.tokenfactory.nebius.com/llms.txt 📄
- Nebius Discord: https://discord.gg/eXYTGhgnhK · Sandboxes contact: contree@nebius.com
- Judges' "Will It Ship?" recording: https://youtu.be/LjCh-ZIyjx4

## 2. Token Factory inference

### 2.1 Endpoint ✓
- Base URL `https://api.tokenfactory.nebius.com/v1/`. It is OpenAI-compatible; use the `openai` SDK with `base_url`. Confirmed with our account on Oct 25.

### 2.2 Nemotron models and live prices (model catalog, $ per 1M tokens) ✓ IDs / 📄 prices

| Model ID | Input | Cached input | Output | Context | Our role |
|---|---|---|---|---|---|
| `nvidia/Nemotron-3-Ultra-550b-a55b` | 1.00 | 0.12 | 3.00 | 1M | Investigator, critic |
| `nvidia/nemotron-3-super-120b-a12b` | 0.30 | 0.06 | 0.90 | 256K listed | Patcher (bake-off) |
| `nvidia/Nemotron-3.5-Super-VL` | 0.30 | 0.06 | 0.90 | 1M | Patcher (bake-off); multimodal |
| `nvidia/Nemotron-3_5-Lightning` (note the underscore) | 0.06 | — | 0.24 | 1M | Fast roles (bake-off) |
| `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | 0.06 | — | 0.24 | 262K | Fast roles; batch map |

Training cutoffs (model cards): Ultra pretraining Sep 2025 / post-training May 2026; Super 3 Jun 2025 / Feb 2026; Lightning Sep 2025 / May 2026.

### 2.3 Features we use, with minimal examples ✓ (JSON mode, tools, caching confirmed Oct 25)
```python
from openai import OpenAI
import os
c = OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=os.environ["NEBIUS_API_KEY"])

# Strict JSON schema (📄 json_schema; ✓ json_object). Put the schema in the prompt too.
r = c.chat.completions.create(
    model="nvidia/Nemotron-3-Ultra-550b-a55b", max_tokens=4000,
    messages=[{"role": "system", "content": "Return JSON matching the schema."},
              {"role": "user", "content": "..."}],
    response_format={"type": "json_schema",
                     "json_schema": {"name": "critique", "schema": CRITIQUE_SCHEMA, "strict": True}})

# Function calling ✓  (tool_choice "auto" or a forced function)
r = c.chat.completions.create(model=..., messages=msgs, tools=TOOLS, tool_choice="auto", max_tokens=16384)
for tc in (r.choices[0].message.tool_calls or []):
    name, args = tc.function.name, json.loads(tc.function.arguments)

# Usage and caching ✓
u = r.usage
cached = getattr(getattr(u, "prompt_tokens_details", None), "cached_tokens", 0) or 0
reasoning = getattr(getattr(u, "completion_tokens_details", None), "reasoning_tokens", None)
text = (r.choices[0].message.content or "").strip()
thinking = getattr(r.choices[0].message, "reasoning", None) or getattr(r.choices[0].message, "reasoning_content", None)
```
- **Caching:** automatic prefix caching, best-effort and per model. Cached tokens are billed at the cached price. It doesn't apply to batch requests. Keep static content first (`AGENT_DESIGN.md` §3). ✓ 4,224 of 4,520 tokens cached on a repeat call.
- **`max_tokens`:** reasoning consumes the budget; with `max_tokens=50`, `content` came back `None` ✓. Use ≥ 1500, and 16K for agent roles.

### 2.4 Reasoning controls ⚠ (fill this table in during T06)

| Control (`extra_body={"chat_template_kwargs": {...}}`) | Ultra | Super 3 | 3.5 Super VL | Lightning | Nano |
|---|---|---|---|---|---|
| `enable_thinking: false` reduces reasoning tokens | ? | ? | ? | ? | ? |
| `reasoning_budget: N` caps thinking | ? | ? | ? | ? | ? |
| `low_effort: true` | ? | ? | ? | ? | ? |
| `force_nonempty_content: true` | ? | ? | ? | ? | ? |
| Recommended temperature / top_p (model card) | ? | ? | ? | ? | ? |

### 2.5 Rate limits 📄
- Baseline 60 requests/min and 400K tokens/min, raised dynamically up to 20×.
- Read the `x-ratelimit-*` response headers; a 429 carries `Retry-After`.
- Our default concurrency is 4.

### 2.6 Batch inference 📄 / ⚠ exact request shape
- **Documented flow:**
  1. upload a JSONL dataset of chat requests;
  2. `POST /v1/operations` with `type: "batch_inference"`, the dataset `src` (with field `mapping`), `params.model` and a `completion_window`;
  3. poll `GET /v1/operations/{id}`;
  4. download the results.
- **Check first:** whether the OpenAI-style `files.create(purpose="batch")` plus `batches.create(endpoint="/v1/chat/completions", completion_window="24h")` also works; it's simpler with the SDK.
- **Test with a 3-request file** before the full 1,140 submission.
- Prompt caching doesn't apply to batch.
- Plan for up to 24 hours of turnaround; the fallback is concurrent calls (`AGENT_DESIGN.md` §10.2).

## 3. Token Factory Sandboxes (beta, "Contree") 📄 / ⚠ access not yet granted
- **Interfaces:**
  - Python SDK 0.3.6 (env `NEBIUS_API_KEY`, `NEBIUS_PROJECT_ID`);
  - CLI `contree-cli==0.9.4` (`contree auth -y`, `contree auth ls`; statuses ok / inactive / timeout / error);
  - REST at `https://api.tokenfactory.nebius.com/sandboxes` (headers `Authorization: Bearer …`, `Project: …`);
  - an MCP server.
- **SDK sketch (verify names against the SDK README):**
  ```python
  from contree_client.httpx import ContreeSyncClient          # or ContreeAsyncClient
  # from contree_sdk import ContreeSync                       # ⚠ import path
  api = ContreeSyncClient(os.environ["NEBIUS_API_KEY"], base_url="https://api.tokenfactory.nebius.com/sandboxes")
  sdk = ContreeSync(api)
  img = sdk.images.oci("docker://ghcr.io/<you>/samebytes-builder:2026-10-25")   # import or reuse
  r = img.run(shell=": sb-nonce=<uuid>; id; uname -a", env={}, cwd="/", disposable=True).wait()
  print(r.exit_code, r.stdout, r.stderr, r.uuid)
  # disposable=False keeps the result image (r.result_image_uuid) for env images / artifacts
  ```
- **Operation states:** PENDING, ASSIGNED, EXECUTING, SUCCESS, FAILED, CANCELLED. `SUCCESS` can still carry a nonzero exit code or `timed_out`; check both. SDK 0.3.6 cancels the operation when `wait()` exits early.
- **Limits (beta):**
  - 50 concurrent operations;
  - stdout/stderr 1 MiB per stream by default (max 10 MiB);
  - images kept 180 days;
  - execution timeout per account (`GET /v1/whoami`).
- **Networking:** `networking.enabled=false` removes the NIC; verify via `/sys/class/net`. The pattern is to fetch inputs in a setup operation, then verify offline from the saved image.
- **Result caching:** the SDK docs show the same command on the same image giving the same result UUID, so always include a nonce (`VERIFICATION_HARNESS.md` §13).
- **`contree build`** supports a Dockerfile subset (FROM, RUN, COPY/ADD, WORKDIR, ENV, ARG, USER; no multi-stage). We prefer OCI import of our exact Docker image.
- **Useful docs pages:** overview; limits, retention and usage; SWE agents (branching); the cookbook recipe "Try two coding fixes and keep the passing branch".

## 4. Tavily 📄
- Python SDK `tavily-python` (0.8.5 in your env).
- `search(query, search_depth="basic"|"advanced", max_results≤20, include_domains≤300, include_domains_mode="restrict"|"prefer", exclude_domains≤150, time_range, start_date, include_raw_content)`.
- `extract(urls=[…])`; also `crawl`, `map` and `research`.
- Session header `X-Session-Id` groups requests (nice for observability in the feedback).
- Best Use of Tavily ($3k) requires a runtime call; our scout is that call.

## 5. NVIDIA tooling notes
- **NeMo Agent Toolkit:** deprecated in Oct 2026 (replaced by NeMo Relay, Helix and Fabric). Don't adopt it this week.
- **NeMo Switchyard** (model routing) is optional; a one-line mention as a "next step" at most.
- Nemotron 3.5 Super technical report (2026-10-21): it mentions agentic software-engineering mid-training, which is why it's in the patcher bake-off.

## 6. Build tools (inside `samebytes-builder`)
- `dpkg-buildpackage -b --no-sign` (non-root uses fakeroot); `apt-get source`; `apt-get build-dep ./dir`; `dpkg-deb -c`; `dpkg -S`; `dpkg-parsechangelog -STimestamp`.
- `faketime -f "+398d" <cmd>` (libfaketime); `FAKETIME_DONT_FAKE_MONOTONIC=1`.
- `diffoscope --json out.json --text out.txt --max-report-size N dirA dirB` (exit 1 means differences).
- reprotest 0.7.33:
  - variations include environment, build_path, kernel, aslr, num_cpus, time, user_group, fileordering, domain_host, home, locales, exec_path, timezone and umask;
  - syntax `--vary=-build_path,…`;
  - `--auto-build` bisects which variation matters;
  - exit codes aren't documented.
- **Typical fix mechanisms:**
  - honour `SOURCE_DATE_EPOCH` in **UTC**: Python `datetime.datetime.fromtimestamp(int(os.environ["SOURCE_DATE_EPOCH"]), tz=datetime.timezone.utc)`; shell `date --utc --date="@$SOURCE_DATE_EPOCH"`; CMake `string(TIMESTAMP … UTC)`;
  - `gzip -n`; `-ffile-prefix-map=`; sort file lists; fixed seeds; avoid capturing `$USER`, `$HOSTNAME` and `uname`.

## 7. Costs
See `AGENT_DESIGN.md` §11 (per step) and `BUILD_PLAN.md` §6 (week budget). The hard cap is `SAMEBYTES_MAX_USD=30` (or 18 if only $25 of credit is available).
