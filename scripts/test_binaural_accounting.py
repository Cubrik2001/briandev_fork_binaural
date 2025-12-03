#!/usr/bin/env python3
import os
import sys
try:
    from dotenv import load_dotenv
except ImportError:
    print("python-dotenv not found. Please install it.")
    sys.exit(1)

def run_command():
    # Load environment variables from .env file in the parent directory
    # script is in scripts/, .env is in ../
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    load_dotenv(env_path)
    
    PROJECT_NAME = os.getenv("PROJECT_NAME", "")
    if not PROJECT_NAME:
        print("Error: PROJECT_NAME not found in .env")
        return

    database = "brian_local"
    module = "binaural_accounting"
    
    # Construct the docker command
    # We use 'odoo' command inside the container. 
    # -d: database
    # -i: install/update module (triggers loading and testing)
    # --test-enable: enable tests
    # --stop-after-init: stop server after initialization (tests run during init)
    
    cmd = f"docker exec -uodoo -it {PROJECT_NAME} odoo -d {database} -i {module} --test-enable --stop-after-init"
    
    print(f"Running tests for module '{module}' on database '{database}'...")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    os.system(cmd)

if __name__ == "__main__":
    run_command()
