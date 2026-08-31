from typing import TypedDict, Optional

class PipelineState(TypedDict):
    """The shared memory object passed between all LangGraph agents."""
    error_logs: str
    target_file: str
    proposed_code: Optional[str]
    sandbox_status: Optional[str]
    retry_count: int
    
    # New Guardrail States
    is_valid_scope: Optional[bool]
    rejection_reason: Optional[str]
