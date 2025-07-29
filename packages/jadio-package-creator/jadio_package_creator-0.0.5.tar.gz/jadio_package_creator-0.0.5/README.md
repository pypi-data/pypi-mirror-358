Jadio Package Creator (JPC)
JPC is a modular CLI utility for the Jadio framework that helps you scaffold new Jadio-compatible packages with an exact, standardized structure.

It brings consistency and automation to creating modular Jadio extensions.

🎯 What Does It Do?
✅ Helps you create Jadio packages that follow the required skeleton.
✅ Stores your preferred target folder for new projects.
✅ Fully CLI-driven and interactive.
✅ Supports adding new CLI commands to your generated packages.
✅ Generates AI-friendly project guides for LLMs to help you finish them.
✅ Ensures all generated packages are ready to be developed and published.

📦 Install
First install the main Jadio framework (required):

bash
Copy
Edit
pip install jadio
Then install JPC:

bash
Copy
Edit
pip install jadio-package-creator
✅ This will make the jpc CLI command available:

bash
Copy
Edit
jpc --help
⚙️ Commands
✅ 1. jpc init
🔹 Must be run first.
🔹 Sets up JPC for the current project.
🔹 Creates jadio_config/jpcconfig.json in your project root if it doesn't already exist.

Example:

bash
Copy
Edit
jpc init
After running, your project will have:

pgsql
Copy
Edit
project-root/
└── jadio_config/
    └── jpcconfig.json
✅ Stores your default creation directory for future scaffolding.

✅ 2. jpc config
🔹 View or set the default project creation directory.
🔹 Updates jpcconfig.json in your project's jadio_config/ folder.

Example:

bash
Copy
Edit
jpc config
✅ 3. jpc create
🔹 Interactive CLI wizard.
🔹 Prompts for:

Package name

Target folder (remembers last-used from config)

🔹 Generates exact Jadio package skeleton in chosen folder:

pgsql
Copy
Edit
[new-project-name]/
├── src/
│   └── [new-project-name]/           # hyphens in name become underscores
│       ├── __init__.py               # __version__ = "0.0.1"
│       └── cli/
│           ├── __init__.py
│           ├── main.py
│           ├── clicommands.json
│       └── core/
│           └── __init__.py           # Empty folder otherwise
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
✅ Ensures core/ in generated project is empty except for __init__.py for user customization.
✅ Ensures package name inside src/ uses valid Python naming (hyphens ➜ underscores).

✅ 4. jpc cli
🔹 Adds a new CLI command to your generated package.
🔹 Works in two modes:

✅ Interactive:

bash
Copy
Edit
jpc cli
Prompts you:

pgsql
Copy
Edit
❓ What would you like your command to be called?
✅ Creates:

cli/[name].py with a starter function.

Updates clicommands.json with correct mapping.

✅ Non-interactive:

bash
Copy
Edit
jpc cli -<name>
No prompt. Just creates it directly.

✅ Always checks for existing files or duplicate entries before adding.

✅ 5. jpc ai
🔹 Generates an AI instruction file in your project root called ai.txt.
🔹 This file is designed as a prompt-ready guide for LLMs (like ChatGPT) to help you complete your project.

✅ Interactive mode:

bash
Copy
Edit
jpc ai
Asks you for a description of the project.

Includes it in ai.txt.

✅ Fast mode:

bash
Copy
Edit
jpc ai -f
Skips description prompt.

Just generates the structure.

✅ The generated ai.txt includes:

Timestamp

Project name

Version from __init__.py

Full folder and file structure (recursively scanned)

TODO section

Hardline instructions so the LLM doesn't change your defined structure or assumptions

✅ Example of generated ai.txt section:

pgsql
Copy
Edit
## HARDLINE INSTRUCTIONS
- Do not change the folder or file structure above
- Only fill in the content of the files as shown
- Follow exact module/function names in clicommands.json
- Do not add extra commands or files
- Do not assume or guess new features
- Maintain the CLI as defined
🗂️ jpcconfig.json
Located inside:

bash
Copy
Edit
project-root/jadio_config/jpcconfig.json
Example contents:

json
Copy
Edit
{
  "creation_directory": "C:\\JadioPackages"
}
✅ Created once by jpc init.
✅ Managed by jpc config.
✅ Used by jpc create to remember last target folder.

✅ How It Works Internally
JPC itself is a valid Jadio package following this same skeleton.

It contains all template files in its core/ folder.

Uses those templates to scaffold new projects.

Ensures generated core/ in new projects is empty for the user to customize.

Lets you keep expanding your CLI over time with jpc cli and document it for AI help with jpc ai.

💼 License
MIT License

🌐 Links
Jadio Framework

PyPI: jadio

PyPI: jadio-package-creator

Build modular. Build Jadio. 🚀

