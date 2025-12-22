---
name: agent-working
description: Core workflow for agents executing beads tasks. Invoke FIRST before starting any assigned work. Covers task reading, notes updates, TodoWrite integration, side quest handling.
---

# Agent Working

**MANDATORY**: Invoke this skill before starting any assigned task.

This skill provides the shared workflow pattern for all agents executing beads tasks.

## Core Workflow

### 1. Receive Task ID

You receive a **beads task ID**, not a description. The task ID is your source of truth.

### 2. Read Task Context

```bash
bd show <task-id> --json
```

**Read in this order:**
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

### 3. Execute Work

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

### 4. Update Acceptance Criteria

Mark criteria as complete when verified:

```bash
bd update <task-id> --acceptance "- [x] First criterion (done)
- [x] Second criterion (done)
- [ ] Third criterion (pending)" --json
```

Update acceptance criteria as you complete each item, not just at the end.

### 5. Close Task

```bash
bd close <task-id> -r "Brief summary" --json
```

The close reason is a label. Main context lives in the final notes update.

### 6. Report to Control Tower

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

**Response:**
1. Create issue: `bd create "Side quest title" -t task -d "Context" --deps discovered-from:<current-task> --json`
2. Assess: **Blocker** or **deferrable**?
3. If deferrable: Continue current work, side quest is queued
4. If blocker: **Do NOT switch tasks yourself.** Document the blocker in your current task's notes, then surface to Control Tower immediately. Control Tower assigns work—you don't reassign yourself.

For full side quest workflow, see [WORKFLOWS.md](../beads/references/WORKFLOWS.md#side-quests).

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
- [ ] bd show <task-id> --json
- [ ] Read notes field first
- [ ] Review acceptance criteria
- [ ] Create TodoWrite from criteria
- [ ] Begin work
```

**During work:**
```
- [ ] Update notes at milestones
- [ ] Mark acceptance criteria [x] as completed
- [ ] Track side quests with discovered-from
- [ ] Escalate blockers immediately (don't switch tasks)
```

**Completing work:**
```
- [ ] Final notes update
- [ ] All acceptance criteria marked [x]
- [ ] bd close <task-id> -r "Summary" --json
- [ ] Report deliverables to Control Tower
```

For comprehensive checklists, see [WORKFLOWS.md](../beads/references/WORKFLOWS.md#checklist-templates).

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Work from conversation context alone | Read `bd show <task-id> --json` first |
| Update notes only at end | Update at milestones |
| Write vague notes ("made progress") | Write specific notes ("Implemented X, Y remains") |
| Ignore side quests | Track with discovered-from |
| Switch to blocker task yourself | Document blocker, surface to Control Tower |
| Leave acceptance criteria unchecked | Mark `[x]` as each criterion is met |
| Guess at architectural decisions | Escalate to Control Tower |
