# hiivmind-arcana-skills

Transform and transport Claude Code skills to other Claude surfaces.

## The Problem

Claude has **3 distinct skill surfaces** that don't sync automatically:

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Skills                        │
│                    (source realm)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            │        ARCANA             │
            │  (transformation layer)   │
            └─────────────┬─────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Claude Code │   │ claude.ai   │   │ Messages    │
│ (filesystem)│   │ (ZIP upload)│   │ API         │
├─────────────┤   ├─────────────┤   ├─────────────┤
│ Personal/   │   │ Individual  │   │ Workspace-  │
│ project     │   │ user only   │   │ wide        │
└─────────────┘   └─────────────┘   └─────────────┘
     source          /arcana           /arcana
                   export-zip        upload-api
```

| Surface | Storage | Sharing Scope | How to Install |
|---------|---------|---------------|----------------|
| **Claude Code** | Local filesystem | Personal or per-project | Copy files or install plugin |
| **claude.ai Web** | Cloud (per-user) | Individual only | Upload ZIP via Settings > Features |
| **Messages API** | Cloud (per-workspace) | Workspace-wide | Upload via `/v1/skills` API |

This plugin bridges the gap, letting you publish Claude Code skills to the other surfaces.

## Installation

```bash
claude plugin install /path/to/hiivmind-arcana-skills
```

Or add to your Claude Code plugins directory:
```bash
cp -r hiivmind-arcana-skills ~/.claude/plugins/
```

## Usage

### Export for claude.ai (ZIP)

```
/arcana export-zip ~/my-plugin/skills/my-skill
```

Creates a self-contained ZIP ready for upload to claude.ai → Settings → Features → Skills.

### Upload to Messages API

```
/arcana upload-api ~/my-plugin/skills/my-skill
```

Uploads directly to the Anthropic Skills API for workspace-wide availability.

### Discover Skills

```
/arcana discover ~/my-plugin
```

Find and analyze all skills in a plugin directory.

## Architecture: LLM-Driven

This plugin follows a fundamentally different approach than traditional tooling:

**Python does mechanics. Claude does thinking.**

| Task | Who Does It |
|------|-------------|
| Find skills in directory | Claude (Glob/Read) |
| Understand what a skill does | Claude (Read + reasoning) |
| Decide what files to bundle | Claude (semantic analysis) |
| Validate name/description | Claude (pattern-guided) |
| Create ZIP from file list | Python (zip_skill.py) |
| Upload to API | Python (api.py) |
| Track state | Python (state.py) |

### Why LLM-Driven?

Traditional approaches use regex patterns to detect file references. This is:
- **Brittle**: Keeps missing patterns
- **Over-engineered**: Complex regex for something an LLM naturally understands
- **Wrong paradigm**: Deterministic code trying to do semantic understanding

Claude can understand context:
- `"See config-parsing.md for details"` → reference to bundle
- `"Output will be in output.json"` → generated file, don't bundle
- `"Similar to git status"` → not a file reference

## What Gets Transformed

Claude Code skills can have fields that aren't supported by other surfaces:

| Field | Claude Code | API/claude.ai | Action |
|-------|:-----------:|:-------------:|--------|
| `name` | ✓ | ✓ | Keep |
| `description` | ✓ | ✓ | Keep |
| `allowed-tools` | ✓ | ✗ | Strip |
| `model` | ✓ | ✗ | Strip |
| `context` | ✓ | ✗ | Strip |
| `agent` | ✓ | ✗ | Strip |
| `hooks` | ✓ | ✗ | Strip |
| `user-invocable` | ✓ | ✗ | Strip |

## Validation

The API has stricter requirements than Claude Code:

- **name**: ≤64 characters, lowercase letters/numbers/hyphens only, cannot contain "anthropic" or "claude"
- **description**: ≤1024 characters, non-empty, no XML tags

Claude validates and suggests fixes before export/upload.

## Project Structure

```
hiivmind-arcana-skills/
├── .claude-plugin/
│   └── plugin.json
├── lib/
│   ├── patterns/           # HOW to do things
│   │   ├── skill-analysis.md
│   │   ├── dependency-resolution.md
│   │   ├── frontmatter-transform.md
│   │   ├── validation.md
│   │   └── state-tracking.md
│   ├── references/         # WHAT exists
│   │   ├── api-spec.md
│   │   ├── validation-rules.md
│   │   ├── surface-comparison.md
│   │   └── cc-only-fields.md
│   └── tools/              # Minimal Python
│       ├── zip_skill.py
│       ├── api.py
│       └── state.py
├── skills/
│   ├── arcana/             # Gateway
│   ├── arcana-discover/
│   ├── arcana-export-zip/
│   └── arcana-upload-api/
└── README.md
```

## Requirements

- Python 3.8+
- `ANTHROPIC_API_KEY` environment variable (for API upload only)

## License

MIT
