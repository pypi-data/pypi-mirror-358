import os
import json
from pathlib import Path

def run_init():
    print("⚡️ Running JPC INIT...")

    # Assume current working directory is project root
    project_root = Path.cwd()
    jadio_config_dir = project_root / "jadio_config"
    jpc_config_file = jadio_config_dir / "jpcconfig.json"

    # Ensure jadio_config/ exists
    if not jadio_config_dir.exists():
        print(f"✅ Creating folder: {jadio_config_dir}")
        jadio_config_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"ℹ️ Found existing folder: {jadio_config_dir}")

    # Check if jpcconfig.json exists
    if jpc_config_file.exists():
        print(f"✅ jpcconfig.json already exists at {jpc_config_file}. No changes made.")
        return

    # Create new jpcconfig.json with default empty path
    default_config = {
        "creation_directory": ""
    }

    with open(jpc_config_file, "w") as f:
        json.dump(default_config, f, indent=2)

    print(f"✅ Created new jpcconfig.json at {jpc_config_file}")
