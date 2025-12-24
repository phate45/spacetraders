---
name: reviewing-tasks
description: Control Tower self-review of completed agent work. Use when reviewing a task yourself (without delegating to code-reviewer agent) to verify acceptance criteria, deliverable quality, and worktree hygiene before escalating to Mark.
---

<objective>
Review completed agent work systematically before escalating to Mark. This is for when you (Control Tower) perform the first-gate review yourself rather than delegating to the code-reviewer agent.

For delegated reviews, use `/agent-reviewing` skill via the code-reviewer agent instead.
</objective>

<quick_start>
For task in `review` status:

```bash
# Get specific fields (bd show returns array, use .[0])
bd show <id> --json | jq '.[0] | {acceptance_criteria, notes, design}'

# Check worktree state (use -C since you're in project root)
git -C worktrees/<id> log --oneline master..HEAD
git -C worktrees/<id> status
git -C worktrees/<id> diff master..HEAD --stat
```

Then verify each acceptance criterion has evidence, not just claims.
</quick_start>

<essential_principles>
**Evidence over claims.** Agent says "✓ criterion met" means nothing. Check that the deliverable actually satisfies the criterion.

**First gate catches mechanical issues.** Missing files, broken builds, incomplete criteria, stray changes. Mark handles judgment calls (architecture, style, approach).

**Fail fast, fail clear.** If something's wrong, report it specifically. "Criterion X not met because Y" beats "needs work."
</essential_principles>

<process>
**1. Load Context**

Read task details (note: `bd show` returns an array):
```bash
bd show <id> --json | jq '.[0] | {acceptance_criteria, notes, design}'
```

Without `.[0]`, jq errors with "Cannot index array with string".

Extract:
- `acceptance_criteria` — What success looks like
- `notes` — Agent's COMPLETED/CRITERIA sections
- `design` — Intended approach

**2. Verify Acceptance Criteria**

For EACH criterion in `acceptance_criteria`:
- Find evidence in deliverables (not just agent's claim)
- Check that evidence actually satisfies the criterion
- Note any gaps or partial completions

Common failure modes:
- Agent claims criterion met but deliverable doesn't show it
- Criterion technically met but in wrong location/format
- Criterion met for happy path but not edge cases

**3. Check Deliverable Quality**

Review the actual changes:
```bash
git -C worktrees/<id> diff master..HEAD --stat   # What files changed
git -C worktrees/<id> show HEAD                  # Last commit details
```

Quality checks:
- Does implementation match design approach?
- Are there obvious bugs or issues?
- Is code/content in the right location?
- Any debug artifacts left behind? (console.log, TODO comments, test files)

**4. Verify Worktree Hygiene**

```bash
git -C worktrees/<id> status                     # Uncommitted changes?
git -C worktrees/<id> log --oneline master..HEAD # Clean commit history?
```

Hygiene checks:
- No uncommitted changes
- Commit messages are descriptive
- No unrelated changes bundled in
- Branch is rebased cleanly onto master (or will rebase cleanly)

**5. Review Notes Field**

Check agent's notes for:
- COMPLETED section matches actual deliverables
- CRITERIA section accurately reflects what's done vs pending
- KEY_DECISIONS captured (if any architectural choices made)

Notes quality matters for session continuity—bad notes mean lost context.

**6. Make Decision**

**APPROVE** (escalate to Mark) when:
- All acceptance criteria have verified evidence
- Deliverable quality is acceptable
- Worktree is clean
- Notes are accurate

**REQUEST CHANGES** when:
- Any criterion lacks evidence
- Obvious quality issues exist
- Worktree has uncommitted changes
- Notes are inaccurate or incomplete

For changes, update task notes with specific feedback:
```bash
bd update <id> --status in_progress --notes "FEEDBACK:
- Criterion X: [specific issue]
- [Other issues]

NEXT: [What agent should do]"
```
</process>

<review_output>
When escalating to Mark, provide:

```
## Review: <task-title>

**Verdict:** Ready for final review

**Acceptance Criteria:**
- ✓ Criterion 1: [evidence location/verification]
- ✓ Criterion 2: [evidence location/verification]

**Deliverables:**
- [file]: [what it does]

**Commits:** N commits, clean history

**Notes:** Accurate and complete

**Concerns (if any):** [judgment calls for Mark]
```

Keep it concise. Mark will read the actual code.
</review_output>

<anti_patterns>
<pitfall name="trusting_agent_claims">
Agent's CRITERIA section says "✓ All done" — meaningless without verification. Check the actual deliverables.
</pitfall>

<pitfall name="approving_incomplete_work">
If one criterion is partial or unclear, don't approve. Request clarification or changes.
</pitfall>

<pitfall name="vague_feedback">
"Needs work" helps no one. Specify exactly what's wrong and what to do about it.
</pitfall>

<pitfall name="reviewing_judgment_calls">
Architecture decisions, style choices, approach tradeoffs — these are Mark's domain. First gate catches mechanical issues only.
</pitfall>
</anti_patterns>

<success_criteria>
Review is complete when:
- [ ] All acceptance criteria verified with evidence
- [ ] Deliverable quality checked (no obvious bugs/issues)
- [ ] Worktree hygiene verified (clean, no stray changes)
- [ ] Notes field accuracy confirmed
- [ ] Clear verdict: APPROVE (escalate) or REQUEST CHANGES (with specifics)
</success_criteria>
