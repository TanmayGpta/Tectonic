# 🌍 Tectonic
**Agentic Infrastructure Auto-Remediation CI/CD Pipeline**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)
![LLM](https://img.shields.io/badge/Local_LLM-Qwen_2.5_Coder-purple)
![Docker](https://img.shields.io/badge/Docker-Sandbox-2496ED?logo=docker)

Tectonic is a closed-loop, multi-agent AI system designed to automatically detect, diagnose, and remediate broken Infrastructure-as-Code (IaC) deployments before they hit production. 

By leveraging **LangGraph** for state orchestration, **Retrieval-Augmented Generation (RAG)** for syntax grounding, and localized **Docker** environments for safe code execution, Tectonic turns catastrophic pipeline failures into automated, self-healing Pull Requests.

---

## 🚀 Key Features

* **🧠 Multi-Agent Architecture:** Utilizes specialized agents (Observer, Engineer, and Reviewer) to parse stack traces, generate fixes, and validate security.
* **📚 RAG-Grounded Inference:** Prevents LLM hallucinations by querying a local Vector DB (ChromaDB) for official infrastructure documentation prior to generating fixes.
* **🛡️ Ephemeral Sandbox Validation:** Never pushes untested code. Tectonic spins up local Docker containers to execute and validate the AI's fixes. If the test fails, the agentic loop self-corrects based on the new error log.
* **🔒 Zero-Trust Local Inference:** Runs inference locally via Ollama (`qwen2.5-coder:7b`) to ensure sensitive enterprise infrastructure code is never sent to public APIs.
* **🔄 GitOps Integration:** Automatically pushes validated fixes to the repository and opens detailed Pull Requests.

---

## 🏗️ System Architecture (The Self-Healing Loop)

The core engine is built on a LangGraph state machine passing strictly typed `Pydantic` models between nodes:

1. **Failure Detected:** CI/CD triggers Tectonic upon an IaC crash.
2. **Observer Node:** Extracts pure stack traces from raw logs.
3. **RAG Node:** Fetches relevant Docker/Terraform documentation.
4. **Engineer Node:** Diagnoses the root cause and generates a fix using `qwen2.5-coder:7b`.
5. **Sandbox Node:** Executes the fix locally. 
    * ❌ *If failed:* Routes the new error back to the Engineer (The Loop).
    * ✅ *If successful:* Proceeds to execution.
6. **GitOps Node:** Opens a GitHub PR with the validated code.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Orchestration** | `LangGraph` | Manages the multi-agent state machine and cyclic failure loops. |
| **Inference Engine** | `Ollama` + `Qwen 2.5` | Handles local LLM code generation and log diagnosis. |
| **Data Validation** | `Pydantic` | Enforces strict JSON structures on the LLM's output. |
| **Vector Database** | `ChromaDB` | Stores IaC documentation for RAG. |
| **Sandbox Environment**| `Docker Engine` | Spins up ephemeral containers to test generated fixes. |

---

## 🏁 Getting Started

### Prerequisites
* Windows Subsystem for Linux (WSL2) or standard Linux environment.
* Python 3.10+
* Docker Desktop (with WSL integration enabled)
* Ollama installed on the Host machine with the Qwen 2.5 Coder model (`ollama run qwen2.5-coder:7b`)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YourUsername/Tectonic.git
   cd Tectonic
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify LLM Connection**
   Ensure your host machine is running Ollama, and test the WSL bridge:
   ```bash
   python3 test_connection.py
   ```
