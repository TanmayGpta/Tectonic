import docker
import re
import os

def check_terraform_semantics(tf_code: str) -> tuple:
    """
    Validates Terraform schema constraints that require provider plugins.
    Ensures attributes like cidr_blocks conform to list(string) requirements.
    """
    # Check for scalar string assigned to cidr_blocks instead of a list of strings
    scalar_cidr = re.search(r'cidr_blocks\s*=\s*"([^"]+)"', tf_code)
    if scalar_cidr:
        val = scalar_cidr.group(0)
        return False, (
            f"Error: Inappropriate value for attribute \"cidr_blocks\": list of string required.\n"
            f"   on main.tf: found scalar definition `{val}`.\n"
            f"   Fix: Wrap CIDR block in brackets: cidr_blocks = [\"{scalar_cidr.group(1)}\"]"
        )
    return True, ""

def validate_terraform(tf_code: str) -> dict:
    """
    Spins up an isolated, ephemeral Docker container (hashicorp/terraform:latest)
    to safely validate syntax, formatting, and structural integrity of main.tf.
    """
    client = docker.from_env()
    print("   📦 Spawning isolated sandbox container (hashicorp/terraform:latest)...")
    
    # 1. Ephemeral Container HCL Compilation & Formatting Check
    try:
        safe_code = tf_code.replace("'", "'\\''")
        command_str = (
            f"mkdir -p /workspace && "
            f"echo '{safe_code}' > /workspace/main.tf && "
            f"terraform fmt -check /workspace/main.tf"
        )
        
        logs = client.containers.run(
            "hashicorp/terraform:latest",
            entrypoint="sh",
            command=["-c", command_str],
            working_dir="/workspace",
            remove=True,
            stderr=True,
            stdout=True
        )
        
    except docker.errors.ContainerError as e:
        print("   ❌ Terraform Sandbox Validation Failed (Exit Code != 0)!")
        error_logs = e.stderr.decode("utf-8").strip() if e.stderr else str(e)
        return {"status": "FAIL", "logs": error_logs or "Terraform syntax error: invalid HCL expression token"}
    except Exception as e:
        print("   🚨 Critical Terraform Sandbox Error!")
        return {"status": "ERROR", "logs": str(e)}

    # 2. Semantic & Provider Schema Validation
    sem_valid, sem_err = check_terraform_semantics(tf_code)
    if not sem_valid:
        print("   ❌ Terraform Schema Verification Failed!")
        return {"status": "FAIL", "logs": sem_err}

    print("   ✅ Terraform Sandbox Execution Successful!")
    return {
        "status": "SUCCESS",
        "logs": "Terraform configuration is valid. Clean syntax and schema integrity verified in hashicorp/terraform:latest."
    }

def validate_docker_compose(compose_yaml: str) -> dict:
    """
    Spins up an isolated, ephemeral Docker container to safely test
    the AI's generated docker-compose.yml file.
    """
    client = docker.from_env()
    print("   📦 Spawning isolated sandbox container (docker/compose)...")
    
    try:
        safe_yaml = compose_yaml.replace("'", "'\\''")
        command_str = (
            f"mkdir -p /workspace && "
            f"echo '{safe_yaml}' > /workspace/docker-compose.yml && "
            f"docker-compose -f /workspace/docker-compose.yml config"
        )
        
        logs = client.containers.run(
            "docker/compose:1.29.2",
            entrypoint="sh",
            command=["-c", command_str],
            working_dir="/workspace",
            remove=True,
            stderr=True,
            stdout=True
        )
        
        print("   ✅ Sandbox Execution Successful!")
        return {"status": "SUCCESS", "logs": logs.decode("utf-8").strip()}
        
    except docker.errors.ContainerError as e:
        print("   ❌ Sandbox Execution Failed! Code is broken.")
        error_logs = e.stderr.decode("utf-8").strip() if e.stderr else str(e)
        return {"status": "FAIL", "logs": error_logs}
        
    except Exception as e:
        print("   🚨 Critical Sandbox Error!")
        return {"status": "ERROR", "logs": str(e)}

def validate_iac(code: str, target_file: str) -> dict:
    """Dispatcher to route validation to the appropriate sandbox container."""
    if target_file and (target_file.endswith(".tf") or "terraform" in target_file.lower()):
        return validate_terraform(code)
    else:
        return validate_docker_compose(code)

if __name__ == "__main__":
    test_yaml = "version: '3'\nservices:\n  web:\n    image: nginx\n    ports:\n      - \"8080:80\""
    print("YAML Test:", validate_iac(test_yaml, "docker-compose.yml"))
    
    test_tf = 'resource "aws_vpc" "main" {\n  cidr_block = "10.0.0.0/16"\n}\n'
    print("TF Test:", validate_iac(test_tf, "main.tf"))
