---
name: creating-vault-documentation
description: Persist research findings, design notes, or technical documentation to Mark's vault during task execution. Use when agents discover insights, make design decisions, or need to document findings for future reference.
---

<objective>
Agents working on tasks often discover insights, design decisions, or research findings that should be preserved for future reference. This skill guides agents in creating properly formatted vault notes in Mark's vault at `/home/phate/Documents/second-brain/01_Projects/spacetraders/`.

These notes differ from work logs (which use `/writing-work-logs`) and project documentation files (which live in the project working directory). Vault notes capture conversational research, design explorations, and technical decision records.
</objective>

<quick_start>
Create a vault note with minimal YAML frontmatter:

```bash
# Get current timestamp from system reminders
# Example: Temporal grounding: Tuesday, 2025-12-24 14:32:18

Write(
  file_path="/home/phate/Documents/second-brain/01_Projects/spacetraders/Note Name.md",
  content="---
created: 2025-12-24T14:32:18
modified: 2025-12-24T14:32:18
---

# Note Name

[content]"
)
```

Report back to the user what you created and where it's located.
</quick_start>

<when_to_create_vault_notes>
Create vault notes when you discover:

**Research findings:**
- API behavior patterns discovered during implementation
- Performance characteristics measured during testing
- Third-party library capabilities and limitations
- Integration patterns that work or don't work

**Design decisions:**
- Architectural choices made during task execution
- Trade-offs evaluated and rationale for selection
- Alternative approaches considered and rejected
- Technical constraints discovered

**Technical documentation:**
- How subsystems interact
- Data flow patterns
- Configuration requirements
- Deployment considerations

**Do NOT create vault notes for:**
- Work session logs (use `/writing-work-logs` instead)
- Project documentation (README, CONTRIBUTING, etc. - those belong in working directory)
- TODO lists or task tracking (use beads for that)
- Trivial findings that don't warrant persistence
</when_to_create_vault_notes>

<vault_location_rules>
**Vault directory:** `/home/phate/Documents/second-brain/01_Projects/spacetraders/`

**File placement:**
- Root level: Most documentation notes
- `logs/`: Work session logs only (use `/writing-work-logs`)
- Subdirectories: Create only if organizing related notes (e.g., `architecture/`, `research/`)

**File naming:**
- Descriptive, clear names
- Use spaces in names: `API Design Decisions.md`
- Capital case for major words: `Architecture Notes.md`
- Examples: `Performance Optimization Research.md`, `Token Lifecycle Design.md`
</vault_location_rules>

<frontmatter_requirements>
**Required YAML fields:**
```yaml
---
created: 2025-12-24T14:32:18
modified: 2025-12-24T14:32:18
---
```

**Critical rules:**
- Use actual timestamps from system reminders (format: `Temporal grounding: <day>, <date> <time>`)
- NEVER use placeholder times like `00:00:00`
- Only `created` and `modified` fields required
- Update `modified` timestamp when editing existing notes
- ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`

**Getting the timestamp:**
Current timestamp is available in system reminders from the UserPromptSubmit hook. Look for:
```
Temporal grounding: Tuesday, 2025-12-24 14:32:18
```

Convert to ISO 8601: `2025-12-24T14:32:18`
</frontmatter_requirements>

<linking_conventions>
**WikiLinks for vault notes:**
```markdown
See [[Architecture Notes]] for system design details.
Reference [[API Design Decisions]] for endpoint patterns.
```

**Standard markdown links for project files:**
```markdown
Implementation in [src/api/client.rs](/home/phate/BigProjects/spacetraders/src/api/client.rs)
Configuration example in [config.toml](../../config.toml)
```

**When to use which:**
- `[[WikiLinks]]` - References to other vault notes
- `[Standard](links)` - References to project source files, documentation, external URLs
</linking_conventions>

<content_guidelines>
**Write for future Mark:**
- Provide context and reasoning, not just facts
- Explain why decisions were made
- Document trade-offs considered
- Include enough detail to reconstruct your thinking

**Structure suggestions:**
```markdown
# Note Title

## Context
What prompted this research/decision?

## Findings
What did you discover/decide?

## Rationale
Why this approach over alternatives?

## Implementation Notes
Specific details, gotchas, configuration
```

**Use markdown freely:**
- Headings for structure
- Bold for emphasis
- Lists for clarity
- Code blocks for examples
- Tables for comparisons
</content_guidelines>

<workflow>
**Step 1: Decide if findings warrant persistence**

Ask yourself:
- Will this be useful in future sessions?
- Does this document a design decision?
- Did I discover non-obvious behavior?
- Would future Mark want to know this?

If no, document in commit message or work log instead.

**Step 2: Choose appropriate note type**

- Research findings → `[Topic] Research.md`
- Design decisions → `[Feature] Design.md` or `[Topic] Design Decisions.md`
- Architecture → `Architecture Notes.md` or `[Subsystem] Architecture.md`
- Technical → `[Topic] Technical Notes.md`

**Step 3: Get current timestamp**

Extract from system reminders:
```
Temporal grounding: Tuesday, 2025-12-24 14:32:18
```

Convert to ISO 8601: `2025-12-24T14:32:18`

**Step 4: Create note with Write tool**

Use minimal frontmatter and descriptive content:

```bash
Write(
  file_path="/home/phate/Documents/second-brain/01_Projects/spacetraders/[Note Name].md",
  content="---
created: 2025-12-24T14:32:18
modified: 2025-12-24T14:32:18
---

# Note Name

[Your content here]
"
)
```

**Step 5: Report back**

Tell the user:
- What you created
- Where it's located
- Brief summary of what it contains
</workflow>

<updating_existing_notes>
If adding to an existing vault note:

1. **Read the note first** using Read tool
2. **Preserve existing frontmatter** but update `modified` timestamp
3. **Add your content** in appropriate location
4. **Write back** using Write tool (overwrites entire file)

Example:
```bash
# Read existing note
Read(file_path="/home/phate/Documents/second-brain/01_Projects/spacetraders/Architecture Notes.md")

# Update with new timestamp and additional content
Write(
  file_path="/home/phate/Documents/second-brain/01_Projects/spacetraders/Architecture Notes.md",
  content="---
created: 2025-11-01T09:15:22
modified: 2025-12-24T14:32:18
---

[Existing content preserved]

## New Section
[Your new content]
"
)
```
</updating_existing_notes>

<anti_patterns>
**Placeholder timestamps:**
- ❌ `created: 2025-01-01T00:00:00`
- ✅ `created: 2025-12-24T14:32:18` (actual timestamp from system reminders)

**Vague file names:**
- ❌ `notes.md`, `temp.md`, `research.md`
- ✅ `Token Lifecycle Research.md`, `API Client Design Decisions.md`

**Writing to project directory:**
- ❌ `/home/phate/BigProjects/spacetraders/notes/research.md`
- ✅ `/home/phate/Documents/second-brain/01_Projects/spacetraders/Research Notes.md`

**Creating work logs here:**
- ❌ Using this skill for work session documentation
- ✅ Use `/writing-work-logs` for session documentation

**Minimal content:**
- ❌ "Implemented feature X. Works now."
- ✅ "Implemented feature X using approach Y because Z constraint. Considered approaches A and B but rejected due to..."

**Wrong linking format:**
- ❌ `See Architecture Notes.md` (no link)
- ❌ `See [Architecture Notes.md](Architecture Notes.md)` (standard link for vault note)
- ✅ `See [[Architecture Notes]]` (WikiLink for vault note)
</anti_patterns>

<success_criteria>
Vault note is properly created when:

- File location: `/home/phate/Documents/second-brain/01_Projects/spacetraders/[Note Name].md`
- YAML frontmatter: Minimal (only `created` and `modified` fields)
- Timestamps: Actual timestamps from system reminders (no `00:00:00` placeholders)
- File name: Descriptive and clear
- Content: Provides context, reasoning, and sufficient detail
- Links: WikiLinks for vault notes, standard markdown for project files
- User notification: Reported what was created and where
</success_criteria>
