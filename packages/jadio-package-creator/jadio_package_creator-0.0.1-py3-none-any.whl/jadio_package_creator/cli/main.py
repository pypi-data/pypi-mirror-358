import json
import sys
import importlib
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: jpc <command>")
        sys.exit(1)

    command = sys.argv[1]
    commands_file = Path(__file__).parent / "clicommands.json"

    with open(commands_file) as f:
        commands = json.load(f)

    if command not in commands:
        print(f"Unknown command: {command}")
        sys.exit(1)

    module_name = commands[command]["module"]
    function_name = commands[command]["function"]

    module = importlib.import_module(f"jadio_package_creator.cli.{module_name}")
    func = getattr(module, function_name)
    func()

if __name__ == "__main__":
    main()
