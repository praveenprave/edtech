import json
import os
import sys

CONFIG_FILE = "infra/config.json"

def generate_env_file(branch_name):
    """
    Reads config.json and determines the environment based on the branch.
    Writes key=value pairs to 'workspace_env.sh' for sourcing in Cloud Build.
    """
    # 1. Determine Environment
    env = "dev"
    if branch_name == "main":
        env = "prod"
    
    print(f"🔧 Detailed Config: Branch='{branch_name}' -> Environment='{env}'")

    # 2. Load Config
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Error: Config file missing at {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, "r") as f:
        full_config = json.load(f)
    
    if env not in full_config:
        print(f"❌ Error: Environment '{env}' is not defined in config.json")
        sys.exit(1)

    env_config = full_config[env]

    # 3. Write Export Script
    # We write to a file that subsequent Cloud Build steps can 'source'
    with open("workspace_env.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"export TARGET_ENV='{env}'\n")
        
        for key, value in env_config.items():
            # Escape value just in case
            safe_value = str(value).replace("'", "'\\''") 
            f.write(f"export {key}='{safe_value}'\n")
            
    print("✅ 'workspace_env.sh' created successfully.")

if __name__ == "__main__":
    # Cloud Build provides branch name via substitution, usually passed as arg
    # Fallback to 'dev' if not provided (e.g. manual build without substitution)
    branch = sys.argv[1] if len(sys.argv) > 1 else "dev"
    generate_env_file(branch)
