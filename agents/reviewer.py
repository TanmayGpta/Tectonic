from state import PipelineState
from sandbox.executor import validate_docker_compose

def sandbox_node(state: PipelineState) -> PipelineState:
    """Takes the AI's proposed code and tests it safely inside an isolated Docker container."""
    print("\n🛡️ [Sandbox Agent]: Validating proposed code in isolated container...")
    
    # Run the code through our actual Docker sandbox engine
    result = validate_docker_compose(state["proposed_code"])
    
    new_state = {
        "sandbox_status": result["status"],
        "retry_count": state.get("retry_count", 0) + 1
    }
    
    # If it failed, we feed the new error log back into the state so Qwen can learn from it!
    if result["status"] == "FAIL":
        new_state["error_logs"] = result["logs"]
        
    return new_state
