from state import PipelineState
from sandbox.executor import validate_iac

def sandbox_node(state: PipelineState) -> PipelineState:
    """Takes the AI's proposed code and tests it safely inside an isolated Docker container."""
    target_file = state.get("target_file", "docker-compose.yml")
    print(f"\n🛡️ [Sandbox Agent]: Validating proposed code for '{target_file}' in isolated container...")
    
    # Run the code through our Docker sandbox dispatcher (docker/compose or hashicorp/terraform)
    result = validate_iac(state["proposed_code"], target_file)
    
    new_state = {
        "sandbox_status": result["status"],
        "sandbox_logs": result.get("logs", ""),
        "retry_count": state.get("retry_count", 0) + 1
    }
    
    # If it failed, feed the compiler/linter error log back into the state so Engineer can reflect and correct!
    if result["status"] == "FAIL":
        new_state["error_logs"] = result["logs"]
        
    return new_state
