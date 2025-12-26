---
name: agent-researching
description: Core workflow for research agents. Invoke FIRST before starting any assigned research task. Covers task reading, notes updates, TodoWrite integration, output destinations, and checkpoint patterns. Read-only operations on main repo.
---

<objective>
This skill defines the standardized workflow for research agents investigating questions, gathering context, and documenting findings. Unlike implementation agents, researchers operate read-only on the main repository—no worktrees, no code changes, no merges.

**Key principles:**
- Agents are stateless across invocations—all context lives in beads fields
- Work happens in the main repo (read-only)—no worktree isolation
- Notes field is the primary output and context carrier
- Optional outputs: vault documentation, plans/ proposals
- Checkpoint state before yielding (errors, blockers, decisions needed)
</objective>

<mandatory_reading>
Before starting research, read these shared references:
- `.claude/skills/shared/beads-field-reference.md` — Field semantics and context hierarchy
- `.claude/skills/shared/notes-format.md` — Notes field structure and update patterns
</mandatory_reading>

<essential_principles>
## Read-Only Discipline

Research agents do NOT modify the codebase. You read, analyze, and document—you don't implement.

**Allowed:**
- Read tool for all file access
- Grep/Glob for searching
- Bash for read-only commands (rg, git log, git show, etc.)
- Write to task notes field (via `bd update`)
- Write to vault documentation
- Write to plans/ directory (proposals, not implementation)

**Forbidden:**
- Edit/Write tools on source code
- Git commits in main repo
- Any file modification outside vault/plans

## Context Hierarchy

Task context flows through beads fields in priority order:
1. **notes** — Current state, most recent session handoff (read this FIRST on resume)
2. **comments** — External feedback from prior research or reviews
3. **acceptance_criteria** — Research questions to answer, your checklist
4. **design** — Investigation approach (if specified)
5. **description** — Research scope (WHY and WHAT to investigate)

## Checkpoint and Resume Model

Agents can be resumed via the Task tool's resume mechanism. When you cannot proceed:
1. Update notes field with current findings and state
2. Summarize situation in your output
3. Return (do NOT continue with a different task)

Control Tower can then:
- Provide additional context
- Resume you with clarification
- Reassign the research

## State Persistence

The notes field is your persistent memory across checkpoints.

**⚠️ CRITICAL:** `bd update --notes` REPLACES the entire field. If you don't synthesize previous findings into your update, that context is **lost**. See `.claude/skills/shared/notes-format.md` for the full warning.

**Key rules:**
- Overwrite previous notes (don't append history)
- Write for zero-context resume
- Include specific findings, current state, concrete next step
- Document blockers and key discoveries
</essential_principles>

<quick_start>
**Minimal research workflow:**

1. Run `begin-research <task-id>` via Bash tool
2. Parse JSON output for task context
3. Create TodoWrite with research topic as first item
4. Read notes field first (if resume), then acceptance criteria
5. Investigate systematically, updating notes at milestones
6. Write to vault/plans if findings warrant persistent docs
7. Set status to review: `bd update <id> --status review --notes "..." --json`
8. Report findings in your output

**If blocked:** Update notes, document blocker, return (don't switch tasks).
</quick_start>

<workflow>
<step name="initialize_research">
## Step 1: Initialize Research Context

Use the Bash tool to run the `begin-research` command:

```bash
begin-research <task-id>
```

This command:
- Fetches task info from beads
- Sets task status to `in_progress`
- Outputs JSON with task context (no worktree—you work in main repo)

**Output structure:**
```json
{
  "task": {
    "id": "spacetraders-abc",
    "title": "...",
    "description": "...",
    "design": "...",
    "acceptance_criteria": "...",
    "notes": "...",
    "comments": [{"id": 1, "author": "...", "text": "...", "created_at": "..."}]
  },
  "mode": "research"
}
```

Note: No `workspace` field—research operates on main repo directly.

**If the script errors:** STOP. Document the error, return. Do not improvise.
</step>

<step name="create_todo_list">
## Step 2: Create TodoWrite List

Create TodoWrite from research questions/criteria:

```
TodoWrite([
  {
    content: "Research <task-id>: <brief topic>",
    activeForm: "Researching <brief topic>",
    status: "in_progress"
  },
  {
    content: "First research question",
    activeForm: "Investigating first question",
    status: "pending"
  },
  {
    content: "Document findings",
    activeForm: "Documenting findings",
    status: "pending"
  }
])
```

The first item anchors the research focus (analogous to worktree path for implementers).
</step>

<step name="read_task_context">
## Step 3: Read Task Context

From `begin-research` output, read fields in priority order:

**If resuming (notes field has content):**
1. **notes field** — Start here. Contains findings from previous session.
2. **comments** — Check for feedback or additional context.
3. **acceptance_criteria** — Cross-reference with your findings.

**If new research:**
1. **acceptance_criteria** — Research questions to answer
2. **design field** — Investigation approach (if provided)
3. **description** — Research scope and motivation

**If acceptance_criteria is empty:** STOP AND REPORT to Control Tower. You need clear questions to investigate.
</step>

<step name="execute_research">
## Step 4: Execute Research

Investigate systematically. Update notes at milestones.

**Research patterns:**
- Use Grep/Glob to find relevant code
- Use Read to examine files
- Use Bash for git history, file stats, etc.
- Synthesize findings as you go

**When to update notes:**
- After answering a research question
- When discovering significant findings
- Before any decision that needs user input
- When hitting blockers
- Before checkpointing

**Notes update command:**

```bash
bd update <task-id> --notes "COMPLETED: [questions answered, findings]

IN_PROGRESS: [current investigation]

KEY_FINDINGS: [important discoveries]

NEXT: [concrete next step]

BLOCKERS: [if any]" --json
```

**Track criteria in CRITERIA section:**

```
CRITERIA: ✓ Question 1 answered, ✓ Question 2 answered | Remaining: Question 3
```
</step>

<step name="handle_side_quests">
## Step 5: Handle Side Quests

Research often uncovers work outside scope:
- Bugs discovered during investigation
- Follow-up research questions
- Implementation tasks revealed

**When you find something:** Invoke `/discovering-issues` skill immediately.

Do NOT:
- Ignore discoveries (they inform future work)
- Switch to implementing what you found
- Expand scope without approval
</step>

<step name="write_outputs">
## Step 6: Write Outputs

Research output goes to three possible locations:

**1. Task Notes Field (always)**
- Summary of findings
- Key conclusions
- Criteria tracking
- Links to detailed docs if created

**2. Vault Documentation (lasting value)**
- Technical decision records
- Architecture analysis
- Research summaries
- Location: `/home/phate/Documents/second-brain/01_Projects/spacetraders/`
- Use `/creating-vault-documentation` skill

**3. plans/ Directory (project proposals)**
- Design proposals
- Implementation plans
- Architecture sketches
- Location: `/home/phate/BigProjects/spacetraders/plans/`

**Guidelines:**
- Keep notes field concise (reference detailed docs)
- Vault docs for research with lasting value
- plans/ for proposals that inform future implementation
</step>

<step name="checkpoint_if_blocked">
## Step 7: Checkpoint If Blocked

If you cannot proceed:

1. **Update notes field** with current findings:
   ```bash
   bd update <task-id> --notes "COMPLETED: [findings so far]

   IN_PROGRESS: [current state]

   BLOCKERS: [specific blocker with context]

   NEXT: [what needs to happen]" --json
   ```

2. **Summarize in your output:**
   - What was researched
   - What the blocker is
   - What's needed to proceed

3. **Return** (do NOT switch tasks)
</step>

<step name="complete_research">
## Step 8: Complete Research

When all research questions are answered:

1. **Final notes update with status:**
   ```bash
   bd update <task-id> \
     --status review \
     --notes "COMPLETED: [all findings summary]

   KEY_FINDINGS: [important discoveries]

   CRITERIA: ✓ All research questions answered

   VAULT_DOCS: [if created, with paths]" \
     --json
   ```

2. **If you created vault/plans docs:** Commit them:
   ```bash
   git add plans/<file>.md && git commit -m "docs(<id>): <summary>"
   ```

Do NOT use `bd close`—closing happens after Control Tower review.
</step>

<step name="report_completion">
## Step 9: Report to Control Tower

Your output must include:

1. **Findings** — What was discovered (specific, concrete)
2. **Conclusions** — Key insights and recommendations
3. **Documentation** — Vault docs or plans created (with paths)
4. **Follow-up work** — Side quests discovered (with IDs if created)
5. **Blockers** — Anything preventing completion (if checkpointing)

**Format:**

```
## Research Complete: <Task Title>

**Findings:**
- [Key finding 1]
- [Key finding 2]

**Conclusions:**
[Summary and recommendations]

**Documentation:**
- /path/to/vault/doc.md (if created)

**Status:** Ready for review (or: Blocked, awaiting resume)

**Follow-up:**
- Issue #xyz: Discovered task (if any)
```
</step>
</workflow>

<escalation_rules>
## When to Checkpoint and Return

Checkpoint immediately when:

**Information Gaps:**
- Missing context needed to answer questions
- Need access to systems/docs you can't reach
- Domain knowledge required from Mark

**Scope Issues:**
- Research scope larger than described
- Questions reveal deeper investigation needed
- Conflicting information requiring judgment

**Decision Points:**
- Multiple valid interpretations
- Findings that change project direction
- Recommendations requiring approval

**Do NOT:**
- Make assumptions about ambiguous findings
- Expand scope without approval
- Skip questions you can't fully answer
</escalation_rules>

<anti_patterns>
## Common Mistakes

| Don't | Do Instead |
|-------|------------|
| Skip `begin-research` | Always run `begin-research <task-id>` first |
| Modify source code | Research is read-only |
| Update notes only at end | Update at milestones throughout |
| Write vague findings ("looked at code") | Write specific findings ("Function X uses pattern Y") |
| Ignore side quests | Invoke `/discovering-issues` immediately |
| Continue after errors | Checkpoint state, document error, return |
| Make architectural recommendations without evidence | Document evidence, let Mark decide |
| Skip CRITERIA in notes | Track research question progress |
</anti_patterns>

<success_criteria>
Research is successful when:

**Context:**
- [ ] Task context loaded via `begin-research`
- [ ] Notes field read first on resume
- [ ] Research questions understood

**Execution:**
- [ ] TodoWrite tracks progress
- [ ] Notes updated at milestones
- [ ] Side quests captured via `/discovering-issues`

**Output:**
- [ ] All research questions answered (or blockers documented)
- [ ] Findings documented in notes field
- [ ] Vault/plans docs created if warranted
- [ ] Status set to `review`

**Quality:**
- [ ] Findings are specific and evidence-based
- [ ] Notes pass "future-me test"
- [ ] Conclusions follow from evidence
</success_criteria>
