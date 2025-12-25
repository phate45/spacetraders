# Session Context - Dec 25, 2025 (01:50)

## What This Project Is

SpaceTraders API client with a sophisticated **agent delegation system**. Mark (human) works with Claude (Control Tower) who orchestrates specialized subagents for implementation work.

## Current Architecture

### Agent Hierarchy
```
Mark (human)
  └── Control Tower (main Claude instance)
        ├── task-executor (implementation agent)
        ├── task-reviewer (review agent)
        └── rust-implementer (Rust-specific, WIP)
```

### Key Patterns

**Worktree Isolation:**
- Agents work in `./worktrees/<task-id>/` (never main repo)
- `begin-work <id>` creates worktree + branch, sets status to in_progress
- `end-work <id>` rebases, merges to master, cleans up, closes task, pushes

**Two-Gate Review:**
1. First gate: task-reviewer agent catches mechanical issues
2. Second gate: Mark reviews judgment calls (architecture, style)

**Checkpoint-and-Yield:**
- Agents document state in notes field and return (don't "escalate")
- Control Tower can resume agents via Task tool with resolution

**Comments vs Notes:**
- `notes` field = agent's work record (COMPLETED, CRITERIA, KEY_DECISIONS)
- `comments` = external feedback (review findings via `bd comment`)
- `bd update --notes` **REPLACES** entire field — critical warning added everywhere

### Key Files

| File | Purpose |
|------|---------|
| `.claude/agents/task-executor.md` | Blueprint agent for implementation |
| `.claude/agents/task-reviewer.md` | Blueprint agent for review |
| `.claude/skills/agent-working/SKILL.md` | Implementation workflow skill |
| `.claude/skills/agent-reviewing/SKILL.md` | Review workflow skill |
| `scripts/begin-work.py` | Worktree setup, outputs JSON context |
| `scripts/end-work.py` | Merge workflow, closes task |

### Beads Task Tracker

Use `bd` commands for task management:
```bash
bd ready              # Available work
bd show <id> --json   # Task details (returns array, use jq '.[0]')
bd update <id> --status review --notes "..." --json
bd comment <id> "..." -a "agent-name" --json
bd close <id> -r "reason" --json
bd sync               # Commit beads changes
```

## In-Progress Work

### Task: spacetraders-vgj (Open)
**Title:** Enhance agent-reviewing skill with missing sections

**Problem:** Gap analysis found agent-reviewing skill incomplete compared to agent-working:
1. Missing file path requirements (Read/Grep need full worktree paths)
2. Missing beads field reference table
3. Missing error handling patterns (permission denied, git failures)
4. Missing escalation boundaries (when to defer vs block)

**Proposed Solution:** Add missing sections to agent-reviewing, possibly extracting shared content to `skills/shared/` for deduplication.

**Context:** The task-reviewer agent uses `/agent-reviewing` as its mandatory initialization skill (like task-executor uses `/agent-working`). If agent-reviewing is incomplete, reviewers will hit gaps.

## Recent Decisions

1. **Comments for review feedback:** Reviewers use `bd comment` instead of `bd update --notes` to preserve agent's checkpoint state
2. **Task-reviewer replaces code-reviewer:** New agent follows blueprint structure, references skill
3. **@ syntax in agents undocumented:** Can't use file inclusion in agent.md files (tested, no official support)
4. **Notes field data loss warnings:** Added to task-executor, notes-format, agent-working, discovering-issues

## File Path Convention

**Inside worktree (after `cd worktrees/<id>`):**
- Shell commands: relative paths work
- Read/Edit tools: MUST use full paths (`/home/phate/BigProjects/spacetraders/worktrees/<id>/...`)
- bd commands: work from anywhere (finds .beads/ automatically)

## Scripts Reference

**begin-work.py output:**
```json
{
  "task": { "id", "title", "description", "design", "acceptance_criteria", "notes", "comments": [...] },
  "workspace": { "worktree_path", "worktree_name", "branch_name" },
  "mode": "new" | "resume",
  "resume_context": { "commits", "uncommitted_changes", "notes_sections" }
}
```

**end-work.py:** validate → pull → rebase → merge (ff) → cleanup worktree → close task → bd sync → push

## What NOT To Do

- Don't use `bd update --notes` without reading existing notes first (data loss)
- Don't use `rm -rf worktrees/<id>` (use `git worktree remove`)
- Don't skip `bd sync` before push
- Don't run scripts in `scripts/` without Mark's direction

## Session Start Protocol

```bash
python3 scripts/session-start.py --pretty  # Returns ready work, in-progress, drafts
```

Then report state to Mark.
