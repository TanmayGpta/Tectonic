import pytest
from prometheus_client import REGISTRY

import utils
from main import routing_logic, scope_routing_logic
from metrics import iac_kind, split_model


def _sample(name, **labels):
    return REGISTRY.get_sample_value(name, labels) or 0.0


def test_iac_kind_matches_engineer_rule():
    assert iac_kind("main.tf") == "terraform"
    assert iac_kind("infra/terraform.json") == "terraform"
    assert iac_kind("docker-compose.yml") == "compose"


def test_split_model_defaults_bare_names_to_ollama():
    assert split_model("groq:qwen/qwen3.8-27b") == ("groq", "qwen/qwen3.8-27b")
    assert split_model("ollama:qwen2.5-coder:3b") == ("ollama", "qwen2.5-coder:3b")
    assert split_model("llama3") == ("ollama", "llama3")


def test_router_records_fixed_and_failed_outcomes():
    labels = dict(iac="terraform", model="test:router")
    base = {"target_file": "main.tf", "model_choice": "test:router"}
    fixed_before = _sample("tectonic_remediations_total", outcome="fixed", **labels)
    failed_before = _sample("tectonic_remediations_total", outcome="failed", **labels)

    assert routing_logic({**base, "sandbox_status": "SUCCESS", "retry_count": 2}) == "explainer"
    assert routing_logic({**base, "sandbox_status": "FAIL", "retry_count": 3}) == "end"
    # A mid-loop retry is not a finished run and must not be counted
    assert routing_logic({**base, "sandbox_status": "FAIL", "retry_count": 1}) == "continue"

    assert _sample("tectonic_remediations_total", outcome="fixed", **labels) == fixed_before + 1
    assert _sample("tectonic_remediations_total", outcome="failed", **labels) == failed_before + 1


def test_gatekeeper_rejection_is_counted():
    labels = dict(iac="compose", model="test:reject", outcome="rejected")
    before = _sample("tectonic_remediations_total", **labels)
    state = {"is_valid_scope": False, "rejection_reason": "Out-of-scope", "model_choice": "test:reject"}
    assert scope_routing_logic(state) == "end"
    assert _sample("tectonic_remediations_total", **labels) == before + 1


def test_query_llm_counts_provider_errors(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("rate limited")
    monkeypatch.setattr(utils, "_call_provider", boom)
    labels = dict(provider="groq", model="fake-model", status="error")
    before = _sample("tectonic_llm_requests_total", **labels)
    with pytest.raises(RuntimeError):
        utils.query_llm("hi", "groq:fake-model")
    assert _sample("tectonic_llm_requests_total", **labels) == before + 1
