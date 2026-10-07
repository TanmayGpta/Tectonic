import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

from main import app
from sandbox.executor import validate_iac
import difflib

def main():
    parser = argparse.ArgumentParser(description="Tectonic Headless CI/CD Autonomous Remediator")
    parser.add_argument("--file", required=True, help="Path to broken IaC file (e.g. docker-compose.yml or main.tf)")
    parser.add_argument("--error-file", help="Path to file containing stderr / CI failure logs")
    parser.add_argument("--error-log", help="Raw error string if not using a log file")
    parser.add_argument("--model", default="groq:qwen/qwen3.8-27b", help="Model selector (default: groq:qwen/qwen3.8-27b for sub-second cloud inference)")
    parser.add_argument("--output-body", default="tectonic_pr_body.md", help="Where to output PR markdown description")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ Error: Target file '{args.file}' does not exist.")
        sys.exit(1)
        
    with open(args.file, "r") as f:
        original_code = f.read()
        
    # Read error log
    error_logs = ""
    if args.error_file and os.path.exists(args.error_file):
        with open(args.error_file, "r") as f:
            error_logs = f.read().strip()
    elif args.error_log:
        error_logs = args.error_log.strip()
    else:
        # Pre-flight run to generate error if none provided
        print(f"🔍 No error log provided. Running pre-flight dry run on '{args.file}'...")
        res = validate_iac(original_code, args.file)
        if res.get("status") == "FAIL":
            error_logs = res.get("logs", "Pre-flight validation failed.")
        else:
            print("✅ File is already valid. No remediation required.")
            sys.exit(0)
            
    print(f"\n🚨 [Tectonic CI Intercept]: Detected failure in '{args.file}':\n{error_logs}\n")
    print(f"🤖 [Tectonic Agentic Core]: Invoking 5-Agent LangGraph loop with model '{args.model}'...")
    
    initial_state = {
        "error_logs": error_logs,
        "target_file": os.path.basename(args.file),
        "proposed_code": None,
        "sandbox_status": None,
        "retry_count": 0,
        "is_valid_scope": None,
        "rejection_reason": None,
        "sandbox_logs": None,
        "original_code": original_code,
        "model_choice": args.model
    }
    
    result = app.invoke(initial_state)
    
    if result.get("sandbox_status") == "SUCCESS":
        remediated_code = result.get("proposed_code", "")
        explanation = result.get("explanation", "")
        
        # 1. Overwrite the file with the sandbox-validated code
        with open(args.file, "w") as f:
            f.write(remediated_code)
            
        print(f"✅ Remediated code successfully written to '{args.file}'.")
        
        # 2. Compute Unified Diff
        diff_lines = list(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            remediated_code.splitlines(keepends=True),
            fromfile=f"a/{args.file}",
            tofile=f"b/{args.file}"
        ))
        diff_text = "".join(diff_lines) if diff_lines else "# No line changes detected"
        
        # 3. Write PR Body Markdown
        pr_markdown = f"""## 🌋 Tectonic Autonomous Remediation

### 📋 Overview
An automated infrastructure syntax failure was detected in `{args.file}` during CI/CD execution.
Tectonic's **5-Agent LangGraph Engine** autonomously diagnosed the root cause, synthesized an AST-compliant fix, and verified zero regression inside an isolated ephemeral sandbox container.

### 🔍 Unified Git Diff
```diff
{diff_text}
```

### 🧠 Explainable AI (XAI) Diagnostic Audit
{explanation}

### 🛡️ Verification Proof
* **Sandbox Verification**: `SUCCESS` (Exit Code 0)
* **Scope Guardrail**: `APPROVED` (Pydantic DevOps Filter)
* **Remediation Engine**: Tectonic Autonomous Multi-Agent State Machine
"""
        with open(args.output_body, "w") as f:
            f.write(pr_markdown)
            
        print(f"📄 Pull Request body written to '{args.output_body}'.")
        sys.exit(0)
    else:
        print("❌ Tectonic was unable to achieve zero-regression remediation within retry limits.")
        sys.exit(1)

if __name__ == "__main__":
    main()
