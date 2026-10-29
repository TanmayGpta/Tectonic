# Tectonic

Autonomous IaC auto-remediation engine. A broken `docker-compose.yml` or `main.tf` + its error log goes through a LangGraph agent loop that proposes a fix, validates it in an ephemeral Docker container, and explains it. Delivered via a Streamlit console, a headless CLI, and a GitHub Actions workflow that opens a fix PR.

## Layout
- `main.py` — builds/compiles the LangGraph `app`: observer → gatekeeper → engineer → sandbox → (retry engineer ≤ `MAX_RETRIES`=3 | explainer) → END.
- `state.py` — `PipelineState` TypedDict shared by all nodes. New state fields go here **and** in every `initial_state` dict (`main.py`, `cli_remediate.py`, `dashboard.py`, `pages/2_CICD_Pipeline.py`).
- `metrics.py` — Prometheus metrics (`tectonic_*`). Outcomes recorded in `main.py` routers, node timing via `timed_node`, LLM metrics in `query_llm`, sandbox metrics in `agents/reviewer.py`. Streamlit serves `:8000/metrics` (`TECTONIC_METRICS_PORT`); CLI pushes to `PROMETHEUS_PUSHGATEWAY_URL` if set. Keep labels bounded (no file paths).
- `monitoring/` — Prometheus + Pushgateway + Grafana stack (provisioned dashboard `tectonic-overview`, alert rules). Separate from the root demo `docker-compose.yml`.
- `utils.py` — `query_llm(prompt, model_choice, is_json, temperature)`: single entry point for all LLM calls; `get_ollama_host()` probes for Ollama.
- `agents/` — one node per file, each returns a **partial** state dict.
  - `observer.py` ingest log (falls back to a mock error), `gatekeeper.py` keyword fast-path + LLM/Pydantic scope check, `engineer.py` RAG (Chroma → fallback `docs/*.txt`) + fix generation, `reviewer.py` the sandbox node (wraps `sandbox/executor.py`), `explainer.py` XAI markdown, `gitops.py` builds a *simulated* PR payload for the UI (not a real PR).
- `sandbox/executor.py` — `validate_iac(code, target_file)` dispatches to `docker/compose:1.29.2` (`config`) or `hashicorp/terraform:latest` (`fmt -check` + regex semantic check). Needs Docker socket.
- `cli_remediate.py` — headless runner used by CI; overwrites the target file on success and writes a PR body markdown + `tectonic_summary.json`.
- `notifier/` — `telegram.py` pushes fix/escalation alerts from CI (no-op without creds); `telegram_bot.py` is a long-polling listener that turns the alert's Approve/Reject buttons into GitHub merge/close calls (only for `TELEGRAM_CHAT_ID`).
- `dashboard.py` + `pages/` — Streamlit console (main studio, RAG playground, CI/CD simulator).
- `vector_db/` — `scraper.py` / `build_db.py` populate ChromaDB at `vector_db/chroma_storage/` (gitignored) with `nomic-embed-text` embeddings. `inject_rule.py` adds a demo compliance rule.
- `.github/workflows/tectonic-remediate.yml` — lints compose + terraform on push; on failure runs the CLI with Groq and opens a PR via `gh`.
- `docker-compose.yml`, `main.tf` — the **demo target manifests** the CI heals. Breaking them on a `test/*` branch is how the loop is demoed; don't "clean them up" casually.

## Models
`model_choice` strings are `provider:model`: `ollama:<m>` (default `ollama:qwen2.5-coder:3b`), `groq:<m>`, `nvidia:<m>`. Add providers inside `query_llm`, never call provider APIs from agents directly.

## Env (`.env`, never commit)
`GROQ_API_KEY`, `NVIDIA_API_KEY`, `OLLAMA_HOST_IP` (optional override); for the Telegram bot `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GITHUB_REPO` (owner/repo), `GITHUB_TOKEN` (PAT). CI uses repo secrets `GROQ_API_KEY`, `NVIDIA_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

## Run
```bash
source .venv/bin/activate && pip install -r requirements.txt   # inside WSL
streamlit run dashboard.py                                      # console on :8501
python cli_remediate.py --file main.tf --model groq:<model>     # headless; dry-runs sandbox if no --error-log
python main.py                                                  # graph with mock error
docker compose up --build                                       # containerised console (mounts docker.sock)
docker compose -f monitoring/docker-compose.yml up -d           # Prometheus :9090, Pushgateway :9091, Grafana :3000 (admin/tectonic)
```
Tests: `python -m pytest` (`tests/`, no LLM or Docker needed; mock `query_llm` via monkeypatch). For end-to-end checks run `python sandbox/executor.py` and a CLI remediation on a deliberately broken copy of a manifest.

## Conventions
- Python 3.10+ (CI 3.10, Dockerfile 3.12). Plain functions, no classes except Pydantic models.
- Agents log progress with emoji-prefixed `print` (`[Agent Name]: ...`); keep that style.
- Treat `target_file` as Terraform if it ends in `.tf` or contains "terraform", else Docker Compose — this check is duplicated in engineer/executor; keep them consistent.
- Repo lives in WSL (`/home/tanmay/Tectonic`); from Windows tools, git needs `-c safe.directory=*`.
