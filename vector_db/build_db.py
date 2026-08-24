import requests
import chromadb
import os

# Configuration
WINDOWS_IP = "172.22.16.1"
OLLAMA_EMBED_URL = f"http://{WINDOWS_IP}:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"

def get_embedding(text: str):
    """Calls Ollama to generate an embedding vector for a given text."""
    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text
    }
    response = requests.post(OLLAMA_EMBED_URL, json=payload)
    response.raise_for_status()
    return response.json()["embedding"]

def build_knowledge_base():
    print("📚 Reading documentation...")
    # 1. Read our Knowledge Base Document
    doc_path = os.path.join(os.path.dirname(__file__), "..", "docs", "docker_compose_syntax.txt")
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Chunking
    # We simply split by double-newlines to separate the different topics
    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
    
    print(f"🔪 Chunked document into {len(chunks)} pieces.")

    # 3. Initialize ChromaDB
    print("🗄️ Initializing ChromaDB storage...")
    db_path = os.path.join(os.path.dirname(__file__), "chroma_storage")
    client = chromadb.PersistentClient(path=db_path)
    
    # Create or reset a collection named "iac_docs"
    try:
        client.delete_collection("iac_docs")
    except Exception:
        pass # Collection didn't exist yet
        
    collection = client.create_collection(name="iac_docs")

    # 4. Generate Embeddings & Store in DB
    print(f"🧠 Asking Ollama ({EMBEDDING_MODEL}) to generate embeddings...")
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        
        # Store in ChromaDB
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": "docker_compose_syntax.txt"}]
        )
        print(f"  -> Embedded chunk {i+1}/{len(chunks)}")

    print("\n✅ Knowledge Base successfully built and stored in vector_db/chroma_storage!")

if __name__ == "__main__":
    build_knowledge_base()
