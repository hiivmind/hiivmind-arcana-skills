#!/usr/bin/env python3
"""Thin wrapper for Anthropic Skills API.

This tool handles the mechanical parts of API interaction.
Claude decides WHEN and WHAT to upload; this tool does the HTTP work.

Usage:
    python3 api.py upload /path/to/skill.zip --title "My Skill"
    python3 api.py version skill_01AbCd... /path/to/skill.zip
    python3 api.py list
    python3 api.py get skill_01AbCd...
    python3 api.py delete skill_01AbCd...
    python3 api.py diagnose

Requires ANTHROPIC_API_KEY environment variable.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: uv pip install requests", file=sys.stderr)
    sys.exit(1)


API_BASE = "https://api.anthropic.com/v1/skills"

BETA_HEADER = "skills-2025-10-02"

HEADERS = {
    "anthropic-version": "2023-06-01",
    "anthropic-beta": BETA_HEADER,
}

DEBUG = False


def debug_log(msg: str) -> None:
    if DEBUG:
        print(f"[debug] {msg}", file=sys.stderr)


def debug_request(method: str, url: str, headers: dict, **kwargs) -> None:
    if not DEBUG:
        return
    safe_headers = {k: (v[:12] + "..." if k == "x-api-key" else v) for k, v in headers.items()}
    print(f"[debug] {method} {url}", file=sys.stderr)
    print(f"[debug] headers: {json.dumps(safe_headers, indent=2)}", file=sys.stderr)
    if "data" in kwargs:
        print(f"[debug] data: {kwargs['data']}", file=sys.stderr)


def debug_response(response) -> None:
    if not DEBUG:
        return
    print(f"[debug] status: {response.status_code}", file=sys.stderr)
    print(f"[debug] response headers: {dict(response.headers)}", file=sys.stderr)
    body = response.text[:2000] if len(response.text) > 2000 else response.text
    print(f"[debug] body: {body}", file=sys.stderr)


def resolve_api_key() -> str:
    """Resolve API key from environment, falling back to shell profile."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        debug_log("API key found in environment")
        return key

    for profile in ["~/.bashrc", "~/.zshrc", "~/.profile", "~/.bash_profile"]:
        path = os.path.expanduser(profile)
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("export ANTHROPIC_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip("'\"")
                        if val:
                            debug_log(f"API key found in {profile}")
                            return val
        except OSError:
            continue

    print("Error: ANTHROPIC_API_KEY not found in environment or shell profiles", file=sys.stderr)
    print("Set it with: export ANTHROPIC_API_KEY=sk-ant-...", file=sys.stderr)
    sys.exit(1)


def handle_error(response) -> None:
    """Print a structured error with diagnostic hints."""
    status = response.status_code
    try:
        body = response.json()
        error_type = body.get("error", {}).get("type", "unknown")
        error_msg = body.get("error", {}).get("message", response.text)
    except (ValueError, KeyError):
        error_type = "unknown"
        error_msg = response.text

    print(f"Error {status} ({error_type}): {error_msg}", file=sys.stderr)

    hints = {
        401: "Check your API key is valid and not revoked.",
        403: "Your API key may lack permissions. Check workspace access.",
        404: (
            "The /v1/skills endpoint returned 404. Possible causes:\n"
            "  - Skills API may not be enabled for your workspace\n"
            "  - The beta header may need updating (current: {beta})\n"
            "  - Try: curl -s -o /dev/null -w '%{{http_code}}' -H 'x-api-key: $KEY' "
            "-H 'anthropic-version: 2023-06-01' -H 'anthropic-beta: {beta}' "
            "https://api.anthropic.com/v1/skills"
        ).format(beta=BETA_HEADER),
        413: "ZIP file is too large. Check file size.",
        422: "Validation error. Check skill name/description constraints.",
        429: "Rate limited. Wait and retry.",
    }

    if status in hints:
        print(f"Hint: {hints[status]}", file=sys.stderr)

    if status >= 500:
        print("Hint: Server error. Retry in a moment, or check status.anthropic.com", file=sys.stderr)

    debug_response(response)
    sys.exit(1)


def make_request(method: str, url: str, **kwargs) -> requests.Response:
    """Make an authenticated API request with debug logging."""
    headers = {**HEADERS, "x-api-key": resolve_api_key()}
    if "headers" in kwargs:
        headers.update(kwargs.pop("headers"))

    debug_request(method, url, headers, **kwargs)

    response = requests.request(method, url, headers=headers, **kwargs)

    debug_response(response)

    if not response.ok:
        handle_error(response)

    return response


def upload(zip_path: str, title: str) -> dict:
    """Upload a new skill."""
    zip_file = Path(zip_path)
    if not zip_file.exists():
        print(f"Error: ZIP file not found: {zip_path}", file=sys.stderr)
        sys.exit(1)

    debug_log(f"Uploading {zip_file.name} ({zip_file.stat().st_size} bytes)")

    with open(zip_file, "rb") as f:
        response = make_request(
            "POST", API_BASE,
            files={"file": (zip_file.name, f, "application/zip")},
            data={"title": title},
        )

    result = response.json()
    print(json.dumps(result, indent=2))
    return result


def create_version(skill_id: str, zip_path: str) -> dict:
    """Create a new version of an existing skill."""
    zip_file = Path(zip_path)
    if not zip_file.exists():
        print(f"Error: ZIP file not found: {zip_path}", file=sys.stderr)
        sys.exit(1)

    debug_log(f"Uploading new version for {skill_id}")

    with open(zip_file, "rb") as f:
        response = make_request(
            "POST", f"{API_BASE}/{skill_id}/versions",
            files={"file": (zip_file.name, f, "application/zip")},
        )

    result = response.json()
    print(json.dumps(result, indent=2))
    return result


def list_skills() -> list:
    """List all skills in the workspace."""
    response = make_request("GET", API_BASE)
    result = response.json()

    data = result.get("data", [])
    if not data:
        print("No skills found.")
        return []

    print(json.dumps(result, indent=2))
    return data


def get_skill(skill_id: str) -> dict:
    """Get details for a single skill."""
    response = make_request("GET", f"{API_BASE}/{skill_id}")
    result = response.json()
    print(json.dumps(result, indent=2))
    return result


def delete_skill(skill_id: str) -> None:
    """Delete a skill."""
    make_request("DELETE", f"{API_BASE}/{skill_id}")
    print(f"Deleted: {skill_id}")


def diagnose() -> None:
    """Check API connectivity and auth, report what works and what doesn't."""
    print("=== Skills API Diagnostics ===\n")

    key = resolve_api_key()
    masked = key[:12] + "..." + key[-4:] if len(key) > 16 else "***"
    print(f"API key: {masked}")
    print(f"Endpoint: {API_BASE}")
    print(f"Beta header: {BETA_HEADER}")
    print()

    # Test 1: Auth — hit /v1/models which is always available
    print("[1/3] Testing auth via /v1/models...")
    try:
        r = requests.get(
            "https://api.anthropic.com/v1/models",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            timeout=10,
        )
        if r.ok:
            print(f"  OK — authenticated successfully (status {r.status_code})")
        else:
            print(f"  FAIL — status {r.status_code}: {r.text[:200]}")
            return
    except requests.exceptions.RequestException as e:
        print(f"  FAIL — network error: {e}")
        return

    # Test 2: Skills endpoint without beta header
    print("[2/3] Testing /v1/skills without beta header...")
    try:
        r = requests.get(
            API_BASE,
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            timeout=10,
        )
        print(f"  Status {r.status_code}: {r.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"  FAIL — network error: {e}")

    # Test 3: Skills endpoint with beta header
    print(f"[3/3] Testing /v1/skills with beta header ({BETA_HEADER})...")
    try:
        r = requests.get(
            API_BASE,
            headers={**HEADERS, "x-api-key": key},
            timeout=10,
        )
        print(f"  Status {r.status_code}: {r.text[:200]}")
        if r.ok:
            data = r.json().get("data", [])
            print(f"\n  Skills API is working. Found {len(data)} skill(s).")
        elif r.status_code == 404:
            print("\n  Skills API returned 404 — endpoint may not be enabled for this workspace.")
            print("  Try the managed-agents beta header instead:")
            print(f"  anthropic-beta: managed-agents-2026-04-01")

            # Bonus: try with managed-agents header
            r2 = requests.get(
                API_BASE,
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "anthropic-beta": "managed-agents-2026-04-01",
                },
                timeout=10,
            )
            print(f"\n  With managed-agents header: status {r2.status_code}")
            if r2.ok:
                print("  That worked! Update BETA_HEADER in this script.")
    except requests.exceptions.RequestException as e:
        print(f"  FAIL — network error: {e}")


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

    # Get a specific skill
    python3 api.py get skill_01AbCdEfGh

    # Delete a skill
    python3 api.py delete skill_01AbCdEfGh

    # Diagnose connectivity issues
    python3 api.py diagnose

    # Debug mode (any command)
    python3 api.py --debug list

Environment:
    ANTHROPIC_API_KEY - Required (checked in env, then shell profiles)
        """
    )

    parser.add_argument("--debug", action="store_true", help="Print request/response details")

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_upload = subparsers.add_parser("upload", help="Upload a new skill")
    p_upload.add_argument("zip_path", help="Path to skill ZIP file")
    p_upload.add_argument("--title", "-t", required=True, help="Display title for the skill")

    p_version = subparsers.add_parser("version", help="Create new version of existing skill")
    p_version.add_argument("skill_id", help="Existing skill ID")
    p_version.add_argument("zip_path", help="Path to updated skill ZIP file")

    subparsers.add_parser("list", help="List all skills")

    p_get = subparsers.add_parser("get", help="Get details for a skill")
    p_get.add_argument("skill_id", help="Skill ID to retrieve")

    p_delete = subparsers.add_parser("delete", help="Delete a skill")
    p_delete.add_argument("skill_id", help="Skill ID to delete")

    subparsers.add_parser("diagnose", help="Check API connectivity and auth")

    args = parser.parse_args()

    global DEBUG
    DEBUG = args.debug

    try:
        if args.command == "upload":
            upload(args.zip_path, args.title)
        elif args.command == "version":
            create_version(args.skill_id, args.zip_path)
        elif args.command == "list":
            list_skills()
        elif args.command == "get":
            get_skill(args.skill_id)
        elif args.command == "delete":
            delete_skill(args.skill_id)
        elif args.command == "diagnose":
            diagnose()
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
