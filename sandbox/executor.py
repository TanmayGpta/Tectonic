import docker
import tempfile
import os

def validate_docker_compose(compose_yaml: str) -> dict:
    """
    Spins up an isolated, ephemeral Docker container to safely test
    the AI's generated docker-compose.yml file.
    """
    # Connect to the local Docker daemon
    client = docker.from_env()
    
    # 1. STAGING: Save the AI's code to a secure temporary directory
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "docker-compose.yml")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(compose_yaml)
        
    print("   📦 Spawning isolated sandbox container (docker/compose)...")
    
    try:
        # 2. ISOLATION & EXECUTION: 
        # We use the official docker/compose container image to validate the file.
        # The 'remove=True' flag guarantees the container is instantly deleted after running.
        logs = client.containers.run(
            "docker/compose:1.29.2",
            command=["-f", "/workspace/docker-compose.yml", "config"],
            volumes={temp_dir: {'bind': '/workspace', 'mode': 'ro'}},
            remove=True, # Auto-destruction
            stderr=True,
            stdout=True
        )
        
        print("   ✅ Sandbox Execution Successful!")
        return {"status": "SUCCESS", "logs": logs.decode("utf-8").strip()}
        
    except docker.errors.ContainerError as e:
        # 3. SCRAPING: If it crashes, we scrape the exact error logs
        print("   ❌ Sandbox Execution Failed! Code is broken.")
        error_logs = e.stderr.decode("utf-8").strip() if e.stderr else str(e)
        return {"status": "FAIL", "logs": error_logs}
        
    except Exception as e:
        print("   🚨 Critical Sandbox Error!")
        return {"status": "ERROR", "logs": str(e)}

if __name__ == "__main__":
    # A quick test to prove the sandbox works
    test_code = "version: '3'\nservices:\n  web:\n    image: nginx\n    ports: 8080:80" # Invalid port syntax
    print(validate_docker_compose(test_code))
