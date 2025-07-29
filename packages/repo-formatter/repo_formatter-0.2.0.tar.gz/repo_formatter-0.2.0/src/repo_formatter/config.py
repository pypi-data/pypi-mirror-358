import yaml
from pathlib import Path
from typing import Dict, Optional, Any

DEFAULT_CONFIG_NAME = ".repo_formatter.yaml"

DEFAULT_CONFIG = {
    "exclude_paths": [
        ".git",
        ".vscode",
        ".devcontainer",
        "__pycache__",
        "node_modules",
        "build",
        "dist",
        ".venv",
        "venv",
        "env",
        ".env",
    ],
    "force_include": [], # Files/paths to force include even if in exclude_paths
    "include_extensions": [], # Empty list means include all
    "anonymize": {}, # e.g., {"YourName": "Contributor A"}
}

def load_config(config_path: Optional[str] = None, start_dir: str = '.') -> Dict[str, Any]:
    """
    Loads configuration from a YAML file.
    Searches for the default config file name if no path is provided.
    Merges found config with defaults.
    """
    loaded_config = {}
    found_path = None

    if config_path:
        path = Path(config_path)
        if path.is_file():
            found_path = path
    else:
        # Search upwards from start_dir for the default config file
        current_dir = Path(start_dir).resolve()
        while True:
            potential_path = current_dir / DEFAULT_CONFIG_NAME
            if potential_path.is_file():
                found_path = potential_path
                break
            if current_dir.parent == current_dir: # Reached root
                break
            current_dir = current_dir.parent

    if found_path:
        print(f"Loading configuration from: {found_path}")
        try:
            with open(found_path, 'r') as f:
                loaded_config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not read or parse config file {found_path}: {e}")
            loaded_config = {}
    else:
        if config_path: # User specified a path but it wasn't found
             print(f"Warning: Specified config file not found: {config_path}")
        else: # No config specified and default not found
             print(f"No configuration file '{DEFAULT_CONFIG_NAME}' found. Using defaults.")


    # Merge loaded config with defaults (loaded values override defaults)
    # Deep merge isn't strictly necessary here as the structure is simple
    final_config = DEFAULT_CONFIG.copy()

    # Ensure lists and dicts from loaded_config are valid
    exclude_paths = loaded_config.get('exclude_paths')
    if isinstance(exclude_paths, list):
        # Combine default and loaded exclusions, remove duplicates
        final_config['exclude_paths'] = list(set(final_config['exclude_paths'] + exclude_paths))
    elif exclude_paths is not None:
         print(f"Warning: 'exclude_paths' in config is not a list. Ignoring.")

    force_include = loaded_config.get('force_include')
    if isinstance(force_include, list):
        final_config['force_include'] = force_include
    elif force_include is not None:
         print(f"Warning: 'force_include' in config is not a list. Ignoring.")

    include_extensions = loaded_config.get('include_extensions')
    if isinstance(include_extensions, list):
        # Overwrite default (empty list means include all)
        final_config['include_extensions'] = [ext.lower() for ext in include_extensions if isinstance(ext, str)]
    elif include_extensions is not None:
         print(f"Warning: 'include_extensions' in config is not a list. Ignoring.")

    anonymize = loaded_config.get('anonymize')
    if isinstance(anonymize, dict):
         final_config['anonymize'] = anonymize
    elif anonymize is not None:
         print(f"Warning: 'anonymize' in config is not a dict. Ignoring.")


    # Ensure all keys exist
    for key in DEFAULT_CONFIG:
        if key not in final_config:
            final_config[key] = DEFAULT_CONFIG[key]

    return final_config