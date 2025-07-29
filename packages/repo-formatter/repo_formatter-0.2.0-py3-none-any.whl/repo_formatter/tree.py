import os
from pathlib import Path
from typing import List, Set

def generate_tree_string(start_path: Path, exclude_paths: List[str], force_include: List[str], include_extensions: List[str], anonymizer=None) -> str:
    """
    Generates a string representation of the directory tree, respecting exclusions.
    """
    tree_lines = []
    exclude_set = set(exclude_paths)
    force_include_list = force_include or []
    resolved_start_path = start_path.resolve()

    def is_excluded(path: Path) -> bool:
        """Check if a path should be excluded, considering force-include rules."""
        try:
            relative_path_str = str(path.relative_to(resolved_start_path))
        except ValueError:
            return True  # Not in the project directory, skip.

        # 1. Check for force inclusion. If a path is force-included, it's never excluded.
        for force in force_include_list:
            if relative_path_str == force or relative_path_str.startswith(force + os.path.sep):
                return False

        # 2. Check for exclusion.
        is_excluded_path = False
        for exclude in exclude_set:
            # Check for full path match or if it's a subdirectory of an excluded path.
            if relative_path_str == exclude or relative_path_str.startswith(exclude + os.path.sep):
                is_excluded_path = True
                break
        # Also check for direct name match (e.g., 'node_modules').
        if not is_excluded_path and path.name in exclude_set:
            is_excluded_path = True

        if is_excluded_path:
            # If it's an excluded directory, we must check if it contains a force-included item.
            # If so, we cannot exclude it from the tree.
            if path.is_dir():
                for force in force_include_list:
                    if force.startswith(relative_path_str + os.path.sep):
                        return False  # Don't exclude, a child needs to be shown.
            return True  # It's definitely excluded.

        return False

    def add_items(directory: Path, prefix: str = ""):
        # Sort items for consistent order, directories first.
        try:
            items = sorted(list(directory.iterdir()), key=lambda p: (p.is_file(), p.name.lower()))
        except OSError:
            # Cannot access directory, skip it.
            return
            
        pointers = ['├── '] * (len(items) - 1) + ['└── ']

        for pointer, path in zip(pointers, items):
            if is_excluded(path):
                continue

            anonymized_name = anonymizer.anonymize(path.name) if anonymizer else path.name

            if path.is_dir():
                tree_lines.append(f"{prefix}{pointer}{anonymized_name}/")
                extension = prefix + ('│   ' if pointer == '├── ' else '    ')
                add_items(path, prefix=extension)
            elif path.is_file():
                # Check extension if include_extensions is specified.
                if not include_extensions or path.suffix.lower() in include_extensions:
                    tree_lines.append(f"{prefix}{pointer}{anonymized_name}")

    # Start the tree generation.
    anonymized_root = anonymizer.anonymize(resolved_start_path.name) if anonymizer else resolved_start_path.name
    tree_lines.append(f"{anonymized_root}/")
    add_items(resolved_start_path)
    return "\n".join(tree_lines)
