import json
import requests
from pydantic import BaseModel, Field, ValidationError
from state import PipelineState

WINDOWS_IP = "host.docker.internal"

# ==========================================
# PYDANTIC GUARDRAIL SCHEMA
# ==========================================
class ScopeValidation(BaseModel):
    is_valid_iac: bool = Field(description="True ONLY if the input is related to Docker, Terraform, CI/CD, or infrastructure code. False otherwise.")
    reason: str = Field(description="A 1-sentence explanation of why it was approved or rejected.")

def gatekeeper_node(state: PipelineState) -> PipelineState:
    """The Input Guardrail. Uses Pydantic to ensure the user isn't asking out-of-scope questions."""
    print("\n🛡️ [Gatekeeper]: Validating input scope using Pydantic Guardrails...")
    
    prompt = f"""You are a strict Security Gatekeeper for a DevOps CI/CD pipeline.
Evaluate the following user input/error log:

"{state['error_logs']}"

Determine if this input is related to Infrastructure-as-Code (Docker, Terraform, YAML parsing, CI/CD, etc).
If they ask a general knowledge question (like 'what is the capital of France' or 'write a python script'), you MUST reject it.

You MUST respond with ONLY raw, valid JSON matching this schema:
{{
    "is_valid_iac": true or false,
    "reason": "your explanation"
}}
"""
    
    # We explicitly tell Ollama to force JSON formatting
    payload = {"model": "qwen2.5-coder:3b", "prompt": prompt, "stream": False, "format": "json"}
    
    try:
        res = requests.post(f"http://{WINDOWS_IP}:11434/api/generate", json=payload).json()
        
        # ==========================================
        # PYDANTIC IN ACTION
        # ==========================================
        # This line forces the LLM's raw text into a strict Python object. 
        # If the LLM hallucinated, this instantly throws an error.
        validation_result = ScopeValidation.model_validate_json(res["response"])
        
        return {
            "is_valid_scope": validation_result.is_valid_iac,
            "rejection_reason": validation_result.reason if not validation_result.is_valid_iac else ""
        }
        
    except ValidationError as e:
        # If Pydantic catches a hallucination, we fail-safe and reject the input.
        print(f"⚠️ [Gatekeeper]: Pydantic validation failed! Rejecting input for safety. Error: {e}")
        return {"is_valid_scope": False, "rejection_reason": "Failed security formatting check (Pydantic ValidationError)."}
    except Exception as e:
        return {"is_valid_scope": False, "rejection_reason": f"System error: {e}"}
