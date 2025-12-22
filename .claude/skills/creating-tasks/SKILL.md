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

## Field Semantics

The three core fields serve distinct purposes:

| Field | Contains | Characteristic |
|-------|----------|----------------|
| `description` | WHY and WHAT — the problem statement | Immutable once set |
| `design` | HOW — implementation approach | Can evolve during work |
| `acceptance-criteria` | WHAT SUCCESS LOOKS LIKE — verifiable outcomes | Should remain stable |

**The critical distinction:** Design describes your approach (which may change). Acceptance criteria describe the outcomes that must be true regardless of approach.

For the full explanation with examples, see [Design vs Acceptance Criteria](../beads/references/ISSUE_CREATION.md#design-vs-acceptance).

## Interactive Task Creation

When creating tasks collaboratively with Mark, task creation is **not complete** until all three fields are populated:

- [ ] `description` — Problem statement captured
- [ ] `design` — Implementation approach defined
- [ ] `acceptance-criteria` — Success criteria specified

Don't finalize a task with empty design or acceptance-criteria fields. If the approach isn't clear yet, that's a signal the task needs more discussion before creation.

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

## Notes Field for Complex Issues

For issues that may span sessions or require detailed context, use the notes field:

```bash
bd update <id> --notes "IMPLEMENTATION GUIDE

APPROACH:
[Chosen approach and why]

KEY_DECISIONS:
[User input, architectural choices]

NEXT:
[Concrete next step for resumption]"
```

The notes field persists across sessions and survives context compaction. Write notes as if explaining to a future agent with zero conversation history.

**When to use notes:**
- Multi-session work
- Complex technical implementation
- Research findings that inform approach
- User decisions that affect design

For comprehensive notes patterns and resumability guidelines, see the [beads skill](../beads/SKILL.md).

## Verification

After creating:

```bash
bd show <id>  # Verify description and metadata
```
