---
name: agent-reviewing
description: Review agent for first-gate verification of completed work. Use when assigned as reviewer for a task in 'review' status. Operates in worktree, documents findings as task comment, returns summary for CT escalation decision.
---

<objective>
Systematically verify completed agent work before escalation to Mark. You are the first gate in a two-gate review—catch mechanical issues (missing criteria, obvious bugs, hygiene problems) so Mark's review focuses on judgment calls.

Your findings go in a task **comment** (not notes—that's the agent's work record). Control Tower sees only your summary and decides whether to escalate or request changes.
</objective>

<mandatory_reading>
Before reviewing, read these shared references:
- `.claude/skills/shared/worktree-paths.md` — File path requirements for Read/Grep tools
- `.claude/skills/shared/beads-field-reference.md` — Field semantics and reading priority
- `.claude/skills/shared/notes-format.md` — Notes field structure (to validate agent's checkpoint)
</mandatory_reading>

<quick_start>
You are reviewing task `<id>`.

1. Initialize review context:
   ```bash
   begin-review <id>
   ```
   This validates the task is in `review` status, confirms the worktree exists, and returns JSON with task fields and workspace info.

2. Enter worktree: `cd <worktree_path> && pwd`
3. Verify each criterion with evidence from deliverables
4. Document findings as task comment (`bd comment`)
5. Return summary to Control Tower
</quick_start>

<essential_principles>
**Evidence over claims.** Agent's notes say "✓ done"—meaningless. Check the actual deliverables satisfy each criterion.

**First gate = mechanical issues.** Missing files, broken builds, incomplete criteria, hygiene problems. Leave architecture and style judgment to Mark.

**Comments are your primary output.** Write detailed findings as a task comment. Control Tower and Mark read comments for the full picture—your returned message is just the summary. Agent's notes field stays intact.

**Fail fast, fail specific.** "Criterion X not met: file Y missing function Z" beats "needs work."
</essential_principles>

<workflow>
**1. Initialize Review Context**

```bash
begin-review <id>
```

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
    "comments": [{"id": 1, "author": "task-executor", "text": "...", "created_at": "..."}]
  },
  "workspace": {
    "worktree_path": "worktrees/abc",
    "worktree_name": "abc",
    "branch_name": "task/abc"
  },
  "mode": "review",
  "resume_context": {
    "commits": ["abc123 commit title", ...],
    "uncommitted_changes": ["M file.rs", ...],
    "notes_sections": ["COMPLETED", "CRITERIA", ...]
  }
}
```

**Key fields for review:**
- `task.acceptance_criteria` — What success looks like (plain list, read-only)
- `task.notes` — Agent's COMPLETED/CRITERIA sections (verify these claims)
- `task.comments` — Any prior review feedback
- `resume_context.commits` — What the agent committed (review these)
- `resume_context.uncommitted_changes` — Should be empty if agent finished cleanly

**If script errors:** Task isn't in `review` status or worktree doesn't exist. STOP AND REPORT to Control Tower.

**If acceptance_criteria is empty or malformed:** STOP AND REPORT to Control Tower. You cannot review without clear criteria.

**2. Enter Worktree**

```bash
cd <worktree_path> && pwd
```

All subsequent git commands run in this directory—no `-C` flags needed.

**3. Review Deliverables**

Check what actually changed:
```bash
git log --oneline master..HEAD    # Commits on this branch
git diff master..HEAD --stat      # Files changed
git status                        # Uncommitted changes?
```

Read the changed files. Understand what was built.

**4. Verify Each Criterion**

For EACH item in `acceptance_criteria`:
- Find evidence in the deliverables
- Verify evidence actually satisfies the criterion
- Note gaps, partial completions, or concerns

Common failure modes:
- Agent claims met, deliverable doesn't show it
- Met in wrong location/format
- Met for happy path, not edge cases

**5. Check Hygiene**

- No uncommitted changes (`git status` clean)
- Commit messages are descriptive
- No unrelated changes bundled in
- No debug artifacts (console.log, TODO, test files)

All hygiene issues are valid feedback for the implementer to address—report them in your comment. The distinction between blocking issues and observations:
- **Blockers:** Failing tests, broken build, uncommitted changes, missing required files
- **Observations:** Missing comments, discovered side quests, minor style inconsistencies

**6. Document Findings**

Add your review as a **comment** (preserves agent's notes):
```bash
bd comment <id> "REVIEW:
Date: <date>

CRITERIA_VERIFICATION:
- [Criterion 1]: ✓ Verified - [evidence location]
- [Criterion 2]: ✓ Verified - [evidence location]
- [Criterion 3]: ✗ NOT MET - [specific reason]

QUALITY_ISSUES:
- [Issue 1, if any]
- [Issue 2, if any]

HYGIENE:
- Commits: [N commits, clean/messy history]
- Uncommitted: [none/list]
- Artifacts: [none/list]

VERDICT: APPROVE | REQUEST_CHANGES
REASON: [Brief explanation]

NEXT: [If changes needed, what specifically]" -a "task-reviewer" --json
```

**Why comments instead of notes?** The agent's notes field contains their work record (COMPLETED, CRITERIA, KEY_DECISIONS). Using `bd comment` keeps review feedback separate—the agent can read your feedback without losing their checkpoint state.

**7. Return Summary**

Your returned message to Control Tower should be concise:

```
## Review Complete: <task-title>

**Verdict:** APPROVE / REQUEST_CHANGES

**Criteria:** N/M verified
**Issues:** [count or "none"]

[If REQUEST_CHANGES: key issues in 1-2 sentences]

Full findings in task comments.
```

Control Tower reads comments for detail, then decides to escalate to Mark or resume the original agent with feedback.
</workflow>

<verdict_guidelines>
**APPROVE** when:
- All acceptance criteria verified with evidence
- No obvious quality issues
- Worktree is clean
- Notes accurately reflect work done

**REQUEST_CHANGES** when:
- Any criterion lacks evidence
- Obvious bugs or issues exist
- Uncommitted changes present
- Significant hygiene problems

**When uncertain:** Document the uncertainty in your comment and let Control Tower decide. "Criterion X technically met but implementation seems fragile" is useful information.
</verdict_guidelines>

<anti_patterns>
<pitfall name="trusting_self_reporting">
Agent's CRITERIA section shows checkmarks. Verify each one independently—self-reported completion is not evidence.
</pitfall>

<pitfall name="vague_findings">
"Some issues found" tells Control Tower nothing. Specific: "Criterion 2 not met: function missing error handling for empty input."
</pitfall>

<pitfall name="judging_architecture">
"Should have used a different pattern" is Mark's call. You verify criteria are met, not whether the approach was optimal.
</pitfall>

<pitfall name="skipping_comment">
Your summary is just a pointer. The comment contains the audit trail. Always add a comment with full findings.
</pitfall>
</anti_patterns>

<error_handling>
## When Things Go Wrong

**Worktree access fails:**
```
Error: worktree doesn't exist / permission denied
```
STOP. Return to Control Tower with error. Don't improvise or check main repo instead.

**Git commands fail:**
```
Error: not a git repository / cannot read commits
```
Document the error. You cannot verify hygiene without git access. Return with partial findings.

**bd commands fail:**
```
Error: cannot add comment / task not found
```
Document findings in your output instead. Control Tower can add the comment manually. Don't silently skip documentation.

**Cannot read deliverables:**
```
Error: file not found / permission denied on Read
```
This might BE a finding (agent didn't create expected files). Check acceptance criteria—if file should exist, that's a criterion failure. If it's a permissions issue, return with error.

**Pattern:** When blocked, document what you could verify, what you couldn't, and why. Partial review with clear gaps beats silent failure.
</error_handling>

<escalation_boundaries>
## Your Scope vs Mark's Scope

**Your job (first gate):**
- Verify each acceptance criterion has evidence
- Check deliverables exist and are plausible
- Catch obvious bugs, missing files, hygiene issues
- Validate agent's notes reflect actual work

**Mark's job (second gate):**
- Architecture and design quality
- Code style and idiom choices
- Whether the approach was optimal
- Subjective quality judgments

**When you find something in Mark's territory:**

Don't block on it. Document as an observation, not a criterion failure:

```
OBSERVATIONS:
- Implementation uses pattern X; Mark may prefer Y (not blocking)
```

Then APPROVE if criteria are met, letting Mark make the call.

**When genuinely uncertain:**

If you can't tell whether a criterion is met:

```
UNCERTAIN:
- Criterion 3: "Error handling complete" — found try/catch but unsure if all cases covered
```

Document the uncertainty, provide what evidence you found, let Control Tower decide.

**Discovering unrelated issues:**

If you find bugs or problems outside the acceptance criteria scope:

1. Invoke `/discovering-issues` skill to create a draft task
2. Note the task ID in your comment: `DISCOVERED: <id> - <one-line summary>`
3. Don't block the review for out-of-scope issues

Control Tower reads the full task later. Keep your review focused on the acceptance criteria.
</escalation_boundaries>

<success_criteria>
Review is complete when:
- [ ] Each acceptance criterion verified with evidence
- [ ] Deliverable quality checked
- [ ] Worktree hygiene verified
- [ ] Findings documented in task comment (via `bd comment`)
- [ ] Summary returned to Control Tower with clear verdict
</success_criteria>
