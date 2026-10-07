import os
import re
import requests
import chromadb
from state import PipelineState
from utils import get_ollama_host, query_llm

def clean_code_fence(raw_text: str) -> str:
    """Strips markdown code fences (```yaml ... ```) if the LLM output includes them."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text

def engineer_node(state: PipelineState) -> PipelineState:
    """Performs RAG to fetch official docs, then prompts Qwen LLM to remediate the code."""
    host = get_ollama_host()
    retry_count = state.get("retry_count", 0) + 1
    target_file = state.get("target_file", "docker-compose.yml")
    original_code = state.get("original_code", "")
    error = state.get("error_logs", "")
    
    print(f"\n🛠️ [Engineer Agent]: Diagnosing issue for '{target_file}' (Attempt {retry_count})...")
    
    # 1. RAG RETRIEVAL FROM CHROMADB
    print("   🔍 Searching ChromaDB Knowledge Base for related syntax rules...")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_db", "chroma_storage")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name="iac_docs")
    
    # Enrich the embedding query with the target file context
    query_text = f"{target_file} error: {error}"
    embed_payload = {"model": "nomic-embed-text", "prompt": query_text}
    embed_res = requests.post(f"http://{host}:11434/api/embeddings", json=embed_payload, timeout=20).json()
    
    # Retrieve the top 2 matching context chunks
    results = collection.query(query_embeddings=[embed_res["embedding"]], n_results=2)
    retrieved_docs = results.get("documents", [[]])[0]
    context = "\n\n".join(retrieved_docs) if retrieved_docs else "Refer to standard syntax specifications."

    # 2. LLM PROMPTING WITH CONTEXT & ORIGINAL MANIFEST
    is_tf = target_file.endswith(".tf") or "terraform" in target_file.lower()
    iac_type = "HashiCorp Terraform (HCL)" if is_tf else "Docker Compose (YAML)"
    
    print(f"   🧠 Asking Qwen Coder to generate verified {iac_type} fix...")
    prompt = f"""You are an elite Site Reliability Engineer and Infrastructure-as-Code compiler expert.
Your task is to fix the syntax or configuration error in the provided {target_file} manifest based on the official documentation rules.

TARGET FILE:
{target_file} ({iac_type})

ERROR LOG:
{error}

OFFICIAL DOCUMENTATION RULES:
{context}

ORIGINAL MANIFEST CODE:
{original_code}

INSTRUCTIONS:
1. Maintain the full structure and all services/resources of the original code.
2. Fix the exact syntax or type error identified in the error log.
3. Respond ONLY with the complete, fixed raw {target_file} code.
4. Do NOT output markdown code fences (like ```), markdown formatting, or explanations. Return raw code only.
"""
    
    model_choice = state.get("model_choice", "ollama:qwen2.5-coder:3b")
    print(f"   🧠 Synthesizing remediated code using [{model_choice}]...")
    raw_response = query_llm(prompt, model_choice=model_choice, is_json=False, temperature=0.1)
    fixed_code = clean_code_fence(raw_response)
    
    return {"proposed_code": fixed_code}
