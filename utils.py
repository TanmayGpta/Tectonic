import os
import requests
from dotenv import load_dotenv

# Automatically load environment variables
env_paths = [
    os.path.join(os.path.dirname(__file__), ".env"),
    "/home/tanmay/Archon_IDT/.env",
    "/home/tanmay/Tectonic/.env"
]
for p in env_paths:
    if os.path.exists(p):
        load_dotenv(p)
        break

_CACHED_OLLAMA_HOST = None

def get_ollama_host() -> str:
    """
    Dynamically discovers the correct host address for Ollama, whether running
    inside Docker (host.docker.internal), native WSL2 (localhost / gateway IP),
    or direct host environment.
    """
    global _CACHED_OLLAMA_HOST
    if _CACHED_OLLAMA_HOST:
        return _CACHED_OLLAMA_HOST

    # 1. Check environment variable override
    env_host = os.getenv("OLLAMA_HOST_IP")
    if env_host:
        _CACHED_OLLAMA_HOST = env_host
        return env_host

    # 2. Candidate hosts to probe
    candidates = [
        "host.docker.internal",
        "localhost",
        "127.0.0.1",
        "172.22.16.1"
    ]

    for host in candidates:
        try:
            res = requests.get(f"http://{host}:11434/api/tags", timeout=1.0)
            if res.status_code == 200:
                _CACHED_OLLAMA_HOST = host
                return host
        except Exception:
            continue

    return "host.docker.internal"

def query_llm(prompt: str, model_choice: str = "ollama:qwen2.5-coder:3b", is_json: bool = False, temperature: float = 0.0) -> str:
    """
    Unified multi-provider inference engine. Routes requests to either:
    1. Local Ollama (air-gapped, zero-cost, private)
    2. GroqCloud LPU (high-throughput, 500 T/s, deep coder models)
    """
    selected = model_choice or "ollama:qwen2.5-coder:3b"
    
    if selected.startswith("groq:"):
        model_name = selected.replace("groq:", "").strip()
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key:
            raise ValueError("GROQ_API_KEY environment variable is not configured.")
            
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        system_role = (
            "You are a DevOps Security Gatekeeper. Respond ONLY in valid JSON format."
            if is_json else
            "You are an elite Site Reliability Engineer and IaC compiler expert. Respond ONLY with raw code without markdown formatting."
        )
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature
        }
        if is_json:
            payload["response_format"] = {"type": "json_object"}
            
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=40)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()

    elif selected.startswith("nvidia:"):
        model_name = selected.replace("nvidia:", "").strip()
        nv_key = os.getenv("NVIDIA_API_KEY", "")
        if not nv_key:
            raise ValueError("NVIDIA_API_KEY environment variable is not configured.")
            
        headers = {
            "Authorization": f"Bearer {nv_key}",
            "Content-Type": "application/json"
        }
        system_role = (
            "You are a DevOps Security Gatekeeper. Respond ONLY in valid JSON format."
            if is_json else
            "You are an elite Site Reliability Engineer and IaC compiler expert. Respond ONLY with raw code without markdown formatting."
        )
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature
        }
        if is_json:
            payload["response_format"] = {"type": "json_object"}
            
        res = requests.post("https://integrate.api.nvidia.com/v1/chat/completions", headers=headers, json=payload, timeout=40)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
        
    else:
        # Local Ollama
        host = get_ollama_host()
        model_name = selected.replace("ollama:", "").strip() or "qwen2.5-coder:3b"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.1 if is_json else 0.2
            }
        }
        if is_json:
            payload["format"] = "json"
            
        res = requests.post(f"http://{host}:11434/api/generate", json=payload, timeout=60).json()
        return res.get("response", "").strip()
