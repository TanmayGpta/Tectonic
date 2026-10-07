from state import PipelineState
from utils import query_llm

def explainer_node(state: PipelineState) -> PipelineState:
    """
    Explainable AI (XAI) Diagnostic Agent.
    Synthesizes a structured root-cause explanation highlighting why the original
    code caused compiler failure, the parser mechanics involved, and why the
    remediated code restores compliance.
    """
    target = state.get("target_file", "docker-compose.yml")
    print(f"\n🧠 [Explainer Agent (XAI)]: Synthesizing root-cause diagnostic for '{target}'...")
    
    error = state.get("error_logs", "")
    original = state.get("original_code", "")
    proposed = state.get("proposed_code", "")
    model_choice = state.get("model_choice", "ollama:qwen2.5-coder:3b")
    
    prompt = f"""You are an elite Explainable AI (XAI) DevOps Root-Cause Analyst.
Analyze the infrastructure failure and the validated remediation below:

TARGET MANIFEST:
{target}

COMPILER / RUNTIME ERROR:
{error}

ORIGINAL BROKEN MANIFEST:
{original}

AUTONOMOUSLY REMEDIATED CODE (SANDBOX APPROVED):
{proposed}

Provide a crisp, professional, high-signal technical explanation formatted in Markdown with these three sections:

### 1. Root Cause Analysis
Explain the exact token, syntax, or type discrepancy in the original manifest that triggered the incident.

### 2. Compiler & Parser Mechanics
Explain what the Docker Compose or HashiCorp Terraform parser encountered and why the runtime rejected the configuration (e.g. key-value map vs array sequence, scalar string vs list of strings).

### 3. Remediation & Verification Impact
Explain what precise structural change was made to resolve the crash and how it guarantees specification conformance.

Keep your explanation clear, educational, and concise. Do not reprint the entire code.
"""

    explanation = query_llm(prompt, model_choice=model_choice, is_json=False, temperature=0.1)
    return {"explanation": explanation}
