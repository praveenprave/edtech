import json
import os
import sys
import subprocess

CONFIG_FILE = "infra/config.json"

def load_config(env):
    """Loads the configuration for the specified environment."""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Error: Config file not found at {CONFIG_FILE}")
        sys.exit(1)
        
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    
    if env not in data:
        print(f"❌ Error: Environment '{env}' not found in {CONFIG_FILE}")
        print(f"Available environments: {list(data.keys())}")
        sys.exit(1)
        
    return data[env]

def deploy(env):
    """Constructs and runs the gcloud builds submit command."""
    print(f"🚀 Preparing to deploy to [{env.upper()}]...")
    config = load_config(env)
    
    # Extract params
    project_id = config.get("PROJECT_ID")
    
    if not project_id:
        print("❌ Error: PROJECT_ID is missing in config.")
        sys.exit(1)

    # Construct Substitution String
    # Format: _VAR=VAL,_VAR2=VAL2
    # We map keys in JSON to substitution keys (prefixed with _)
    substitutions = []
    for key, value in config.items():
        if key == "PROJECT_ID": continue # Project ID is passed as a flag, not just substitution
        substitutions.append(f"_{key}={value}")
    
    subs_string = ",".join(substitutions)
    
    # Construct Command
    command = [
        "gcloud", "builds", "submit",
        "--config", "cloudbuild.yaml",
        "--project", project_id,
        "--substitutions", subs_string
    ]
    
    # Print readable command
    print("\nExecuting Command:")
    print(" ".join(command))
    print("\n" + "-"*40 + "\n")
    
    # Execute
    try:
        subprocess.run(command, check=True)
        print(f"\n✅ Deployment to {env} Successful!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Deployment Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 deploy.py <env>")
        print("Example: python3 deploy.py dev")
        sys.exit(1)
        
    target_env = sys.argv[1].lower()
    deploy(target_env)
