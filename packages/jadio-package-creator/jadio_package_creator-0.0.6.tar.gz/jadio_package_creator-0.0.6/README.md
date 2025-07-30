Jadio Package Creator (JPC)
Jadio Package Creator (JPC) is the official CLI utility for the [Jadio Framework], designed to help you quickly scaffold, customize, and publish new Jadio-compatible packages with consistent, professional structure.

It automates repetitive setup steps and enforces a standardized layout for all Jadio extensions, making collaboration and maintenance easier.

Overview of Features
Fully interactive CLI wizard for generating new Jadio packages
Remembers your preferred target folder for future projects
Allows adding new CLI commands any time to your generated packages
Generates an AI-friendly guide to help LLMs assist in developing your package
Ensures all generated projects are ready to be developed and published to PyPI

Installation
First install the core Jadio framework (required):

pip install jadio

Then install the Jadio Package Creator:

pip install jadio-package-creator

This will make the jpc CLI command available in your environment.

Available Commands

1. jpc init
Sets up JPC for use in your project folder.
Creates a jadio_config/jpcconfig.json file if it doesn't already exist.
Stores your default target folder for new packages.
Must be run at least once per project to initialize configuration.

What it does:
Creates a new folder structure in your project root:

project-root/
└── jadio_config/
    └── jpcconfig.json

2. jpc config
Lets you view or update the saved default project creation directory.
Edits the creation_directory value in your jpcconfig.json config file.

Example usage:
When you run this, you can see or set the path where new packages will be created by default.

3. jpc create
This is the main interactive wizard for creating new Jadio packages.

How it works:
Prompts you for the target creation folder.
Defaults to the last-used directory stored in config.
If none is saved yet, defaults to your current working directory.
Always ensures there's a valid path, so pressing Enter never breaks.
Prompts for the new package name.
Hyphens in the name are automatically converted to underscores to ensure valid Python package naming.
Generates the complete, standardized Jadio package skeleton in the target folder.

Then enters an interactive CLI script-adding loop:
Asks you if you want to add a new CLI command script.
You can add as many as you want (each with its own Python module and JSON command registration).
Always checks for duplicate filenames or JSON entries before adding.
Finally, automatically runs AI module generation to produce a ready-to-use ai.txt instruction file at the end of the creation process.

Generated Folder Structure:

markdown
Copy
Edit
[new-project-name]/
├── src/
│   └── [new_project_name]/
│       ├── __init__.py         (includes __version__ = "0.0.1")
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   └── clicommands.json
│       ├── core/
│       │   └── __init__.py
│       └── ai/
│           └── __init__.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore

✅ Ensures that core/ and ai/ are empty except for __init__.py, ready for your customization.
✅ Remembers your preferred target folder automatically for next time.
✅ Lets you expand CLI commands at creation time, without having to re-run anything later.
✅ Always generates an ai.txt guide to help LLMs understand your project structure and rules.

4. jpc cli
Adds a new CLI command script to an existing Jadio package.

Fully modular: use it any time after creation to expand your CLI.

Two Modes:

Interactive mode:
Asks you for the new command's name.
Creates the Python module for it in the CLI folder.
Updates clicommands.json with correct module/function mapping.

Non-interactive mode:
Lets you specify the command name directly without prompts.

Safety features:
Always checks for existing filenames before writing.
Always checks for duplicate command entries in clicommands.json.

5. jpc ai
Generates an AI-friendly instruction file in your project root called ai.txt.
Designed as a prompt-ready guide for LLMs (like ChatGPT) to help you finish your project.

Modes:

Interactive mode:
Asks you to enter a short description for the project.
Includes this in ai.txt.

Fast mode:
Skips the description prompt and just generates the structure immediately.

Contents of ai.txt:
Timestamp of generation
Project name
Version (from __init__.py)
Full, recursively scanned folder and file structure
A clear TODO section listing development steps
Hardline instructions preventing structural changes

Example of Hardline Instructions Section:

## HARDLINE INSTRUCTIONS
- Do not change the folder or file structure above
- Only fill in the content of the files as shown
- Follow exact module/function names in clicommands.json
- Do not add extra commands or files
- Do not assume or guess new features
- Maintain the CLI as defined
Configuration File
jpcconfig.json

Always stored inside the jadio_config/ folder in your project root.

Stores your preferred default target folder for new package creation.

Example contents:


{
  "creation_directory": "C:\\JadioPackages"
}

✅ Created once by jpc init.
✅ Managed and updated by jpc config.
✅ Used automatically by jpc create.

How It Works Internally
JPC itself is a valid Jadio package built using the same skeleton it generates for you:
Includes its own CLI commands and templates.
Uses those templates to scaffold new packages with correct structure.
Leaves core/ and ai/ folders empty in new projects for your own implementation.
Lets you add as many CLI commands as you want over time.
Ensures your project is fully documented for AI helpers via the AI module.

License
MIT License

Build modular. Build Jadio. 🚀
