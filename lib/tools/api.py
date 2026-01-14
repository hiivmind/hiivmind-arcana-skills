#!/usr/bin/env python3
"""Thin wrapper for Anthropic Skills API.

This tool handles the mechanical parts of API interaction.
Claude decides WHEN and WHAT to upload; this tool does the HTTP work.

Usage:
    python3 api.py upload /path/to/skill.zip --title "My Skill"
    python3 api.py version skill_01AbCd... /path/to/skill.zip
    python3 api.py list
    python3 api.py delete skill_01AbCd...

Requires ANTHROPIC_API_KEY environment variable.
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


API_BASE = "https://api.anthropic.com/v1/skills"

HEADERS = {
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "skills-2025-10-02,code-execution-2025-08-25"
}


def get_api_key() -> str:
    """Get API key from environment."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return key


def upload(zip_path: str, title: str) -> dict:
    """Upload a new skill.

    Args:
        zip_path: Path to ZIP file
        title: Display title for the skill

    Returns:
        API response with skill_id
    """
    headers = {**HEADERS, "x-api-key": get_api_key()}

    zip_file = Path(zip_path)
    if not zip_file.exists():
        print(f"Error: ZIP file not found: {zip_path}", file=sys.stderr)
        sys.exit(1)

    with open(zip_file, "rb") as f:
        response = requests.post(
            API_BASE,
            headers=headers,
            files={"file": (zip_file.name, f, "application/zip")},
            data={"title": title}
        )

    if not response.ok:
        print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    print(json.dumps(result, indent=2))
    return result


def create_version(skill_id: str, zip_path: str) -> dict:
    """Create a new version of an existing skill.

    Args:
        skill_id: Existing skill ID
        zip_path: Path to updated ZIP file

    Returns:
        API response with version info
    """
    headers = {**HEADERS, "x-api-key": get_api_key()}

    zip_file = Path(zip_path)
    if not zip_file.exists():
        print(f"Error: ZIP file not found: {zip_path}", file=sys.stderr)
        sys.exit(1)

    with open(zip_file, "rb") as f:
        response = requests.post(
            f"{API_BASE}/{skill_id}/versions",
            headers=headers,
            files={"file": (zip_file.name, f, "application/zip")}
        )

    if not response.ok:
        print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    print(json.dumps(result, indent=2))
    return result


def list_skills() -> list:
    """List all skills in the workspace.

    Returns:
        List of skill objects
    """
    headers = {**HEADERS, "x-api-key": get_api_key()}

    response = requests.get(API_BASE, headers=headers)

    if not response.ok:
        print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    result = response.json()
    print(json.dumps(result, indent=2))
    return result


def delete(skill_id: str) -> None:
    """Delete a skill.

    Args:
        skill_id: Skill ID to delete
    """
    headers = {**HEADERS, "x-api-key": get_api_key()}

    response = requests.delete(f"{API_BASE}/{skill_id}", headers=headers)

    if not response.ok:
        print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)

    print(f"Deleted: {skill_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Anthropic Skills API wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Upload a new skill
    python3 api.py upload /tmp/my-skill.zip --title "My Skill"

    # Create new version of existing skill
    python3 api.py version skill_01AbCdEfGh /tmp/my-skill.zip

    # List all skills
    python3 api.py list

    # Delete a skill
    python3 api.py delete skill_01AbCdEfGh

Environment:
    ANTHROPIC_API_KEY - Required for all operations
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # upload command
    p_upload = subparsers.add_parser("upload", help="Upload a new skill")
    p_upload.add_argument("zip_path", help="Path to skill ZIP file")
    p_upload.add_argument("--title", "-t", required=True, help="Display title for the skill")

    # version command
    p_version = subparsers.add_parser("version", help="Create new version of existing skill")
    p_version.add_argument("skill_id", help="Existing skill ID")
    p_version.add_argument("zip_path", help="Path to updated skill ZIP file")

    # list command
    subparsers.add_parser("list", help="List all skills")

    # delete command
    p_delete = subparsers.add_parser("delete", help="Delete a skill")
    p_delete.add_argument("skill_id", help="Skill ID to delete")

    args = parser.parse_args()

    try:
        if args.command == "upload":
            upload(args.zip_path, args.title)
        elif args.command == "version":
            create_version(args.skill_id, args.zip_path)
        elif args.command == "list":
            list_skills()
        elif args.command == "delete":
            delete(args.skill_id)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
