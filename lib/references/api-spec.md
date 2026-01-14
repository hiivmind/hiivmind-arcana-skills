# Reference: Anthropic Skills API

## Base URL

```
https://api.anthropic.com/v1/skills
```

## Authentication

All requests require:

```http
x-api-key: $ANTHROPIC_API_KEY
anthropic-version: 2023-06-01
```

## Beta Headers

The Skills API is in beta. Include:

```http
anthropic-beta: skills-2025-10-02,code-execution-2025-08-25
```

---

## Endpoints

### Create Skill

```http
POST /v1/skills
Content-Type: multipart/form-data
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | ZIP file containing skill |
| `title` | string | Yes | Display name for the skill |

**Response:**
```json
{
  "id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
  "title": "My Skill",
  "version": 1,
  "created_at": "2026-01-14T10:30:00Z"
}
```

---

### Create New Version

```http
POST /v1/skills/{skill_id}/versions
Content-Type: multipart/form-data
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | ZIP file containing updated skill |

**Response:**
```json
{
  "id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
  "version": 2,
  "created_at": "2026-01-14T11:00:00Z"
}
```

---

### List Skills

```http
GET /v1/skills
```

**Response:**
```json
{
  "data": [
    {
      "id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
      "title": "My Skill",
      "version": 2,
      "created_at": "2026-01-14T10:30:00Z"
    }
  ]
}
```

---

### Delete Skill

```http
DELETE /v1/skills/{skill_id}
```

**Response:** 204 No Content

---

## ZIP Structure

The ZIP file must have this structure:

```
skill-name/
├── SKILL.md          # Required
├── scripts/          # Optional
│   └── helper.py
├── data/             # Optional
│   └── index.md
└── examples/         # Optional
    └── example.md
```

**Critical Requirements:**

1. **Folder name must match `name` in frontmatter**
   - If SKILL.md has `name: my-skill`, the folder must be `my-skill/`

2. **SKILL.md must be at root of skill folder**
   - `my-skill/SKILL.md` ✓
   - `my-skill/docs/SKILL.md` ✗

3. **All paths are relative to skill folder**
   - References like `scripts/helper.py` resolve to `my-skill/scripts/helper.py`

---

## Using Skills via Messages API

Once uploaded, use skills in API requests:

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 1024,
  "container": {
    "skills": [
      {
        "type": "custom",
        "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
        "version": "latest"
      }
    ]
  },
  "messages": [
    {"role": "user", "content": "Use my skill to..."}
  ]
}
```

**Version options:**
- `"latest"` - Always use most recent version
- `1`, `2`, etc. - Pin to specific version

---

## Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 400 | Invalid request | Check ZIP structure, name validation |
| 401 | Unauthorized | Check API key |
| 404 | Skill not found | Verify skill_id |
| 413 | ZIP too large | Reduce file size |
| 422 | Validation error | Check name/description constraints |
| 429 | Rate limited | Retry with backoff |

---

## Rate Limits

- **Create/Update:** 10 requests per minute
- **List/Delete:** 60 requests per minute

Use exponential backoff on 429 responses.
