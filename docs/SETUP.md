# Setup on the personal laptop (Windows + WSL2 + Docker Desktop)

> Do all of this on your **personal** laptop and accounts (Q-012). Never use NetApp devices, keys, proxies, Teams or OneDrive for project code or keys.
> Time: about 60–90 minutes, mostly downloads.

## 1. Before you start
- **Rotate keys.** The earlier zip shared over Teams/OneDrive contained `.env`.
  - In the Token Factory console, create a new API key and delete the old one.
  - In the Tavily dashboard, regenerate the key.
- **Hardware:** 16 GB+ RAM recommended (give WSL 10–12 GB), 80 GB free disk, virtualization enabled.

## 2. WSL2 and resources
In an admin PowerShell:
```powershell
wsl --install -d Ubuntu-24.04
wsl --set-default-version 2
wsl --update
```
Create `C:\Users\<you>\.wslconfig`:
```ini
[wsl2]
memory=12GB
processors=8
swap=8GB
```
Then run `wsl --shutdown` and reopen Ubuntu. Inside WSL, check with `nproc; free -g`.

## 3. Docker Desktop
- Settings → General → **Use the WSL 2 based engine**.
- Settings → Resources → WSL Integration → enable **Ubuntu-24.04**.
- In WSL: `docker version && docker run --rm hello-world`.

## 4. Repo in the Linux filesystem (not `/mnt/c` or `/mnt/d`)
```bash
sudo apt update && sudo apt install -y git curl jq ca-certificates
git config --global core.autocrlf false
mkdir -p ~/src && cd ~/src
git clone https://github.com/anshuost18/SameBytes.git && cd SameBytes
```
- Copy this doc pack in: the `docs/`, `docker/` and root files from the pack go over the repo.
- Keep your `.pre-commit-config.yaml` and `.secrets.baseline`.
- Delete the Windows `.venv` reference; it isn't usable in WSL.
- Builds on NTFS (`/mnt/d/...`) are many times slower, and permissions and timestamps behave differently.

## 5. Python toolchain (uv)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh && exec $SHELL
uv python install 3.12
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e ".[dev]"          # after pyproject.toml exists (ARCHITECTURE.md §3)
pre-commit install
```
Replace the old Windows `pip freeze` `requirements.txt` with `pyproject.toml` plus `uv lock`.

## 6. Keys (`.env`, gitignored)
```bash
cp .env.example .env && nano .env      # paste the NEW keys; never paste keys into chats
set -a; source .env; set +a
curl -s https://api.tokenfactory.nebius.com/v1/models -H "Authorization: Bearer $NEBIUS_API_KEY" \
  | jq -r '.data[].id' | grep -i nemotron
```
You should see the Ultra, Super, 3.5 Super VL, 3.5 Lightning and Nano IDs (`TECH_REFERENCE.md` §2.2).

## 7. `samebytes doctor` (implement in T05/T06; until then run these by hand)

| Check | Command / expectation |
|---|---|
| Docker works offline | `docker run --rm --network none debian:unstable true` |
| Builder image | `docker build -t samebytes-builder:2026-10-25 -f docker/Dockerfile docker/` succeeds; `docker run --rm samebytes-builder:2026-10-25 bash -c 'locale -a \| grep -c et_EE; ls /usr/share/zoneinfo/Etc/GMT+12; faketime -f +398d date; id pbuilder1; id pbuilder2'` |
| Disk | `docker system df` and `df -h ~` show ≥ 40 GB free |
| LLM reachable | 1 call per model with `max_tokens=1500`; record latency |
| Reasoning controls | `enable_thinking` true vs false changes `reasoning_tokens` (`AGENT_DESIGN.md` §2.1) |
| JSON schema strict | `response_format={"type":"json_schema","json_schema":{"name":"t","schema":{…},"strict":true}}` returns valid JSON |
| Tool calling | A forced `tool_choice` returns `tool_calls` |
| Caching | The second identical call shows `usage.prompt_tokens_details.cached_tokens > 0` |
| Tavily | `TavilyClient(api_key).search("argparse-manpage SOURCE_DATE_EPOCH", max_results=3)` returns results |
| Sandboxes (when granted) | §8 |

## 7b. GitHub Pages and Actions (do once, 5 minutes; Person A)
- Repo → Settings → **Pages** → Source: **GitHub Actions**. The repo must be public (it is).
- Repo → Settings → **Actions → General**: allow GitHub Actions; leave workflow permissions at the default *Read repository contents*. `verify.yml` grants `packages: write` only to its `env` job and `packages: read` to the build jobs (`VERIFICATION_HARNESS.md` §14). New `ghcr.io` packages are private by default; the build jobs log in with `GITHUB_TOKEN`, so that's fine. Fallback if pushing fails (Q-021): `docker save` the env image into an artifact and `docker load` it in both build jobs, then check the image ID matches.
- First `verify.yml` run: pick one package (`autoflake=2.4.0-1`) and confirm A and B land on different runners (job logs show different `Runner name`/hostnames) **and pulled the same env digest**.
- No Nebius or Tavily secret is ever added to the repo's Actions secrets (verification needs none).

## 7c. Keyless check (what a judge or your teammate runs, no `.env`)
```bash
git clone https://github.com/anshuost18/SameBytes && cd SameBytes
uv venv --python 3.12 && source .venv/bin/activate && uv pip install -e .
samebytes replay published/flagship-blind     # plays back the recorded agent session (labelled REPLAY), no network, no key
```

## 8. Sandboxes (when access is granted)
```bash
uv tool install "contree-cli==0.9.4"
export NEBIUS_AI_PROJECT=<your project id>
contree auth -y && contree auth ls        # status should be "ok" (not "inactive")
curl -s https://api.tokenfactory.nebius.com/sandboxes/v1/whoami \
  -H "Authorization: Bearer $NEBIUS_API_KEY" -H "Project: $NEBIUS_PROJECT_ID" | jq
```
Then run the probe operation from `VERIFICATION_HARNESS.md` §13 and record the answers in `DECISIONS.md` Q-003.

## 9. Moving this doc pack to the personal laptop
Use a personal channel only: a personal email to yourself, a personal USB drive, or a personal cloud drive. Not NetApp Teams or OneDrive. Then commit it from the personal laptop.
