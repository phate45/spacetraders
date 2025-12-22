---
name: discovering-issues
description: Log work discovered while working on other tasks. Use when finding bugs, TODOs, or follow-up work during implementation.
---

# Discovering Issues

When working on a task, you often discover additional work that needs tracking. Use `discovered-from` to maintain context and audit trail.

## Command Pattern

```bash
bd create "Discovered issue title" \
  -t task|bug|feature \
  -p 0-4 \
  -d "Description including discovery context" \
  --deps discovered-from:<parent-id> \
  --json
```

## Why `discovered-from` Matters

The `discovered-from` dependency:

1. **Inherits `source_repo`** - Automatically links to same repository context
2. **Creates audit trail** - Shows how work was discovered
3. **Prevents orphaned tasks** - Maintains relationship to parent work
4. **Aids prioritization** - Related work stays grouped

## Example

While implementing `spacetraders-abc` (user authentication), you discover the token validation doesn't check expiry:

```bash
bd create "Auth tokens not validated for expiry" \
  -t bug \
  -p 1 \
  -d "Token validation accepts expired tokens. Security issue. Found while implementing user authentication (spacetraders-abc)." \
  --deps discovered-from:spacetraders-abc \
  --json
```

## Description Requirements

Discovered issues should include:

- **What** - The problem or work needed
- **Why it matters** - Impact or urgency
- **Discovery context** - What you were doing when you found it

## Dependencies vs Discovery

| Flag | Meaning | Use When |
|------|---------|----------|
| `--deps discovered-from:<id>` | Found while working on parent | Logging incidental discoveries |
| `--deps blocks:<id>` | This issue blocks another | Creating prerequisite work |
| `bd dep add <id> <blocks>` | Add dependency after creation | Linking existing issues |

**Dependency direction trap**: See [dependency-direction.md](../shared/dependency-direction.md) for the common cognitive error when adding dependencies.

## Verification

After creating:

```bash
bd show <new-id>  # Verify discovered-from link appears
bd show <parent-id>  # Verify parent shows the discovery
```

## Workflow Context

When you discover issues during work, capture the workflow context that would help future sessions understand:

1. **Don't just log the issue** - Include the reasoning and context
2. **Update parent issue notes** - If the discovery affects the parent work, document it

```bash
# Update parent issue notes with discovery context
bd update <parent-id> --notes "IN_PROGRESS: Auth implementation

DISCOVERED:
- Token validation missing expiry check (tracked: spacetraders-xyz)
- Will need follow-up after auth flow complete

NEXT: Continue auth flow, expiry bug tracked separately"
```

The notes field survives context compaction and session boundaries. Write as if explaining to a future agent with zero conversation history.

For comprehensive workflow patterns, see the [beads skill](../beads/SKILL.md).
