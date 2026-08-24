import streamlit as st
from main import app
import time

# UI Configuration
st.set_page_config(page_title="Tectonic AI", page_icon="🌋", layout="wide")

st.title("🌋 Tectonic: Agentic Auto-Remediation")
st.markdown("Watch the multi-agent LangGraph pipeline autonomously diagnose, rewrite, and validate broken infrastructure code.")

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Pipeline Orchestrator")
    trigger = st.button("🔥 Simulate CI/CD Pipeline Failure", type="primary")

with col2:
    st.subheader("Live State Memory")
    state_box = st.empty()
    state_box.info("Waiting for pipeline to start...")

if trigger:
    st.divider()
    st.subheader("Live Agent Activity")
    
    # Initialize empty state
    initial_state = {
        "error_logs": "",
        "target_file": "",
        "proposed_code": None,
        "sandbox_status": None,
        "retry_count": 0
    }
    
    log_container = st.container()
    
    # Stream the graph execution step-by-step
    with st.spinner("Pipeline active... Qwen is thinking..."):
        for output in app.stream(initial_state):
            for node_name, node_state in output.items():
                
                # Update the live JSON memory box
                state_box.json(node_state)
                
                with log_container:
                    if node_name == "observer":
                        st.error(f"👀 **Observer Agent**: Detected pipeline failure in `{node_state.get('target_file')}`\n\n`{node_state.get('error_logs')}`")
                        
                    elif node_name == "engineer":
                        st.warning(f"🛠️ **Engineer Agent (Attempt {node_state.get('retry_count')})**: Retrieving RAG context and generating fix via Qwen...")
                        with st.expander("View Generated Code"):
                            st.code(node_state.get("proposed_code"), language="yaml")
                            
                    elif node_name == "sandbox":
                        if node_state.get("sandbox_status") == "SUCCESS":
                            st.success("🛡️ **Sandbox Agent**: Validation Passed! Code executed successfully in isolated Docker container.")
                        else:
                            st.error(f"🛡️ **Sandbox Agent**: Validation Failed! Intercepted error:\n\n`{node_state.get('error_logs')}`")
                            st.info("🔄 **Router**: Rejecting code and sending error log back to Engineer...")
                
                # Tiny artificial delay so the UI doesn't flash instantly
                time.sleep(0.5) 
                
    st.balloons()
