import json
import requests
from pydantic import BaseModel, Field, ValidationError
from state import PipelineState
from utils import get_ollama_host, query_llm

# ==========================================
# PYDANTIC GUARDRAIL SCHEMA
# ==========================================
class ScopeValidation(BaseModel):
    is_valid_iac: bool = Field(description="Set to true if the text is an error log, YAML, Docker, Terraform, HCL, or infrastructure code. Set to false for random conversation.")
    reason: str = Field(description="A short explanation.")

def gatekeeper_node(state: PipelineState) -> PipelineState:
    """The Input Guardrail. Uses deterministic fast-path rules and Pydantic Guardrails to ensure safety."""
    print("\n🛡️ [Gatekeeper]: Validating input scope using Pydantic Guardrails...")
    
    error_input = state.get("error_logs", "").strip()
    
    # 1. Deterministic Heuristic Evaluation (Fast Path)
    chat_triggers = [
        "capital of", "poem", "joke", "weather", "who are you", "story about",
        "how are you", "tell me a", "recipe", "song", "meaning of life"
    ]
    iac_indicators = [
        "yaml:", "mapping values", "docker", "ports", "error", "traceback",
        "exception", "failed", "exit code", "terraform", "syntax", "hcl",
        "provider", "resource", "cidr_blocks", "aws_", "ingress", "egress",
        "inappropriate value", "did not find expected key", "line ", "attribute",
        "unsupported argument", "missing mandatory label", "compliance error"
    ]
    
    is_obvious_chat = any(q in error_input.lower() for q in chat_triggers)
    is_obvious_iac = any(k in error_input.lower() for k in iac_indicators)
    
    if is_obvious_iac and not is_obvious_chat:
        return {
            "is_valid_scope": True,
            "rejection_reason": ""
        }
    
    if is_obvious_chat:
        return {
            "is_valid_scope": False,
            "rejection_reason": "Out-of-scope conversational prompt detected. Only DevOps/IaC incident logs and manifests are permitted."
        }

    # 2. LLM-Assisted Classification with Few-Shot Guidance & Zero Temperature
    prompt = f"""You are a DevOps Security Gatekeeper.
Classify whether the following input is a DevOps/infrastructure error log or code vs out-of-scope conversational chat.

Examples of VALID (is_valid_iac = true):
- "yaml: line 4: mapping values are not allowed in this context. Found '5432:5432'" -> true
- "docker-compose build failed with exit code 1" -> true
- "Error: invalid configuration parameter 'ports'" -> true
- "Error: Inappropriate value for attribute 'cidr_blocks': list of string required." -> true
- "Error: Unsupported argument on main.tf line 36" -> true
- "compliance error: service 'api' is missing mandatory label 'x-company-status'" -> true

Examples of INVALID (is_valid_iac = false):
- "What is the capital of France?" -> false
- "Tell me a joke" -> false
- "Write a poem about clouds" -> false
- "Who won the game yesterday?" -> false

Input:
\"{error_input}\"

Respond ONLY with valid JSON:
{{
    "is_valid_iac": true,
    "reason": "concise explanation"
}}
"""
    
    model_choice = state.get("model_choice", "ollama:qwen2.5-coder:3b")
    try:
        raw_response = query_llm(prompt, model_choice=model_choice, is_json=True, temperature=0.0)
        
        # ==========================================
        # PYDANTIC IN ACTION
        # ==========================================
        validation_result = ScopeValidation.model_validate_json(raw_response)
        
        return {
            "is_valid_scope": validation_result.is_valid_iac,
            "rejection_reason": validation_result.reason if not validation_result.is_valid_iac else ""
        }
        
    except requests.exceptions.ConnectionError:
        host = get_ollama_host()
        print(f"⚠️ [Gatekeeper]: Cannot connect to inference engine ({model_choice}).")
        return {
            "is_valid_scope": False, 
            "rejection_reason": f"Inference engine ({model_choice}) is unreachable. Please verify network or start local Ollama."
        }
    except ValidationError as e:
        print(f"⚠️ [Gatekeeper]: Pydantic validation failed! Rejecting input for safety. Error: {e}")
        return {"is_valid_scope": False, "rejection_reason": "Failed security formatting check (Pydantic ValidationError)."}
    except Exception as e:
        return {"is_valid_scope": False, "rejection_reason": f"System error: {e}"}
