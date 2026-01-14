# Reference: Claude Code-Only Fields

These YAML frontmatter fields are specific to Claude Code and must be stripped when exporting to other surfaces.

---

## Fields to Strip

| Field | Type | Claude Code Purpose |
|-------|------|---------------------|
| `allowed-tools` | array | Restrict which tools the skill can use |
| `hooks` | object | Event-driven automation (pre/post tool use) |
| `context` | array | Inject additional files into context |
| `agent` | object | Subagent configuration |
| `model` | string | Force specific model (haiku, sonnet, opus) |
| `user-invocable` | boolean | Enable as slash command |
| `disable-model-invocation` | boolean | Prevent automatic invocation |

---

## Detailed Explanations

### allowed-tools

**Purpose:** Restricts which tools the skill is allowed to use.

```yaml
allowed-tools: ["Read", "Glob", "Grep"]
```

**Why strip:** The API doesn't support tool restrictions. Skills run with whatever tools the container allows.

**Impact:** Skills that rely on tool restrictions for safety may behave differently.

---

### hooks

**Purpose:** Event-driven automation triggered before/after tool use.

```yaml
hooks:
  PreToolUse:
    - matcher: Bash
      script: validate_command.sh
```

**Why strip:** The API has no hook system.

**Impact:** Validation and automation hooks won't run.

---

### context

**Purpose:** Inject additional files into Claude's context when skill is active.

```yaml
context:
  - lib/patterns/common.md
  - data/reference.yaml
```

**Why strip:** The API handles context differently.

**Adaptation:** Bundle these files and reference them in the skill body instead.

---

### agent

**Purpose:** Configure subagent spawning for the skill.

```yaml
agent:
  model: haiku
  tools: ["Read", "Write"]
```

**Why strip:** The API doesn't support subagent spawning from skills.

**Impact:** Skills that spawn subagents won't work as designed.

---

### model

**Purpose:** Force the skill to use a specific Claude model.

```yaml
model: haiku
```

**Why strip:** Model selection is controlled at the API request level, not by skills.

**Impact:** Users control which model processes the skill.

---

### user-invocable

**Purpose:** Enable the skill as a slash command (`/skill-name`).

```yaml
user-invocable: true
```

**Why strip:** Slash commands are a Claude Code feature.

**Impact:** None - this is just metadata for Claude Code.

---

### disable-model-invocation

**Purpose:** Prevent Claude from automatically invoking the skill.

```yaml
disable-model-invocation: true
```

**Why strip:** The API doesn't auto-invoke skills.

**Impact:** None - this is a Claude Code behavior control.

---

## Fields to Keep

| Field | Purpose | Required |
|-------|---------|----------|
| `name` | Skill identifier | Yes |
| `description` | What the skill does | Yes |
| `version` | Version number | No (optional) |

---

## Example Transformation

**Before (Claude Code):**
```yaml
---
name: github-helper
description: Helps with GitHub operations
version: 1.0.0
allowed-tools: ["Bash", "Read"]
model: haiku
hooks:
  PreToolUse:
    - matcher: Bash
      script: validate.sh
context:
  - lib/patterns/github.md
user-invocable: true
---
```

**After (API/claude.ai):**
```yaml
---
name: github-helper
description: Helps with GitHub operations
version: 1.0.0
---
```

The stripped fields are removed. Any context files should be bundled and referenced in the skill body.
