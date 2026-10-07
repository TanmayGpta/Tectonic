import os
import sys
import glob
import requests
import chromadb

# Ensure parent directory is in Python path for utils import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from utils import get_ollama_host
except ImportError:
    def get_ollama_host():
        return os.getenv("OLLAMA_HOST_IP", "172.22.16.1")

EMBEDDING_MODEL = "nomic-embed-text"

def get_ollama_embed_url() -> str:
    host = get_ollama_host()
    return f"http://{host}:11434/api/embeddings"

def get_embedding(text: str) -> list:
    """Calls Ollama to generate an embedding vector for a given text."""
    url = get_ollama_embed_url()
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["embedding"]

def build_knowledge_base():
    """
    Automatically discovers and ingests all IaC documentation in docs/
    (Docker Compose, HashiCorp Terraform AWS & Core HCL syntax rules)
    into persistent ChromaDB storage.
    """
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
    doc_files = glob.glob(os.path.join(docs_dir, "*.txt")) + glob.glob(os.path.join(docs_dir, "*.md"))
    
    print(f"📚 Discovered {len(doc_files)} documentation manifest(s) in {docs_dir}:")
    for fpath in doc_files:
        print(f"   • {os.path.basename(fpath)}")

    # Initialize ChromaDB persistent storage
    db_path = os.path.join(os.path.dirname(__file__), "chroma_storage")
    print(f"\n🗄️ Initializing ChromaDB persistent storage at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    
    try:
        client.delete_collection("iac_docs")
        print("   ♻️ Cleared existing 'iac_docs' collection.")
    except Exception:
        pass
        
    collection = client.create_collection(name="iac_docs")
    
    total_embedded = 0
    host = get_ollama_host()
    print(f"🧠 Querying Ollama embedding engine ({EMBEDDING_MODEL}) at http://{host}:11434 ...")

    for file_path in doc_files:
        filename = os.path.basename(file_path)
        iac_type = "terraform" if "terraform" in filename.lower() else "docker-compose"
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split into logical sections by double-newlines
        raw_chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
        print(f"\n📄 Processing '{filename}' ({iac_type}): {len(raw_chunks)} sections found")

        for i, chunk in enumerate(raw_chunks):
            # Skip tiny headers or empty fragments
            if len(chunk) < 20:
                continue
                
            chunk_id = f"{os.path.splitext(filename)[0]}_chunk_{i}"
            try:
                embedding = get_embedding(chunk)
                collection.add(
                    ids=[chunk_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        "source": filename,
                        "iac_type": iac_type,
                        "chunk_index": i
                    }]
                )
                total_embedded += 1
                print(f"   ✓ Embedded [{iac_type}] chunk {i+1}/{len(raw_chunks)}")
            except Exception as e:
                print(f"   ❌ Failed to embed chunk {i}: {e}")

    print(f"\n✅ Knowledge Base built successfully! {total_embedded} total chunks persisted in ChromaDB.")

if __name__ == "__main__":
    build_knowledge_base()
