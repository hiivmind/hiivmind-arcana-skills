#!/usr/bin/env python3
"""Create a ZIP file from an explicit file list.

This tool takes a list of files and creates a ZIP with a skill-name/ prefix.
Claude determines WHAT to bundle; this tool does the mechanical work.

Usage:
    python3 zip_skill.py --name my-skill --output /tmp/my-skill.zip \
        --base-path /path/to/skill \
        file1.md file2.py data/index.md

    # Or with files from different locations:
    python3 zip_skill.py --name my-skill --output /tmp/my-skill.zip \
        /full/path/to/SKILL.md \
        /full/path/to/data/index.md
"""

import argparse
import sys
import zipfile
from pathlib import Path


def create_zip(
    name: str,
    output: str,
    files: list[str],
    base_path: str | None = None
) -> str:
    """Create a ZIP file with skill-name/ prefix.

    Args:
        name: Skill name (becomes folder in ZIP)
        output: Output ZIP path
        files: List of file paths to include
        base_path: If provided, paths are made relative to this

    Returns:
        Path to created ZIP file
    """
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    base = Path(base_path) if base_path else None
    added_files = []

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            source = Path(file_path)

            if not source.exists():
                print(f"Warning: {file_path} does not exist, skipping", file=sys.stderr)
                continue

            if not source.is_file():
                print(f"Warning: {file_path} is not a file, skipping", file=sys.stderr)
                continue

            # Calculate the archive name
            if base:
                try:
                    rel_path = source.resolve().relative_to(base.resolve())
                except ValueError:
                    # File is not under base_path, use just the filename
                    rel_path = source.name
            else:
                rel_path = source.name

            archive_name = f"{name}/{rel_path}"

            # Avoid duplicates
            if archive_name in added_files:
                print(f"Warning: {archive_name} already added, skipping duplicate", file=sys.stderr)
                continue

            zf.write(source, archive_name)
            added_files.append(archive_name)
            print(f"Added: {archive_name}")

    print(f"\nCreated: {output_path}")
    print(f"Total files: {len(added_files)}")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Create a ZIP file from a list of files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage with base path
    python3 zip_skill.py --name my-skill --output ~/Downloads/my-skill.zip \\
        --base-path /path/to/skill \\
        SKILL.md data/index.md scripts/helper.py

    # Full paths (no base path)
    python3 zip_skill.py --name my-skill --output ~/Downloads/my-skill.zip \\
        /path/to/SKILL.md /path/to/data/index.md
        """
    )

    parser.add_argument(
        "--name", "-n",
        required=True,
        help="Skill name (becomes root folder in ZIP)"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output ZIP file path"
    )

    parser.add_argument(
        "--base-path", "-b",
        help="Base path for calculating relative paths in ZIP"
    )

    parser.add_argument(
        "files",
        nargs="+",
        help="Files to include in the ZIP"
    )

    args = parser.parse_args()

    try:
        create_zip(args.name, args.output, args.files, args.base_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
