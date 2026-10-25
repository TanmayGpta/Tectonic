import agents.gatekeeper as gatekeeper
from agents.gatekeeper import gatekeeper_node
from sandbox.executor import check_terraform_semantics


def _fail_if_llm_called(*args, **kwargs):
    raise AssertionError("Gatekeeper fast-path should not call the LLM")


def test_gatekeeper_accepts_iac_error_log_without_llm(monkeypatch):
    monkeypatch.setattr(gatekeeper, "query_llm", _fail_if_llm_called)
    result = gatekeeper_node({"error_logs": "yaml: line 4: mapping values are not allowed in this context"})
    assert result["is_valid_scope"] is True


def test_gatekeeper_rejects_conversational_prompt(monkeypatch):
    monkeypatch.setattr(gatekeeper, "query_llm", _fail_if_llm_called)
    result = gatekeeper_node({"error_logs": "Tell me a joke"})
    assert result["is_valid_scope"] is False
    assert "Out-of-scope" in result["rejection_reason"]


def test_gatekeeper_rejects_malformed_llm_json(monkeypatch):
    # Ambiguous input skips the fast path; a response violating the Pydantic schema must be rejected
    monkeypatch.setattr(gatekeeper, "query_llm", lambda *a, **k: '{"verdict": "yes"}')
    result = gatekeeper_node({"error_logs": "something went sideways in prod"})
    assert result["is_valid_scope"] is False
    assert "ValidationError" in result["rejection_reason"]


def test_terraform_semantics_requires_cidr_blocks_list():
    ok, err = check_terraform_semantics('cidr_blocks = "0.0.0.0/0"')
    assert ok is False
    assert "list of string required" in err

    ok, err = check_terraform_semantics('cidr_blocks = ["0.0.0.0/0"]')
    assert ok is True
    assert err == ""
