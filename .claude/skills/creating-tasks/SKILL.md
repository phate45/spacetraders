---
name: creating-tasks
description: Create well-documented beads tasks with proper descriptions and flags. Use when creating new bd issues, tasks, bugs, or features.
---

# Creating Tasks

Create beads issues with complete context so future work sessions understand scope and intent.

## Command Pattern

```bash
bd create "Title" \
  -t task|bug|feature \
  -p 0-4 \
  -d "Description" \
  --json
```

**Always use `--json`** for structured output.

## Writing Good Descriptions

Issues without descriptions lack context for future work. Always include:

- **Why** - Problem statement or motivation
- **What** - Scope of work
- **How discovered** - Context if applicable

### Good Example

```bash
bd create "Fix auth bug in login handler" \
  -t bug \
  -p 1 \
  -d "Login fails with 500 error when password contains special characters. Found while testing auth flow." \
  --json
```

### Bad Example

```bash
bd create "Fix auth bug" -t bug -p 1 --json  # What bug? Where? Why?
```

## Priority Scale

| Priority | Meaning | Use When |
|----------|---------|----------|
| 0 | Critical | Security vulnerabilities, data loss risks |
| 1 | High | Major features, important bugs |
| 2 | Medium | Default for most work |
| 3 | Low | Polish, nice-to-haves |
| 4 | Backlog | Future consideration |

## Adding Dependencies

When creating tasks that depend on other work:

```bash
bd create "Write tests for auth" -t task -p 2 -d "..." --json
bd dep add <new-id> <blocking-id>
```

**Dependency direction trap**: See [dependency-direction.md](../shared/dependency-direction.md) for the common cognitive error when adding dependencies.

## Type Selection

| Type | Use When |
|------|----------|
| `task` | General work items, implementation |
| `bug` | Something is broken |
| `feature` | New capability |

## Verification

After creating:

```bash
bd show <id>  # Verify description and metadata
```
