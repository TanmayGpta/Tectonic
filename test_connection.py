import requests
import subprocess
import sys

# Hardcoded the exact Windows Host IP based on my background scan of your machine
windows_ip = "172.22.16.1"
OLLAMA_URL = f"http://{windows_ip}:11434/api/generate"

payload = {
    "model": "qwen2.5-coder:3b",
    "prompt": "Hello from the WSL environment! Are you receiving this on Windows?",
    "stream": False
}

def test_ollama_connection():
    try:
        print(f"Sending request to exact Windows Host IP at {OLLAMA_URL}...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=5)
        response.raise_for_status()
        
        result = response.json()
        print("\n✅ SUCCESS! Response from Qwen 2.5 Coder:")
        print(result.get("response", ""))
        
    except Exception as e:
        print(f"\n❌ FAILED to connect: {e}")

if __name__ == "__main__":
    test_ollama_connection()
