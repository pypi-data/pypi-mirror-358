import json
from pathlib import Path

def create_cli_script(cli_dir, command_name=None):
    print("⚡️ Running JPC CLI COMMAND CREATOR...")

    commands_file = cli_dir / "clicommands.json"

    if not cli_dir.exists():
        print(f"❌ Error: CLI folder does not exist at {cli_dir}")
        return

    # Load existing clicommands.json
    if not commands_file.exists():
        print("⚠️ clicommands.json not found. Creating a new one...")
        commands_data = {}
    else:
        try:
            with commands_file.open("r") as f:
                commands_data = json.load(f)
        except json.JSONDecodeError:
            commands_data = {}

    # Prompt for command name if not given
    if not command_name:
        command_name = input("❓ What would you like your command to be called? ").strip()

    if not command_name:
        print("❌ No command name provided. Aborting.")
        return

    # Check for existing .py
    new_py_file = cli_dir / f"{command_name}.py"
    if new_py_file.exists():
        print(f"❌ {new_py_file.name} already exists. Aborting.")
        return

    # Check for existing in clicommands.json
    if command_name in commands_data:
        print(f"❌ Command '{command_name}' already exists in clicommands.json. Aborting.")
        return

    # Create new .py file
    new_py_file.write_text(f"""def run_{command_name}(args):
    print("⚡️ Running {command_name} command...")
""")

    # Add to clicommands.json
    commands_data[command_name] = {
        "module": command_name,
        "function": f"run_{command_name}"
    }

    with commands_file.open("w") as f:
        json.dump(commands_data, f, indent=2)

    print(f"✅ Created cli/{command_name}.py")
    print(f"✅ Added '{command_name}' to clicommands.json")
