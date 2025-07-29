import sys
import json
import re
from pathlib import Path
from datetime import datetime

def run_ai(args):
    print("⚡️ Running JPC AI HELPER...")

    project_root = Path.cwd()
    src_dir = project_root / "src"

    # Find the single package inside src
    packages = [p for p in src_dir.iterdir() if p.is_dir()]
    if not packages:
        print("❌ Error: No package found in src/")
        return

    package_dir = packages[0]
    package_name = package_dir.name

    # Default description
    description = ""

    # Check for forced mode
    if args and args[0].startswith("-") and args[0][1:] == "f":
        print("✅ Fast mode: No description prompt.")
    else:
        description = input("❓ Describe this project (short sentence): ").strip()

    # Attempt to get version from __init__.py
    init_file = package_dir / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        version = match.group(1) if match else "Unknown"
    else:
        version = "Unknown"

    # Recursively scan the folder structure
    folder_lines = []
    def scan_dir(path, prefix=""):
        for item in sorted(path.iterdir()):
            if item.is_file():
                folder_lines.append(f"{prefix}{item.name}")
            elif item.is_dir():
                folder_lines.append(f"{prefix}{item.name}/")
                scan_dir(item, prefix + "  ")

    scan_dir(src_dir)

    # Create ai.txt
    output_file = project_root / "ai.txt"
    timestamp = datetime.now().isoformat()

    with output_file.open("w") as f:
        f.write(f"# AI Instruction File\n\n")
        f.write(f"Generated: {timestamp}\n\n")
        f.write(f"## Project Name\n{package_name}\n\n")
        f.write(f"## Version\n{version}\n\n")
        if description:
            f.write(f"## Project Description\n{description}\n\n")
        f.write(f"## Folder Structure\n")
        for line in folder_lines:
            f.write(f"{line}\n")
        f.write(f"\n## TODO\n")
        f.write(f"- Fill in CLI command logic\n")
        f.write(f"- Add docstrings\n")
        f.write(f"- Implement missing functions\n")
        f.write(f"- Ensure all clicommands.json entries match modules/functions\n")
        f.write(f"\n## HARDLINE INSTRUCTIONS\n")
        f.write(f"- Do not change the folder or file structure above\n")
        f.write(f"- Only fill in the content of the files as shown\n")
        f.write(f"- Follow exact module/function names in clicommands.json\n")
        f.write(f"- Do not add extra commands or files\n")
        f.write(f"- Do not assume or guess new features\n")
        f.write(f"- Maintain the CLI as defined\n")

    print(f"✅ AI Instruction file generated at: {output_file}")
