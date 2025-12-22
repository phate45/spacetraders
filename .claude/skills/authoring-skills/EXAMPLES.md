# Skill Authoring Examples

This document provides real-world skill creation examples, from conception through deployment.

## Table of Contents

- Scenario 1: Git Workflow Skill (Team-facing, procedural)
- Scenario 2: Java Code Style Skill (Development standards, reference-heavy)
- Scenario 3: PDF Processing Skill (Script-driven, utility)
- Scenario 4: BigQuery Analysis Skill (Domain-organized, reference-heavy)

---

## Scenario 1: Git Workflow Skill

**Problem**: Team members repeatedly ask how to commit changes, create branches, handle merge conflicts. Everyone needs consistent processes.

**Concrete examples**:
- "How do I commit my changes safely?"
- "What's the correct branch naming convention?"
- "How do I handle merge conflicts?"
- "When should I use rebase vs merge?"

### Planning Phase

**Reusable content identified**:
1. **WORKFLOWS.md**: 5-7 complete procedures (commit, branch, rebase, conflict resolution, push)
2. **REFERENCE.md**: Commit message format, branch naming rules, safety checks
3. **TROUBLESHOOTING.md**: Common errors, how to undo operations, branch cleanup

**Why this structure**:
- Procedural skill (workflows are core)
- Safety-critical (validation and feedback loops needed)
- Reference-heavy (rules and conventions matter)

### SKILL.md (Entry Point)

```markdown
---
name: managing-git-operations
description: Manage git commits and branches with safety checks and consistency. Use when committing changes, creating branches, staging files, or resolving merge conflicts. Enforces branch rules, prevents .gitignore commits, ensures professional commit messages.
---

# Managing Git Operations

Team coordination requires consistent git practices. This skill provides safe, validated workflows for commits, branches, and conflict resolution.

## Core Principles

1. **Single checkpoint per action**: Confirm once before executing
2. **Safety first**: Validate branch, files, and message before committing
3. **Consistency**: Enforce naming conventions and commit format
4. **Clarity**: Explicit about what's changing and why

## Quick Reference

**Creating a feature branch**:
```bash
git checkout -b feature/EDBIC-1234-short-description
```

**Committing changes** (see WORKFLOWS.md for full procedure):
```bash
git diff --cached --name-only  # Review staged files
git commit -m "EDBIC-1234 - Description of change"
```

**Safe merge conflict resolution**:
See [WORKFLOWS.md](WORKFLOWS.md) for step-by-step "Resolving Merge Conflicts" workflow.

## Workflows

For complete procedures with validation steps, see [WORKFLOWS.md](WORKFLOWS.md):

- **Committing changes** (with safety checks)
- **Creating feature branches** (with naming validation)
- **Rebasing onto develop**
- **Resolving merge conflicts** (step-by-step with conflict markers explained)
- **Pushing with verification**

## Reference Material

- **Commit message format**: See [REFERENCE.md](REFERENCE.md#commit-format)
- **Branch naming conventions**: See [REFERENCE.md](REFERENCE.md#branch-naming)
- **NEVER rules**: See [REFERENCE.md](REFERENCE.md#safety-rules)

## Troubleshooting

Common issues and solutions in [TROUBLESHOOTING.md](TROUBLESHOOTING.md):

- "I committed to the wrong branch"
- "How do I undo my last commit?"
- "I see merge conflict markers, what now?"
- "My branch is out of date with develop"
```

### Supporting Files Structure

**WORKFLOWS.md snippet**:
```markdown
## Workflow: Committing Changes

**When to use**: After modifying code, ready to commit

**Estimated time**: 3-5 minutes per commit

### Step 1: Review Current State
Run: `git status`
Output: Shows modified files and current branch

Checkpoint question: Is this the right branch? Are these the files you meant to change?

### Step 2: Review Changes
Run: `git diff --cached --name-only`
Lists all staged files

If you haven't staged files yet:
```bash
git add file1.js file2.js  # Add specific files
# OR
git add .                  # Add all changes
```

### Step 3: Verify No .gitignore Changes
Run: `git diff --cached --name-only | grep "^\.gitignore$"`

If this returns anything:
```bash
git restore --staged .gitignore
```

### Step 4: Check Branch Safety
Run: `git rev-parse --abbrev-ref HEAD`
Verify output is NOT `develop` or `release/*`

### Step 5: Checkpoint Before Commit
Present summary:

```
Ready to commit:

Branch: feature/EDBIC-1234-implement-oauth2
Files changed:
  - src/auth/OAuth2Service.java
  - test/AuthTest.java

Message:
  EDBIC-1234 - Implement OAuth2 Client Credentials authentication

Continue? (yes / edit message / cancel)
```

### Step 6: Execute Commit
Run: `git commit -m "$(cat <<'EOF'\nEDBIC-1234 - Implement OAuth2 Client Credentials authentication\nEOF\n)"`
```

**REFERENCE.md snippet**:
```markdown
## Commit Message Format

All commits use the format: `EDBIC-<ticket-id> - <description>`

### Good Examples
- EDBIC-1234 - Implement OAuth2 Client Credentials for mail authentication
- EDBIC-1008 - Fix null pointer exception in EdifactParser
- EDBIC-1149 - Extract token management into dedicated service

### Strong Action Verbs
- Implement, add, create (new functionality)
- Fix, resolve, address (bug fixes)
- Extract, refactor, simplify (refactoring)
- Update, enhance, improve (improvements)
- Document, clarify (documentation)

### NEVER Rules
- NEVER commit to `develop` without explicit approval
- NEVER commit `.gitignore` unless explicitly requested
- NEVER commit `credentials.json`, `.env`, or secrets
- NEVER force push to `develop` or `release/*`
- NEVER skip pre-commit hooks without asking
```

**TROUBLESHOOTING.md snippet**:
```markdown
## Q: I committed to the wrong branch, how do I fix it?

**Solution**:
1. Get the commit hash: `git log -1 --oneline` (shows your last commit)
2. Reset your current branch: `git reset HEAD~1` (undoes the commit, keeps changes)
3. Checkout the correct branch: `git checkout feature/correct-branch`
4. Commit again to the right branch

Total time: 2 minutes

## Q: How do I undo my last commit?

**Keep the changes**:
```bash
git reset --soft HEAD~1
```
Changes stay staged and ready to recommit.

**Discard the changes**:
```bash
git reset --hard HEAD~1
```
WARNING: This is destructive and cannot be undone.
```

### Deployment

1. Create skill directory: `.claude/skills/managing-git-operations/`
2. Add all files (SKILL.md, WORKFLOWS.md, REFERENCE.md, TROUBLESHOOTING.md)
3. Update settings.local.json:
   ```json
   "managing-git-operations": true
   ```
4. Test on real tasks (actual branch creation, commits)
5. Iterate based on usage

---

## Scenario 2: Java Code Style Skill

**Problem**: All Java developers need to follow consistent style standards. Standards are complex (val/var, final parameters, Lombok, Java 21 features). Hard to remember, easy to forget.

**Concrete examples**:
- "Should I use `var` or `val` for this variable?"
- "Do I need the `final` keyword on method parameters?"
- "How do I use Lombok annotations correctly?"
- "What Java 21 features should I use?"

### Planning Phase

**Reusable content identified**:
1. **Source of truth**: `.claude/code-style.md` (comprehensive, 600+ lines)
2. **SKILL.md**: Quick checklist + reference to code-style.md
3. **EXAMPLES.md**: 6 real-world scenarios (OAuth2, test, builder, switch expressions, pattern matching, streams)
4. **TROUBLESHOOTING.md**: Edge cases, common violations, diagnostic checklist

**Why this structure**:
- Code style is declarative (reference-based)
- Complex standards (need both quick checklist and detailed reference)
- Learning curve (benefit from concrete before/after examples)

### SKILL.md (Entry Point)

```markdown
---
name: validating-java-code
description: Validate Java code against mandatory style standards before writing. Use when starting code generation, writing tests, or refactoring. Enforces val/var, final parameters, Lombok, and Java 21 features per .claude/code-style.md.
---

# Validating Java Code

Before writing Java code, validate against our mandatory style standards. Standards are defined in `.claude/code-style.md` (the source of truth).

## Core Validation Checklist

Before committing any Java code, verify:

- [ ] **Local variables**: Use `val` (immutable) or `var` (mutable), NEVER explicit types
- [ ] **Method parameters**: ALL parameters marked `final`
- [ ] **Lombok**: Use @Getter, @Setter, @Builder, @Slf4j where appropriate
- [ ] **Java 21 features**: Use records, switch expressions, pattern matching
- [ ] **Collections**: Immutable when possible, avoid mutable defaults
- [ ] **Optional**: Used for nullability, not for missing values

## Quick Reference

**Local variables**:
```java
// GOOD: Using val/var
val user = userService.getUser(id);
var count = 0;

// BAD: Explicit types
String name = "John";
Integer count = 0;
```

**Method parameters**:
```java
// GOOD: ALL parameters final
public void processUser(final User user, final String action) { }

// BAD: Missing final
public void processUser(User user, String action) { }
```

**Lombok**:
```java
// Use @Getter, @Setter, @Builder, @Slf4j, @AllArgsConstructor
@Getter
@Setter
@Builder
public class UserService { }
```

**Java 21 features**:
```java
// Records for immutable data
public record User(String name, String email) { }

// Switch expressions
var message = switch(status) {
    case ACTIVE -> "User is active";
    case INACTIVE -> "User inactive";
    default -> "Unknown";
};

// Pattern matching
if (obj instanceof String str) {
    System.out.println(str.length());
}
```

## Detailed Reference

See `.claude/code-style.md` for comprehensive style guide including:
- Variable naming conventions
- Method organization
- Annotation usage
- Stream best practices
- Error handling patterns

## Examples

See [EXAMPLES.md](EXAMPLES.md) for 6 real-world scenarios:

1. OAuth2 Service implementation (val/var, final params, Lombok)
2. Integration test setup (records, pattern matching)
3. Builder pattern with Lombok (@Builder)
4. Switch expressions with Java 21
5. Pattern matching for type checking
6. Stream operations and functional patterns

## Edge Cases & Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for:
- When to use val vs var
- Lombok annotation combinations
- Stream operation chains
- Pattern matching edge cases
```

### Supporting Files

**EXAMPLES.md snippet - OAuth2 Service**:

Before:
```java
public class OAuth2Service {
    private String clientId;
    private String clientSecret;
    private String tokenUrl;

    public OAuth2Service(String clientId, String clientSecret, String tokenUrl) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.tokenUrl = tokenUrl;
    }

    public String getToken() throws Exception {
        HttpClient client = HttpClient.newHttpClient();
        // ... rest of implementation
    }
}
```

After:
```java
@Getter
@Slf4j
public class OAuth2Service {
    private final String clientId;
    private final String clientSecret;
    private final String tokenUrl;

    @Builder
    public OAuth2Service(final String clientId, final String clientSecret, final String tokenUrl) {
        this.clientId = clientId;
        this.clientSecret = clientSecret;
        this.tokenUrl = tokenUrl;
    }

    public String getToken() throws Exception {
        val client = HttpClient.newHttpClient();
        // ... rest of implementation
    }
}
```

**Diff analysis**:
- ✓ Added @Getter, @Slf4j annotations
- ✓ Changed to @Builder constructor
- ✓ All parameters marked `final`
- ✓ Used `val` for local variables
- ✓ Removed explicit getters (Lombok generates them)

---

## Scenario 3: PDF Processing Skill

**Problem**: Multiple tools need to process PDFs (rotate, extract, merge). Same operations written repeatedly as one-off scripts.

**Concrete examples**:
- "Extract text from this PDF"
- "Rotate pages in this PDF"
- "Merge multiple PDFs"

### Planning Phase

**Reusable content identified**:
1. **scripts/**: `extract_text.py`, `rotate_pages.py`, `merge_pdfs.py` (deterministic, reused)
2. **REFERENCE.md**: Input/output formats, command-line flags, error codes
3. **EXAMPLES.md**: Complete workflows (extract + save, rotate + verify, merge + validate)

**Why this structure**:
- Script-driven (utilities executed repeatedly)
- Deterministic (same code, same results)
- Reference-heavy (input/output formats matter)

### SKILL.md (Entry Point)

```markdown
---
name: processing-pdfs
description: Extract text, rotate pages, and merge PDF files. Use when working with PDF files or when you need to extract content, modify page orientation, or combine multiple documents.
---

# Processing PDFs

Use utility scripts for common PDF operations. All scripts handle errors gracefully and validate inputs.

## Available Operations

| Script | Purpose | When to use |
|--------|---------|-------------|
| `extract_text.py` | Extract text from all pages | Converting PDF to text |
| `rotate_pages.py` | Rotate pages 90/180/270 degrees | Fixing page orientation |
| `merge_pdfs.py` | Combine multiple PDFs | Assembling documents |

## Quick Start

Extract text:
```bash
python scripts/extract_text.py input.pdf > output.txt
```

Rotate pages:
```bash
python scripts/rotate_pages.py input.pdf 90 output.pdf
```

Merge PDFs:
```bash
python scripts/merge_pdfs.py doc1.pdf doc2.pdf output.pdf
```

## Complete Operations Reference

See [REFERENCE.md](REFERENCE.md) for:
- Input/output format specifications
- All command-line flags
- Error codes and what they mean
- Configuration options

## Real-World Examples

See [EXAMPLES.md](EXAMPLES.md) for complete workflows:

1. **Extract and save** - Extract text, verify output, save to file
2. **Rotate and verify** - Rotate, check result, confirm quality
3. **Merge and validate** - Combine documents, verify page count
```

---

## Scenario 4: BigQuery Analysis Skill

**Problem**: Team analyzes BigQuery data from multiple domains (finance, sales, product). Each domain has different tables, schemas, query patterns. Information scattered across multiple documents.

**Concrete examples**:
- "What was our revenue last quarter?" (finance)
- "How many deals are in the pipeline?" (sales)
- "What's our API usage trend?" (product)

### Planning Phase

**Reusable content identified**:
1. **Domain-organized references**: `reference/finance.md`, `reference/sales.md`, `reference/product.md`
2. **SKILL.md**: Navigation, query patterns, common filters
3. **EXAMPLES.md**: 3-5 queries per domain with output
4. **REFERENCE.md**: Overall query guidelines, common functions

**Why this structure**:
- Domain-organized (multiple independent domains)
- Reference-heavy (schemas matter)
- Scalable (adding new domains doesn't bloat SKILL.md)

### SKILL.md (Entry Point)

```markdown
---
name: analyzing-bigquery
description: Query BigQuery datasets across finance, sales, and product domains. Use when analyzing business metrics, creating reports, or exploring data. Includes table schemas, common queries, and filtering rules.
---

# Analyzing BigQuery

Access BigQuery data from finance, sales, and product domains. Each domain has specific tables, schemas, and filtering rules.

## Available Domains

**Finance** → Revenue, billing, contracts
See [reference/finance.md](reference/finance.md)

**Sales** → Opportunities, pipeline, accounts
See [reference/sales.md](reference/sales.md)

**Product** → API usage, features, adoption
See [reference/product.md](reference/product.md)

## Query Rules

Always apply these filters:
- Exclude test accounts: `WHERE customer_type != 'test'`
- Use UTC timestamps
- Include date range in WHERE clause

## Common Query Pattern

```sql
SELECT
  DATE(event_time) as date,
  COUNT(*) as count,
  SUM(amount) as total
FROM dataset.table_name
WHERE
  DATE(event_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND customer_type != 'test'
GROUP BY date
ORDER BY date DESC
```

## Find Specific Metrics

Use grep to search for metrics:
```bash
grep -i "revenue" reference/finance.md
grep -i "pipeline" reference/sales.md
grep -i "api usage" reference/product.md
```

## Real-World Examples

See [EXAMPLES.md](EXAMPLES.md) for complete queries and outputs.

## Complete Reference

See [REFERENCE.md](REFERENCE.md) for BigQuery functions, syntax, and advanced patterns.
```

### reference/finance.md Structure

```markdown
# Finance Domain - BigQuery

## Tables

### orders
- order_id (STRING) - Unique identifier
- customer_id (STRING) - Customer
- amount (FLOAT64) - Order amount in USD
- created_at (TIMESTAMP) - Creation time
- status (STRING) - active, completed, canceled

### subscriptions
- subscription_id (STRING)
- customer_id (STRING)
- monthly_amount (FLOAT64)
- start_date (DATE)
- end_date (DATE)
- status (STRING)

## Metrics

### Monthly Revenue
```sql
SELECT
  DATE_TRUNC(created_at, MONTH) as month,
  SUM(amount) as revenue
FROM dataset.orders
WHERE customer_type != 'test'
GROUP BY month
```

### Subscription MRR (Monthly Recurring Revenue)
```sql
SELECT
  DATE(CURRENT_DATE()) as date,
  SUM(monthly_amount) as mrr
FROM dataset.subscriptions
WHERE
  start_date <= CURRENT_DATE()
  AND (end_date IS NULL OR end_date >= CURRENT_DATE())
```
```

---

## Summary: What These Examples Show

**Git Workflow Skill**: How to build a procedural skill with safety validation
- Workflow-first pattern
- Inline validation and feedback loops
- Reference material for rules and conventions

**Java Code Style Skill**: How to reference external source of truth
- Reference-based pattern
- Comprehensive examples showing transformations
- Troubleshooting for edge cases

**PDF Processing Skill**: How to wrap deterministic scripts
- Script-driven pattern
- Reference material for input/output formats
- Real-world workflows using scripts

**BigQuery Analysis Skill**: How to organize by domain
- Domain-organized pattern
- Progressive disclosure (load only relevant domain)
- Scalable to many domains

Each pattern solves different authoring problems. Pick the pattern that matches your content's structure.
