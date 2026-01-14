# Pattern: Frontmatter Transform

## Purpose

Strip Claude Code-specific fields from SKILL.md frontmatter to make it compatible with other surfaces.

## When to Use

After skill analysis, before creating the ZIP or uploading to API.

---

## Frontmatter Structure

SKILL.md files have YAML frontmatter between `---` markers:

```markdown
---
name: my-skill
description: Does something useful
allowed-tools: ["Bash", "Read"]
model: haiku
---

# Skill Content

Instructions go here...
```

---

## Fields to Strip

| Field | Why Strip |
|-------|-----------|
| `allowed-tools` | API doesn't support tool restrictions |
| `hooks` | No hook system on other surfaces |
| `context` | Context handling differs |
| `agent` | No subagent support |
| `model` | Model set at request level |
| `user-invocable` | Slash commands are CC-only |
| `disable-model-invocation` | CC behavior control |

## Fields to Keep

| Field | Why Keep |
|-------|----------|
| `name` | Required by API |
| `description` | Required by API |
| `version` | Useful metadata |

---

## Transformation Process

### Step 1: Extract Frontmatter

Find content between first and second `---`:

```python
# Conceptual - Claude does this by reading
lines = skill_content.split('\n')
if lines[0] == '---':
    end_index = lines[1:].index('---') + 1
    frontmatter = '\n'.join(lines[1:end_index])
    body = '\n'.join(lines[end_index+1:])
```

### Step 2: Parse YAML

Parse the frontmatter as YAML to get a dictionary of fields.

### Step 3: Remove Stripped Fields

Remove these keys if present:
- `allowed-tools`
- `hooks`
- `context`
- `agent`
- `model`
- `user-invocable`
- `disable-model-invocation`

### Step 4: Validate Remaining Fields

Check against validation rules (see `lib/references/validation-rules.md`):
- `name`: ≤64 chars, lowercase/numbers/hyphens, no "anthropic"/"claude"
- `description`: ≤1024 chars, non-empty, no XML tags

### Step 5: Reconstruct SKILL.md

Rebuild with clean frontmatter:

```markdown
---
name: my-skill
description: Does something useful
---

# Skill Content

Instructions go here...
```

---

## Example Transformation

### Before

```yaml
---
name: github-helper
description: Helps with GitHub operations
version: 1.0.0
allowed-tools: ["Bash", "Read", "Glob"]
model: haiku
hooks:
  PreToolUse:
    - matcher: Bash
      script: validate.sh
context:
  - lib/patterns/github.md
user-invocable: true
disable-model-invocation: false
---

# GitHub Helper

This skill helps you work with GitHub...
```

### After

```yaml
---
name: github-helper
description: Helps with GitHub operations
version: 1.0.0
---

# GitHub Helper

This skill helps you work with GitHub...
```

---

## Handling Context Files

If the original skill has a `context` field:

```yaml
context:
  - lib/patterns/github.md
  - data/config.yaml
```

These files were automatically injected into Claude's context in Claude Code. On other surfaces, you need to:

1. **Bundle the files** - Include them in the ZIP
2. **Reference in body** - Add instructions to read them:

```markdown
---
name: github-helper
description: Helps with GitHub operations
---

# GitHub Helper

Before starting, read these reference files:
- `lib/patterns/github.md` - Common patterns
- `data/config.yaml` - Configuration

This skill helps you work with GitHub...
```

---

## Validation Failures

If validation fails after stripping, report to user:

| Problem | Suggestion |
|---------|------------|
| Name too long | "Name 'very-long-name...' exceeds 64 chars. Suggest: 'shorter-name'" |
| Invalid name chars | "Name has invalid characters. Suggest: 'valid-name'" |
| Contains "claude" | "Name cannot contain 'claude'. Suggest: 'cc-helper' or 'code-helper'" |
| Empty description | "Description is empty. Suggest using first paragraph of skill body" |

**Don't silently fix** - let the user decide how to rename.

---

## Claude's Role

As Claude, you perform this transformation by:

1. **Reading** the SKILL.md
2. **Mentally parsing** the frontmatter
3. **Identifying** fields to strip
4. **Checking** validation rules
5. **Writing** a new version with clean frontmatter

You don't need Python for this - you can understand and rewrite the YAML directly. Only use Python tools for the mechanical parts (creating ZIP, API calls).
