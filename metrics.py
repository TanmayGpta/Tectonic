import os
import time
from prometheus_client import Counter, Histogram, REGISTRY, start_http_server, push_to_gateway

# ==========================================
# METRIC DEFINITIONS (scraped by Prometheus, visualised in Grafana)
# ==========================================
REMEDIATIONS = Counter(
    "tectonic_remediations_total",
    "Pipeline runs by final outcome (fixed | failed | rejected)",
    ["iac", "model", "outcome"],
)
REMEDIATION_ATTEMPTS = Histogram(
    "tectonic_remediation_attempts",
    "Engineer -> Sandbox attempts used per finished remediation",
    ["iac", "model", "outcome"],
    buckets=(1, 2, 3, 4, 5),
)
NODE_DURATION = Histogram(
    "tectonic_node_duration_seconds",
    "Wall time spent inside each LangGraph agent node",
    ["node"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 20, 40, 60, 120),
)
LLM_REQUESTS = Counter(
    "tectonic_llm_requests_total",
    "LLM calls made through query_llm",
    ["provider", "model", "status"],
)
LLM_DURATION = Histogram(
    "tectonic_llm_request_duration_seconds",
    "LLM call latency",
    ["provider", "model"],
    buckets=(0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60),
)
SANDBOX_VALIDATIONS = Counter(
    "tectonic_sandbox_validations_total",
    "Sandbox validations by result",
    ["iac", "status"],
)
SANDBOX_DURATION = Histogram(
    "tectonic_sandbox_duration_seconds",
    "Ephemeral container validation time",
    ["iac"],
    buckets=(0.5, 1, 2, 4, 8, 15, 30, 60),
)

_SERVER_STARTED = False


def iac_kind(target_file: str) -> str:
    """Bounded label for the manifest type (same rule as engineer/executor)."""
    if target_file and (target_file.endswith(".tf") or "terraform" in target_file.lower()):
        return "terraform"
    return "compose"


def split_model(model_choice: str) -> tuple:
    """'groq:qwen/qwen3' -> ('groq', 'qwen/qwen3'); bare names are Ollama."""
    provider, sep, model = (model_choice or "").partition(":")
    if sep and provider in ("ollama", "groq", "nvidia"):
        return provider, model.strip()
    return "ollama", (model_choice or "").strip()


def record_remediation(state: dict, outcome: str) -> None:
    iac = iac_kind(state.get("target_file", ""))
    model = state.get("model_choice") or "unknown"
    REMEDIATIONS.labels(iac, model, outcome).inc()
    if outcome != "rejected":
        REMEDIATION_ATTEMPTS.labels(iac, model, outcome).observe(state.get("retry_count", 0))


def timed_node(name: str, fn):
    """Wraps a LangGraph node so its runtime lands in NODE_DURATION."""
    def wrapper(state):
        start = time.perf_counter()
        try:
            return fn(state)
        finally:
            NODE_DURATION.labels(name).observe(time.perf_counter() - start)
    wrapper.__name__ = getattr(fn, "__name__", name)
    return wrapper


def start_metrics_server() -> None:
    """Idempotent: Streamlit reruns scripts, but the module (and this flag) persists."""
    global _SERVER_STARTED
    if _SERVER_STARTED:
        return
    port = int(os.getenv("TECTONIC_METRICS_PORT", "8000"))
    try:
        start_http_server(port)
        print(f"📈 [Metrics]: Prometheus endpoint live on :{port}/metrics")
    except OSError as e:
        print(f"⚠️ [Metrics]: Could not bind :{port} ({e}); metrics endpoint disabled.")
    _SERVER_STARTED = True


def push_metrics(job: str = "tectonic_cli") -> None:
    """For short-lived runs (CLI/CI). No-op unless PROMETHEUS_PUSHGATEWAY_URL is set."""
    url = os.getenv("PROMETHEUS_PUSHGATEWAY_URL")
    if not url:
        return
    try:
        push_to_gateway(url, job=job, registry=REGISTRY)
        print(f"📈 [Metrics]: Pushed run metrics to {url}")
    except Exception as e:
        print(f"⚠️ [Metrics]: Pushgateway push failed: {e}")
