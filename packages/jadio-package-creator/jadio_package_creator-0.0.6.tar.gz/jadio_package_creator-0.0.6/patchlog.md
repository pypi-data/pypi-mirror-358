# Patch Log

## v0.0.6 (2025-06-27)

### 🚀 Major Enhancements

- **Improved creation flow in `jpc create`:**
  - Target creation folder prompt now correctly defaults to either:
    - Saved `creation_directory` in config, or
    - Current working directory if none is saved.
  - Prevents empty entry errors by always ensuring a valid path.
  - Saves the final choice back to `jpcconfig.json` automatically for next time.

- **Interactive CLI Command Loop:**
  - After creating the base skeleton, `jpc create` now:
    - Repeatedly prompts the user to add new CLI command scripts.
    - Lets you create as many CLI commands as you want in one run.
    - Ensures no duplicate filenames or command entries in `clicommands.json`.

- **Automatic AI Module Generation:**
  - `jpc create` automatically generates `ai.txt` at the end of the CLI command loop.
  - Produces a full AI instruction file with:
    - Timestamp
    - Project name
    - Version
    - Full folder structure
    - TODO and Hardline Instructions sections
  - Designed to help LLMs understand your project without guessing.

---

### 🛠️ CLI Command Refactors

- **`jpc cli`**:
  - Refactored to take `cli_dir` as a direct parameter.
  - Removes reliance on current working directory to find the CLI folder.
  - Allows integration directly inside `jpc create` for interactive script generation.

- **`jpc ai`**:
  - Now accepts `ai_dir` directly.
  - Dynamically resolves project root, src, and package name based on provided path.
  - No more hardcoded `cwd` assumptions.
  - Always writes `ai.txt` to the correct package root.

---

### ✅ Bug Fixes

- Fixed issue where pressing Enter with no saved creation directory would abort.
- Ensured that default path prompt always has a valid fallback.
- Cleaned duplicate checking logic in `clicommands.json`.

---

### 📚 Documentation

- Fully rewritten `README.md` for GitHub and PyPI.
  - Clean, professional, and standardized.
  - Includes new interactive CLI loop and AI generation steps.
  - Describes all commands clearly with expected behaviors and generated structure.

---

### 💼 Notes

- This version aligns JPC with modern CLI best practices.
- Ensures consistent, production-ready skeleton generation for all Jadio packages.
- Fully ready for PyPI publication.

---

Build modular. Build Jadio. 🚀