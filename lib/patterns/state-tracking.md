# Pattern: State Tracking

## Purpose

Track skills uploaded to the Anthropic Skills API for updates and deletion.

## When to Use

- After uploading a skill to the API
- Before uploading to check if skill already exists
- When listing uploaded skills
- When deleting a skill

---

## State File

**Location:** `~/.claude/hiivmind-arcana.state.yaml`

**Schema:**
```yaml
version: "1.0"
uploads:
  skill-name:
    skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
    version: 1
    last_sync: "2026-01-14T10:30:00Z"
    source_path: /path/to/original/skill
```

---

## Operations

### Check if Skill Exists

Before uploading, check if the skill has been uploaded before:

```bash
python3 {PLUGIN_ROOT}/lib/tools/state.py get my-skill
```

**Output if exists:**
```yaml
my-skill:
  skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
  version: 2
  last_sync: "2026-01-14T10:30:00Z"
  source_path: /home/user/plugins/my-plugin/skills/my-skill
```

**Output if not exists:**
```
Not found: my-skill
(exit code 1)
```

### Record Upload

After successful upload, record the mapping:

```bash
python3 {PLUGIN_ROOT}/lib/tools/state.py set my-skill \
  --skill-id skill_01AbCdEfGhIjKlMnOpQrStUv \
  --source-path /path/to/skill
```

This will:
- Create entry if new
- Increment version if existing
- Update last_sync timestamp

### List All Uploads

Show all skills that have been uploaded:

```bash
python3 {PLUGIN_ROOT}/lib/tools/state.py list
```

**Output:**
```yaml
my-skill:
  skill_id: skill_01AbCdEfGhIjKlMnOpQrStUv
  version: 2
  last_sync: "2026-01-14T10:30:00Z"
  source_path: /home/user/plugins/my-plugin/skills/my-skill
other-skill:
  skill_id: skill_01XyZaBcDeFgHiJkLmNoPq
  version: 1
  last_sync: "2026-01-13T15:45:00Z"
  source_path: /home/user/plugins/other-plugin/skills/other-skill
```

### Delete Record

Remove a skill from tracking (after deleting from API):

```bash
python3 {PLUGIN_ROOT}/lib/tools/state.py delete my-skill
```

---

## Upload Flow with State

### New Skill

```
1. Check state: get my-skill
   → Not found

2. Upload to API: POST /v1/skills
   → Returns skill_id

3. Record in state: set my-skill --skill-id XXX
```

### Existing Skill (Update)

```
1. Check state: get my-skill
   → Found: skill_id = skill_01AbCd...

2. Create new version: POST /v1/skills/{skill_id}/versions
   → Returns new version number

3. Update state: set my-skill --skill-id XXX
   → Increments version, updates timestamp
```

---

## Workflow Integration

### In arcana-upload-api skill:

```markdown
## Step 1: Check Existing

Before uploading, check if this skill has been uploaded before:

\`\`\`bash
python3 {PLUGIN_ROOT}/lib/tools/state.py get $SKILL_NAME
\`\`\`

If found:
- Inform user: "Skill already uploaded (v2). Creating new version..."
- Use the stored skill_id for version creation

If not found:
- Inform user: "New skill. Creating..."
- Will get skill_id from create response

## Step 2: Upload

[... upload logic ...]

## Step 3: Record

After successful upload:

\`\`\`bash
python3 {PLUGIN_ROOT}/lib/tools/state.py set $SKILL_NAME \
  --skill-id $SKILL_ID \
  --source-path $SKILL_PATH
\`\`\`
```

---

## State File Management

### File Not Found

If state file doesn't exist:
- `get` returns "Not found" for any skill
- `set` creates the file
- `list` returns empty output
- `delete` returns "Not found"

### Corrupted File

If state file is corrupted:
- Backup the file
- Create fresh state
- Warn user about lost mappings

### Multiple Machines

State is local - if you use the API from multiple machines:
- Each machine has its own state
- Skill may show as "new" on machine B even if uploaded from A
- Consider: Could extend to query API for existing skills

---

## Example Session

```
$ python3 lib/tools/state.py list
(empty - no uploads yet)

$ # Upload a skill...
$ python3 lib/tools/state.py set my-skill \
    --skill-id skill_01AbCdEfGh \
    --source-path /home/user/skills/my-skill
Saved: my-skill → skill_01AbCdEfGh

$ python3 lib/tools/state.py get my-skill
my-skill:
  skill_id: skill_01AbCdEfGh
  version: 1
  last_sync: "2026-01-14T10:30:00Z"
  source_path: /home/user/skills/my-skill

$ # Update the skill...
$ python3 lib/tools/state.py set my-skill \
    --skill-id skill_01AbCdEfGh \
    --source-path /home/user/skills/my-skill
Saved: my-skill → skill_01AbCdEfGh

$ python3 lib/tools/state.py get my-skill
my-skill:
  skill_id: skill_01AbCdEfGh
  version: 2  # Incremented!
  last_sync: "2026-01-14T11:00:00Z"
  source_path: /home/user/skills/my-skill
```
