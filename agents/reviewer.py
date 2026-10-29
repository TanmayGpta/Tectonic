from state import PipelineState
import time
from sandbox.executor import validate_iac
from metrics import SANDBOX_VALIDATIONS, SANDBOX_DURATION, iac_kind

def sandbox_node(state: PipelineState) -> PipelineState:
    """Takes the AI's proposed code and tests it safely inside an isolated Docker container."""
    target_file = state.get("target_file", "docker-compose.yml")
    print(f"\n🛡️ [Sandbox Agent]: Validating proposed code for '{target_file}' in isolated container...")
    
    # Run the code through our Docker sandbox dispatcher (docker/compose or hashicorp/terraform)
    start = time.perf_counter()
    result = validate_iac(state["proposed_code"], target_file)
    SANDBOX_DURATION.labels(iac_kind(target_file)).observe(time.perf_counter() - start)
    SANDBOX_VALIDATIONS.labels(iac_kind(target_file), result["status"]).inc()
    
    new_state = {
        "sandbox_status": result["status"],
        "sandbox_logs": result.get("logs", ""),
        "retry_count": state.get("retry_count", 0) + 1
    }
    
    # If it failed, feed the compiler/linter error log back into the state so Engineer can reflect and correct!
    if result["status"] == "FAIL":
        new_state["error_logs"] = result["logs"]
        
    return new_state
