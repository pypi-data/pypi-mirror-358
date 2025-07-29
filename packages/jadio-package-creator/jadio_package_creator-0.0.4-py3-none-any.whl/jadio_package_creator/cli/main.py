import json
import sys
import importlib
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: jpc <command> [options]")
        sys.exit(1)

    command = sys.argv[1]
    extra_args = sys.argv[2:]

    commands_file = Path(__file__).parent / "clicommands.json"

    if not commands_file.exists():
        print("❌ Error: clicommands.json not found.")
        sys.exit(1)

    with open(commands_file) as f:
        try:
            commands = json.load(f)
        except json.JSONDecodeError:
            print("❌ Error: clicommands.json is not valid JSON.")
            sys.exit(1)

    if command not in commands:
        print(f"❌ Unknown command: {command}")
        print("✅ Available commands:", ", ".join(commands.keys()))
        sys.exit(1)

    module_name = commands[command]["module"]
    function_name = commands[command]["function"]

    try:
        module = importlib.import_module(f"jadio_package_creator.cli.{module_name}")
        func = getattr(module, function_name)
    except Exception as e:
        print(f"❌ Failed to load command '{command}': {e}")
        sys.exit(1)

    # Call with extra args
    func(extra_args)

if __name__ == "__main__":
    main()
