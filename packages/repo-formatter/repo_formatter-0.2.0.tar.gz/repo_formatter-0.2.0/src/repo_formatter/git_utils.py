import subprocess
from pathlib import Path
from typing import Tuple, List

def _run_git_command(args: List[str], cwd: str) -> Tuple[bool, str]:
    """Runs a git command and returns (success, output_or_error)."""
    try:
        process = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=False, # Don't raise exception on non-zero exit
            encoding='utf-8',
            errors='ignore' # Ignore decoding errors for potentially binary diffs
        )
        if process.returncode == 0:
            return True, process.stdout
        else:
            error_message = f"Git command failed: {' '.join(['git'] + args)}\n"
            error_message += f"Stderr: {process.stderr}\n"
            error_message += f"Stdout: {process.stdout}"
            return False, error_message
    except FileNotFoundError:
        return False, "Error: 'git' command not found. Is Git installed and in your PATH?"
    except Exception as e:
        return False, f"Error running git command: {e}"

def get_current_changes_diff(repo_path: str) -> Tuple[bool, str]:
    """Gets the diff for uncommitted changes."""
    print(f"Getting diff for current changes in: {repo_path}")
    return _run_git_command(["diff", "HEAD"], cwd=repo_path)

def get_commit_diff(repo_path: str, diff_target: str) -> Tuple[bool, str]:
    """Gets the diff between two commits/branches or a commit and HEAD."""
    target1 = diff_target
    target2 = "HEAD" # Default comparison target

    # Check if diff_target contains '...' for range diff
    if '...' in diff_target:
        parts = diff_target.split('...', 1)
        target1 = parts[0]
        target2 = parts[1]
        print(f"Getting diff between {target1} and {target2} in: {repo_path}")
        return _run_git_command(["diff", f"{target1}...{target2}"], cwd=repo_path)
    elif '..' in diff_target:
         parts = diff_target.split('..', 1)
         target1 = parts[0]
         target2 = parts[1]
         print(f"Getting diff between {target1} and {target2} in: {repo_path}")
         return _run_git_command(["diff", f"{target1}..{target2}"], cwd=repo_path)
    else:
        # Assume diff against target and working tree or HEAD if single ref
        # Let's default to diffing against HEAD for simplicity if only one ref given
        print(f"Getting diff between {diff_target} and HEAD in: {repo_path}")
        return _run_git_command(["diff", diff_target], cwd=repo_path) # Diff between target and working tree
        # Or: return _run_git_command(["diff", f"{diff_target}..HEAD"], cwd=repo_path) # Diff between target and HEAD commit

def check_repo(repo_path: str) -> bool:
    """Checks if the path is a git repository."""
    git_dir = Path(repo_path) / ".git"
    return git_dir.is_dir()