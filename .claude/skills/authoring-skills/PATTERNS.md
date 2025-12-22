# Skill Architecture Patterns

This document provides detailed patterns for organizing skill content based on complexity and domain.

## Table of Contents

- Simple Skills
- Tiered Reference Pattern
- Domain-Organized Pattern
- Workflow-First Pattern
- Script-Driven Pattern
- Hybrid Patterns

---

## Simple Skills

**When to use**: Skill solves a single, straightforward task with minimal supporting information.

**Structure**:
```
skill-name/
├── SKILL.md (complete, 50-200 lines)
└── (optional) assets/
```

**Example**: A skill that teaches Claude how to use a specific tool or API.

**SKILL.md organization**:
1. What does this skill do? (1-2 sentences)
2. Quick example
3. Common parameters/options
4. When to use vs when not to use

**File count**: 1-2 files. Everything fits in SKILL.md.

---

## Tiered Reference Pattern

**When to use**: Skill has extensive reference material (schemas, APIs, documentation) that Claude should reference contextually.

**Structure**:
```
skill-name/
├── SKILL.md (entry point, 150-300 lines)
├── REFERENCE.md (comprehensive reference, 500-1500 lines)
├── EXAMPLES.md (5-10 concrete scenarios)
└── TROUBLESHOOTING.md (edge cases, diagnostics)
```

**SKILL.md content**:
- Purpose statement
- When to use this skill
- Quick reference (most common operations)
- Links to REFERENCE.md sections for detailed docs

**REFERENCE.md content**:
- Complete API documentation
- All available methods/functions
- Parameter descriptions
- Return values
- Complete table of contents for navigation

**EXAMPLES.md content**:
- 5-10 real-world scenarios
- Before/after transformations
- Decision trees for choosing approaches

**TROUBLESHOOTING.md content**:
- Common errors and solutions
- Edge cases and how to handle them
- Diagnostic commands to debug issues

**Loading behavior**: Claude reads SKILL.md initially, then loads REFERENCE.md, EXAMPLES.md, or TROUBLESHOOTING.md based on the task.

**Example skills**: PDF processing, BigQuery analysis, database operations

---

## Domain-Organized Pattern

**When to use**: Skill spans multiple independent domains; you want Claude to load only domain-relevant information.

**Structure**:
```
skill-name/
├── SKILL.md (navigation, 100-200 lines)
└── reference/
    ├── domain1.md (finance.md)
    ├── domain2.md (sales.md)
    └── domain3.md (product.md)
```

**SKILL.md content**:
- Overview of all domains
- When to use each domain
- Quick reference for each
- Domain organization diagram or table

**reference/domain*.md content**:
- Schemas specific to that domain
- Terminology and definitions
- Common queries/operations
- Examples for that domain

**Loading behavior**: Claude reads SKILL.md, then loads only `reference/finance.md` if asking about revenue, or `reference/sales.md` if asking about pipeline. Unused domain files never consume context.

**Token efficiency**: Scales to 10+ domains without bloating SKILL.md or consuming unnecessary context.

**Example skills**: BigQuery with finance/sales/product/marketing domains, CRM system with multiple entity types

---

## Workflow-First Pattern

**When to use**: Skill is primarily procedural; users follow step-by-step workflows with decision points.

**Structure**:
```
skill-name/
├── SKILL.md (core concepts + workflow overview, 200-300 lines)
├── WORKFLOWS.md (4-8 step-by-step procedures, 500-1000 lines)
├── EXAMPLES.md (real scenarios for each workflow)
└── TROUBLESHOOTING.md (common execution issues)
```

**SKILL.md content**:
- Core concepts and terminology
- When to use each workflow
- Workflow selection guide (decision tree)
- Links to WORKFLOWS.md

**WORKFLOWS.md content**:
- 4-8 complete, self-contained procedures
- Each workflow: 15-30 steps
- Explicit commands with output expectations
- Inline validation steps
- Feedback loops for error correction

**EXAMPLES.md content**:
- Real-world scenario for each workflow
- Full walkthrough with actual inputs/outputs
- Common decision points explained

**Structure pattern for each workflow**:
```markdown
## Workflow: [Name]

**When to use**: [Description of when this workflow applies]

**Estimated time**: [Time estimate]

1. **Step 1**: [Action] (verify with `command`)
2. **Step 2**: [Action] (verify with `command`)
...
N. **Step N**: [Final verification]
```

**Validation integration**: Each workflow includes inline checks:
```markdown
3. Run validation: `scripts/validate.sh input.json`
   - If validation passes → Continue to step 4
   - If validation fails → Review the error message and fix the input, then re-run validation
```

**Example skills**: Git workflows (committing, branching, rebasing), deployment procedures, testing strategies

---

## Script-Driven Pattern

**When to use**: Skill wraps deterministic code that's reused repeatedly (not generated fresh each time).

**Structure**:
```
skill-name/
├── SKILL.md (when to use each script, 150-250 lines)
├── REFERENCE.md (input/output formats, flags, examples)
├── scripts/
│   ├── operation1.py
│   ├── operation2.py
│   └── utility.py
└── assets/
    ├── config.json (template configuration)
    └── sample-input.json (example inputs)
```

**SKILL.md content**:
- Purpose: "When would I run each script?"
- Quick reference table: Script → Use case
- Each script: What it does, when to run it, required inputs
- Safe execution pattern (validation before execution)

**REFERENCE.md content**:
- Complete documentation for each script
- Input format specifications
- Output format specifications
- Configuration options
- Error codes and what they mean

**scripts/ content**:
- Each script solves ONE well-defined problem
- Error handling for common failure modes
- Comments explaining non-obvious logic
- Configuration via files, not magic constants
- Exit codes indicating success/failure

**assets/ content**:
- Template configuration files
- Sample inputs showing expected format
- Configuration examples for common scenarios

**Execution pattern**:
```markdown
1. Prepare input file (see [REFERENCE.md](REFERENCE.md) for format)
2. Optionally validate before running: `python scripts/validate_input.py input.json`
3. Run operation: `python scripts/transform_data.py input.json output.json`
4. Verify output: `python scripts/verify_output.py output.json`
```

**Error handling in scripts**:
```python
try:
    # Main operation
except SpecificError as e:
    print(f"Error: {e}")
    print("Suggestion: Check that input file has required fields")
    sys.exit(1)
```

**Example skills**: PDF tools, data transformation, validation utilities

---

## Hybrid Patterns

Real-world skills often combine patterns. Design based on actual content needs.

### Workflow + Script Pattern

Workflows that execute scripts. Most common hybrid.

```
skill-name/
├── SKILL.md (when to use)
├── WORKFLOWS.md (procedures that call scripts)
├── REFERENCE.md (script documentation)
├── scripts/ (utilities executed by workflows)
└── TROUBLESHOOTING.md (debugging procedures)
```

**Example**: Git workflow skill (WORKFLOWS.md describes commit procedure, scripts handle safety checks)

### Domain + Script Pattern

Multiple domains, each with associated scripts.

```
skill-name/
├── SKILL.md (navigation)
├── reference/
│   ├── finance.md
│   └── sales.md
├── scripts/
│   ├── finance_queries.sql
│   └── sales_queries.sql
└── assets/
    ├── finance_config.json
    └── sales_config.json
```

**Example**: BigQuery skill with domain-specific queries and configurations

### Full-Featured Pattern

Combines all patterns for comprehensive skills.

```
skill-name/
├── SKILL.md (entry point)
├── WORKFLOWS.md (procedures)
├── REFERENCE.md (complete docs)
├── EXAMPLES.md (scenarios)
├── TROUBLESHOOTING.md (debugging)
├── scripts/ (utilities)
└── assets/ (templates)
```

Only use this when the skill truly needs all components. Simpler is usually better.

---

## Decision Framework: Which Pattern?

Use this flowchart to select the right pattern:

```
1. Is this a single, simple task?
   YES → Simple Skills pattern
   NO → Continue

2. Does it have multiple independent domains?
   YES → Domain-Organized pattern (reference/)
   NO → Continue

3. Is it primarily procedural (step-by-step workflows)?
   YES → Workflow-First pattern (WORKFLOWS.md)
   NO → Continue

4. Does it wrap deterministic, reused code?
   YES → Script-Driven pattern (scripts/)
   NO → Continue

5. Does it have extensive reference material?
   YES → Tiered Reference pattern (REFERENCE.md)
   NO → Use Simple Skills or minimal supporting files
```

---

## File Naming Conventions

**Standard files** (predictable locations):
- `SKILL.md` - Main entry point
- `REFERENCE.md` - Complete reference material
- `EXAMPLES.md` - Concrete use cases
- `WORKFLOWS.md` - Step-by-step procedures
- `TROUBLESHOOTING.md` - Edge cases and debugging
- `PATTERNS.md` - Architecture patterns (like this file)

**Directory conventions**:
- `scripts/` - Executable code (Python, Bash, etc.)
- `reference/` - Domain-specific references
- `assets/` - Output resources (templates, boilerplate)

**Rationale**: Consistent naming makes skills discoverable and predictable. Claude recognizes these names and knows where to find information.

---

## Progressive Disclosure in Action

How Claude loads content as the conversation progresses:

**Startup**: Metadata loaded
```
authoring-skills: "Create and refine reusable skills..."
```

**User triggers skill**: SKILL.md loaded (e.g., "Help me design a new skill")
```
SKILL.md: Full body (~500 lines, ~3000 tokens)
```

**User asks about edge case**: TROUBLESHOOTING.md loaded on-demand
```
TROUBLESHOOTING.md: Only loaded when user asks about errors/edge cases
```

**User asks about structure**: PATTERNS.md loaded on-demand
```
PATTERNS.md: Only loaded when user asks about architecture
```

**Total context at any moment**: Metadata + SKILL.md + (0-N supporting files currently needed)

This is why progressive disclosure matters: each file loads independently, keeping context focused.
