# Agent Delegation Architecture

This document is the definitive reference for the agent delegation system. It provides high-level structure with references to detailed documentation.

## Overview

```
Mark (human)
  └── Control Tower (main Claude instance)
        │
        ├── Implementation (worktree)
        │   ├── task-executor    → General implementation
        │   └── rust-implementer → Rust-specific (2024 edition)
        │
        ├── Review (worktree)
        │   └── task-reviewer    → First-gate review
        │
        ├── Research (no worktree)
        │   └── researcher       → Read-only investigation
        │
        └── Utility (no worktree)
            └── quality-gate     → Landing verification
```

**Control Tower (CT)** orchestrates work through task graphs. It delegates focused work to specialized subagents, synthesizes their outputs, and maintains session continuity.

**Subagents** are stateless workers that receive task context via beads fields, execute in isolated worktrees (implementation/review) or directly on main repo (research/utility), and checkpoint state before returning.

## Agent Definitions

| Agent | Definition | Workflow Skill | Purpose |
|-------|------------|----------------|---------|
| task-executor | [`.claude/agents/task-executor.md`](.claude/agents/task-executor.md) | [`/agent-working`](.claude/skills/agent-working/SKILL.md) | General implementation |
| rust-implementer | [`.claude/agents/rust-implementer.md`](.claude/agents/rust-implementer.md) | [`/agent-working`](.claude/skills/agent-working/SKILL.md) | Rust code (has 2024 edition context) |
| task-reviewer | [`.claude/agents/task-reviewer.md`](.claude/agents/task-reviewer.md) | [`/agent-reviewing`](.claude/skills/agent-reviewing/SKILL.md) | First-gate review |
| researcher | [`.claude/agents/researcher.md`](.claude/agents/researcher.md) | [`/agent-researching`](.claude/skills/agent-researching/SKILL.md) | Read-only investigation |
| quality-gate | [`.claude/agents/quality-gate.md`](.claude/agents/quality-gate.md) | — | Landing verification |

### Agent File Structure

Agent `.md` files must be **self-contained**. Unlike `CLAUDE.md`, agent files do not support `@file.md` include directives—the `@` syntax is passed as literal text, forcing agents to manually read referenced files.

**Consequence:** Shared workflow sections (worktree discipline, notes protocol, checkpoint rules) are duplicated across `task-executor.md` and `rust-implementer.md`. When updating shared patterns, sync both files manually.

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

## Execution Modes

Agents operate in one of two modes:

| Mode | Agents | Setup Script | Closure |
|------|--------|--------------|---------|
| Worktree | task-executor, rust-implementer, task-reviewer | `begin-work` | `end-work` (merge) |
| Direct | researcher, quality-gate | `begin-research` or none | `bd close` directly |

**Worktree mode:** Isolated branch, changes merged to master after review.

**Direct mode:** Read-only on main repo, output via notes/comments/vault. No merge step.

## Task Lifecycle

### Scripts

| Script | Purpose | Reference |
|--------|---------|-----------|
| `begin-work <id>` | Create worktree, set status, output JSON context | [`scripts/begin-work.py`](scripts/begin-work.py) |
| `begin-research <id>` | Claim task without worktree, output JSON context | [`scripts/begin-research.sh`](scripts/begin-research.sh) |
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
- `open → in_progress` — `begin-work` or `begin-research` claims task
- `in_progress → review` — Agent completes work
- `review → in_progress` — Feedback requires changes
- `review → closed` — Merged to master (worktree) or closed directly (research)

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
# Agent runs begin-work (or begin-research), works, sets status to review
# CT reviews, coordinates closure (end-work or bd close)
```

**Reference:** [`/dispatching-agents`](.claude/skills/dispatching-agents/SKILL.md) — Agent selection, model choice, prompt construction

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
│   ├── task-executor.md      # Implementation agent
│   ├── rust-implementer.md   # Rust-specific implementation
│   ├── task-reviewer.md      # First-gate review
│   ├── researcher.md         # Read-only investigation
│   └── quality-gate.md       # Landing verification
├── skills/
│   ├── agent-working/        # Implementation workflow
│   ├── agent-reviewing/      # Review workflow
│   ├── agent-researching/    # Research workflow
│   ├── creating-tasks/       # Task creation guidance
│   ├── discovering-issues/   # Side quest capture
│   ├── dispatching-agents/   # Agent dispatch logic (CT)
│   ├── landing-the-plane/    # Session end protocol
│   └── shared/
│       ├── worktree-paths.md
│       ├── beads-field-reference.md
│       └── notes-format.md
├── control-tower-context.md  # CT-only instructions
└── hooks/                    # Claude Code hooks

scripts/
├── begin-work.py             # Worktree setup
├── begin-research.sh         # Research task setup (no worktree)
├── end-work.py               # Merge workflow
└── session-start.py          # Session state report
```
