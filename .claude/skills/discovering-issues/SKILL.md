---
name: discovering-issues
description: Log work discovered while working on other tasks. Use when finding bugs, TODOs, or follow-up work during implementation.
---

# Discovering Issues (Side Quest Protocol)

**Invoke this skill when you've identified a side quest during task execution.**

Side quests are work discovered while doing other work. This skill covers the complete capture protocol.

## Quick Capture Pattern

```bash
# 1. Create the issue
bd create --title "Discovered issue title" \
  -t task|bug|feature \
  -p 0-4 \
  -d "Description with discovery context" \
  --deps discovered-from:<current-task-id> \
  --json

# 2. Mark as draft (needs refinement)
bd update <new-id> --status draft --json
```

**Why two steps:** `bd create` doesn't accept `--status`. Draft status signals "captured but not refined"—these issues won't appear in `bd ready` until promoted to `open`.

## Why `discovered-from` Matters

The `discovered-from` dependency:

1. **Inherits `source_repo`** - Automatically links to same repository context
2. **Creates audit trail** - Shows how work was discovered
3. **Prevents orphaned tasks** - Maintains relationship to parent work
4. **Aids prioritization** - Related work stays grouped

## Blocker vs Deferrable

After capturing, assess immediately:

| Type | Signal | Action |
|------|--------|--------|
| **Deferrable** | Doesn't block current work | Continue current task, side quest queued |
| **Blocker** | Current task cannot complete without this | Stop. Document blocker. Surface to Control Tower. |

**Critical:** If it's a blocker, do NOT switch tasks yourself. Document and escalate. Control Tower assigns work.

### Blocker signals:
- Security vulnerability in code you're touching
- Data loss risk if you proceed
- Architectural issue that invalidates your approach
- Missing dependency that prevents completion

### Deferrable signals:
- Nice-to-have improvement spotted
- Unrelated bug in nearby code
- Refactoring opportunity
- Documentation gap

## Description Requirements

Discovered issues should include:

- **What** - The problem or work needed
- **Why it matters** - Impact or urgency
- **Discovery context** - What you were doing when you found it

**Example:**
```bash
bd create --title "Auth tokens not validated for expiry" \
  -t bug \
  -p 1 \
  -d "Token validation accepts expired tokens. Security issue. Found while implementing user authentication (spacetraders-abc)." \
  --deps discovered-from:spacetraders-abc \
  --json
```

## Update Parent Task Notes

After creating the side quest, update your current task's notes:

```bash
bd update <current-task-id> --notes "IN_PROGRESS: [current work]

DISCOVERED:
- [Brief description] (tracked: <new-issue-id>, status: draft|blocker)

NEXT: [what you're doing next]" --json
```

This creates a breadcrumb trail. When Control Tower reviews your work summary, they'll see what was discovered.

## Dependencies Reference

| Flag | Meaning | Use When |
|------|---------|----------|
| `--deps discovered-from:<id>` | Found while working on parent | Logging incidental discoveries |
| `--deps blocks:<id>` | This issue blocks another | Creating prerequisite work |
| `bd dep add <id> <blocks>` | Add dependency after creation | Linking existing issues |

**Dependency direction trap**: See [dependency-direction.md](../shared/dependency-direction.md) for the common cognitive error.

## Draft Lifecycle

```
Agent discovers → Creates issue → Marks draft
                                      ↓
Control Tower reviews → Refines (adds design, acceptance-criteria)
                                      ↓
                        Promotes to open → Appears in bd ready
```

Draft issues are intentionally minimal. Refinement happens later with Control Tower, not during task execution.

## Complete Example

Working on `spacetraders-abc`. Discover token expiry bug.

```bash
# 1. Capture
bd create --title "Auth tokens not validated for expiry" \
  -t bug -p 1 \
  -d "Token validation accepts expired tokens. Security risk. Found during auth implementation." \
  --deps discovered-from:spacetraders-abc \
  --json
# Returns: spacetraders-xyz

# 2. Mark draft
bd update spacetraders-xyz --status draft --json

# 3. Update parent notes
bd update spacetraders-abc --notes "IN_PROGRESS: Auth flow implementation

DISCOVERED:
- Token expiry not validated (tracked: spacetraders-xyz, draft)

NEXT: Continue auth flow, expiry bug is captured" --json

# 4. Assess: Is this a blocker?
# - Security issue, but current auth work can complete
# - Expiry validation is separate concern
# → Deferrable. Continue current work.
```

## Verification

After creating:

```bash
bd show <new-id> --json   # Verify discovered-from link, draft status
bd show <parent-id> --json # Verify parent notes updated
```

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Create issue and forget to mark draft | Always: create → update --status draft |
| Skip `discovered-from` | Always link to parent task |
| Switch to blocker task yourself | Document blocker, surface to Control Tower |
| Write minimal "fix bug" descriptions | Include what, why, discovery context |
| Forget to update parent notes | Document discovery in current task |
