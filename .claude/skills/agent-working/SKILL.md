---
name: agent-working
description: Core workflow for agents executing beads tasks. Invoke FIRST before starting any assigned work. Covers task reading, notes updates, TodoWrite integration, side quest handling.
---

# Agent Working

**MANDATORY**: Invoke this skill before starting any assigned task.

This skill provides the shared workflow pattern for all agents executing beads tasks.

## Core Workflow

### 1. Initialize Workspace

Use the Bash tool to run `begin-work`:

```bash
Bash(begin-work <task-id>)
```

This command:
- Fetches task info from beads
- Creates worktree + branch if new task, or detects existing for resume
- Sets task status to `in_progress`
- Outputs JSON with everything you need

**Output structure:**
```json
{
  "task": { "id", "title", "description", "design", "acceptance_criteria", "notes" },
  "workspace": { "worktree_path", "worktree_name", "branch_name" },
  "mode": "new" | "resume"
}
```

**If the script errors:** Stop and surface the issue to Control Tower. Do not proceed.

**CRITICAL — What NOT to do:**

`begin-work` is a symlinked shell command, NOT a Python script you invoke directly.

| ❌ WRONG | Why |
|----------|-----|
| `python scripts/begin-work.py` | Never call Python directly |
| `python /path/to/begin-work.py` | The symlink exists for a reason |
| `mcp__host-executor__execute_command` with begin-work | It's a shell command, not a heavy tool |
| Manual worktree creation | Results in wrong naming conventions. Every time. |

Seeing `scripts/begin-work.py` in the codebase does NOT mean you should call Python. The source file's presence is irrelevant. Use the shell command.

**If Bash permission is denied:** STOP. Report to Control Tower. Do NOT improvise workarounds.

### 2. Enter Worktree

```bash
cd <worktree_path> && pwd
```

Verify `pwd` shows `<repo>/worktrees/<id>` before proceeding. All work happens in this directory.

**Tool usage in worktree:**
- **Shell tools** (rg, git, etc.): Use relative paths from working directory
- **Heavy tools** (cargo, bun): Use `execute_command(..., worktree=<worktree_name>)`
- **bd**: Run directly, no `cd` prefix needed—bd finds `.beads/` root automatically

**MANDATORY for Read/Edit tools:** File paths MUST include the worktree path.

```
# ✅ Correct - includes worktree path
Read("/home/.../worktrees/935/README.md")
Edit("/home/.../worktrees/935/src/main.rs", ...)

# ❌ WRONG - points to main repo, NOT the worktree
Read("/home/.../spacetraders/README.md")
Edit("/home/.../spacetraders/src/main.rs", ...)
```

After `cd <worktree>`, your shell working directory changes but Read/Edit still need full paths. Use the `worktree_path` from `begin-work` output.

### 3. Read Task Context

From the `begin-work` output:

1. **Notes field** - Session handoff context (start here if populated)
2. **Acceptance criteria** - Definition of done (your checklist)
3. **Design field** - Implementation approach
4. **Description** - Problem statement

**Reading large reference documents:**

When the task references documentation, use headings to target reads:

```bash
rg "^#+" <path-to-document> -n  # Get headings with line numbers
```

Then use Read tool with `offset` parameter to load only relevant sections, saving context.

### 4. Execute Work

Work systematically. **Update notes at milestones:**

```bash
bd update <task-id> --notes "COMPLETED: [specific deliverables]

IN_PROGRESS: [current state]

NEXT: [concrete next step]

BLOCKERS: [if any]" --json
```

**Update notes when:**
- Completing significant work chunks
- Before decisions that change direction
- When hitting blockers
- Discovering side quests

### 5. Update Acceptance Criteria

Mark criteria as complete when verified:

```bash
bd update <task-id> --acceptance "- [x] First criterion (done)
- [x] Second criterion (done)
- [ ] Third criterion (pending)" --json
```

Update acceptance criteria as you complete each item, not just at the end.

### 6. Submit for Review

When work is complete:

```bash
bd update <task-id> --status review --json
```

**Do NOT use `bd close`.** Closing happens after Control Tower review and merge.

Commit your work before submitting:

```bash
git add -A && git commit -m "<type>(<id>): <summary>"
```

Example: `git commit -m "task(q4x): implement begin-work script"`

### 7. Report to Control Tower

Your response must include:
1. **Deliverables** - What was created/modified
2. **Vault docs** - File paths if documentation created
3. **Follow-up work** - Discovered issues or next steps
4. **Blockers** - Anything preventing completion

## TodoWrite Integration

**Pattern: bd strategic, TodoWrite tactical**

```
bd issue: Strategic objective (multi-session)
  │
  └─ TodoWrite: Tactical execution (this session)
     - [ ] Step from acceptance criteria
     - [ ] Another step
     - [ ] Final verification
```

**Workflow:**
1. Read bd issue, note acceptance criteria
2. Create TodoWrite from acceptance criteria items
3. Execute via TodoWrite (visible progress)
4. Update bd notes at milestones
5. Close bd issue when TodoWrite complete

For detailed integration patterns, see [BOUNDARIES.md](../beads/references/BOUNDARIES.md#integration-patterns).

## Side Quest Handling

**Triggers** - You've discovered a side quest when:
- Implementation reveals unexpected dependency
- Bug found unrelated to current task
- Architectural issue surfaces
- Refactoring opportunity identified

**When you hit a trigger:** Invoke `/discovering-issues` for the complete capture protocol.

The skill covers:
- Two-step capture pattern (create → mark draft)
- Blocker vs deferrable assessment
- Parent task notes update
- Escalation rules

## Notes Format Reference

```
COMPLETED: Specific deliverables (what was built/done)
IN_PROGRESS: Current state + what's partially done
NEXT: Immediate next step (concrete, not vague)
BLOCKERS: What's preventing progress
KEY_DECISIONS: Important context or user guidance
VAULT_DOCS: Documentation created (file paths)
```

**Quality tests:**
- **Future-me test**: Could I resume in 2 weeks with zero conversation history?
- **Stranger test**: Could another developer understand without asking me?

## Field Reference

| Field | Purpose | Contains |
|-------|---------|----------|
| description | Problem statement | WHY and WHAT (immutable) |
| design | Implementation approach | HOW to build it (can evolve) |
| acceptance-criteria | Definition of done | WHAT success looks like (stable) |
| notes | Session handoff | Current state (update frequently) |

**Critical distinction**: Design = HOW (implementation details). Acceptance criteria = WHAT (verifiable outcomes).

For field usage details, see [ISSUE_CREATION.md](../beads/references/ISSUE_CREATION.md#design-vs-acceptance).

## Escalation Triggers

Surface to Control Tower immediately:
- Architectural decisions affecting project structure
- Multiple valid approaches requiring user choice
- Blockers requiring Mark's input
- Scope creep beyond original task
- Side quests that are blockers

## Quick Checklists

**Starting work:**
```
- [ ] begin-work <task-id>
- [ ] cd <worktree_path> && pwd (verify location)
- [ ] Read notes field first
- [ ] Review acceptance criteria
- [ ] Create TodoWrite from criteria
- [ ] Begin work
```

**During work:**
```
- [ ] Update notes at milestones
- [ ] Mark acceptance criteria [x] as completed
- [ ] Handle side quests via /discovering-issues
- [ ] Escalate blockers immediately (don't switch tasks)
- [ ] Commit at appropriate granularity
```

**Completing work:**
```
- [ ] Final notes update
- [ ] All acceptance criteria marked [x]
- [ ] git add -A && git commit -m "..."
- [ ] bd update <task-id> --status review --json
- [ ] Report deliverables to Control Tower
```

For comprehensive checklists, see [WORKFLOWS.md](../beads/references/WORKFLOWS.md#checklist-templates).

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Skip `begin-work` and call `bd show` directly | Always run `begin-work <task-id>` first |
| Work outside the worktree | Verify `pwd` shows worktrees path before starting |
| Read/Edit main repo paths (`/repo/file.rs`) | Use worktree paths (`/repo/worktrees/<id>/file.rs`) |
| Use `bd close` to finish | Use `bd update --status review` |
| Update notes only at end | Update at milestones |
| Write vague notes ("made progress") | Write specific notes ("Implemented X, Y remains") |
| Ignore side quests | Invoke /discovering-issues |
| Switch to blocker task yourself | Document blocker, surface to Control Tower |
| Leave acceptance criteria unchecked | Mark `[x]` as each criterion is met |
| Guess at architectural decisions | Escalate to Control Tower |
| Continue after `begin-work` errors | Stop and surface issue to Control Tower |
