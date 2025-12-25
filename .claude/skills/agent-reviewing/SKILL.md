---
name: agent-reviewing
description: Review agent for first-gate verification of completed work. Use when assigned as reviewer for a task in 'review' status. Operates in worktree, documents findings as task comment, returns summary for CT escalation decision.
---

<objective>
Systematically verify completed agent work before escalation to Mark. You are the first gate in a two-gate review—catch mechanical issues (missing criteria, obvious bugs, hygiene problems) so Mark's review focuses on judgment calls.

Your findings go in a task **comment** (not notes—that's the agent's work record). Control Tower sees only your summary and decides whether to escalate or request changes.
</objective>

<quick_start>
You are reviewing task `<id>` in worktree `worktrees/<id>`.

1. Enter worktree: `cd worktrees/<id> && pwd`
2. Load task context (note the jq pattern—bd show returns an array):
   ```bash
   bd show <id> --json | jq '.[0] | {acceptance_criteria, notes, design}'
   ```
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
**1. Enter Worktree**

```bash
cd worktrees/<id> && pwd
```

All subsequent git commands run in this directory—no `-C` flags needed.

**2. Load Task Context**

```bash
bd show <id> --json | jq '.[0] | {acceptance_criteria, notes, design}'
```

**Important:** `bd show` returns an array. Use `.[0]` to access the task object, then select specific fields. Without this, jq errors on `Cannot index array with string`.

Extract:
- `acceptance_criteria` — What success looks like
- `notes` — Agent's COMPLETED/CRITERIA sections
- `design` — Intended approach

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

NEXT: [If changes needed, what specifically]" -a "code-reviewer" --json
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

**When uncertain:** Document the uncertainty in notes and let Control Tower decide. "Criterion X technically met but implementation seems fragile" is useful information.
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

<success_criteria>
Review is complete when:
- [ ] Each acceptance criterion verified with evidence
- [ ] Deliverable quality checked
- [ ] Worktree hygiene verified
- [ ] Findings documented in task comment (via `bd comment`)
- [ ] Summary returned to Control Tower with clear verdict
</success_criteria>
