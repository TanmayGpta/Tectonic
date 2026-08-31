import os
import requests
from bs4 import BeautifulSoup
import chromadb

# Configuration
WINDOWS_IP = "172.22.16.1"

def scrape_and_embed(url: str):
    print(f"\n🌐 Scraping URL: {url}")
    
    # 1. Fetch the webpage
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to reach URL: {e}")
        return

    # 2. Parse HTML and extract clean text
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # We target the main content block to avoid embedding the website's navigation bar and footer
    main_content = soup.find('main') or soup.find('article') or soup.body
    
    if not main_content:
        print("❌ Could not find main content.")
        return

    text = main_content.get_text(separator='\n')
    
    # Clean up empty lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 3. Intelligent Chunking (Group every ~15 lines to retain context)
    chunks = []
    current_chunk = []
    for line in lines:
        current_chunk.append(line)
        if len(current_chunk) >= 15:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    print(f"🔪 Sliced webpage into {len(chunks)} contextual chunks.")

    # 4. Initialize Database connection
    db_path = os.path.join(os.path.dirname(__file__), "chroma_storage")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_or_create_collection(name="iac_docs")
    
    # 5. Generate Embeddings & Persist
    print("🧠 Asking Ollama to generate embeddings and storing in ChromaDB...")
    success_count = 0
    for i, chunk in enumerate(chunks):
        # Skip chunks that are too small (likely random HTML artifacts)
        if len(chunk) < 30: 
            continue
            
        embed_payload = {"model": "nomic-embed-text", "prompt": chunk}
        try:
            embed_res = requests.post(f"http://{WINDOWS_IP}:11434/api/embeddings", json=embed_payload).json()
            
            # Create a unique ID for this chunk based on the URL
            doc_id = f"{url.split('/')[-2]}_chunk_{i}"
            
            collection.add(
                ids=[doc_id],
                embeddings=[embed_res["embedding"]],
                documents=[chunk],
                metadatas=[{"source": url}]
            )
            success_count += 1
        except Exception as e:
            print(f"  -> Failed to embed chunk {i}: {e}")
            
    print(f"✅ Successfully ingested {success_count} documentation chunks from {url}!")


if __name__ == "__main__":
    # A list of real-world documentation URLs to scrape and ingest
    target_urls = [
        "https://docs.docker.com/get-started/docker-overview/", 
        "https://docs.docker.com/compose/",
        "https://developer.hashicorp.com/terraform/intro"
    ]
    
    print("🚀 Starting Enterprise Data Ingestion Pipeline...")
    for target in target_urls:
        scrape_and_embed(target)
    
    print("\n🎉 Vector Database is now fully loaded with official documentation!")
