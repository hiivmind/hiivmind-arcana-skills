#!/usr/bin/env python3
"""State file management for uploaded skills.

Tracks skills uploaded to the Anthropic Skills API so we can:
- Update existing skills instead of creating duplicates
- Delete skills by name instead of needing the API ID
- See what has been synced and when

Usage:
    python3 state.py get my-skill
    python3 state.py set my-skill --skill-id skill_01AbCd... --source-path /path/to/skill
    python3 state.py list
    python3 state.py delete my-skill

State file: ~/.claude/hiivmind-arcana.state.yaml
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML library required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


STATE_FILE = Path.home() / ".claude" / "hiivmind-arcana.state.yaml"


def load_state() -> dict:
    """Load state from file, creating default if not exists."""
    if STATE_FILE.exists():
        try:
            content = STATE_FILE.read_text()
            return yaml.safe_load(content) or {"version": "1.0", "uploads": {}}
        except Exception as e:
            print(f"Warning: Could not parse state file: {e}", file=sys.stderr)
            return {"version": "1.0", "uploads": {}}
    return {"version": "1.0", "uploads": {}}


def save_state(state: dict) -> None:
    """Save state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(yaml.dump(state, default_flow_style=False, sort_keys=False))


def get_skill(name: str) -> None:
    """Get info for a skill by name."""
    state = load_state()
    entry = state.get("uploads", {}).get(name)

    if entry:
        print(yaml.dump({name: entry}, default_flow_style=False))
    else:
        print(f"Not found: {name}", file=sys.stderr)
        sys.exit(1)


def set_skill(name: str, skill_id: str, source_path: str) -> None:
    """Record or update a skill in state."""
    state = load_state()
    uploads = state.setdefault("uploads", {})

    # Get existing version or start at 0
    existing = uploads.get(name, {})
    current_version = existing.get("version", 0)

    uploads[name] = {
        "skill_id": skill_id,
        "version": current_version + 1,
        "last_sync": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_path": str(Path(source_path).resolve())
    }

    save_state(state)
    print(f"Saved: {name} → {skill_id} (v{current_version + 1})")


def list_skills() -> None:
    """List all tracked skills."""
    state = load_state()
    uploads = state.get("uploads", {})

    if uploads:
        print(yaml.dump(uploads, default_flow_style=False))
    else:
        print("No skills tracked yet.")


def sync_from_api(api_data: list) -> None:
    """Sync state from API list output. Only tracks custom skills."""
    state = load_state()
    uploads = state.setdefault("uploads", {})

    added = 0
    updated = 0
    for skill in api_data:
        if skill.get("source") != "custom":
            continue

        name = skill["display_title"]
        skill_id = skill["id"]
        existing = uploads.get(name)

        if existing and existing.get("skill_id") == skill_id:
            existing["latest_version"] = skill.get("latest_version")
            existing["updated_at"] = skill.get("updated_at")
            updated += 1
        else:
            uploads[name] = {
                "skill_id": skill_id,
                "latest_version": skill.get("latest_version"),
                "created_at": skill.get("created_at"),
                "updated_at": skill.get("updated_at"),
                "source_path": None,
            }
            added += 1

    save_state(state)
    print(f"Synced: {added} added, {updated} updated, {len(uploads)} total tracked")


def delete_skill(name: str) -> None:
    """Remove a skill from tracking."""
    state = load_state()
    uploads = state.get("uploads", {})

    if name in uploads:
        del uploads[name]
        save_state(state)
        print(f"Deleted: {name}")
    else:
        print(f"Not found: {name}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage skill upload state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check if a skill has been uploaded
    python3 state.py get my-skill

    # Record a skill upload
    python3 state.py set my-skill --skill-id skill_01AbCd... --source-path /path/to/skill

    # List all tracked skills
    python3 state.py list

    # Remove a skill from tracking
    python3 state.py delete my-skill

State file: ~/.claude/hiivmind-arcana.state.yaml
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # get command
    p_get = subparsers.add_parser("get", help="Get info for a skill")
    p_get.add_argument("name", help="Skill name")

    # set command
    p_set = subparsers.add_parser("set", help="Record a skill upload")
    p_set.add_argument("name", help="Skill name")
    p_set.add_argument("--skill-id", "-i", required=True, help="API skill ID")
    p_set.add_argument("--source-path", "-p", required=True, help="Path to source skill")

    # list command
    subparsers.add_parser("list", help="List all tracked skills")

    # delete command
    p_del = subparsers.add_parser("delete", help="Remove a skill from tracking")
    p_del.add_argument("name", help="Skill name")

    # sync command
    p_sync = subparsers.add_parser("sync", help="Sync state from API (pipe json from api.py list)")
    p_sync.add_argument("--json", "-j", help="JSON string from api.py list (reads stdin if omitted)")

    args = parser.parse_args()

    if args.command == "get":
        get_skill(args.name)
    elif args.command == "set":
        set_skill(args.name, args.skill_id, args.source_path)
    elif args.command == "list":
        list_skills()
    elif args.command == "delete":
        delete_skill(args.name)
    elif args.command == "sync":
        import json
        if args.json:
            raw = args.json
        else:
            raw = sys.stdin.read()
        data = json.loads(raw)
        skills = data.get("data", data) if isinstance(data, dict) else data
        sync_from_api(skills)


if __name__ == "__main__":
    main()
