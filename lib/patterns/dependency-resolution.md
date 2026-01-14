# Pattern: Dependency Resolution

## Purpose

Identify files referenced by a skill that should be bundled for export.

## When to Use

During skill analysis, when you need to trace file references and build a complete manifest.

---

## Reference Styles

### 1. Plugin Root References

The most common pattern for shared resources:

```markdown
Read `${CLAUDE_PLUGIN_ROOT}/lib/patterns/something.md` for guidance.
```

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/helper.py" --arg value
```

**Resolution:**
1. Find `plugin.json` by searching upward from skill directory
2. The directory containing `plugin.json` is the plugin root
3. Resolve the path relative to plugin root

### 2. Curly Brace Convention

Some skills use `{PLUGIN_ROOT}` (without `$`):

```markdown
See `{PLUGIN_ROOT}/lib/references/api-spec.md` for details.
```

**Resolution:** Same as above - find plugin.json, resolve from there.

### 3. Relative Paths

Paths relative to the skill directory:

```markdown
The index is at `data/index.md`.
Check `../lib/common.md` for shared patterns.
```

**Resolution:** Resolve from the skill's directory.

### 4. Inline Code References

File references in inline code:

```markdown
Read the `data/index.md` file for the complete index.
Run `scripts/build.py` to rebuild the cache.
```

**Resolution:** Context-dependent - are these real files?

### 5. Bash Commands

Scripts and files in bash code blocks:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sync.py" discover "$PATH"
cat data/config.yaml
```

**Resolution:** Extract file paths from commands.

---

## Resolution Strategy

### Step 1: Find Plugin Root

```bash
# Search upward for plugin.json
find_plugin_root() {
    dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/.claude-plugin/plugin.json" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}
```

### Step 2: Resolve Each Reference

| Reference Pattern | Resolution |
|-------------------|------------|
| `${CLAUDE_PLUGIN_ROOT}/path` | `$PLUGIN_ROOT/path` |
| `{PLUGIN_ROOT}/path` | `$PLUGIN_ROOT/path` |
| `./path` or `path` | `$SKILL_DIR/path` |
| `../path` | `$SKILL_DIR/../path` (canonicalize) |

### Step 3: Verify Files Exist

For each resolved path:
1. Check if the file exists
2. If not, it might be:
   - A typo in the skill
   - A file that should exist but doesn't
   - Not actually a file reference (false positive)

### Step 4: Rewrite Paths for ZIP

When bundling, paths become relative to the skill folder in the ZIP:

| Original | ZIP Path |
|----------|----------|
| `/plugin/lib/patterns/x.md` | `lib/patterns/x.md` |
| `/plugin/skills/my-skill/data/y.md` | `data/y.md` |
| `/plugin/scripts/helper.py` | `scripts/helper.py` |

---

## Claude's Advantage

Unlike regex, you understand **semantic context**:

### Real File References

```markdown
# These ARE files to bundle:
Read `lib/patterns/common.md` for the pattern.
Run `python3 scripts/helper.py` to process.
The index is stored in `data/index.md`.
```

### NOT File References

```markdown
# These are NOT files to bundle:
Output will be saved to `output.json`.          # Generated file
Similar to how `git status` works.              # Command example
The API returns a `skill_id` field.             # JSON field name
Create a file called `config.yaml`.             # Instruction to create
```

### Context Clues

| Verb/Context | Likely File Reference? |
|--------------|------------------------|
| "Read X" | Yes - input file |
| "See X for details" | Yes - reference doc |
| "Run X" | Yes - script |
| "Output to X" | No - generated |
| "Create X" | No - instruction |
| "Like X" | No - comparison |
| "Returns X" | No - value/field |

---

## Edge Cases

### Files That Don't Exist

If a referenced file doesn't exist:
1. Check for typos (common: wrong extension, wrong case)
2. It might be optional ("if X exists, read it")
3. It might be documentation for a file the user creates
4. Report as warning, don't fail

### Circular References

If skill A references skill B which references skill A:
- Track what you've already processed
- Don't recurse infinitely
- Bundle each file only once

### Large Files

If a referenced file is very large:
- Warn the user
- Consider if it's truly needed
- ZIP size limits apply

---

## Output Format

After resolution, report the mapping:

```
Resolved dependencies:

From SKILL.md:
  ${CLAUDE_PLUGIN_ROOT}/lib/patterns/common.md
    → /full/path/lib/patterns/common.md
    → (ZIP) lib/patterns/common.md

  data/index.md
    → /full/path/skills/my-skill/data/index.md
    → (ZIP) data/index.md

  scripts/helper.py
    → /full/path/scripts/helper.py
    → (ZIP) scripts/helper.py
```
