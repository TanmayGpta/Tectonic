import os
import requests
import chromadb

WINDOWS_IP = "172.22.16.1"

def inject_proprietary_rule():
    db_path = os.path.join(os.path.dirname(__file__), "vector_db", "chroma_storage")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="iac_docs")
    
    rule_text = """COMPANY COMPLIANCE RULE: 
All docker-compose services must define a custom label 'x-company-status: tectonic-approved'. 
If a docker-compose file is missing this label under a service, you must add it to pass validation."""

    embed_payload = {"model": "nomic-embed-text", "prompt": rule_text}
    embed_res = requests.post(f"http://{WINDOWS_IP}:11434/api/embeddings", json=embed_payload).json()
    
    collection.add(
        ids=["proprietary_rule_1"],
        embeddings=[embed_res["embedding"]],
        documents=[rule_text],
        metadatas=[{"source": "internal_compliance"}]
    )
    print("✅ Proprietary rule injected into ChromaDB!")

if __name__ == "__main__":
    inject_proprietary_rule()
