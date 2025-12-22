---
name: authoring-skills
description: Create and refine reusable skills for Claude agents. Use when authoring skill documentation, designing new skills, structuring SKILL.md files, organizing supporting files, writing skill metadata, or implementing progressive disclosure patterns.
---

# Authoring Skills

Skills are modular packages that extend Claude's capabilities with specialized knowledge, workflows, and tool integrations. This skill guides the interactive design and implementation of effective skills following best practices.

## Skill Structure

Every skill has this anatomy:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description)
│   └── Markdown body (<500 lines)
└── Supporting files (optional)
    ├── REFERENCE.md - API docs, schemas
    ├── EXAMPLES.md - Concrete use cases
    ├── TROUBLESHOOTING.md - Edge cases, diagnostics
    ├── WORKFLOWS.md - Step-by-step procedures
    ├── scripts/ - Executable code
    └── assets/ - Templates, boilerplate
```

**Key principle**: SKILL.md is an overview; detailed content lives in supporting files loaded only when needed (progressive disclosure).

## Interactive Design Process

Work collaboratively with your human partner through these phases. Each phase involves discussion, clarification, and iteration.

### Phase 0: Inventory Search (Before Discovery)

Before starting skill design, check for existing implementations.

**Search the codebase:**
```bash
# Search for relevant functionality
grep -r "feature_keyword" . --include="*.py" --include="*.sh"

# Check existing CLI tools
inv --list  # or project-specific task runners

# Review existing skills
ls .claude/skills/
```

**After discovery conversation (Phase 1), verify the approach:**

Based on the use cases discussed, determine if this is:
- **Wrapping existing code**: Found implementation in codebase that needs documentation/skill interface
- **New implementation**: No existing code found, building from scratch

**Present findings to human partner:**
```
Based on inventory search, I found:
- [List files/commands found, or "No existing implementation"]

This appears to be a [wrapping/new implementation] skill because:
- [Reasoning based on findings]

Should we proceed with:
A) Wrapping the existing [tool/script/command]
B) Building a new implementation
C) Something else

Please confirm the approach before continuing.
```

**If wrapping existing code:** Focus on making it discoverable, adding usage guidance, and documenting edge cases rather than reimplementing.

### Phase 1: Discovery (Interactive)

When starting skill design, gather information through questions:

**Ask about concrete use cases:**
- "What specific problems should this skill solve?"
- "Can you provide example phrases that would trigger this skill?"
- "What context or inputs would you typically provide?"

**Example exchange:**
- Question: "What should the image-editor skill support?"
- Answer: "Editing, rotating, removing red-eye"
- Follow-up: "Can you give examples of how this would be used?"
- Answer: "'Remove the red-eye from this image' or 'Rotate this image 90 degrees'"

**Document the use cases** before proceeding to planning.

### Phase 2: Content Planning (Interactive)

Based on the use cases, propose reusable content structure:

**For each use case, identify:**
- **Scripts**: "This operation is deterministic. Propose: `scripts/rotate_pdf.py`"
- **References**: "This requires documentation. Propose: `REFERENCE.md`"
- **Examples**: "Multiple similar patterns exist. Propose: `EXAMPLES.md` with 5-10 scenarios"
- **Workflows**: "This is multi-step. Propose: `WORKFLOWS.md` with procedures"
- **Troubleshooting**: "Predictable edge cases exist. Propose: `TROUBLESHOOTING.md`"

**Decision Tree: Scripts vs Workflows**

Use this to decide when to create executable scripts vs document workflow steps:

**Create a Script when:**
- Operation is deterministic (same inputs → same outputs)
- Wraps external tools (glab, git, jq) with complex parsing/error handling
- Multiple workflows would call it repeatedly
- Error handling is complex and benefits from code
- Example: `scripts/fetch_mr_context.py` wraps glab CLI, parses JSON, handles auth errors

**Use Workflow steps when:**
- Operation is procedural and requires user decisions between steps
- Steps involve manual inspection or judgment calls
- Interactive CLI navigation needed
- User might need to adjust approach mid-process
- Example: WORKFLOWS.md "Manual Code Review Process" with inspection checkpoints

**For REFERENCE.md content:**
- Data skills: Table schemas, API fields, data types
- Operational skills: CLI command reference, output formats, environment variables
- Workflow skills: State machines, decision trees, architectural diagrams

**Present proposals** for human review and adjustment before creating files.

### Phase 3: Metadata Design (Collaborative)

Draft metadata and present for review.

**Skill naming:**

If human partner explicitly provides a name (e.g., "create a skill named xyz"), review it against best practices:
- Lowercase with hyphens only?
- Verb + "-ing" form (action-oriented)?
- Under 64 characters?
- No reserved words (anthropic, claude)?

If name doesn't follow best practices, suggest renaming:
```
The name "xyz" could be improved:
- Current: xyz-helper (noun-based)
- Suggested: managing-xyz (verb + -ing form, action-oriented)

Reason: Action-oriented names (verb + -ing) help users understand what the skill does at a glance.
```

If no explicit name provided, propose options based on use cases:
```
Based on the use cases, suggest these name options:

Option 1: processing-pdfs (verb + -ing form)
Option 2: managing-databases (verb + -ing form)
Option 3: analyzing-spreadsheets (verb + -ing form)

Which name best captures the skill's purpose?
```

**Naming requirements:**
- Lowercase, hyphens only
- Verb + "-ing" form preferred (action-oriented)
  - ✓ Good: `processing-pdfs`, `reviewing-merge-requests`, `managing-databases`
  - ✗ Avoid: `pdf-processor`, `merge-request-reviewer`, `database-manager`
- Under 64 characters
- No reserved words (anthropic, claude)

**Draft description with specific triggers:**
```yaml
description: Process Excel files, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Description must include:**
1. What the skill does (specific operations)
2. When to use it (concrete trigger phrases)
3. Third person voice
4. Under 1024 characters

**Present draft** to human partner for approval before creating SKILL.md.

### Phase 4: SKILL.md Implementation (Iterative)

Write SKILL.md body collaboratively. Structure:

1. **Purpose** (1-3 sentences)
2. **Quick start** (minimal working example)
3. **Key concepts** (domain knowledge not obvious to Claude)
4. **Reference guide** (links to supporting files)
5. **Safety rules** (NEVER rules if applicable)

**Keep under 500 lines.** Reference supporting files directly from SKILL.md (one level deep). When additional detail is needed, use Read tool to load the referenced file.

**Example reference section:**
```markdown
## Advanced techniques
See [WORKFLOWS.md](WORKFLOWS.md) for step-by-step procedures.
See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for edge cases.
See [EXAMPLES.md](EXAMPLES.md) for concrete use cases.
```

**Persuasion principles for discipline enforcement:**

When designing skills that enforce critical practices (TDD, verification, documentation), apply persuasion principles to resist rationalization under pressure. See [persuasion-principles.md](persuasion-principles.md) for detailed guidance.

**Quick reference:**
- **Authority**: "YOU MUST", "No exceptions" - for non-negotiable practices
- **Commitment**: Require announcements, explicit choices, TodoWrite tracking
- **Social proof**: "X without Y = failure. Every time." - establish norms
- **Unity**: "we're colleagues" - collaborative framing for asking behavior
- **Scarcity**: "IMMEDIATELY after X" - time-bound requirements

Use authority + commitment + social proof for discipline-enforcing skills. Avoid heavy authority for guidance/reference skills. See persuasion-principles.md for detailed psychology, research citations, and ethical considerations.

**Review checkpoint strategy:**

Infer from conversational context:
- **Clear goal evident**: Human provided detailed requirements, specific use cases, existing code to wrap → Assume confident approach (Option B: draft complete, review once)
- **Exploratory conversation**: Vague requirements, multiple possibilities discussed, domain unfamiliar → Assume incremental approach (Option A: review after each major section)
- **Uncertain**: Can't determine from context → Ask upfront

**If uncertain about approach, ask:**
```
I can work through SKILL.md implementation in two ways:

Option A (Incremental): Review after each major section (Purpose, Quick Start, Key Concepts, Reference Guide, Safety Rules)
- Pro: Ensures alignment at each step
- Con: 5+ review checkpoints

Option B (Complete Draft): Draft entire SKILL.md, then one consolidated review
- Pro: Faster, fewer interruptions
- Con: Larger revisions if approach needs adjustment

Based on our discussion, which approach would you prefer?
```

**During implementation:**
- Option A: After each major section, present draft and ask for review
- Option B: Complete full draft, then present entire SKILL.md for review

### Phase 5: Supporting Files (As Needed)

Create only files identified in Phase 2:

- **REFERENCE.md** (500-1000 lines): API docs, schemas, complete reference material. Add table of contents if >100 lines
- **EXAMPLES.md** (400-800 lines): 5-10 concrete before/after examples, decision trees
- **WORKFLOWS.md** (500-800 lines): 4-8 step-by-step procedures with explicit commands
- **TROUBLESHOOTING.md** (500-800 lines): Q&A organized by topic, diagnostic commands
- **scripts/** (as needed): Executable Python/Bash that solves deterministic problems
- **assets/** (as needed): Templates, boilerplate, resources for output

**For each file,** draft content and ask for review before finalizing.

## Recognize When Domain Expertise is Needed

During any phase, if these indicators appear, explicitly ask your human partner for domain expertise:

**Knowledge gaps that block progress:**
- [ ] Unclear what "deterministic" means for this specific use case
- [ ] Cannot articulate 3 realistic troubleshooting scenarios
- [ ] Uncertain what "key concepts" the domain requires
- [ ] Don't know if something should be a script or documented workflow
- [ ] Can't distinguish between edge cases and normal operation
- [ ] Unfamiliar with CLI tools, APIs, or systems being wrapped

**When gaps identified, ask directly:**
```
I've identified a knowledge gap that would affect skill quality:

[Describe the gap: e.g., "I'm unfamiliar with git worktree edge cases and can't anticipate what troubleshooting scenarios to document"]

Would you like to:
A) Provide guidance on [specific topic]
B) Pair with someone who has domain expertise
C) Document this as a TODO for later iteration

This ensures the skill provides accurate, complete guidance.
```

**Remember:** Weak domain expertise is acceptable if acknowledged. Creating incomplete guidance without awareness is not.

## Design Patterns

### Pattern 1: High-Level Overview with References

Use when skill covers multiple domains or has extensive reference material.

**Structure**:
- SKILL.md: Quick start + navigation to supporting files
- REFERENCE.md: Complete API/schema documentation
- EXAMPLES.md: Common patterns
- TROUBLESHOOTING.md: Edge cases

**Best for**: Large skills (BigQuery analysis, PDF processing, complex APIs)

### Pattern 2: Domain-Organized References

Use when skill has multiple independent domains.

**Structure**:
- SKILL.md: Overview + quick reference for each domain
- reference/finance.md, reference/sales.md, etc.

**Benefit**: Claude reads only domain-relevant files, saving context

### Pattern 3: Workflow-First Design

Use when skill is primarily procedural (multi-step workflows).

**Structure**:
- SKILL.md: Core concepts + reference to workflows
- WORKFLOWS.md: 4-8 complete procedures with decision trees
- EXAMPLES.md: Real scenarios matching each workflow

**Best for**: Git operations, testing procedures, deployment processes

### Pattern 4: Script-Driven Design

Use when skill wraps deterministic code that's reused.

**Structure**:
- SKILL.md: When to use each script + where to run
- scripts/: Executable utilities with error handling
- REFERENCE.md: Input/output formats, flags

**Best for**: PDF tools, data transformation, validation

## Critical Decisions

### Keep SKILL.md Under 500 Lines

Why? Once loaded, every line competes with conversation history. Split content into supporting files when approaching this limit. Use progressive disclosure: SKILL.md loads when triggered, other files load on-demand.

### Make Descriptions Specific

Generic: "Helps with documents"
Specific: "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when mentioning PDFs, forms, or document extraction."

The specific description helps Claude discover and select this skill.

### Use Action-Oriented Names (Verb + "-ing")

- ✓ Good: `processing-pdfs`, `analyzing-spreadsheets`, `managing-databases`
- ✗ Avoid: `pdf-processor`, `spreadsheet-analyzer`, `database-manager`

Action-oriented names (verb + "-ing" form) clearly describe what the skill does, making it immediately discoverable.

### Prefer Progressive Disclosure

Load only what's needed:

1. **Always in context**: Metadata (name + description)
2. **When triggered**: SKILL.md body
3. **On-demand**: Supporting files

This keeps token usage low and focused.

### Write in Imperative/Infinitive Form

- ✓ Good: "To accomplish X, do Y" or "Use pdfplumber for extraction"
- ✗ Avoid: "You should do X" or "If you need X, then..."

Imperative form maintains objectivity for AI consumption.

## Avoid Common Pitfalls

- **Too verbose**: Challenge each paragraph—does Claude really need this explanation?
- **Nested references**: Keep references one level deep from SKILL.md; don't reference from references
- **Time-sensitive content**: Use "old patterns" sections instead of dates
- **Inconsistent terminology**: Pick one term (e.g., "field" not "box/element/control") and use it throughout
- **Missing when-to-use triggers**: Description should help Claude decide when to activate the skill
- **Overly specific examples**: Use examples that generalize to similar problems
- **No error handling in scripts**: Scripts should solve problems, not punt to Claude
- **Magic constants**: Every configuration value should have a comment explaining why

## Feedback Loops

For complex workflows, include validation steps:

**Pattern**: Run validator → Fix errors → Repeat

Example:
```markdown
1. Create field mapping (edit fields.json)
2. Validate mapping: `python scripts/validate_fields.py fields.json`
3. If validation fails, review errors and fix fields.json
4. Rerun validation until it passes
5. Execute the main command
```

This catches errors early and prevents cascading failures.

## Next Steps After Initial Implementation

When the skill reaches a natural pause point, suggest next steps:

### Validation Checkpoint

**Suggest running validation:**
```
The skill implementation is complete. Recommended next steps:

1. Review metadata against checklist (see Metadata Validation Checklist below)
2. Verify SKILL.md is under 500 lines: [current line count]
3. Check all supporting files are referenced from SKILL.md
4. Confirm file organization follows chosen pattern

Would you like to proceed with validation, or continue refining the content?
```

### Testing Suggestions

**When ready for testing, propose:**
```
The skill is validation-ready. Suggested testing approach:

1. Test with a concrete use case: [suggest specific example from discovery phase]
2. Observe which files get loaded and when
3. Check if additional context or examples are needed
4. Verify references are clear and discoverable

Would you like to test now, or should I document this as a TODO for later?
```

### Iteration Opportunities

**If the conversation continues after initial implementation:**
```
Current skill status: [summarize what's complete]

Potential improvements identified:
- [List any gaps or areas mentioned during implementation]
- [Suggest additional examples if use cases expanded]
- [Propose troubleshooting entries if edge cases discussed]

Should we address any of these now, or mark them for future iteration?
```

### Integration Checklist

**When approaching session end, offer:**
```
Skill implementation complete. Final integration steps:

- [ ] Add skill to settings.local.json (if project-specific)
- [ ] Document in team wiki/docs (if team-wide)
- [ ] Create work log entry (if tracking skill development)
- [ ] Test with real task before next session

Would you like help with any of these steps?
```

## Metadata Validation Checklist

Before finalizing, verify:

- [ ] **Name**: Lowercase, hyphens, gerund form, <64 chars, no reserved words
- [ ] **Description**: Specific, includes "when to use", third person, <1024 chars
- [ ] **SKILL.md**: Under 500 lines, clear purpose, references supporting files
- [ ] **Supporting files**: Only created when truly needed, well-organized
- [ ] **File paths**: All forward slashes, descriptive names
- [ ] **References**: One level deep from SKILL.md (no nested references)
- [ ] **Examples**: Concrete, not abstract; show real scenarios
- [ ] **Scripts**: Error handling, no magic constants, clear documentation
- [ ] **Terminology**: Consistent throughout all files
- [ ] **Third person**: All instructions objective/imperative, not "you"

## Supporting Resources

This skill's supporting files (use Read tool to load as needed):

- **[BEST-PRACTICES.md](BEST-PRACTICES.md)** - Official Anthropic best practices documentation (comprehensive reference, 1174 lines)
- **[PATTERNS.md](PATTERNS.md)** - Detailed architectural patterns and file organization strategies
- **[EXAMPLES.md](EXAMPLES.md)** - Four complete skill authoring scenarios with before/after code
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common authoring issues, diagnostics, and solutions
- **[persuasion-principles.md](persuasion-principles.md)** - Psychology of persuasion for discipline-enforcing skills (research-backed guidance on authority, commitment, social proof, unity, scarcity)

When authoring a skill, reference BEST-PRACTICES.md as the authoritative source. This SKILL.md provides quick guidance; BEST-PRACTICES.md contains complete specifications. For discipline-enforcing skills (TDD, verification, documentation), consult persuasion-principles.md to design language that resists rationalization under pressure.
