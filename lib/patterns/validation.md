# Pattern: Validation

## Purpose

Validate skill metadata for API compatibility before export or upload.

## When to Use

After frontmatter transformation, before creating ZIP or calling API.

---

## Validation Rules

### Name

| Rule | Requirement |
|------|-------------|
| Required | Yes - must have `name` field |
| Max length | 64 characters |
| Pattern | `^[a-z0-9-]+$` (lowercase, numbers, hyphens) |
| Forbidden | Cannot contain "anthropic" or "claude" |
| ZIP match | Must match folder name in ZIP |

### Description

| Rule | Requirement |
|------|-------------|
| Required | Yes - must have `description` field |
| Max length | 1024 characters |
| Min length | 1 character (non-empty) |
| Forbidden | No XML tags (`<...>`) |

---

## Validation Process

### Step 1: Check Name Exists

```
if no 'name' field:
    ERROR: "Missing required field: name"
```

### Step 2: Validate Name Format

```
name = skill.name

if len(name) > 64:
    ERROR: "Name too long: {len(name)} chars (max 64)"
    SUGGEST: "{name[:64]}"

if not matches ^[a-z0-9-]+$:
    ERROR: "Name has invalid characters"
    SUGGEST: Convert to lowercase, replace invalid chars with hyphens

if "anthropic" in name.lower():
    ERROR: "Name cannot contain 'anthropic'"
    SUGGEST: Remove or replace

if "claude" in name.lower():
    ERROR: "Name cannot contain 'claude'"
    SUGGEST: Replace with 'cc' or remove
```

### Step 3: Check Description Exists

```
if no 'description' field:
    ERROR: "Missing required field: description"
    SUGGEST: Use first paragraph from skill body
```

### Step 4: Validate Description Format

```
desc = skill.description

if len(desc) == 0:
    ERROR: "Description is empty"
    SUGGEST: Use first paragraph from skill body

if len(desc) > 1024:
    ERROR: "Description too long: {len(desc)} chars (max 1024)"
    SUGGEST: Truncate to 1024 chars

if contains XML tags:
    ERROR: "Description contains XML tags"
    SUGGEST: Strip all <...> patterns
```

---

## Common Validation Errors

### Name Issues

| Input | Problem | Suggestion |
|-------|---------|------------|
| `My_Skill` | Uppercase, underscore | `my-skill` |
| `data processor` | Space | `data-processor` |
| `claude-helper` | Contains "claude" | `cc-helper` or `code-helper` |
| `anthropic-sync` | Contains "anthropic" | `api-sync` |
| `really-long-skill-name-that-goes-on-and-on...` | >64 chars | Truncate |

### Description Issues

| Input | Problem | Suggestion |
|-------|---------|------------|
| `""` (empty) | Empty | Extract from body |
| `<b>Bold</b> skill` | XML tags | `Bold skill` |
| (1000+ chars) | Too long | Truncate |

---

## Extracting Description from Body

If description is missing or empty, extract from SKILL.md body:

```markdown
---
name: my-skill
description:   # Empty!
---

# My Skill

This skill helps you process data efficiently using
advanced algorithms and pattern matching.

## Features
...
```

**Suggested description:**
```
This skill helps you process data efficiently using advanced algorithms and pattern matching.
```

Rules for extraction:
1. Skip the first `# Heading` line
2. Take the first non-empty paragraph
3. Truncate to 1024 chars if needed
4. Present to user for approval

---

## Validation Report

After validation, report results:

### Success

```
Validation passed!

Name: my-skill (12 chars) ✓
Description: "Does something useful" (21 chars) ✓
```

### Failure

```
Validation failed!

Name: claude-helper
  ✗ Cannot contain 'claude'
  Suggestion: 'cc-helper' or 'code-helper'

Description: (empty)
  ✗ Description is required
  Suggestion: "This skill helps with..." (from body)

Fix these issues before proceeding.
```

---

## User Interaction

**Don't auto-fix** - present suggestions and let user decide:

```
The skill name 'claude-helper' contains 'claude' which is not allowed.

Suggested alternatives:
1. cc-helper
2. code-helper
3. gh-helper (if GitHub-related)

Which would you like to use, or enter a custom name?
```

This ensures the user controls their skill's identity.
