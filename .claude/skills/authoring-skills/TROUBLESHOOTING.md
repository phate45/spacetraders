# Skill Authoring Troubleshooting

Common challenges when authoring skills and how to address them.

## Table of Contents

- SKILL.md Issues
- Supporting Files Issues
- Discovery & Activation Issues
- Design Problems
- When to Escalate

---

## SKILL.md Issues

### Problem: SKILL.md Exceeds 500 Lines

**Symptom**: Created comprehensive SKILL.md, but it's 800+ lines. Feels bloated but hard to split.

**Root cause**: Too much detail in the entry point. Supporting files aren't being used effectively.

**Solution**:

1. **Identify what can move**:
   - Detailed API documentation → REFERENCE.md
   - Multiple examples → EXAMPLES.md
   - Step-by-step procedures → WORKFLOWS.md
   - Common problems → TROUBLESHOOTING.md

2. **Keep in SKILL.md**:
   - Purpose (2-3 sentences)
   - Quick start (1-2 minimal examples)
   - Core concepts only Claude might not have
   - Navigation to supporting files

3. **Example refactoring**:

   Before: 800 lines of everything
   ```markdown
   # PDF Processing
   [Detailed API docs: 300 lines]
   [10 examples: 200 lines]
   [Error handling guide: 150 lines]
   [Workflows: 150 lines]
   ```

   After: 200 lines with references
   ```markdown
   # PDF Processing

   [Purpose: 5 lines]
   [Quick start: 30 lines]

   For complete documentation, see:
   - [REFERENCE.md](REFERENCE.md) - API documentation
   - [EXAMPLES.md](EXAMPLES.md) - Real-world scenarios
   - [WORKFLOWS.md](WORKFLOWS.md) - Step-by-step procedures
   ```

**Verification**: If SKILL.md > 500 lines, split into supporting files. Aim for 150-300 lines for SKILL.md body.

---

### Problem: Description Too Vague

**Symptom**: Description is "Helps with documents" or "Processes data". Claude doesn't select the skill when it should.

**Root cause**: Description doesn't include "when to use" triggers. Missing specificity.

**Bad examples**:
- "Helps with documents"
- "Processes data"
- "Does stuff with files"
- "Provides utilities"

**Good examples**:
- "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when mentioning PDFs, forms, or document extraction."
- "Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files."

**Solution**:

Rewrite description with this template:

```
<What does it do>. Use when <specific triggers>.
```

**What does it do**:
- Be specific about operations
- Name the tool/domain
- List primary use cases

**Use when**:
- Concrete trigger phrases
- File types or extensions mentioned
- Specific domains or industries
- Common user questions

**Before**:
```yaml
description: Database utility
```

**After**:
```yaml
description: Query and analyze databases with SQL, create reports, export data. Use when working with databases, writing SQL queries, or analyzing database performance.
```

**Verification**: Ask: "Would Claude know to use this skill when the user mentions [X]?" If not, add more specific triggers.

---

## Supporting Files Issues

### Problem: Too Many Supporting Files

**Symptom**: Created 8 supporting files (REFERENCE.md, EXAMPLES.md, PATTERNS.md, TROUBLESHOOTING.md, WORKFLOWS.md, FAQ.md, CHEATSHEET.md, ADVANCED.md). Feels unmaintainable.

**Root cause**: Over-engineering. Adding files for theoretical use cases, not actual needs.

**Solution**:

Create only files that answer real questions:

1. **REFERENCE.md**: "Where's the complete documentation?"
2. **EXAMPLES.md**: "Show me real scenarios"
3. **WORKFLOWS.md**: "What's the step-by-step process?"
4. **TROUBLESHOOTING.md**: "What if something breaks?"

**Only add** if you have actual content:
- Don't create PATTERNS.md unless explaining multiple patterns
- Don't create FAQ.md unless you have real questions
- Don't create CHEATSHEET.md unless it's genuinely different from REFERENCE.md

**Verification**: Can you describe what's in each file? Can you fill it with 200+ lines of real content? If not, merge it into another file or don't create it.

---

### Problem: Nested References (File References Other Files)

**Symptom**: SKILL.md → WORKFLOWS.md → REFERENCE.md chain. Claude partially reads files, missing information.

**Root cause**: References go more than one level deep. Claude previews deeply nested files instead of reading completely.

**Bad structure**:
```
SKILL.md → WORKFLOWS.md → REFERENCE.md (three levels)
SKILL.md → ADVANCED.md → EDGE_CASES.md (three levels)
```

**Good structure**:
```
SKILL.md
├── WORKFLOWS.md (linked from SKILL.md)
├── REFERENCE.md (linked from SKILL.md)
├── EXAMPLES.md (linked from SKILL.md)
└── TROUBLESHOOTING.md (linked from SKILL.md)
```

**Solution**:

All references should be one level deep from SKILL.md:

1. **In SKILL.md**, link directly to supporting files:
   ```markdown
   See [WORKFLOWS.md](WORKFLOWS.md) for procedures.
   See [REFERENCE.md](REFERENCE.md) for documentation.
   ```

2. **In supporting files**, don't reference other supporting files:
   - WORKFLOWS.md should not say "See REFERENCE.md"
   - Include necessary content directly
   - Or organize as subheadings within one file

3. **Exception**: Domain-organized structure is okay:
   ```
   SKILL.md → reference/finance.md (same level)
   SKILL.md → reference/sales.md (same level)
   ```

**Verification**: Check all markdown links. Do they point to SKILL.md-level files? Any links from supporting files to other supporting files?

---

### Problem: File Organization Confusing

**Symptom**: Not sure whether to put content in REFERENCE.md or WORKFLOWS.md or EXAMPLES.md. Multiple files cover similar material.

**Root cause**: Unclear purpose for each file. Overlap in content.

**Solution**:

Use this decision tree:

```
Is this "how to do X" (step-by-step procedure)?
  YES → WORKFLOWS.md
  NO → Continue

Is this "what is X" (definitions, schemas, documentation)?
  YES → REFERENCE.md
  NO → Continue

Is this "example of X in practice" (before/after, real scenarios)?
  YES → EXAMPLES.md
  NO → Continue

Is this "what if X goes wrong" (errors, edge cases)?
  YES → TROUBLESHOOTING.md
  NO → Don't create a file; keep in SKILL.md
```

**Organization cheat sheet**:

| File | Contains | Purpose |
|------|----------|---------|
| SKILL.md | Purpose, quick start, navigation | Entry point |
| REFERENCE.md | Schemas, APIs, complete docs, parameter lists | Look something up |
| EXAMPLES.md | Before/after, real scenarios, decision trees | Learn by example |
| WORKFLOWS.md | Step-by-step procedures, numbered steps | Follow a process |
| TROUBLESHOOTING.md | Errors, edge cases, diagnosis | Debug a problem |

**Verification**: Each file has a single primary purpose? Content doesn't duplicate across files?

---

## Discovery & Activation Issues

### Problem: Skill Never Gets Used

**Symptom**: Created a skill, but Claude never activates it even when it should.

**Root causes**:
1. Description doesn't match user's language
2. Name doesn't make the skill discoverable
3. SKILL.md doesn't make purpose clear enough

**Solution**:

1. **Analyze the description**:
   - Does it match how users phrase problems?
   - Does it include specific triggers?
   - Is it too generic?

2. **Check the name**:
   - Gerund form? (processing-pdfs, not pdf-processor)
   - Lowercase and hyphens only?
   - Descriptive? (not just "helpers" or "utils")

3. **Review SKILL.md opening**:
   - Is the purpose immediately clear?
   - Would Claude know this solves the user's problem?

**Example diagnosis**:

**Problem**: User says "Help me with my database queries" but database-query-helper skill never activates.

**Diagnosis**:
- Description: "Query helper" (too vague, no triggers)
- Name: database-query-helper (weak, no specific domain)
- First sentence: "Helper for queries" (unclear purpose)

**Fix**:
- Description: "Query PostgreSQL databases, analyze schemas, generate reports. Use when writing SQL queries, analyzing database performance, or debugging query issues."
- Name: querying-databases (better, clearer action)
- First sentence: "Execute SQL queries against PostgreSQL databases."

**Verification**: After adjustments, test with real user phrase. Does Claude activate the skill?

---

### Problem: Skill Activates Too Broadly

**Symptom**: Skill activates for tangentially related tasks. Gets in the way.

**Root cause**: Description is too broad. Triggers are too generic.

**Solution**:

Make description more specific:

**Too broad**:
```yaml
description: Process files and data. Use when working with files or processing data.
```

**More specific**:
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when mentioning PDFs, forms, or document extraction.
```

**Verification**: Would this description accidentally trigger for unrelated tasks? Narrow it down if yes.

---

## Design Problems

### Problem: Skill Does Too Much

**Symptom**: One skill handles PDFs, images, and Word documents. It's unwieldy.

**Root cause**: Tried to solve all document problems in one skill.

**Solution**:

Split into focused skills:

**Before**:
```
document-processing/
  SKILL.md (tries to cover PDF, images, Word)
```

**After**:
```
processing-pdfs/
  SKILL.md (PDFs only)

processing-images/
  SKILL.md (images only)

processing-documents/
  SKILL.md (Word docs only)
```

Benefits:
- Each skill stays focused
- Descriptions are more specific
- SKILL.md files are smaller
- Less context bloat

**Rule**: If "when to use" varies by document type, split into separate skills.

---

### Problem: Skill Details Change Constantly

**Symptom**: Created skill for tool/API that changes frequently. Now maintenance is a nightmare.

**Root cause**: Embedded details that shouldn't be in the skill. Need a source of truth elsewhere.

**Solution**:

Move frequently-changing content outside the skill:

**Before**:
```
api-wrapper/
  SKILL.md (hardcoded endpoint URLs, auth tokens, API versions)
```

**After**:
```
api-wrapper/
  SKILL.md (how to use the API, references config file)
  assets/config.json (API endpoints, versions - updated separately)
```

Or reference external documentation:

```
reference-github-api/
  SKILL.md (points to github.com/api/docs for specific endpoints)
  REFERENCE.md (local copy of stable parts; notes which parts change)
```

**Principle**: Embed stable knowledge; reference or externalize changing details.

---

## When to Escalate

### Strange Claude Behavior

**Symptoms that might need revision**:
- Claude reads files in unexpected order
- Claude misses references you included
- Claude forgets instructions when reading supporting files
- Claude makes the same mistake repeatedly despite documentation

**Diagnostics**:

1. **Check file organization**:
   - Are there nested references (file → file → file)?
   - Are file sizes reasonable (<2000 lines)?

2. **Check SKILL.md entry point**:
   - Is it clear what the skill does?
   - Are supporting file references prominent?

3. **Check descriptions**:
   - Are triggers specific enough?
   - Is the purpose immediately clear?

4. **Test with simple task**:
   - Use the skill on a trivial version of the task
   - Observe what files Claude reads
   - Does it follow the expected path?

5. **Consider recursive skill usage**:
   - Does this skill reference another skill?
   - Are there skill dependencies that might confuse Claude?

### Iteration Needed

**Signs that skill needs refinement**:
- Claude solves the problem but inefficiently
- Claude reads many files when one would suffice
- Claude misinterprets instructions
- Multiple people ask "How do I use this skill?"

**Action**:
1. Document what went wrong
2. Identify the gap in the skill (description? SKILL.md content? supporting files?)
3. Make minimal change to address it
4. Test again

**Example**:
- Problem: "Claude rotates PDFs but forgets to validate output"
- Gap: WORKFLOWS.md doesn't have validation step
- Fix: Add verification step to workflow
- Test: Try rotation again, observe if validation happens

---

## Quick Diagnostic Checklist

Running into issues? Use this checklist:

- [ ] **SKILL.md under 500 lines?** If >500, split into supporting files
- [ ] **Description specific?** Includes "when to use" triggers?
- [ ] **Name in gerund form?** (verb-ing, not noun)
- [ ] **No nested references?** All links one level deep from SKILL.md?
- [ ] **Supporting files focused?** Each has a single clear purpose?
- [ ] **Third person writing?** No "you" or "I" language?
- [ ] **Examples concrete?** Show real scenarios, not abstract?
- [ ] **Scripts have error handling?** Don't punt to Claude?
- [ ] **Workflows have validation steps?** Inline checks?
- [ ] **File paths use forward slashes?** (works on all platforms)

If any checkbox is unchecked, address it. Run through checklist before sharing skill.
