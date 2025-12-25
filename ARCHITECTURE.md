# Agent Delegation Architecture

This document is the definitive reference for the agent delegation system. It provides high-level structure with references to detailed documentation.

## Overview

```
Mark (human)
  └── Control Tower (main Claude instance)
        ├── task-executor   → Implementation work
        ├── task-reviewer   → First-gate review
        └── rust-implementer → Rust-specific implementation
```

**Control Tower (CT)** orchestrates work through task graphs. It delegates focused work to specialized subagents, synthesizes their outputs, and maintains session continuity.

**Subagents** are stateless workers that receive task context via beads fields, execute in isolated worktrees, and checkpoint state before returning.

## Agent Definitions

| Agent | Definition | Workflow Skill | Purpose |
|-------|------------|----------------|---------|
| task-executor | [`.claude/agents/task-executor.md`](.claude/agents/task-executor.md) | [`/agent-working`](.claude/skills/agent-working/SKILL.md) | General implementation |
| task-reviewer | [`.claude/agents/task-reviewer.md`](.claude/agents/task-reviewer.md) | [`/agent-reviewing`](.claude/skills/agent-reviewing/SKILL.md) | First-gate review |
| rust-implementer | [`.claude/agents/rust-implementer.md`](.claude/agents/rust-implementer.md) | [`/agent-working`](.claude/skills/agent-working/SKILL.md) | Rust code (has 2024 edition context) |

### Built-in Agents

Available via Task tool's `subagent_type` parameter:
- `Explore` — Codebase exploration and context gathering
- `Plan` — Implementation planning
- `claude-code-guide` — Claude Code documentation lookup

## Worktree Isolation

Agents work in isolated git worktrees, never the main repository.

```
spacetraders/
├── src/                    # Main repo (CT only)
├── worktrees/
│   ├── abc/                # Agent working on task abc
│   └── xyz/                # Agent working on task xyz
└── .beads/                 # Task tracker (shared)
```

**Key rules:**
- Worktrees live at `./worktrees/<task-id>`
- Branches follow `task/<id>` naming
- File operations require full absolute paths for Claude tools
- Shell commands use relative paths after `cd`

**Reference:** [`shared/worktree-paths.md`](.claude/skills/shared/worktree-paths.md)

## Task Lifecycle

### Scripts

| Script | Purpose | Reference |
|--------|---------|-----------|
| `begin-work <id>` | Create worktree, set status, output JSON context | [`scripts/begin-work.py`](scripts/begin-work.py) |
| `end-work <id>` | Rebase, merge, cleanup, close task | [`scripts/end-work.py`](scripts/end-work.py) |

### Status Flow

```
draft ──────► open ──────► in_progress ──────► review ──────► closed
  │             │              │                  │              │
  │             │              │                  │              │
  │             └──────────────┴──────────────────┘              │
  │                            │                                 │
  └────────────────────────────┴─────────────────────────────────┘
                          (reopen)
```

**Transitions:**
- `draft → open` — Side quest refined, ready for work
- `open → in_progress` — `begin-work` claims task
- `in_progress → review` — Agent completes work
- `review → in_progress` — Feedback requires changes
- `review → closed` — Merged to master

## Two-Gate Review

Work passes through two review gates before merge:

### Gate 1: Mechanical Review (Agent or CT)

First gate catches obvious issues:
- Missing acceptance criteria
- Broken builds or failing tests
- Hygiene problems (uncommitted changes, debug artifacts)
- Missing required files

**Reference:** [`agent-reviewing/SKILL.md`](.claude/skills/agent-reviewing/SKILL.md)

### Gate 2: Judgment Review (Mark)

Second gate handles subjective decisions:
- Architecture and design quality
- Code style and idiom choices
- Whether the approach was optimal

## Checkpoint-and-Yield Model

Agents don't "escalate"—they checkpoint state and return. CT can then:
- Resolve blockers and resume the agent
- Reassign the work
- Escalate to Mark

**Checkpoint triggers:**
- Permission denied or environment errors
- Architectural decisions requiring human choice
- Ambiguous requirements needing clarification
- Scope significantly larger than described

**Reference:** [`agent-working/SKILL.md#escalation_rules`](.claude/skills/agent-working/SKILL.md)

## Beads Integration

[Beads](https://github.com/phate45/beads) is the task tracker. All strategic work flows through beads.

### Field Semantics

| Field | Mutability | Purpose |
|-------|------------|---------|
| `description` | Immutable | WHY and WHAT |
| `design` | Evolves | HOW to build |
| `acceptance_criteria` | **Read-only** (agents) | Definition of done (plain list) |
| `notes` | Frequent | Agent's checkpoint state |
| `comments` | Append-only | External feedback (reviews, CT notes) |

**Reference:** [`shared/beads-field-reference.md`](.claude/skills/shared/beads-field-reference.md)

### Notes vs Comments

```
notes field           comments field
─────────────         ──────────────
Agent's work record   External feedback
COMPLETED, CRITERIA   Review findings
Checkpoint state      CT guidance
─────────────         ──────────────
bd update --notes     bd comment -a "author"
REPLACES content      APPENDS to list
```

**Critical:** `bd update --notes` replaces the entire field. Agents must synthesize state, not append history.

**Reference:** [`shared/notes-format.md`](.claude/skills/shared/notes-format.md)

## Shared References

Skills declare dependencies via `<mandatory_reading>` sections:

| Reference | Purpose |
|-----------|---------|
| [`shared/worktree-paths.md`](.claude/skills/shared/worktree-paths.md) | File path requirements for tools |
| [`shared/beads-field-reference.md`](.claude/skills/shared/beads-field-reference.md) | Field semantics and reading priority |
| [`shared/notes-format.md`](.claude/skills/shared/notes-format.md) | Notes field structure and patterns |

## CT-Only Context

Control Tower receives additional context not available to subagents:

- [`.claude/control-tower-context.md`](.claude/control-tower-context.md) — Communication style, delegation model, session protocol
- CT skills: `/creating-tasks`, `/landing-the-plane`, `/writing-work-logs`

## Quick Reference

### Delegation Decision

```
Can task be done in one tool call?
  YES → Do it directly
  NO  → Create beads task, delegate to agent
```

### Agent Dispatch

```bash
# CT creates task, dispatches agent
bd create --title="..." --type=task
# Agent runs begin-work, works in worktree, sets status to review
# CT reviews, coordinates merge, cleans up
```

### Worktree Cleanup (after merge)

```bash
git worktree remove worktrees/<id>   # Removes worktree + git metadata
git branch -d task/<id>              # Deletes branch
```

**Never** use `rm -rf worktrees/<id>` directly—leaves git metadata stale.

## File Index

```
.claude/
├── agents/
│   ├── task-executor.md      # Implementation agent blueprint
│   ├── task-reviewer.md      # Review agent blueprint
│   └── rust-implementer.md   # Rust-specific agent
├── skills/
│   ├── agent-working/        # Implementation workflow
│   ├── agent-reviewing/      # Review workflow
│   ├── creating-tasks/       # Task creation guidance
│   ├── discovering-issues/   # Side quest capture
│   ├── landing-the-plane/    # Session end protocol
│   └── shared/
│       ├── worktree-paths.md
│       ├── beads-field-reference.md
│       └── notes-format.md
├── control-tower-context.md  # CT-only instructions
└── hooks/                    # Claude Code hooks

scripts/
├── begin-work.py             # Worktree setup
├── end-work.py               # Merge workflow
└── session-start.py          # Session state report
```
