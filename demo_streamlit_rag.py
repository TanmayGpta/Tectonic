import streamlit as st
import os
import requests
import chromadb

# Configuration
WINDOWS_IP = "172.22.16.1"
OLLAMA_API = f"http://{WINDOWS_IP}:11434/api/generate"
MODEL = "qwen2.5-coder:3b"

st.set_page_config(page_title="RAG Comparison", page_icon="⚖️", layout="wide")

st.title("⚖️ Exercise 3: RAG vs. No-RAG LLM")
st.markdown("Enter a prompt or error log below to see how Vector Database grounding changes the LLM's output.")

def ask_qwen(prompt: str) -> str:
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    response = requests.post(OLLAMA_API, json=payload)
    return response.json()["response"].strip()

# User Input
error_log = st.text_area(
    "Enter a DevOps Error Log or Question:", 
    value="yaml: line 4: mapping values are not allowed in this context. Found '5432:5432'",
    height=100
)

if st.button("Generate Comparison", type="primary"):
    
    col1, col2 = st.columns(2)
    
    # ---------------------------------------------------------
    # SCENARIO 1: WITHOUT RAG
    # ---------------------------------------------------------
    with col1:
        st.subheader("❌ Without RAG (Blind LLM)")
        with st.spinner("Qwen is thinking without context..."):
            prompt_no_rag = f"""You are a helpful DevOps AI Assistant. 
The user has asked a question or provided an error log:
{error_log}

Please answer their question or provide the fixed code. Keep your response brief, direct, and concise (limit explanations to 2-3 short sentences)."""
            
            res_no_rag = ask_qwen(prompt_no_rag)
            st.markdown(res_no_rag)
            
    # ---------------------------------------------------------
    # SCENARIO 2: WITH RAG
    # ---------------------------------------------------------
    with col2:
        st.subheader("✅ With RAG (Grounded LLM)")
        with st.spinner("Searching ChromaDB and thinking..."):
            # 1. Query ChromaDB
            db_path = os.path.join(os.path.dirname(__file__), "vector_db", "chroma_storage")
            client = chromadb.PersistentClient(path=db_path)
            collection = client.get_collection(name="iac_docs")
            
            embed_payload = {"model": "nomic-embed-text", "prompt": error_log}
            embed_res = requests.post(f"http://{WINDOWS_IP}:11434/api/embeddings", json=embed_payload).json()
            results = collection.query(query_embeddings=[embed_res["embedding"]], n_results=1)
            
            context = results["documents"][0][0] if results["documents"][0] else "No relevant context found."
            
            # Show the retrieved context in the UI so the professor can see it!
            with st.expander("View Retrieved Knowledge Base Document", expanded=True):
                st.info(context)
            
            # 2. Prompt LLM
            prompt_with_rag = f"""You are a helpful DevOps AI Assistant. 
The user has asked a question or provided an error log:
{error_log}

OFFICIAL DOCUMENTATION RULES:
{context}

Please answer their question or provide the fixed code based strictly on the documentation provided. Keep your response brief, direct, and concise (limit explanations to 2-3 short sentences)."""
            
            res_with_rag = ask_qwen(prompt_with_rag)
            st.markdown(res_with_rag)
