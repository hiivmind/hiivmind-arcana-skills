# Reference: Validation Rules

## Overview

The Anthropic Skills API has stricter validation than Claude Code. Skills must pass these checks before upload.

---

## Name Validation

| Rule | Requirement |
|------|-------------|
| Required | Yes |
| Max length | 64 characters |
| Pattern | `^[a-z0-9-]+$` |
| Forbidden | Cannot contain "anthropic" or "claude" |
| ZIP match | Must match folder name in ZIP |

### Valid Names

```
✓ my-skill
✓ data-processor
✓ github-helper
✓ api-sync-v2
```

### Invalid Names

```
✗ My_Skill          (uppercase, underscore)
✗ data processor    (space)
✗ claude-helper     (contains "claude")
✗ anthropic-sync    (contains "anthropic")
✗ this-is-a-very-long-skill-name-that-exceeds-the-maximum-allowed-length
```

### Fix Suggestions

| Problem | Suggestion |
|---------|------------|
| Uppercase | Convert to lowercase |
| Underscores | Replace with hyphens |
| Spaces | Replace with hyphens |
| Contains "claude" | Remove or replace (e.g., "cc-helper") |
| Contains "anthropic" | Remove or replace |
| Too long | Truncate to 64 characters |

---

## Description Validation

| Rule | Requirement |
|------|-------------|
| Required | Yes |
| Max length | 1024 characters |
| Min length | 1 character (non-empty) |
| Forbidden | No XML tags |

### Valid Descriptions

```
✓ A skill that helps with data processing
✓ Sync GitHub issues to project boards with automatic status updates
✓ Multi-line descriptions
  are allowed and can span
  several lines
```

### Invalid Descriptions

```
✗ ""                              (empty)
✗ <script>alert('xss')</script>   (contains XML tags)
✗ Process <data> items            (contains XML-like tags)
```

### Fix Suggestions

| Problem | Suggestion |
|---------|------------|
| Empty | Extract first paragraph from SKILL.md body |
| Too long | Truncate to 1024 characters |
| Contains XML | Strip all `<...>` patterns |

---

## Frontmatter Format

The frontmatter must be valid YAML between `---` markers:

```yaml
---
name: my-skill
description: A skill that does something useful
---
```

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Parse error | Invalid YAML | Check quotes, indentation |
| Missing name | No `name` field | Add required field |
| Missing description | No `description` field | Add required field |

---

## ZIP Structure Validation

| Check | Requirement |
|-------|-------------|
| Root folder | Single folder at ZIP root |
| Folder name | Must match `name` in frontmatter |
| SKILL.md | Must exist at `folder/SKILL.md` |
| No hidden files | Avoid `.git/`, `.DS_Store`, etc. |

### Valid Structure

```
my-skill/
├── SKILL.md
├── data/
│   └── index.md
└── scripts/
    └── helper.py
```

### Invalid Structures

```
# Multiple root folders
skill-a/
skill-b/

# No root folder
SKILL.md
data/

# Wrong folder name (if name: my-skill)
wrong-name/
└── SKILL.md

# Missing SKILL.md
my-skill/
└── only-data.md
```

---

## Validation Order

When validating a skill, check in this order:

1. **SKILL.md exists** - Can't proceed without it
2. **Frontmatter parses** - Valid YAML
3. **Name present** - Required field
4. **Name valid** - Passes all name rules
5. **Description present** - Required field
6. **Description valid** - Passes all description rules
7. **ZIP structure** - Folder matches name

Stop and report on first error. Don't batch all errors - fix one at a time.
