---
name: writing-work-logs
description: Write work session logs for the vault. Use when documenting completed work, at session end, or when Mark asks to log work.
---

# Writing Work Logs

Control Tower responsibility: synthesize task-level work into coherent session narratives.

## Location

Work logs live in Mark's vault:

```
/home/phate/Documents/second-brain/01_Projects/spacetraders/logs/YYYY-MM-DD.md
```

## Before Writing

**Invoke the technical-writing skill FIRST:**

```
/technical-writing
```

This ensures active voice, concrete language, and elimination of weak verbs.

## File Format

```markdown
---
created: 2025-12-22T14:30:00
modified: 2025-12-22T14:30:00
---

## [Topic/Theme]

Opening narrative paragraph explaining what was accomplished and why.

**Subsection Header:**
- Specific implementation detail
- Another concrete point
- Reasoning or context

**Another Subsection:**
- More details
- Technical decisions made

---

## [Another Topic]

[Next work block...]
```

## Writing Guidelines

### Do

- Use `## [Topic]` headings for each work block
- Write opening narrative explaining the "why"
- Use **bold subsection headers** for aspects
- Include specific, concrete details
- Explain reasoning and tradeoffs
- Use active voice throughout

### Avoid

- Passive voice ("was updated", "has been changed")
- Vague terms ("improved", "worked on", "fixed some issues")
- Minimal summaries without context
- File-change lists without narrative

## Synthesis Process

Agents write task-level comments in beads issues. Control Tower:

1. Reviews completed tasks and their comments
2. Identifies themes and related work
3. Synthesizes into coherent narrative blocks
4. Writes for "future Mark who won't remember context"

## Example

**Bad (file-change list):**
```
- Updated CLAUDE.md
- Created 3 skills
- Deleted AGENTS.md
```

**Good (narrative with context):**
```markdown
## Documentation Progressive Disclosure Refactor

Restructured agent documentation to use progressive disclosure pattern. Context-triggered knowledge moved from always-loaded CLAUDE.md into skills that activate when needed.

**Skills Created:**
- `creating-tasks` - Good description patterns, proper flags
- `landing-the-plane` - Session-end protocol with anti-patterns
- `writing-work-logs` - This meta-skill for Control Tower

**Rationale:**
Agents don't need landing protocol in context during implementation work. Loading it only at session end reduces token overhead and keeps focus on current task.

**Doc Changes:**
- CLAUDE.md absorbed bd quick reference from deleted AGENTS.md
- AGENTS.md removed (content distributed to skills)
```

## Timestamps

Get current timestamp from system reminder (UserPromptSubmit hook):
```
Temporal grounding: Monday, 2025-12-22 14:30:00
```

Use actual timestamps, never placeholders like `00:00:00`.
