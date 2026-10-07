from typing import TypedDict, Optional

class PipelineState(TypedDict):
    """The shared memory object passed between all LangGraph agents."""
    error_logs: str
    target_file: str
    proposed_code: Optional[str]
    sandbox_status: Optional[str]
    retry_count: int
    
    # Guardrail, Sandbox & Telemetry States
    is_valid_scope: Optional[bool]
    rejection_reason: Optional[str]
    sandbox_logs: Optional[str]
    original_code: Optional[str]
    model_choice: Optional[str]
    
    # Explainable AI (XAI) State
    explanation: Optional[str]
