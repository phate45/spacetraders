---
name: creating-vault-documentation
description: Create research notes and planning documents in Mark's vault. Use when documenting research findings, technical decisions, or planning work that should persist beyond the session.
---

# Creating Vault Documentation

Create persistent documentation in Mark's vault for research, planning, and technical decisions.

## Vault Location

```
/home/phate/Documents/second-brain/01_Projects/spacetraders/
```

**This is NOT the project working directory.** The vault is Mark's personal knowledge base, separate from the git repository.

## When to Create Vault Documentation

- Research findings that inform future work
- Technical decision records (ADRs)
- Architecture explorations and design notes
- Planning documents
- Reference material discovered during implementation

**NOT for:**
- Project documentation (README, CONTRIBUTING, etc. go in working directory)
- Beads issue notes (use `bd update --notes`)

## File Format

```markdown
---
created: 2025-12-22T16:15:00
modified: 2025-12-22T16:15:00
---

# Document Title

[Content here]
```

**Frontmatter rules:**
- Only `created` and `modified` fields required
- Use actual timestamps from system reminder (UserPromptSubmit hook)
- NEVER use placeholder times like `00:00:00`
- Update `modified` when editing existing notes

## File Naming

Use descriptive, clear names:

```
Architecture Notes.md
API Design Decisions.md
SpaceTraders Rate Limiting Research.md
Fleet Management Strategy.md
```

## Linking

| Link Type | Syntax | Use When |
|-----------|--------|----------|
| WikiLinks | `[[Other Note]]` | Referencing other vault notes |
| Markdown links | `[text](path)` | Referencing project files |

## Creating a Document

```python
Write(
  file_path="/home/phate/Documents/second-brain/01_Projects/spacetraders/Note Name.md",
  content="""---
created: 2025-12-22T16:15:00
modified: 2025-12-22T16:15:00
---

# Note Name

[Content]
"""
)
```

## CRITICAL: Report and Persist

After creating vault documentation, **you MUST do both:**

### 1. Update Beads Notes (Persistence)

Add documentation to the task's notes field so it survives session boundaries:

```bash
bd update <task-id> --notes "COMPLETED: [other work]

VAULT_DOCS:
- Rate Limiting Research.md: API rate limits, backoff strategies
- [other docs created]

NEXT: [next steps]"
```

The `VAULT_DOCS` section ensures future sessions know what documentation exists.

### 2. Report to Control Tower (Immediate)

Include in your task summary when returning work:

```
Created vault documentation:
- Path: /home/phate/Documents/second-brain/01_Projects/spacetraders/Rate Limiting Research.md
- Contains: API rate limit analysis, backoff strategies, quota management patterns
- Relevance: Informs fleet automation design to avoid 429 errors
```

**Both are required.** Beads notes persist across sessions; the verbal report gives Control Tower immediate awareness. Unreported or untracked documentation becomes orphaned knowledge.

## Reference

For comprehensive vault integration guidelines, see [vault-integration.md](../../../vault-integration.md) in the project root.
