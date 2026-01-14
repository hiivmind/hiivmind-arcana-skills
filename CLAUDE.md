# CLAUDE.md

This file provides guidance to Claude Code when working with this plugin.

## Plugin Overview

**hiivmind-arcana-skills** transforms Claude Code skills for other Claude surfaces:
- **claude.ai** - ZIP export for individual upload
- **Messages API** - Direct upload for workspace-wide availability

## Architecture

```
lib/
├── patterns/     # HOW to do things (read these to learn procedures)
├── references/   # WHAT exists (read these for specifications)
└── tools/        # Python scripts (call these for mechanical work)

skills/
├── arcana/             # Gateway - routes to appropriate skill
├── arcana-discover/    # Find skills in a directory
├── arcana-export-zip/  # Export for claude.ai
└── arcana-upload-api/  # Upload to Messages API
```

## Key Principle

**Claude does thinking. Python does mechanics.**

- Use `lib/patterns/` to guide your analysis and decisions
- Use `lib/references/` for specifications and constraints
- Use `lib/tools/` only for mechanical operations (zipping, API calls, state I/O)

## Path Convention

`{PLUGIN_ROOT}` = This plugin's root directory (where plugin.json lives)

When skills reference `{PLUGIN_ROOT}/lib/patterns/skill-analysis.md`, read from this plugin's lib folder.

## Common Operations

### Export a skill
1. Read `lib/patterns/skill-analysis.md`
2. Analyze the target skill (understand what it does, what files it needs)
3. Read `lib/patterns/frontmatter-transform.md`
4. Transform the SKILL.md (strip CC-only fields)
5. Read `lib/references/validation-rules.md`
6. Validate name/description
7. Call `lib/tools/zip_skill.py` with the file list

### Upload to API
1. Same as export (steps 1-6)
2. Read `lib/references/api-spec.md`
3. Call `lib/tools/api.py upload`
4. Update state with `lib/tools/state.py`

## State File

Uploads are tracked in `~/.claude/hiivmind-arcana.state.yaml`

## Python Tools

All tools are CLI scripts with `--help`:

```bash
python3 lib/tools/zip_skill.py --help
python3 lib/tools/api.py --help
python3 lib/tools/state.py --help
```
