---
name: agent-working
description: Core workflow for agents executing beads tasks. Invoke FIRST before starting any assigned work. Covers task reading, notes updates, TodoWrite integration, side quest handling, and checkpoint/resume patterns.
---

<objective>
This skill defines the standardized workflow for all agents executing beads tasks in worktrees. It covers the complete lifecycle from workspace initialization through work execution to checkpoint/completion.

Agents operate in isolation, receive task context via beads fields, execute work in dedicated worktrees, and checkpoint state in the notes field for resumption. This skill ensures consistent practices across all agent invocations.

**Key principles:**
- Agents are stateless across invocations - all context lives in beads fields
- Work happens exclusively in worktrees (never main repo)
- Notes field is the context carrier for checkpointing and resumption
- TodoWrite provides tactical execution tracking within a session
- Checkpoint state before yielding (errors, blockers, user decisions needed)
</objective>

<mandatory_reading>
Before starting work, read these shared references:
- `.claude/skills/shared/worktree-paths.md` — File path requirements for Read/Edit/Grep tools
- `.claude/skills/shared/beads-field-reference.md` — Field semantics and context hierarchy
- `.claude/skills/shared/notes-format.md` — Notes field structure and update patterns
</mandatory_reading>

<essential_principles>
## Workspace Isolation

All agent work happens in dedicated worktrees at `./worktrees/<task-id>`. Never work in the main repository. File paths for Read/Edit tools MUST include the full worktree path.

## Context Hierarchy

Task context flows through beads fields in priority order:
1. **notes** - Current state, most recent session handoff (read this FIRST on resume)
2. **comments** - External feedback, especially review findings (check on resume if status was `review`)
3. **acceptance_criteria** - Definition of done, your checklist
4. **design** - Implementation approach (HOW to build)
5. **description** - Problem statement (WHY and WHAT)

## Checkpoint and Resume Model

Agents can be resumed via the Task tool's resume mechanism. When you cannot proceed (blockers, errors, need user input):
1. Update notes field with current state using standard format
2. Summarize situation in your output
3. Return (do NOT continue working on a different task)

Control Tower can then:
- Resolve the blocker
- Resume you via Task tool with additional context
- Reassign the work

## State Persistence

The notes field is your persistent memory across checkpoints.

**⚠️ CRITICAL:** `bd update --notes` REPLACES the entire field. If you don't synthesize previous state into your update, that context is **lost**. See `.claude/skills/shared/notes-format.md` for the full warning and correct pattern.

**Key rules:**
- Overwrite previous notes (don't append history)
- Write for zero-context resume (passes "future-me test" and "stranger test")
- Include specific accomplishments, current state, concrete next step
- Document blockers and key decisions
</essential_principles>

<quick_start>
**Minimal agent workflow:**

1. Run `begin-work <task-id>` via Bash tool
2. Parse JSON output for worktree path and task context
3. `cd <worktree_path> && pwd` to enter workspace
4. Create TodoWrite with worktree path as first item (spatial anchor)
5. Read notes field first (if resume), then acceptance criteria
6. Execute work, updating notes at milestones (include CRITERIA section for progress)
7. Commit when ready: `git add -A && git commit -m "..."`
8. Set status to review: `bd update <id> --status review --json`
9. Report deliverables in your output

**If blocked:** Update notes, document blocker, return (don't switch tasks).

**Workflow continuity:** If `begin-work` returns `mode: resume`, check what's already done before restarting work. Review git log, existing files, and notes field to understand current state. Don't redo completed work.
</quick_start>

<workflow>
<step name="initialize_workspace">
## Step 1: Initialize Workspace

Use the Bash tool to run the `begin-work` command:

```bash
begin-work <task-id>
```

This command:
- Fetches task info from beads
- Creates worktree + branch if new task, or detects existing for resume
- Sets task status to `in_progress`
- Outputs JSON with all context you need

**Output structure:**
```json
{
  "task": {
    "id": "abc",
    "title": "...",
    "description": "...",
    "design": "...",
    "acceptance_criteria": "...",
    "notes": "...",
    "comments": [{"id": 1, "author": "code-reviewer", "text": "...", "created_at": "..."}]
  },
  "workspace": {
    "worktree_path": "/full/path/to/worktrees/abc",
    "worktree_name": "abc",
    "branch_name": "task/abc"
  },
  "mode": "new" | "resume",
  "resume_context": {  // Only present when mode="resume"
    "commits": ["abc123 commit title", ...],
    "uncommitted_changes": ["M file.rs", ...],
    "notes_sections": ["COMPLETED", "IN_PROGRESS", ...]
  }
}
```

**On resume mode:** The `resume_context` tells you what's already done:
- **commits**: Prior commits on the branch (check before redoing work)
- **uncommitted_changes**: Files modified but not committed
- **notes_sections**: Which sections exist in notes field (read them!)

**If the script errors:** STOP. Document the error, return. Do not proceed or improvise workarounds.

**CRITICAL - What NOT to do:**

`begin-work` is a symlinked shell command. Use it via Bash tool.

| ❌ WRONG | Why |
|----------|-----|
| `python scripts/begin-work.py` | Never call Python directly |
| `python /path/to/begin-work.py` | The symlink exists for a reason |
| `mcp__host-executor__execute_command` with begin-work | Shell command, not heavy tool |
| Manual worktree creation | Wrong naming conventions, missing setup |

**If Bash permission is denied:** STOP. Return with error report. Do NOT improvise.
</step>

<step name="enter_worktree">
## Step 2: Enter Worktree

Change to the worktree directory and verify location:

```bash
cd <worktree_path> && pwd
```

Verify `pwd` output shows `<repo>/worktrees/<id>` before proceeding.

**File path requirements:** See `shared/worktree-paths.md` for full details.

- **Shell tools** (rg, git, etc.): Relative paths work after `cd`
- **Read/Edit/Write/Grep/Glob**: MUST use full absolute paths including `/worktrees/<id>/`
- **Heavy tools** (cargo, bun): Use `mcp__host-executor__execute_command(..., worktree=<worktree_name>)`
- **bd**: Works from anywhere—finds `.beads/` automatically
</step>

<step name="create_todo_list">
## Step 3: Create TodoWrite List

Create TodoWrite from acceptance criteria with worktree path as first item:

```
TodoWrite([
  {
    content: "Working in worktree: /full/path/to/worktrees/abc",
    activeForm: "Working in worktree: /full/path/to/worktrees/abc",
    status: "completed"
  },
  {
    content: "First acceptance criterion",
    activeForm: "Working on first acceptance criterion",
    status: "in_progress"
  },
  {
    content: "Second acceptance criterion",
    activeForm: "Working on second acceptance criterion",
    status: "pending"
  }
])
```

**Why worktree path first?**
- Provides spatial grounding for the agent
- Clear visual reminder of workspace isolation
- Prevents accidental main repo edits
- Mark as completed immediately after creation
</step>

<step name="read_task_context">
## Step 4: Read Task Context

From `begin-work` output, read fields in priority order:

**If mode = "resume":**
1. **notes field** - Start here. Contains handoff from previous session.
2. **acceptance_criteria** - Check what's already marked `[x]` as done
3. **design field** (if needed) - Review implementation approach
4. **description** (if needed) - Refresh on problem statement

**If mode = "new":**
1. **acceptance_criteria** - Your definition of done
2. **design field** - Implementation approach (HOW to build)
3. **description** - Problem statement (WHY and WHAT)
4. **notes field** - Usually empty for new tasks

**Reading large reference documents:**

When task references documentation, target specific sections:

```bash
rg "^#+" <path-to-document> -n  # Get headings with line numbers
```

Then use Read tool with `offset` and `limit` parameters to load only relevant sections.
</step>

<step name="execute_work">
## Step 5: Execute Work

Work systematically through acceptance criteria. Update notes at milestones.

**When to update notes:**
- After completing significant work chunks
- Before decisions that change direction or need user input
- When hitting blockers or errors
- Before checkpointing (if yielding control)
- When discovering side quests

**Notes update command:**

```bash
bd update <task-id> --notes "COMPLETED: [specific deliverables]

IN_PROGRESS: [current state with details]

NEXT: [concrete next step, not vague]

BLOCKERS: [specific blockers with context]

KEY_DECISIONS: [important choices or user guidance]" --json
```

See `.claude/skills/shared/notes-format.md` for format details and examples.

**Track acceptance criteria in CRITERIA section:**

Include a CRITERIA section in your notes update showing which criteria are complete:

```
CRITERIA: ✓ First criterion, ✓ Second criterion | Remaining: Third criterion
```

Mark criteria complete when VERIFIED, not just implemented. Do NOT use `bd update --acceptance`—track progress in notes instead.

**Update TodoWrite status:**
- Mark current item `in_progress` when you start it
- Mark `completed` when done
- Always have exactly ONE item in_progress
</step>

<step name="handle_side_quests">
## Step 6: Handle Side Quests

**Triggers** - You've discovered a side quest when:
- Implementation reveals unexpected dependency
- Bug found unrelated to current task
- Architectural issue surfaces
- Refactoring opportunity identified

**When you hit a trigger:** Invoke `/discovering-issues` skill immediately.

The skill covers:
- Two-step capture pattern (create issue → mark as draft)
- Blocker vs. deferrable assessment
- Parent task notes update
- Escalation rules

**Do NOT:**
- Ignore side quests (they compound)
- Switch to working on the side quest yourself (context switch penalty)
- Treat blockers as deferrable (delays completion)
</step>

<step name="checkpoint_if_blocked">
## Step 7: Checkpoint If Blocked

If you cannot proceed (errors, blockers, need user input), checkpoint state:

1. **Update notes field** with current state:
   ```bash
   bd update <task-id> --notes "COMPLETED: [what was built]

   IN_PROGRESS: [current work state]

   BLOCKERS: [specific blocker with full context]

   NEXT: [what needs to happen to unblock]

   KEY_DECISIONS: [any relevant context]" --json
   ```

2. **Commit current work** (if any changes):
   ```bash
   git add -A && git commit -m "task(<id>): checkpoint before <blocker-summary>"
   ```

3. **Summarize in your output:**
   - What was completed
   - What the blocker is
   - What's needed to proceed
   - Current worktree and branch

4. **Return** (do NOT switch to a different task)

Control Tower can then resolve and resume you via Task tool with:
- Additional context
- User decisions
- Environment fixes
- Blocker resolution
</step>

<step name="complete_work">
## Step 8: Complete Work

When all acceptance criteria are met:

1. **Final commit:**
   ```bash
   git add -A && git commit -m "<type>(<id>): <summary>"
   ```

   Example: `git commit -m "task(abc): implement begin-work script"`

2. **Final status update with notes:**
   ```bash
   bd update <task-id> --status review --notes "COMPLETED: [all deliverables summary]

   CRITERIA: ✓ All criteria verified and met

   VAULT_DOCS: [any documentation created, with paths]" --json
   ```

   **Do NOT use `bd close`** - closing happens after Control Tower review and merge.
</step>

<step name="report_completion">
## Step 9: Report to Control Tower

Your output must include:

1. **Deliverables** - What was created/modified (file paths)
2. **Vault docs** - Documentation created (if any, with full paths)
3. **Follow-up work** - Side quests discovered (with IDs if created)
4. **Blockers** - Anything preventing completion (if checkpointing)
5. **Key decisions** - Important choices made during implementation

**Format:**

```
## Work Completed: <Task Title>

**Deliverables:**
- /path/to/worktrees/abc/src/new_file.rs - New implementation
- /path/to/worktrees/abc/src/existing.rs - Updated function X
- /path/to/worktrees/abc/README.md - Updated documentation

**Status:** Ready for review (or: Blocked, awaiting resume)

**Follow-up work:**
- Issue #xyz: Discovered refactoring opportunity (deferrable)

**Key decisions:**
- Chose approach X over Y because [reason]
```
</step>
</workflow>

<todowrite_integration>
## TodoWrite Integration Pattern

**Strategy:** beads is strategic (multi-session persistence), TodoWrite is tactical (current session execution).

```
beads task: Strategic objective
  │
  └─ TodoWrite: Tactical execution steps
     1. [completed] Worktree path (spatial anchor)
     2. [in_progress] Current acceptance criterion
     3. [pending] Next acceptance criterion
     4. [pending] Final verification
```

**Workflow:**
1. Read beads issue, note acceptance criteria
2. Create TodoWrite from criteria items (with worktree path first)
3. Execute via TodoWrite for visible progress
4. Update beads notes at milestones (not every step)
5. Mark beads criteria `[x]` as TodoWrite items complete
6. Update beads status to `review` when all TodoWrite items done

**Why this pattern:**
- TodoWrite gives real-time progress visibility in current session
- beads notes give resumability across sessions
- No duplication (TodoWrite for steps, beads for state)
- Clear separation of tactical vs strategic tracking
</todowrite_integration>

<escalation_rules>
## When to Checkpoint and Return

Checkpoint state and return immediately when:

**Technical Blockers:**
- Permission denied errors (file access, command execution)
- Missing dependencies or tools
- Environment configuration issues
- API/service unavailable

**Architectural Decisions:**
- Multiple valid approaches requiring user choice
- Changes affecting project structure or conventions
- Technology selection decisions
- Breaking changes or migrations

**User Input Required:**
- Ambiguous requirements needing clarification
- Design decisions requiring domain knowledge
- Priority/scope trade-off decisions
- Approval needed before proceeding

**Scope Issues:**
- Task scope significantly larger than described
- Side quest that's a blocker (not deferrable)
- Requirements conflict discovered

**Do NOT:**
- Try to fix environment issues yourself (checkpoint and return)
- Make architectural decisions unilaterally (checkpoint and ask)
- Expand scope without approval (checkpoint and clarify)
- Switch to working on blocker side quests (checkpoint and return)
</escalation_rules>

<field_reference>
## Beads Field Usage

See `shared/beads-field-reference.md` for full field semantics.

**Quick reference:**
- `notes` — Your checkpoint state (read first on resume)
- `comments` — External feedback (check if returning from review)
- `acceptance_criteria` — Definition of done
- `design` — HOW to build (can evolve)
- `description` — WHY and WHAT (immutable)

**Critical:** `bd update --notes` REPLACES entire field. See `shared/notes-format.md` for correct pattern.
</field_reference>

<anti_patterns>
## Common Mistakes

| Don't | Do Instead |
|-------|------------|
| Skip `begin-work` and call `bd show` directly | Always run `begin-work <task-id>` first |
| Work outside the worktree | Verify `pwd` shows worktrees path before starting |
| Use main repo paths for Read/Edit | Use full worktree paths for file operations |
| Skip worktree path in TodoWrite first item | Always anchor with worktree path first |
| Use `bd close` to finish | Use `bd update --status review` |
| Update notes only at end | Update at milestones throughout work |
| Write vague notes ("made progress") | Write specific notes ("Implemented X, Y remains") |
| Ignore side quests | Invoke `/discovering-issues` immediately |
| Try to fix blockers yourself | Checkpoint state, document blocker, return |
| Continue after `begin-work` errors | Stop and return with error report |
| Make architectural decisions alone | Checkpoint and escalate for user input |
| Skip CRITERIA in notes updates | Track criteria progress in notes CRITERIA section |
| Omit KEY_DECISIONS from notes | Document important choices and rationale |
| Append to notes field | Overwrite previous notes (current state only) |
</anti_patterns>

<reference_checklists>
## Quick Checklists

**Starting work:**
```
- [ ] Run `begin-work <task-id>` via Bash tool
- [ ] Parse JSON output (worktree_path, task context)
- [ ] cd <worktree_path> && pwd (verify location)
- [ ] Create TodoWrite with worktree path as first item
- [ ] Read notes field first (if resume), then criteria
- [ ] If resume: check git log and existing files for completed work
- [ ] Mark first TodoWrite item after worktree as in_progress
- [ ] Begin work
```

**During work:**
```
- [ ] Update notes at milestones (include CRITERIA section)
- [ ] Update TodoWrite status (in_progress → completed)
- [ ] Handle side quests via /discovering-issues
- [ ] Commit at appropriate granularity
- [ ] If blocked: checkpoint notes, return (don't switch tasks)
```

**Completing work:**
```
- [ ] All acceptance criteria verified
- [ ] Final commit: git add -A && git commit -m "..."
- [ ] All TodoWrite items completed
- [ ] Set status with notes: bd update <id> --status review --notes "..." --json
- [ ] Report deliverables in output (file paths, decisions)
```

**Checkpointing (if blocked):**
```
- [ ] Update notes with COMPLETED, IN_PROGRESS, BLOCKERS, NEXT
- [ ] Commit current work: git add -A && git commit -m "checkpoint: ..."
- [ ] Document blocker with full context in notes
- [ ] Summarize situation in output
- [ ] Return (do not switch to different task)
```
</reference_checklists>

<success_criteria>
Agent workflow is successful when:

**Workspace:**
- [ ] Worktree created/resumed via `begin-work`
- [ ] All file operations use full worktree paths
- [ ] TodoWrite first item anchors worktree path
- [ ] Work happens exclusively in worktree (not main repo)

**Context:**
- [ ] Notes field read first on resume
- [ ] Acceptance criteria guide execution
- [ ] Task context fully understood before starting

**Execution:**
- [ ] TodoWrite tracks tactical progress
- [ ] Notes updated at milestones (with CRITERIA section)
- [ ] Side quests captured via `/discovering-issues`

**Checkpointing:**
- [ ] Notes field contains resumable state
- [ ] Blockers documented with full context
- [ ] Work committed before checkpoint
- [ ] Agent returns (doesn't switch tasks)

**Completion:**
- [ ] All acceptance criteria marked `[x]`
- [ ] Status set to `review`
- [ ] Deliverables reported with file paths
- [ ] Key decisions documented

**Quality:**
- [ ] Notes pass "future-me test" (can resume in 2 weeks)
- [ ] Notes pass "stranger test" (another dev can understand)
- [ ] No architectural decisions made unilaterally
- [ ] Commits have clear, descriptive messages
</success_criteria>
