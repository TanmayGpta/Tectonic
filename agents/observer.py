from state import PipelineState

def observer_node(state: PipelineState) -> PipelineState:
    """Ingests failed CI/CD logs and triggers the pipeline."""
    target_file = state.get("target_file", "docker-compose.yml")
    print(f"\n👀 [Observer Agent]: Ingesting incident log for target: {target_file}")
    
    # If error_logs already provided (e.g. from UI scenario), preserve it
    if state.get("error_logs"):
        return {
            "error_logs": state["error_logs"],
            "target_file": target_file,
            "original_code": state.get("original_code"),
            "retry_count": 0
        }
    
    # Default mock syntax error if none provided
    return {
        "error_logs": "yaml: line 4: mapping values are not allowed in this context. Found '5432:5432'",
        "target_file": "docker-compose.yml",
        "retry_count": 0
    }
