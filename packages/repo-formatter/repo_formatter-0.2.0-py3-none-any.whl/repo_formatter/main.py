import argparse
import sys
from pathlib import Path

from . import config as cfg
from . import core
from . import git_utils
from . import token_estimator
from .anonymizer import Anonymizer

OUTPUT_FILENAME = "repository.md"

def cli():
    parser = argparse.ArgumentParser(
        description="Format repository content into a single Markdown file."
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="The target directory to process (default: current directory).",
    )

    # Mode arguments
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-m", "--mode",
        choices=["normal", "class", "patch"],
        default="normal",
        help="Processing mode: 'normal' (default), 'class', or 'patch'.",
    )
    parser.add_argument(
        "--class-name",
        metavar="NAME",
        help="The class name to search for in 'class' mode.",
    )
    parser.add_argument(
        "--diff-target",
        metavar="TARGET",
        help="Specify the target for 'patch' mode. "
             "Use 'current' for uncommitted changes, or a commit/branch name (e.g., 'main', 'HEAD~1', 'feature-branch..main').",
    )

    # Configuration and Options
    parser.add_argument(
        "-c", "--config",
        metavar="PATH",
        help=f"Path to the configuration YAML file (default: searches for {cfg.DEFAULT_CONFIG_NAME}).",
    )
    parser.add_argument(
        "-a", "--anonymize",
        action="store_true",
        help="Enable anonymization based on config file rules.",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILENAME",
        default=OUTPUT_FILENAME,
        help=f"Name of the output Markdown file (default: {OUTPUT_FILENAME}).",
    )

    args = parser.parse_args()

    # --- Input Validation ---
    target_dir = Path(args.directory).resolve()
    if not target_dir.is_dir():
        print(f"Error: Directory not found: {args.directory}")
        sys.exit(1)

    if args.mode == "class" and not args.class_name:
        print("Error: --class-name is required for 'class' mode.")
        sys.exit(1)

    if args.mode == "patch" and not args.diff_target:
        print("Error: --diff-target is required for 'patch' mode (e.g., 'current', 'main', 'HEAD~1').")
        sys.exit(1)

    output_file_path = target_dir / args.output

    # --- Load Configuration ---
    try:
        config = cfg.load_config(args.config, str(target_dir))
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # --- Execute Mode ---
    markdown_content = ""
    final_output_path = output_file_path # Default output path

    if args.mode == "patch":
        print(f"Running in Patch mode (target: {args.diff_target})...")
        if not git_utils.check_repo(str(target_dir)):
             print(f"Error: Target directory '{target_dir}' is not a Git repository.")
             sys.exit(1)

        success = False
        diff_output = ""
        if args.diff_target.lower() == "current":
            success, diff_output = git_utils.get_current_changes_diff(str(target_dir))
        else:
            success, diff_output = git_utils.get_commit_diff(str(target_dir), args.diff_target)

        if not success:
            print(f"Error getting diff:\n{diff_output}") # diff_output contains error message on failure
            sys.exit(1)

        if not diff_output.strip():
             print("No differences found for the specified target.")
             # Decide whether to create an empty file or exit
             # Let's create a file indicating no diff
             markdown_content = f"# Git Diff: {args.diff_target}\n\n```diff\nNo differences found.\n```"
        else:
            # Anonymize the diff output if requested
            if args.anonymize:
                anonymizer = Anonymizer(config.get('anonymize', {}))
                diff_output = anonymizer.anonymize(diff_output)

            markdown_content = f"# Git Diff: {args.diff_target}\n\n"
            markdown_content += "```diff\n"
            markdown_content += diff_output.strip() + "\n" # Ensure trailing newline
            markdown_content += "```"
        # In patch mode, output file might be better placed outside the repo?
        # For now, place it inside like other modes.
        final_output_path = target_dir / f"diff_{args.diff_target.replace('/', '_').replace('.', '_')}.md"


    elif args.mode == "class":
        print(f"Running in Class mode (searching for '{args.class_name}')...")
        markdown_content, _ = core.format_repo_to_markdown(
            str(target_dir), config, args.anonymize, class_name=args.class_name
        )
        final_output_path = target_dir / f"class_{args.class_name}.md"

    else: # Normal mode
        print("Running in Normal mode...")
        markdown_content, _ = core.format_repo_to_markdown(
            str(target_dir), config, args.anonymize
        )
        final_output_path = target_dir / args.output # Use default or specified output name


    # --- Write Output ---
    try:
        with open(final_output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"\nSuccessfully generated Markdown file: {final_output_path}")
    except Exception as e:
        print(f"\nError writing output file {final_output_path}: {e}")
        sys.exit(1)

    # --- Estimate Tokens ---
    tokens = token_estimator.estimate_tokens(markdown_content)
    # tokens = token_estimator.estimate_tokens_tiktoken(markdown_content) # If using tiktoken
    print(f"Estimated token count (basic): ~{tokens}")

if __name__ == "__main__":
    cli()