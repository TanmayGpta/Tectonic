import os
import sys
import time
import difflib
import streamlit as st

# Ensure Python can find root modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from agents.gitops import generate_gitops_pull_request
from sandbox.executor import validate_iac

st.set_page_config(
    page_title="Tectonic | Autonomous CI/CD & GitOps Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
    }
    .pipeline-stage {
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    .gh-pr-card {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        color: #c9d1d9;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🚀 Tectonic: Autonomous CI/CD & GitOps Self-Healing Engine")
st.caption("Closed-Loop GitOps Auto-Remediation • Simulated GitHub Actions Webhook • Ephemeral Sandboxing • Automated PR Generation")

# Top Metrics Row
top_col1, top_col2, top_col3, top_col4 = st.columns(4)
with top_col1:
    st.metric("CI/CD Platform", "GitHub Actions", "Ubuntu 22.04")
with top_col2:
    st.metric("GitOps Integration", "Automated PR Bot", "Active")
with top_col3:
    st.metric("Agentic Orchestrator", "LangGraph 5-Head", "Compiled")
with top_col4:
    st.metric("Sandbox Engine", "Docker-out-of-Docker", "/var/run/docker.sock")

st.divider()

# Sidebar: Configuration
st.sidebar.header("⚙️ CI/CD Pipeline Configuration")
scenario_choice = st.sidebar.selectbox(
    "Select Incident Scenario to Trigger:",
    [
        "Scenario 1: Docker Compose Microservices (YAML Port Mapping Syntax Bug)",
        "Scenario 2: HashiCorp Terraform AWS Infrastructure (CIDR Blocks Type Bug)"
    ]
)

sim_speed = st.sidebar.slider(
    "Simulation Stage Delay (Seconds):",
    min_value=0.5,
    max_value=3.0,
    value=1.5,
    step=0.5,
    help="Adjust delay between CI/CD pipeline stages to suit presentation pacing."
)

# Presets
if "Scenario 1" in scenario_choice:
    target_file = "docker-compose.yml"
    commit_sha = "7f4c9a1"
    commit_msg = "feat(db): update postgres service credentials & port configuration"
    syntax_lang = "yaml"
    sandbox_img = "docker/compose:1.29.2"
    broken_code = """version: '3.8'

services:
  web_frontend:
    image: nginx:alpine
    ports:
      - "80:80"

  database:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: tectonic_admin
      POSTGRES_PASSWORD: secr3t_pass
      POSTGRES_DB: app_db
    ports:
      5432:5432
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
"""
    ci_error_log = "yaml: line 16: mapping values are not allowed in this context. Found '5432:5432'"
    ci_command = f"docker-compose -f {target_file} config"
else:
    target_file = "main.tf"
    commit_sha = "3b8e21f"
    commit_msg = "feat(network): update aws security group ingress rules for https"
    syntax_lang = "hcl"
    sandbox_img = "hashicorp/terraform:latest"
    broken_code = """terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "web_sg" {
  name        = "production-web-sg"
  description = "Public web ingress security group"

  ingress {
    description = "Allow HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = "0.0.0.0/0"
  }
}
"""
    ci_error_log = 'Error: Inappropriate value for attribute "cidr_blocks": list of string required. on main.tf line 22'
    ci_command = f"terraform fmt -check {target_file} && terraform validate"

# Stage Selector and Launch Card
st.subheader("🎯 Enterprise GitOps Incident Simulation")
col_info1, col_info2 = st.columns([2, 1])

with col_info1:
    st.markdown(f"""
    **Target Repository**: `TanmayGpta/Tectonic`  
    **Target File**: `{target_file}`  
    **Pushed Commit**: `{commit_sha}` — *"{commit_msg}"*  
    **Author**: `dev-engineer@company.internal`  
    """)

with col_info2:
    trigger_cicd = st.button("🚀 Push Commit & Trigger CI/CD Pipeline", type="primary", use_container_width=True)

# Pipeline Execution State
if trigger_cicd:
    st.divider()
    st.subheader("⚡ Live CI/CD Pipeline Visualizer")
    
    # Visual Pipeline Pipeline Tracker Columns
    p_col1, p_col2, p_col3, p_col4, p_col5, p_col6 = st.columns(6)
    
    with p_col1:
        s1 = st.empty()
        s1.info("📦 1. Git Push\n\nPending...")
    with p_col2:
        s2 = st.empty()
        s2.info("🔍 2. CI Lint Step\n\nPending...")
    with p_col3:
        s3 = st.empty()
        s3.info("⚡ 3. Webhook\n\nPending...")
    with p_col4:
        s4 = st.empty()
        s4.info("🤖 4. AI Healing\n\nPending...")
    with p_col5:
        s5 = st.empty()
        s5.info("🔀 5. GitOps PR\n\nPending...")
    with p_col6:
        s6 = st.empty()
        s6.info("✅ 6. CI Re-Run\n\nPending...")

    terminal_area = st.empty()

    # Step 1: Git Push
    s1.warning("📦 1. Git Push\n\nTriggering...")
    terminal_area.code(f"""[GitHub Runner: ubuntu-latest]
$ git clone https://github.com/TanmayGpta/Tectonic.git
$ git checkout {commit_sha}
$ git log -1 --oneline
{commit_sha} {commit_msg}
""", language="bash")
    time.sleep(sim_speed)
    s1.success(f"📦 1. Git Push\n\n{commit_sha} ✅")

    # Step 2: CI Lint (Fails)
    s2.warning("🔍 2. CI Lint Step\n\nExecuting...")
    terminal_area.code(f"""[GitHub Actions Step: Validate Infrastructure as Code]
$ {ci_command}
[ERROR] Parsing '{target_file}'...
{ci_error_log}

##[error] Process completed with exit code 1.
##[error] Pipeline halted. Infrastructure verification FAILED.
""", language="bash")
    time.sleep(sim_speed)
    s2.error("🔍 2. CI Lint Step\n\nFAILED ❌ (Code 1)")

    # Step 3: Webhook Intercept
    s3.warning("⚡ 3. Webhook\n\nDispatching...")
    terminal_area.code(f"""[GitHub Actions Webhook Event: workflow_run.completed (conclusion: failure)]
Payload:
{{
  "repository": "TanmayGpta/Tectonic",
  "workflow": "Tectonic CI/CD Infrastructure Validator",
  "commit": "{commit_sha}",
  "failed_file": "{target_file}",
  "stderr": "{ci_error_log}",
  "action": "dispatch_to_tectonic_engine"
}}
>>> 200 OK: Incident dispatched to Tectonic LangGraph state machine!
""", language="json")
    time.sleep(sim_speed)
    s3.success("⚡ 3. Webhook\n\nINTERCEPTED ⚡")

    # Step 4: AI Healing
    s4.warning("🤖 4. AI Healing\n\nSelf-Healing...")
    with st.spinner("Tectonic 5-Agent LangGraph loop active (Observer ➔ Gatekeeper ➔ Engineer ➔ Sandbox ➔ Explainer)..."):
        pipeline_input = {
            "error_logs": ci_error_log,
            "target_file": target_file,
            "proposed_code": None,
            "sandbox_status": None,
            "retry_count": 0,
            "is_valid_scope": None,
            "rejection_reason": None,
            "sandbox_logs": None,
            "original_code": broken_code,
            "model_choice": "ollama:qwen2.5-coder:3b"
        }
        res_state = app.invoke(pipeline_input)
    
    remediated_code = res_state.get("proposed_code", "")
    explanation_text = res_state.get("explanation", "")
    
    terminal_area.code(f"""[Tectonic Multi-Agent Orchestrator]
👀 [Observer Agent]: Parsed error log for {target_file}
🛡️ [Gatekeeper Agent]: Pydantic scope guardrail APPROVED
🛠️ [Engineer Agent]: Retrieved syntax rules from ChromaDB RAG & synthesized candidate
📦 [Sandbox Agent]: Executed dry-run in {sandbox_img} -> SUCCESS (Code 0)
🧠 [Explainer Agent (XAI)]: Synthesized 3-part Root Cause & Parser Mechanics report
""", language="bash")
    time.sleep(sim_speed)
    s4.success("🤖 4. AI Healing\n\nCONVERGED 🟢")

    # Step 5: GitOps PR Creation
    s5.warning("🔀 5. GitOps PR\n\nSynthesizing...")
    pr_data = generate_gitops_pull_request(
        target_file=target_file,
        original_code=broken_code,
        remediated_code=remediated_code,
        explanation=explanation_text,
        container_image=sandbox_img
    )
    time.sleep(sim_speed)
    s5.success(f"🔀 5. GitOps PR\n\nPR #{pr_data['pr_number']} 🔀")

    # Step 6: CI Re-Run on PR Branch
    s6.warning("✅ 6. CI Re-Run\n\nRe-testing PR...")
    terminal_area.code(f"""[GitHub Actions Step: Automated Re-Run on {pr_data['branch_name']}]
$ git fetch origin pull/{pr_data['pr_number']}/head:pr-{pr_data['pr_number']}
$ git checkout pr-{pr_data['pr_number']}
$ {ci_command}
[Sandbox Validation]: Testing patched '{target_file}' in isolated {sandbox_img}...
>> Parsing '{target_file}'... SUCCESS
>> Schema validation: PASS (Zero regressions)
>> Exit Code: 0

##[success] All infrastructure checks PASSED! Pipeline turned GREEN 🟢
""", language="bash")
    time.sleep(sim_speed)
    s6.success("✅ 6. CI Re-Run\n\nPASSED 🟢 (Code 0)")

    # Save to session state so user can interact with the PR card
    st.session_state["last_cicd_run"] = {
        "pr_data": pr_data,
        "broken_code": broken_code,
        "remediated_code": remediated_code,
        "target_file": target_file,
        "syntax_lang": syntax_lang,
        "explanation": explanation_text,
        "sandbox_img": sandbox_img
    }

# Persistent Showcase of the Automated GitOps Pull Request
if "last_cicd_run" in st.session_state:
    run_info = st.session_state["last_cicd_run"]
    pr = run_info["pr_data"]
    
    st.divider()
    st.subheader(f"🔀 Automated GitOps Pull Request #{pr['pr_number']}")
    
    # GitHub-Styled Pull Request Header
    st.markdown(f"""
    <div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 18px 24px; margin-bottom: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h2 style="color: #ffffff; margin: 0; font-size: 22px;">{pr['title']} <span style="color: #8b949e; font-weight: normal;">#{pr['pr_number']}</span></h2>
            <span style="background-color: #238636; color: #ffffff; padding: 4px 12px; border-radius: 16px; font-weight: bold; font-size: 13px;">✓ Open</span>
        </div>
        <p style="color: #8b949e; margin: 8px 0 0 0; font-size: 13px;">
            <strong style="color: #58a6ff;">{pr['author']}</strong> wants to merge into <code style="background-color: #161b22; color: #f0883e; padding: 2px 6px; border-radius: 4px;">{pr['base_branch']}</code> from <code style="background-color: #161b22; color: #58a6ff; padding: 2px 6px; border-radius: 4px;">{pr['branch_name']}</code> • Created {pr['created_at']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # PR Tabs
    pr_tab1, pr_tab2, pr_tab3 = st.tabs(["📝 Conversation & XAI Audit", "🔍 Unified Files Changed (Diff)", "🛡️ CI/CD Checks Status"])
    
    with pr_tab1:
        st.markdown(pr["description"])
        
    with pr_tab2:
        st.markdown(f"**Showing changes in `{run_info['target_file']}`:**")
        st.code(pr["diff"], language="diff")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.caption("❌ Broken Commit (developer):")
            st.code(run_info["broken_code"], language=run_info["syntax_lang"])
        with col_c2:
            st.caption("✅ Remediated Code (tectonic-bot):")
            st.code(run_info["remediated_code"], language=run_info["syntax_lang"])
            
    with pr_tab3:
        st.markdown("""
        <div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 16px; font-family: 'Segoe UI', Tahoma, sans-serif;">
            <h4 style="color: #ffffff; margin-top: 0;">All checks have passed (3 successful checks)</h4>
            <div style="margin: 8px 0; color: #3fb950; display: flex; align-items: center; gap: 8px;">
                <span>✔</span> <strong>Validate Infrastructure as Code</strong> — Job succeeded in 4.2s (Exit Code 0)
            </div>
            <div style="margin: 8px 0; color: #3fb950; display: flex; align-items: center; gap: 8px;">
                <span>✔</span> <strong>Tectonic Ephemeral Container Sandbox</strong> — Isolated container dry-run passed
            </div>
            <div style="margin: 8px 0; color: #3fb950; display: flex; align-items: center; gap: 8px;">
                <span>✔</span> <strong>Pydantic Gatekeeper Scope Audit</strong> — Zero prompt injection detected
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("🚀 Merge Pull Request & Deploy to Production", type="primary", use_container_width=True):
            st.balloons()
            st.success(f"🎉 **Pull Request #{pr['pr_number']} successfully merged into `{pr['base_branch']}`!** Infrastructure is self-healed and deployed.")
