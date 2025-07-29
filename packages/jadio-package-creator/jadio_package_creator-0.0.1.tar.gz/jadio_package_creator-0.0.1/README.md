# Jadio Package Creator (JPC)

**JPC** is a modular CLI utility for the [Jadio framework](https://github.com/JaxxyJadio/jadio) that helps you scaffold new Jadio-compatible packages with an exact, standardized structure.

It brings consistency and automation to creating modular Jadio extensions.

---

## 🎯 What Does It Do?

✅ Helps you create Jadio packages that follow the required skeleton.  
✅ Stores your preferred target folder for new projects.  
✅ Fully CLI-driven and interactive.  
✅ Ensures all generated packages are ready to be developed and published.

---

## 📦 Install

First install the main **Jadio framework** (required):

```bash
pip install jadio
```

Then install **JPC**:

```bash
pip install jadio-package-creator
```

✅ This will make the `jpc` CLI command available:

```bash
jpc --help
```

---

## ⚙️ Commands

### ✅ 1. `jpc init`

🔹 **Must be run first**.  
🔹 Sets up JPC for the current project.  
🔹 Creates `jadio_config/jpcconfig.json` in your project root **if it doesn't already exist**.

Example:

```bash
jpc init
```

After running, your project will have:

```
project-root/
└── jadio_config/
    └── jpcconfig.json
```

✅ Stores your default creation directory for future scaffolding.

---

### ✅ 2. `jpc config`

🔹 View or set the **default project creation directory**.  
🔹 Updates `jpcconfig.json` in your project's `jadio_config/` folder.

Example:

```bash
jpc config
```

---

### ✅ 3. `jpc create`

🔹 Interactive CLI wizard.  
🔹 Prompts for:
- Package name
- Target folder (remembers last-used from config)

🔹 Generates **exact Jadio package skeleton** in chosen folder:

```
[new-project-name]/
├── src/
│   └── [new-project-name]/
│       ├── __init__.py         # __version__ = "0.0.1"
│       └── cli/
│           ├── __init__.py
│           ├── main.py
│           ├── clicommands.json
│       └── core/
│           └── __init__.py     # Empty folder otherwise
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

✅ Ensures `core/` in generated project is empty except for `__init__.py` for user customization.

---

## 🗂️ jpcconfig.json

Located inside:

```
project-root/jadio_config/jpcconfig.json
```

Example contents:

```json
{
  "creation_directory": "C:\\JadioPackages"
}
```

✅ Created once by `jpc init`.  
✅ Managed by `jpc config`.  
✅ Used by `jpc create` to remember last target folder.

---

## ✅ How It Works Internally

- JPC *itself* is a valid Jadio package following this same skeleton.  
- It contains all template files in its **core/** folder.  
- Uses those templates to scaffold new projects.  
- Ensures generated **core/** in new projects is empty for the user to customize.

---

## 💼 License

MIT License

---

## 🌐 Links

- [Jadio Framework](https://github.com/JaxxyJadio/jadio)
- [PyPI: jadio](https://pypi.org/project/jadio/)
- [PyPI: jadio-package-creator](https://pypi.org/project/jadio-package-creator/)

---

**Build modular. Build Jadio. 🚀**
