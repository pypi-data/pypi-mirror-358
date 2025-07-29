import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from .anonymizer import Anonymizer
from .tree import generate_tree_string

# Max file size to read (e.g., 5MB) to avoid memory issues with huge files
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

def is_likely_binary(file_path: Path) -> bool:
    """Check if a file is likely binary by reading the first few bytes."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024) # Read the first 1KB
            return b'\x00' in chunk # Null byte is a strong indicator of binary files
    except Exception:
        return True # Treat read errors as potentially binary/problematic

def _should_skip(
    path: Path,
    root_dir: Path,
    exclude_paths: List[str],
    include_extensions: List[str],
    force_include: List[str] = None,
    class_name: Optional[str] = None,
    check_content: bool = False
) -> bool:
    """Determines if a file or directory should be skipped based on configuration."""
    if force_include is None:
        force_include = []

    try:
        relative_path_str = str(path.relative_to(root_dir))
    except ValueError:
        # The path is not within the root directory, which can happen with symlinks.
        # We'll treat it as something to skip.
        return True

    # 1. Check for force inclusion
    # If a path is explicitly force-included, we ignore subsequent exclusion rules.
    is_force_included = False
    for force in force_include:
        if relative_path_str == force or relative_path_str.startswith(force + os.path.sep):
            # It's a match or a child of a match. Don't skip based on rules.
            # Still need to check for things like file size for files.
            is_force_included = True
            break
    
    if is_force_included:
        if path.is_file():
            # Still check for fundamental issues like size or accessibility
            try:
                if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    print(f"Warning: Force-included file is too large: {path.relative_to(root_dir)}")
                    return True
            except OSError:
                print(f"Warning: Could not access force-included file {path.relative_to(root_dir)}. Skipping.")
                return True
        return False  # Don't skip this item

    # 2. Check for exclusion
    is_excluded = False
    for exclude in exclude_paths:
        # Check for exact match or if the path is inside an excluded directory
        if relative_path_str == exclude or relative_path_str.startswith(exclude + os.path.sep):
            is_excluded = True
            break
        # Also check just the name (e.g., 'node_modules')
        if path.name == exclude:
            is_excluded = True
            break

    if is_excluded:
        # If it's an excluded path, we must still check if it's a parent of a force-included path.
        # This prevents `os.walk` from skipping a directory like `data` if `data/input.txt` is forced.
        if path.is_dir():
            for force in force_include:
                if force.startswith(relative_path_str + os.path.sep):
                    return False  # Don't skip this directory, a child is force-included.
        return True  # It's genuinely excluded.


    if path.is_file():
        # Check file size
        try:
            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                print(f"Skipping large file: {path.relative_to(root_dir)}")
                return True
        except OSError:
             print(f"Warning: Could not get size for {path.relative_to(root_dir)}. Skipping.")
             return True # Skip if we can't get size

        # Check extensions if specified
        if include_extensions and path.suffix.lower() not in include_extensions:
            # print(f"Skipping {path.relative_to(root_dir)} (extension mismatch)")
            return True

        # Check if likely binary
        if is_likely_binary(path):
            print(f"Skipping likely binary file: {path.relative_to(root_dir)}")
            return True

        # Check content for class name if in class mode
        if check_content and class_name:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if class_name not in content:
                        # print(f"Skipping {path.relative_to(root_dir)} (class name '{class_name}' not found)")
                        return True
            except Exception as e:
                print(f"Warning: Could not read {path.relative_to(root_dir)} for class check: {e}. Skipping.")
                return True # Skip if reading fails

    return False


def format_repo_to_markdown(
    root_dir: str,
    config: Dict,
    anonymize_flag: bool,
    class_name: Optional[str] = None
) -> Tuple[str, List[Path]]:
    """
    Generates the markdown content for the repository.
    Returns the markdown string and a list of included file paths.
    """
    root_path = Path(root_dir).resolve()
    exclude_paths = config.get('exclude_paths', [])
    force_include = config.get('force_include', [])
    include_extensions = config.get('include_extensions', [])
    anonymize_rules = config.get('anonymize', {}) if anonymize_flag else {}

    anonymizer = Anonymizer(anonymize_rules)

    markdown_content = []
    included_files = []

    # 1. Generate Tree Structure
    print("Generating directory tree...")
    tree_string = generate_tree_string(root_path, exclude_paths, force_include, include_extensions, anonymizer if anonymize_flag else None)
    markdown_content.append("# Repository Structure")
    markdown_content.append("```")
    markdown_content.append(tree_string)
    markdown_content.append("```")
    markdown_content.append("\n---\n") # Separator

    # 2. Walk through the directory and collect file contents
    print("Collecting and formatting file contents...")
    markdown_content.append("# File Contents")

    # Use os.walk for better control over skipping directories
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        current_path = Path(dirpath)

        # Filter dirnames in-place to prevent descending into excluded directories
        # Important: Modify dirnames[:] to change the list os.walk uses
        original_dirnames = list(dirnames) # Copy for iteration
        dirnames[:] = [d for d in original_dirnames if not _should_skip(current_path / d, root_path, exclude_paths, [], force_include)]


        for filename in filenames:
            file_path = current_path / filename

            # Determine if we need to check content based on mode
            check_content_for_class = (class_name is not None)

            if _should_skip(file_path, root_path, exclude_paths, include_extensions, force_include, class_name, check_content_for_class):
                continue

            relative_path = file_path.relative_to(root_path)
            anonymized_rel_path_str = anonymizer.anonymize_path(str(relative_path)) if anonymize_flag else str(relative_path)

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if anonymize_flag:
                    content = anonymizer.anonymize(content)

                # Determine language for syntax highlighting (optional but nice)
                lang = file_path.suffix.lstrip('.').lower()
                if lang == 'md': lang = 'markdown'
                if lang == 'py': lang = 'python'
                if lang == 'js': lang = 'javascript'
                if lang == 'ts': lang = 'typescript'
                if lang == 'h': lang = 'cpp' # Treat .h as C++
                if lang == 'hpp': lang = 'cpp'
                if lang == 'c': lang = 'c'
                if lang == 'cpp': lang = 'cpp'
                if lang == 'java': lang = 'java'
                if lang == 'sh': lang = 'bash'
                if lang == 'yml': lang = 'yaml'
                # Add more mappings as needed

                markdown_content.append(f"\n## `{anonymized_rel_path_str}`\n")
                markdown_content.append(f"```{lang}")
                markdown_content.append(content.strip()) # Strip leading/trailing whitespace from content
                markdown_content.append("```")
                included_files.append(relative_path) # Store original relative path

            except Exception as e:
                print(f"Warning: Could not process file {relative_path}: {e}")

    if not included_files:
         markdown_content.append("\n*No files were included based on the current filters.*")

    return "\n".join(markdown_content), included_files
