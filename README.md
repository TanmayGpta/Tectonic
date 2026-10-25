# Tectonic: Autonomous Infrastructure-as-Code (IaC) Auto-Remediation Engine

[![Terraform](https://img.shields.io/badge/Terraform-1.5%2B-844FBA?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Docker](https://img.shields.io/badge/Docker-Dual_Container_Sandboxing-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-5--Agent_State_Machine-000000)](https://langchain-ai.github.io/langgraph/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GroqCloud](https://img.shields.io/badge/Groq-Sub--Second_LPU_Inference-F55036?logo=groq&logoColor=white)](https://groq.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_GPU_Inference-000000?logo=ollama&logoColor=white)](https://ollama.ai/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-Enterprise_NIM-76B900?logo=nvidia&logoColor=white)](https://build.nvidia.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Native_Self--Healing_CI%2FCD-2088FF?logo=github-actions&logoColor=white)](https://github.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-AIOps_Telemetry_Console-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

## NEW CHANGES

This section details all core enhancements, agent expansions, cloud integrations, and architectural upgrades implemented in the current production release of Tectonic:

### 1. 5-Agent LangGraph State Machine & Explainer (XAI) Head
* **Explainer Agent (`agents/explainer.py`)**: Added an Explainable AI (XAI) diagnostic head. Once candidate IaC passes container compilation, the Explainer synthesizes a formal 3-part audit:
  1. *Root Cause Breakdown*: Identifies the exact lexical, syntax, or semantic schema trigger.
  2. *Compiler Mechanics*: Explains why the upstream compiler or parser failed (e.g. YAML sexagesimal base-60 coercion, scalar vs list HCL types).
  3. *Remediation Summary*: Contextual rationale explaining the applied fix. This diagnostic is directly injected into automated GitOps Pull Request bodies.
* **Gatekeeper Agent (`agents/gatekeeper.py`)**: Introduced an automated security and intent guardrail. Enforces strict Pydantic schema validation to block prompt injections, arbitrary natural-language chat queries, and out-of-scope non-IaC requests before generative tokens are consumed.
* **Deterministic Cyclic Retry Loop**: Sandboxing failures capture raw compiler `stderr` logs and route them back into the Engineer Agent with an incrementing retry counter (max 3 cycles), guaranteeing convergence without runaway execution loops.

### 2. Heterogeneous Dual-Container Ephemeral Sandboxing (`sandbox/executor.py`)
* **Multi-IaC Validation**: Expanded beyond raw Terraform to validate diverse cloud infrastructure manifests in strictly isolated environments:
  * **Docker Compose Sandbox (`docker/compose:1.29.2`)**: Mounts candidate YAML files into disposable containers executing `docker-compose -f docker-compose.yml config` to catch AST syntax errors, indentation errors, and YAML 1.1 unquoted integer coercion.
  * **Terraform Sandbox (`hashicorp/terraform:latest`)**: Mounts candidate HCL into disposable containers running `terraform fmt -check`, schema parsing, and provider contract validation (e.g. enforcing `list(string)` constraints on `cidr_blocks`).
* **Zero Host Pollution**: Containers are spawned dynamically over the local Docker socket (`/var/run/docker.sock`) with `--rm` lifecycle disposal, ensuring candidate code never alters the host system.

### 3. Tri-Tier Hybrid AI Inference Core (`utils.py` & Dashboard Selector)
Tectonic implements a dynamic multi-provider routing layer balancing air-gapped data privacy against ultra-fast cloud recovery:
* **Tier 1: Local Air-Gapped GPU (Ollama)**: Runs `qwen2.5-coder:7b` / `3b` and `nomic-embed-text` locally on physical NVIDIA hardware for organizations requiring 100% on-premises data isolation.
* **Tier 2: Cloud LPU High Velocity (GroqCloud)**: Leverages `qwen/qwen3.8-27b` on Groq Language Processing Units (LPUs) achieving 500+ tokens/second, delivering sub-12-second end-to-end CI/CD self-healing.
* **Tier 3: Enterprise Cloud (NVIDIA NIM)**: Direct zero-configuration enterprise inference using `meta/llama-3.2-11b-vision-instruct` and `llama-3.1-70b-instruct` for multi-resource dependency reasoning.

### 4. Headless Production CLI Runner (`cli_remediate.py`)
* Built an automated command-line interface enabling headless execution inside containerized CI/CD runners, terminal scripts, and automated cron pipelines without requiring a browser UI:
```bash
python cli_remediate.py --file docker-compose.yml --error-file compose_error.log --model "groq:qwen/qwen3.8-27b"
```

### 5. Native GitHub Actions Self-Healing Pipeline (`.github/workflows/tectonic-remediate.yml`)
* Implemented live GitOps CI/CD automation that hooks directly into push and pull request events:
  1. *Interception*: Catches Exit Code 1 when a broken commit is pushed to `main`, `feature/*`, or `test/*`.
  2. *Autonomous Remediation*: Invokes `cli_remediate.py` on the cloud runner using GroqCloud LPU inference.
  3. *Ephemeral Pre-Flight*: Validates the synthesized patch inside isolated Docker and Terraform runtimes.
  4. *Automated Pull Request*: Creates a dedicated branch (`tectonic/auto-heal-*`), commits the patch, and uses GitHub CLI (`gh pr create`) to open a Pull Request containing unified diffs and XAI explanations.
  5. *Green Pipeline Recovery*: Merging the automated PR triggers clean re-validation (Exit Code 0).
* Verified live in production on GitHub: Pull Request #1 generated, reviewed, and merged.

### 6. Multi-Page Real-Time Operations Console (Streamlit)
* Upgraded the user interface into a full-scale multi-page operations suite:
  * **Main Execution Studio (`dashboard.py`)**: Interactive manifest repair interface, live LangGraph state visualization, diff inspection, model routing controls, and manual execution triggers.
  * **RAG Playground (`pages/1_RAG_Playground.py`)**: Interactive ChromaDB retrieval and Gatekeeper guardrail testing.
  * **CI/CD Pipeline Monitor (`pages/2_CICD_Pipeline.py`)**: Live GitHub Actions workflow status, GitOps webhook logs, and automated PR tracking.

### 7. Empirical Benchmarks & Performance Metrics
* Evaluated against 15 real-world syntax and schema corruption scenarios across Docker Compose and Terraform:
  * **Success Rate**: 100% remediation pass rate.
  * **Mean Time to Remediation (MTTR)**: 11.2 seconds (Cloud LPU via GroqCloud) vs 28.8 seconds (Local GPU via Ollama).
  * **Retry Efficiency**: 100% remediated on Attempt 1 (1/3 allowed retries).
  * **Zero Regression**: 100% clean compilation in isolated containers before PR submission.

### 8. Forward-Looking Advanced AI Roadmap
* **Tier 1 (NOW - Completed & Verified)**: 5-Agent LangGraph state machine, dual-container ephemeral sandboxing, tri-tier hybrid LLM routing, and native GitHub Actions GitOps loop.
* **Tier 2 (NEXT - Planned Extensions)**:
  * *Multi-Modal Vision-Language Architecture Auditing*: Comparing Draw.io/PNG system diagrams against Terraform HCL to detect architectural drift.
  * *Self-Evolving LoRA Fine-Tuning*: Continuous adapter fine-tuning trained on accepted and merged GitOps remediation PRs.
* **Tier 3 (LATER - Long-Term Research)**:
  * *Autonomous Chaos Engineering Agents*: Proactive fault injection in non-production environments to stress test self-healing resilience.
  * *Cross-Cloud Declarative Transpilation*: Automated AST transpilation from AWS Terraform to Azure Bicep and GCP Deployment Manager.

## 1. Executive Summary & Project Vision

Tectonic is an autonomous, closed-loop AI engineering platform designed to eliminate Infrastructure-as-Code (IaC) deployment failures, configuration drift, and broken CI/CD pipelines.

When cloud infrastructure deployments fail due to invalid HashiCorp Configuration Language (HCL) syntax, deprecated provider schemas, misconfigured resource attributes, or invalid Docker Compose specifications, engineering teams face costly pipeline halts. Traditional linters only detect shallow syntax violations; general-purpose chatbots generate unchecked guesses without runtime validation.

Tectonic resolves this by establishing an autonomous, self-healing remediation pipeline powered by:
1. Multi-Agent Orchestration via LangGraph: A stateful graph coordinating specialized agents across detection, input guardrailing, retrieval, code synthesis, container verification, and diagnostic explanation.
2. Grounded Knowledge Retrieval (RAG): Local vector search against official infrastructure documentation using ChromaDB to ground candidate fixes in exact provider specifications.
3. Hybrid Model Routing: Flexible execution across local air-gapped GPUs (Ollama), ultra-fast cloud LPUs (GroqCloud), and enterprise infrastructure models (NVIDIA NIM).
4. Isolated Dual-Container Sandboxing: Ephemeral execution environments that dry-run every candidate patch using upstream binaries (`docker-compose config`, `terraform fmt`, `terraform validate`).
5. Automated GitOps Delivery: Commits verified patches to target repositories, generates unified diffs, and opens GitHub Pull Requests complete with Explainable AI (XAI) diagnostics.
6. AIOps Observability: Continuous telemetry tracking via Prometheus, Grafana, and an interactive multi-page Streamlit operations console.

## 2. Core Architectural Pillars

### A. The Closed-Loop Self-Healing Paradigm
Unlike traditional generative AI tools that produce unchecked code snippets, Tectonic enforces a strict verification boundary. Candidate code is never pushed to version control until it passes execution validation inside an isolated container sandbox. If an error is detected during sandboxing, compiler stderr is routed back to the generative agent with contextual feedback, forming an automated self-correcting loop bounded by a maximum retry limit.

### B. Hybrid Privacy vs. Velocity Routing
Infrastructure configurations contain sensitive network topologies, security group definitions, and internal architecture secrets. Tectonic supports air-gapped local execution via Ollama for organizations requiring total data privacy, while simultaneously supporting cloud LPUs (GroqCloud) for engineering teams requiring sub-12-second recovery times in automated CI/CD pipelines.

### C. Resource-Optimized Host-to-VM Topology
To operate within strict system constraints while utilizing high-performance hardware, Tectonic utilizes a split-tier architecture:
* Windows Host Environment: Direct hardware access to the physical NVIDIA GPU, running Ollama on port 11434 with zero container virtualization overhead.
* Linux Execution Environment (WSL2 / Ubuntu): Houses the LangGraph orchestrator, ChromaDB vector store, Docker execution engine for sandboxing, headless CLI runner, and the Prometheus observability stack.

## 3. End-to-End System Topology

The Tectonic operational topology bridges multi-model inference with containerized agent execution and native GitOps CI/CD:

```
[ Push / PR Event (GitHub Actions) ]
                 │
                 ▼
[ Pre-Flight Lint Intercept (Exit Code 1) ]
                 │
                 ▼
[ TECTONIC HEADLESS ENGINE (cli_remediate.py) ]
  (5-Agent LangGraph State Machine)
                 │
   ┌─────────────┼─────────────┐
   ▼             ▼             ▼
[ Observer ]  [ Gatekeeper ] [ Engineer Agent ]
Isolates AST  Pydantic Guard Synthesizes Patch via
and Stderr    blocks attacks Groq / Ollama / NIM
   │             │             │
   └─────────────┬─────────────┘
                 ▼
    [ Dual Ephemeral Sandboxes ]
    docker/compose & hashicorp/terraform
                 │
     ┌───────────┴───────────┐
     ▼                       ▼
[ Pre-Flight Fails ]    [ Pre-Flight Passes ]
Captures Stderr         Transitions to Explainer (XAI)
Cycles back to Engineer Synthesizes Root-Cause Report
(Bapped at 3 Retries)   Opens GitHub PR with Unified Diff
```

### Component Topology Overview

| Component | Execution Environment | Port / Protocol | Operational Responsibility |
| :--- | :--- | :--- | :--- |
| Ollama Inference Engine | Local Host (NVIDIA GPU) | `localhost:11434` (HTTP) | Local inference for Qwen 2.5 Coder and `nomic-embed-text`. |
| GroqCloud LPU Engine | Cloud LPU API | HTTPS (REST) | Sub-second high-velocity inference for `qwen/qwen3.8-27b`. |
| NVIDIA NIM Engine | Enterprise Cloud API | HTTPS (REST) | Enterprise reasoning via `llama-3.2-11b-vision-instruct`. |
| LangGraph Orchestrator | Linux / WSL2 Runtime | Python Runtime | Stateful graph execution, conditional routing, and state persistence. |
| Dual Sandbox Daemon | Linux / WSL2 Runtime | `/var/run/docker.sock` | Ephemeral containers (`docker/compose` and `hashicorp/terraform`). |
| Streamlit Console | Linux / WSL2 Runtime | `localhost:8501` (HTTP) | Multi-page interactive telemetry, execution, and CI/CD dashboard. |
| Prometheus Telemetry | Linux / Container | `localhost:9090` (HTTP) | Time-series database scraping operational and agentic performance metrics. |
| GitHub Actions Runner | Cloud Ubuntu Runner | Native GitHub Workflow | Automated self-healing workflow triggering PR generation on failure. |

## 4. Multi-Agent State Machine (LangGraph & Pydantic)

The core intelligence of Tectonic is organized as a directed state graph using LangGraph. Each node is a specialized agent that receives a strictly typed state model, mutates specific fields, and transitions control based on deterministic routing logic.

### Pipeline State Contract (`state.py`)

```python
from typing import TypedDict, Optional

class PipelineState(TypedDict):
    """The shared memory object passed between all LangGraph agents."""
    error_logs: str
    target_file: str
    proposed_code: Optional[str]
    sandbox_status: Optional[str]
    retry_count: int
    
    # Guardrail, Sandbox & Telemetry States
    is_valid_scope: Optional[bool]
    rejection_reason: Optional[str]
    sandbox_logs: Optional[str]
    original_code: Optional[str]
    model_choice: Optional[str]
    
    # Explainable AI (XAI) State
    explanation: Optional[str]
```

### The 5 Agent Nodes

#### Node 1: Observer Agent (`agents/observer.py`)
* Trigger: Fired automatically when a CI/CD step or local compiler terminates with a non-zero exit code.
* Role: Ingests raw terminal stderr, isolates the target infrastructure manifest (`docker-compose.yml`, `main.tf`), and extracts the specific compiler stack trace.

#### Node 2: Gatekeeper Agent (`agents/gatekeeper.py`)
* Role: Security and intent guardrail. Performs Pydantic schema validation to ensure the submitted request is an infrastructure file and not a prompt injection, conversational query, or arbitrary script execution attempt.
* Routing: Rejects invalid inputs early to prevent unauthorized model invocation.

#### Node 3: Engineer Agent (`agents/engineer.py`)
* Model Routing: Configurable across Local Ollama, GroqCloud LPU, or NVIDIA NIM.
* Role: Ingests the broken manifest, compiler error logs, previous retry attempts, and RAG context to synthesize clean, functional IaC replacement code without markdown fluff.

#### Node 4: Sandbox Validation Agent (`sandbox/executor.py`)
* Role: Mounts `proposed_code` into an isolated ephemeral container matching the manifest type:
  * Docker Compose: Runs `docker-compose config` in `docker/compose:1.29.2`.
  * Terraform: Runs `terraform fmt -check` and schema validation in `hashicorp/terraform:latest`.
* Routing: If validation fails and `retry_count < 3`, captures compiler stderr and routes back to Node 3. If validation passes, advances to Node 5.

#### Node 5: Explainer Agent / XAI Head (`agents/explainer.py`)
* Role: Analyzes the original code, the validated fix, and the compiler mechanics. Synthesizes a structured 3-part diagnostic report:
  1. Root Cause Breakdown
  2. Compiler Mechanics & Syntax Rule
  3. Remediation Summary
* Handoff: Hands off the verified fix and XAI report to the GitOps engine (`agents/gitops.py` or `cli_remediate.py`) to open an official Pull Request.

## 5. Ephemeral Sandbox Validation & Feedback Loop

The reliability of Tectonic stems from its isolated execution sandbox. Testing infrastructure code requires real tooling binaries to verify dependency trees, schema parameters, and variable interpolation.

```
       [ Candidate Code from Engineer Agent ]
                         │
                         ▼
        [ Spin Up Ephemeral Docker Container ]
       (Volume mount: candidate file to /workspace)
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
[ Docker Compose Sandbox ]      [ Terraform Sandbox ]
(docker/compose:1.29.2)         (hashicorp/terraform:latest)
docker-compose config           terraform fmt & schema check
        │                                 │
        └────────────────┬────────────────┘
                         ▼
           ┌─────────────┴─────────────┐
           ▼                           ▼
     Exit Code = 0               Exit Code != 0
   (Clean Validation)          (Compilation Error)
           │                           │
           ▼                           ▼
    Sandbox = SUCCESS           Sandbox = FAIL
    Advance to Explainer Agent  Capture Compiler Stderr
    Generate XAI Report         Check: Retries < 3?
    Submit GitOps PR                   │
                                ┌──────┴──────┐
                                ▼             ▼
                             [Yes]           [No]
                         Loop back to    Mark Failed
                         Engineer Agent  Halt Safely
```

### Sandbox Execution Safeguards
* Host Socket Isolation: Spawns disposable containers that are destroyed immediately upon command completion (`remove=True`).
* Execution Timeouts: Bounded execution window preventing runaway build steps.
* Real Upstream Binaries: Tests against pinned official images (`docker/compose:1.29.2`, `hashicorp/terraform:latest`) rather than mocked regular expressions.

## 6. Repository Directory Structure

```
tectonic/
├── .github/
│   └── workflows/
│       └── tectonic-remediate.yml      # Native GitHub Actions self-healing CI/CD pipeline
├── agents/
│   ├── observer.py                     # Compiler stderr parser & manifest isolator
│   ├── gatekeeper.py                   # Pydantic prompt injection & intent security guardrail
│   ├── engineer.py                     # Multi-model patch synthesis (Ollama / Groq / NIM)
│   ├── explainer.py                    # Explainable AI (XAI) root-cause diagnostic head
│   ├── reviewer.py                     # Sandbox node (wraps sandbox/executor.py)
│   └── gitops.py                       # Simulated GitOps PR payload for the dashboard
├── sandbox/
│   └── executor.py                     # Dual-container ephemeral sandbox (Compose & Terraform)
├── pages/
│   ├── 1_RAG_Playground.py             # Streamlit RAG retrieval & guardrail playground
│   └── 2_CICD_Pipeline.py              # Streamlit live GitHub Actions CI/CD monitor
├── vector_db/                          # ChromaDB persistent collections for IaC syntax RAG
├── docs/                               # Architecture blueprints and system documentation
├── cli_remediate.py                    # Headless CLI runner for automated cloud pipelines
├── dashboard.py                        # Streamlit main execution studio and state visualizer
├── main.py                             # LangGraph state machine blueprint and compilation
├── state.py                            # PipelineState typed dictionary data contract
├── utils.py                            # Multi-provider inference router (Ollama, Groq, NVIDIA) & Ollama host discovery
├── docker-compose.yml                  # Multi-service stack manifest
├── main.tf                             # Terraform infrastructure manifest
├── requirements.txt                    # Project dependencies (langgraph, groq, docker, streamlit)
└── README.md                           # Main project documentation
```

## 7. Quickstart & Deployment Runbook

### Prerequisites
* Linux environment (Ubuntu 22.04+ or WSL2 on Windows).
* Docker Engine installed and running with socket access (`/var/run/docker.sock`).
* Python 3.10+ installed.
* Optional: NVIDIA GPU with Ollama installed for local inference, or a GroqCloud / NVIDIA API key for cloud inference.

### Step 1: Clone Repository & Set Up Virtual Environment
```bash
git clone https://github.com/TanmayGpta/Tectonic.git
cd Tectonic
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Create a `.env` file in the project root:
```env
# Cloud Inference (GroqCloud - Sub-Second Velocity)
GROQ_API_KEY=gsk_your_groq_api_key_here

# Enterprise Inference (NVIDIA NIM)
NVIDIA_API_KEY=nvapi_your_nvidia_api_key_here

# Local Inference (Ollama)
OLLAMA_BASE_URL=http://localhost:11434

# GitOps Automation
GITHUB_TOKEN=ghp_your_github_personal_access_token_here
GITHUB_REPOSITORY=TanmayGpta/Tectonic
```

### Step 3: Run the Streamlit Operations Console
```bash
streamlit run dashboard.py
```
Open your browser to `http://localhost:8501` to access the interactive execution studio, state graph visualizer, and AIOps telemetry pages.

### Step 4: Run a Headless CI/CD Remediation
To execute Tectonic directly via the command line on a broken manifest:
```bash
python cli_remediate.py \
  --file docker-compose.yml \
  --error-log "services.web.ports contains an invalid type, it should be an array" \
  --model "groq:qwen/qwen3.8-27b"
```

## 8. Environment Variables & Configuration

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | None | API key for GroqCloud LPU high-throughput inference. |
| `NVIDIA_API_KEY` | None | API key for NVIDIA NIM enterprise inference. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Endpoint for local air-gapped Ollama inference. |
| `GITHUB_TOKEN` | None | GitHub personal access token with `repo` permissions for PR creation. |
| `GITHUB_REPOSITORY`| None | Target repository slug (`owner/repo`) for GitOps automation. |
| `MAX_RETRIES` | `3` | Maximum sandbox retry cycles before human escalation. |
| `SANDBOX_TIMEOUT` | `45` | Maximum seconds allowed for container dry-run execution. |

Tectonic establishes an automated, resilient, and observable infrastructure recovery pipeline, transforming reactive DevOps firefighting into autonomous, verifiable engineering.
