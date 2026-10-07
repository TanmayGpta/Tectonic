import time
import hashlib
import difflib

def generate_gitops_pull_request(
    target_file: str,
    original_code: str,
    remediated_code: str,
    explanation: str = "",
    container_image: str = "docker/compose:1.29.2"
) -> dict:
    """
    Synthesizes an enterprise-grade GitOps Pull Request payload.
    Emulates an automated GitOps bot creating a self-healing branch,
    generating commit metadata, and attaching XAI root-cause diagnostics.
    """
    timestamp_id = int(time.time())
    short_hash = hashlib.sha256(f"{target_file}{timestamp_id}".encode()).hexdigest()[:7]
    branch_name = f"tectonic/auto-heal-{target_file.replace('.', '-')}-{short_hash}"
    
    # Calculate unified diff
    diff_lines = list(difflib.unified_diff(
        original_code.splitlines(keepends=True),
        remediated_code.splitlines(keepends=True),
        fromfile=f"a/{target_file}",
        tofile=f"b/{target_file}"
    ))
    diff_text = "".join(diff_lines) if diff_lines else "# No line changes detected"
    
    # Generate clean PR title
    if "docker" in target_file.lower():
        title = f"fix(compose): auto-remediate syntax & port mappings in {target_file}"
    elif "tf" in target_file.lower() or "terraform" in target_file.lower():
        title = f"fix(terraform): auto-remediate schema & type constraints in {target_file}"
    else:
        title = f"fix(iac): autonomous self-healing patch for {target_file}"
        
    # Generate clean Markdown description
    description = f"""## 🌋 Tectonic Autonomous Remediation

### 📋 Overview
An automated infrastructure compilation failure was intercepted by Tectonic's CI/CD listener. 
The 5-Agent LangGraph engine autonomously diagnosed the error, synthesized a verified fix, and confirmed zero regression inside an ephemeral sandbox container (`{container_image}`).

---

### 🔍 Unified Git Diff
```diff
{diff_text}
```

---

### 🧠 Explainable AI (XAI) Diagnostic Audit
{explanation if explanation else "Automated remediation verified against official infrastructure schema."}

---

### 🛡️ Verification Evidence
* **Sandbox Runtime**: Ephemeral container `{container_image}`
* **Exit Status**: `SUCCESS` (Code 0)
* **Pydantic Guardrail**: `APPROVED`
* **Autonomous Engine**: Tectonic LangGraph Closed-Loop Multi-Agent State Machine
"""

    return {
        "pr_number": 100 + (timestamp_id % 900),
        "branch_name": branch_name,
        "base_branch": "main",
        "author": "tectonic-bot 🤖",
        "title": title,
        "description": description,
        "diff": diff_text,
        "target_file": target_file,
        "commit_hash": short_hash,
        "status": "OPEN",
        "checks_passed": True,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())
    }
