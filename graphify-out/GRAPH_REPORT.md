# Graph Report - Tectonic  (2026-10-25)

## Corpus Check
- 23 files · ~12,731 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .ini 1)

## Summary
- 174 nodes · 295 edges · 11 communities
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3288eae7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Tectonic: Autonomous Infrastructure-as-Code (IaC) Auto-Remediation Engine
- main.py
- requests
- steps
- executor.py
- tectonic-remediate.yml
- cli_remediate.py
- gatekeeper.py
- 2_CICD_Pipeline.py
- tectonic-dashboard
- Tectonic

## God Nodes (most connected - your core abstractions)
1. `PipelineState` - 18 edges
2. `get_ollama_host()` - 12 edges
3. `gatekeeper_node()` - 11 edges
4. `query_llm()` - 11 edges
5. `Tectonic: Autonomous Infrastructure-as-Code (IaC) Auto-Remediation Engine` - 10 edges
6. `steps` - 9 edges
7. `engineer_node()` - 9 edges
8. `validate_iac()` - 9 edges
9. `NEW CHANGES` - 9 edges
10. `tectonic-dashboard` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Layout` --references--> `PipelineState`  [INFERRED]
  CLAUDE.md → state.py
- `Models` --references--> `query_llm()`  [INFERRED]
  CLAUDE.md → utils.py
- `Run` --references--> `query_llm()`  [INFERRED]
  CLAUDE.md → utils.py
- `gatekeeper_node()` --uses--> `PipelineState`  [INFERRED]
  agents/gatekeeper.py → state.py
- `sandbox_node()` --uses--> `PipelineState`  [INFERRED]
  agents/reviewer.py → state.py

## Import Cycles
- None detected.

## Communities (11 total, 0 thin omitted)

### Community 0 - "Tectonic: Autonomous Infrastructure-as-Code (IaC) Auto-Remediation Engine"
Cohesion: 0.07
Nodes (26): 1. Executive Summary & Project Vision, 2. Core Architectural Pillars, 3. End-to-End System Topology, 4. Multi-Agent State Machine (LangGraph & Pydantic), 5. Ephemeral Sandbox Validation & Feedback Loop, 6. Repository Directory Structure, 7. Quickstart & Deployment Runbook, 8. Environment Variables & Configuration (+18 more)

### Community 1 - "main.py"
Cohesion: 0.15
Nodes (8): clean_code_fence(), engineer_node(), explainer_node(), observer_node(), routing_logic(), scope_routing_logic(), PipelineState, query_llm()

### Community 2 - "requests"
Cohesion: 0.21
Nodes (9): inject_proprietary_rule(), ask_qwen(), get_ollama_host(), build_knowledge_base(), get_embedding(), get_ollama_embed_url(), get_ollama_host(), get_ollama_host() (+1 more)

### Community 3 - "steps"
Cohesion: 0.12
Nodes (16): GITHUB_TOKEN, GROQ_API_KEY, NVIDIA_API_KEY, continue-on-error, env, id, if, name (+8 more)

### Community 4 - "executor.py"
Cohesion: 0.21
Nodes (6): sandbox_node(), check_terraform_semantics(), validate_docker_compose(), validate_iac(), validate_terraform(), test_terraform_semantics_requires_cidr_blocks_list()

### Community 5 - "tectonic-remediate.yml"
Cohesion: 0.13
Nodes (14): jobs, validate-and-heal, name, permissions, contents, pull-requests, branches, branches (+6 more)

### Community 6 - "cli_remediate.py"
Cohesion: 0.16
Nodes (10): main(), 1. 5-Agent LangGraph State Machine & Explainer (XAI) Head, 2. Heterogeneous Dual-Container Ephemeral Sandboxing (`sandbox/executor.py`), 3. Tri-Tier Hybrid AI Inference Core (`utils.py` & Dashboard Selector), 4. Headless Production CLI Runner (`cli_remediate.py`), 5. Native GitHub Actions Self-Healing Pipeline (`.github/workflows/tectonic-remediate.yml`), 6. Multi-Page Real-Time Operations Console (Streamlit), 7. Empirical Benchmarks & Performance Metrics (+2 more)

### Community 7 - "gatekeeper.py"
Cohesion: 0.26
Nodes (6): gatekeeper_node(), ScopeValidation, _fail_if_llm_called(), test_gatekeeper_accepts_iac_error_log_without_llm(), test_gatekeeper_rejects_conversational_prompt(), test_gatekeeper_rejects_malformed_llm_json()

### Community 8 - "2_CICD_Pipeline.py"
Cohesion: 0.30
Nodes (3): generate_gitops_pull_request(), popup_manifest_dialog(), popup_sandbox_terminal_dialog()

### Community 9 - "tectonic-dashboard"
Cohesion: 0.20
Nodes (9): services, tectonic-dashboard, build, command, container_name, extra_hosts, ports, volumes (+1 more)

### Community 10 - "Tectonic"
Cohesion: 0.29
Nodes (6): Conventions, Env (`.env`, never commit), Layout, Models, Run, Tectonic

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `NEW CHANGES` connect `cli_remediate.py` to `Tectonic: Autonomous Infrastructure-as-Code (IaC) Auto-Remediation Engine`?**
  _High betweenness centrality (0.238) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `PipelineState` (e.g. with `engineer_node()` and `explainer_node()`) actually correct?**
  _`PipelineState` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Should `Tectonic: Autonomous Infrastructure-as-Code (IaC) Auto-Remediation Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Why does `main()` connect `cli_remediate.py` to `2_CICD_Pipeline.py`, `executor.py`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `query_llm()` (e.g. with `Models` and `Run`) actually correct?**
  _`query_llm()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Should `steps` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `tectonic-remediate.yml` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._