import os
import requests
import chromadb
from state import PipelineState

WINDOWS_IP = "172.22.16.1"

def engineer_node(state: PipelineState) -> PipelineState:
    """Performs RAG to fetch official docs, then asks Qwen LLM to fix the code."""
    print(f"\n🛠️ [Engineer Agent]: Diagnosing issue (Attempt {state.get('retry_count', 0) + 1})...")
    error = state["error_logs"]
    
    # --- RAG RETRIEVAL ---
    print("   🔍 Searching Knowledge Base for related syntax rules...")
    # Navigate up one directory since this file is now inside the agents/ folder
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vector_db", "chroma_storage")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name="iac_docs")
    
    embed_payload = {"model": "nomic-embed-text", "prompt": error}
    embed_res = requests.post(f"http://{WINDOWS_IP}:11434/api/embeddings", json=embed_payload).json()
    
    results = collection.query(query_embeddings=[embed_res["embedding"]], n_results=1)
    context = results["documents"][0][0]
    
    # --- LLM PROMPTING ---
    print(f"   🧠 Asking Qwen to generate the fix...")
    prompt = f"""You are an expert DevOps AI. Fix the broken docker-compose code based on the official documentation provided.
    
ERROR LOG:
{error}

OFFICIAL DOCUMENTATION RULES:
{context}

Respond ONLY with the complete, fixed raw code for the docker-compose.yml file. Do not include markdown formatting, backticks (```), or explanations. Just the code.
"""
    
    llm_payload = {
        "model": "qwen2.5-coder:3b",
        "prompt": prompt,
        "stream": False
    }
    llm_res = requests.post(f"http://{WINDOWS_IP}:11434/api/generate", json=llm_payload).json()
    fixed_code = llm_res["response"].strip()
    
    return {"proposed_code": fixed_code}
