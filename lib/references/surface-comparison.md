# Reference: Skill Surface Comparison

## Three Surfaces

Claude has three distinct surfaces where skills can be installed:

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Skills                        │
│                    (source realm)                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Claude Code │   │ claude.ai   │   │ Messages    │
│ (filesystem)│   │ (ZIP upload)│   │ API         │
└─────────────┘   └─────────────┘   └─────────────┘
```

---

## Surface Overview

| Aspect | Claude Code | claude.ai | Messages API |
|--------|-------------|-----------|--------------|
| **Storage** | Local filesystem | Cloud (per-user) | Cloud (per-workspace) |
| **Sharing** | Personal/project | Individual only | Workspace-wide |
| **Installation** | Copy files or plugin | Upload ZIP | POST /v1/skills |
| **Updates** | Edit files directly | Re-upload ZIP | Create new version |
| **File Access** | Live (filesystem) | Bundled (ZIP) | Bundled (upload) |

---

## Feature Support Matrix

| Feature | Claude Code | claude.ai | Messages API |
|---------|:-----------:|:---------:|:------------:|
| Custom instructions | ✓ | ✓ | ✓ |
| Supporting files (data, scripts) | ✓ | ✓ | ✓ |
| Tool restrictions (`allowed-tools`) | ✓ | ✗ | ✗ |
| Hooks (pre/post tool use) | ✓ | ✗ | ✗ |
| Model selection (`model`) | ✓ | ✗ | ✗ |
| Subagent config (`agent`) | ✓ | ✗ | ✗ |
| Context injection (`context`) | ✓ | ✗ | ✗ |
| Slash command config | ✓ | ✗ | ✗ |
| Plugin root references | ✓ (live) | ✗ (must bundle) | ✗ (must bundle) |
| Version control | Via git | Manual | Built-in API |

---

## Key Differences

### File References

**Claude Code:**
```markdown
Read `${CLAUDE_PLUGIN_ROOT}/lib/patterns/something.md` for guidance.
```
The file is read live from the filesystem.

**claude.ai / Messages API:**
```markdown
Read `lib/patterns/something.md` for guidance.
```
The file must be bundled in the ZIP. References must be relative to skill folder.

### Tool Restrictions

**Claude Code:**
```yaml
---
name: safe-skill
allowed-tools: ["Read", "Glob"]
---
```
The skill can only use Read and Glob tools.

**claude.ai / Messages API:**
Tool restrictions are not supported. The skill has access to all tools the container allows.

### Model Selection

**Claude Code:**
```yaml
---
name: fast-skill
model: haiku
---
```
Forces the skill to use a specific model.

**claude.ai / Messages API:**
Model is determined by the request or user settings, not the skill.

---

## Migration Considerations

### What Works Unchanged

- **Instructions** - The main body of SKILL.md
- **Data files** - Static content like indexes, examples
- **Basic scripts** - Python/shell scripts called via bash

### What Needs Adaptation

| Feature | Adaptation Required |
|---------|---------------------|
| `${CLAUDE_PLUGIN_ROOT}` | Resolve and bundle files, rewrite paths |
| `allowed-tools` | Remove (won't work, document in skill) |
| `hooks` | Remove (no hook system) |
| `context` | Inline the context into SKILL.md body |
| Live file access | Bundle all needed files |

### What Cannot Be Migrated

| Feature | Reason |
|---------|--------|
| Subagents (`agent`) | API doesn't support subagent spawning |
| Real-time filesystem | Skills are static bundles |
| Hook-based automation | No event system |

---

## Best Practices for Cross-Surface Skills

1. **Keep skills self-contained** - Avoid external dependencies
2. **Use relative paths** - `data/index.md` instead of absolute paths
3. **Document limitations** - Note when features won't work on other surfaces
4. **Test on target** - Export and test on claude.ai before sharing
5. **Version separately** - A skill may need different versions for different surfaces
