import sys
import json
from pathlib import Path

def run_cli(args):
    print("⚡️ Running JPC CLI COMMAND CREATOR...")

    project_root = Path.cwd()
    src_dir = project_root / "src"

    # Locate package folder inside src
    packages = [p for p in src_dir.iterdir() if p.is_dir()]
    if not packages:
        print("❌ Error: No package found in src/.")
        return

    package_dir = packages[0]
    cli_dir = package_dir / "cli"
    commands_file = cli_dir / "clicommands.json"

    if not cli_dir.exists():
        print(f"❌ Error: CLI folder does not exist at {cli_dir}")
        return

    if not commands_file.exists():
        print("⚠️ clicommands.json not found. Creating a new one...")
        commands_data = {}
    else:
        with commands_file.open("r") as f:
            try:
                commands_data = json.load(f)
            except json.JSONDecodeError:
                commands_data = {}

    # Determine command name
    if args and args[0].startswith("-"):
        new_command = args[0][1:]
    else:
        new_command = input("❓ What would you like your command to be called? ").strip()

    if not new_command:
        print("❌ No command name provided. Aborting.")
        return

    # Check for existing .py
    new_py_file = cli_dir / f"{new_command}.py"
    if new_py_file.exists():
        print(f"❌ {new_py_file.name} already exists. Aborting.")
        return

    # Check for existing in clicommands.json
    if new_command in commands_data:
        print(f"❌ Command '{new_command}' already exists in clicommands.json. Aborting.")
        return

    # Create new .py file
    new_py_file.write_text(f"""def run_{new_command}(args):
    print("⚡️ Running {new_command} command...")
""")

    # Add to clicommands.json
    commands_data[new_command] = {
        "module": new_command,
        "function": f"run_{new_command}"
    }

    with commands_file.open("w") as f:
        json.dump(commands_data, f, indent=2)

    print(f"✅ Created cli/{new_command}.py")
    print(f"✅ Added '{new_command}' to clicommands.json")
