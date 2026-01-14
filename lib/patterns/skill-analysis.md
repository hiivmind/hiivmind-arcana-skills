# Pattern: Skill Analysis

## Purpose

Understand what a skill does and what files it needs to function.

## When to Use

Before any export or upload operation. This is the first step in preparing a skill for another surface.

---

## Steps

### 1. Read the SKILL.md

Read the entire SKILL.md file. As you read, understand:

- **What does this skill do?** - The core purpose and functionality
- **What commands/scripts does it reference?** - Python scripts, bash commands, etc.
- **What data files does it depend on?** - Indexes, configurations, examples
- **What external resources does it need?** - APIs, databases, other services

Pay attention to:
- Code blocks with file paths
- Inline code references like `` `data/index.md` ``
- Bash commands that reference scripts
- Instructions that say "read X" or "see Y for details"

### 2. Explore the Skill Directory

Use Glob to find files in the skill's immediate directory:

```
skills/skill-name/
├── SKILL.md         # Always present
├── examples/        # Example files
│   └── *.md
├── data/            # Data files
│   └── *.yaml
└── scripts/         # Local scripts
    └── *.py
```

List what exists and note what appears relevant based on SKILL.md content.

### 3. Explore the Plugin Root

If the SKILL.md references `{PLUGIN_ROOT}` or `${CLAUDE_PLUGIN_ROOT}`:

1. Navigate up from the skill to find `plugin.json`
2. The directory containing `plugin.json` is the plugin root
3. Explore directories referenced in SKILL.md:
   - `lib/` - Patterns and references
   - `scripts/` - Shared Python scripts
   - `data/` - Shared data files

### 4. Build File Manifest

Create a list of files the skill needs:

**Always include:**
- `SKILL.md` (will be transformed)

**Include if referenced:**
- Scripts called in bash commands
- Data files mentioned in instructions
- Pattern/reference files the skill reads
- Example files in the skill's examples/ folder

**Include if in skill directory:**
- Any markdown files
- Any data files (.yaml, .json)
- Any scripts

### 5. Exclude Patterns

**Never include:**
- `.git/` - Version control
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python
- `.source/`, `.cache/` - Build artifacts
- `.local.md` - Local configuration
- `*.tmp`, `*.bak` - Temporary files
- `.DS_Store`, `Thumbs.db` - OS files

---

## Output

Return the file manifest as a list with:
- Absolute paths to each file
- Relative paths for the ZIP structure (from skill directory)

Example:
```
Files to bundle:
1. /path/to/skill/SKILL.md → SKILL.md
2. /path/to/skill/data/index.md → data/index.md
3. /path/to/plugin/lib/patterns/common.md → lib/patterns/common.md
```

---

## Example Analysis

**Skill:** `hiivmind-corpus-atproto`

**Reading SKILL.md, I see:**
- References `data/index.md` for the documentation index
- Calls scripts via `${CLAUDE_PLUGIN_ROOT}/scripts/`
- Mentions `references/` folder for additional docs

**Exploring skill directory:**
- `SKILL.md` - Main skill file
- `data/index.md` - Documentation index
- `references/*.md` - Reference documents

**File manifest:**
```
1. SKILL.md
2. data/index.md
3. references/overview.md
4. references/api.md
```

---

## Claude's Advantage

Unlike regex pattern matching, you can understand **context**:

| Reference | Is it a file to bundle? |
|-----------|------------------------|
| `"See config-parsing.md for details"` | Yes - reference to read |
| `"Output will be in output.json"` | No - generated file |
| `"Similar to git status"` | No - command example |
| `"Run python3 scripts/build.py"` | Yes - script to bundle |
| `"The API returns a skill_id"` | No - just documentation |

Use your judgment based on the instruction's intent.
