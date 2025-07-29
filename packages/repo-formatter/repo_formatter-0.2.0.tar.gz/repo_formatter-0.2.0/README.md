# Repository Formatter

A command-line tool to format repository content into a single Markdown file (`repository.md`). It includes options for filtering, anonymization, and different processing modes.

* There is a ton of other options for this.

[![PyPI version](https://badge.fury.io/py/repo-formatter.svg)](https://badge.fury.io/py/repo-formatter)

## Features

*   Generates a Markdown file with repository structure and file contents.
*   Filters files/directories based on paths and extensions via a config file.
*   Anonymizes specified strings in file paths and content.
*   Supports different modes:
    *   `normal`: Process the entire repository (respecting filters).
    *   `class`: Include only files containing a specific class name.
    *   `patch`: Include a git diff instead of file contents.
*   Estimates the token count of the generated Markdown using `tiktoken`.
*   Configurable via a `.repo_formatter.yaml` file.

## Installation

**From PyPI (Recommended):**

```bash
pip install repo-formatter
```

**From Source (for Development):**

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/repo-formatter.git # <-- UPDATE URL
    cd repo-formatter
    ```
2.  Install in editable mode (includes development dependencies):
    ```bash
    pip install -e .[dev]
    ```

## Usage

```bash
repo-formatter [OPTIONS] [DIRECTORY]
```

**Arguments:**

*   `DIRECTORY`: The path to the repository/directory to process (default: current directory).

**Options:**

*   `-m MODE`, `--mode MODE`: Processing mode (`normal`, `class`, `patch`). Default: `normal`.
*   `--class-name NAME`: Required for `class` mode. The name to search for.
*   `--diff-target TARGET`: Required for `patch` mode. Use `current` for uncommitted changes, or a git ref/range (e.g., `main`, `HEAD~2`, `v1.0..v1.1`).
*   `-c PATH`, `--config PATH`: Path to the YAML configuration file. If not provided, searches for `.repo_formatter.yaml` in the target directory and its parents.
*   `-a`, `--anonymize`: Enable anonymization using rules from the config file.
*   `-o FILENAME`, `--output FILENAME`: Output Markdown filename (default: `repository.md`, or mode-specific names like `diff_....md`, `class_....md`).

**Examples:**

```bash
# Process the current directory with default settings
repo-formatter

# Process a specific directory
repo-formatter ../my-other-project

# Use a specific config file and enable anonymization
repo-formatter -c /path/to/my_config.yaml -a .

# Find all files containing "UserManager"
repo-formatter --mode class --class-name UserManager

# Get uncommitted changes as a patch file (diff_current.md)
repo-formatter --mode patch --diff-target current

# Get the diff between 'develop' branch and 'main' branch (diff_develop..main.md)
repo-formatter --mode patch --diff-target develop..main
```

## Configuration (`.repo_formatter.yaml`)

Create a `.repo_formatter.yaml` file in the root of your repository (or specify with `-c`).

```yaml
# Paths to exclude, relative to the repository root.
# This matches the full path, so 'data' excludes the 'data' directory at the root,
# and 'app/logs' excludes 'logs' inside 'app'.
exclude_paths:
  - .git
  - .vscode
  - node_modules
  - build
  - dist
  - venv
  - __pycache__
  - specific_file_to_ignore.log
  - app/content # Excludes the 'content' directory inside 'app'

# Force the inclusion of specific files or directories, even if they are in an excluded path.
# This is useful for including a specific file from an otherwise excluded directory.
force_include:
  - docs/IMPORTANT.md # Include this file even if 'docs' is in exclude_paths.

# List of file extensions to include (lowercase, including the dot).
# If empty or omitted, all extensions (not excluded by path) are included.
include_extensions:
  - .py
  - .js
  - .html
  - .css
  - .md

# Dictionary of strings to anonymize (case-insensitive keys).
# The replacement value's case will try to mimic the original match.
anonymize:
  "CompanyName": "ClientProject"
  "internal_api_key": "REDACTED_KEY"
  "ProjectX": "CodenameZephyr"
```

## Development (using Devcontainer)

1.  Make sure you have Docker and the VS Code "Dev Containers" extension installed.
2.  Open the `repo-formatter` folder in VS Code.
3.  When prompted, click "Reopen in Container".
4.  VS Code will build the container and install dependencies.
5.  You can now run/debug the tool within the isolated container environment. The terminal in VS Code will be inside the container.

```bash
# Inside the devcontainer terminal
repo-formatter --help
repo-formatter sample_project # Test on the sample project
repo-formatter sample_project -a # Test anonymization
# Initialize git in sample_project to test patch mode
cd sample_project
git init
git add .
git commit -m "Initial commit"
echo "// New comment" >> src/main.cpp
cd ..
repo-formatter sample_project --mode patch --diff-target current
```

## Token Estimation

The tool uses the `tiktoken` library to provide accurate token counts for OpenAI models. The library is installed automatically as a dependency.
