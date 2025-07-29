import json
from pathlib import Path

def run_config():
    print("⚡️ Running JPC CONFIG...")

    project_root = Path.cwd()
    jadio_config_dir = project_root / "jadio_config"
    jpc_config_file = jadio_config_dir / "jpcconfig.json"

    if not jadio_config_dir.exists() or not jpc_config_file.exists():
        print("❌ Error: jpcconfig.json not found. Have you run 'jpc init' first?")
        return

    # Load existing config
    with open(jpc_config_file) as f:
        config = json.load(f)

    current_dir = config.get("creation_directory", "")
    print(f"\n✅ Current project creation directory:\n{current_dir if current_dir else '(not set)'}\n")

    # Prompt for new directory
    new_dir = input("Enter new creation directory path (or press Enter to keep current): ").strip()

    if not new_dir:
        print("✅ No changes made. Keeping existing directory.")
        return

    # Update config
    config["creation_directory"] = new_dir

    with open(jpc_config_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Updated creation_directory to:\n{new_dir}")
