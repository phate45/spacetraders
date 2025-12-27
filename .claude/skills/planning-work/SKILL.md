---
name: planning-work
description: Orchestrate full planning workflow from idea to actionable beads epic. Use when Mark wants to plan, build, or design multi-task features.
---

# Planning Work

Orchestrate the full planning workflow: from idea to actionable beads epic with implementation-ready tasks.

## When to Invoke

Trigger on: "plan", "build", "design", "let's work on X", or any request requiring multi-task implementation.

## Critical Context

**Planning consumes significant context.** The resulting plan and epic must be:
- Thorough and self-contained
- Implementation-ready without CT's planning context
- Execution likely happens in a fresh session

Do NOT assume the executing CT will remember planning discussions. Everything goes into the plan document and task fields.

## Workflow

### 1. Create Epic Upfront

Before any research or planning, create the containing epic:

```bash
bd create --title "[Feature/Goal Name]" --type epic --priority 1 --json
```

This epic will contain:
- Research tasks (during planning)
- Implementation tasks (after planning)

Record the epic ID—all subsequent tasks use `--parent <epic-id>`.

### 2. Enter Plan Mode

```
EnterPlanMode
```

Use Claude's first-class planning infrastructure. Do NOT reinvent.

### 3. Research Phase (CT-Style)

Research uses **tracked tasks and researcher agents**, not ad-hoc exploration.

**For each research question:**

1. **Create the research task under the epic:**
   ```bash
   bd create --title "Research: [specific topic]" --type task --parent <epic-id> \
     --description "Investigate [question]. Document findings for planning." --json
   ```

2. **Dispatch researcher agent to execute it:**
   ```
   Task(
     subagent_type: "researcher",
     model: "haiku",
     prompt: "Execute research task <task-id>. Invoke /agent-researching skill first.",
     ...
   )
   ```

The researcher will:
- Claim the task via `begin-research <id>`
- Investigate and write findings to task notes
- Return findings summary to CT

**Parallelize aggressively** where appropriate. Create multiple research tasks, then dispatch multiple researcher agents in a single message. They run concurrently.
After research completes, synthesize findings from task notes into the plan.
Multiple rounds of research to answer questions that arise from the preceding round(s) is encouraged. You don't need to find all answers at once.
However, _consult the results with Mark to gain insight in between_. This will help you decide what _exactly_ you need to research further, preventing wasting of resources and Mark's time.

### 4. Write Plan Document

Structure each phase for direct beads translation:

```markdown
# Plan: [Feature Name]

## Summary

[1-3 sentence overview. Becomes epic description.]

## Motivation

[The overall goal and expectations of the epic. High level view on the whole feature, unifying the scope of all the individual phases below.]

## Files

[List of files to create/modify. Include in epic description.]

## Phases

### Phase 1: [Title]

**Description:**
[WHY and WHAT. Immutable problem statement. Becomes task description field.]

**Design:**
[HOW to implement. Approach, patterns, decisions. Becomes task design field.]

**Acceptance Criteria:**
- Verifiable outcome 1
- Verifiable outcome 2
[Becomes task acceptance_criteria field.]

**Parallel:** yes|no
[Can this run concurrently with other phases? Default: no (sequential)]

### Phase 2: [Title]
...
```

### 5. Scope Validation

Before exiting plan mode, verify EVERY phase has:
- Actionable description (not "figure out X")
- Clear design approach (not "TBD")
- Verifiable acceptance criteria (not "works correctly")

**If any phase requires "figure it out later" or "depends on unknowns," the scope is wrong.**

Push back:

> "This scope can't be fully planned. Either narrow to [concrete subset] or clarify [specific unknowns] before we proceed."

Do NOT create placeholder tasks for undefined work. Incomplete planning means incomplete scope.

### 6. Exit Plan Mode

```
ExitPlanMode
```

Wait for Mark's approval of the plan (required Claude Code step).

### 7. Convert Plan to Tasks (MANDATORY)

**Immediately after approval**, invoke the plan-to-beads agent:

```
Task(
  subagent_type: "plan-to-beads",
  prompt: "Convert plan at [path] to beads tasks under epic <epic-id>.",
  ...
)
```

This agent:
- Updates epic description with final summary
- Creates implementation tasks with proper fields
- Wires dependencies (sequential and parallel based on plan)
- Tasks are OPEN status, ready for execution
- Returns epic structure for approval

### 8. Approve and Execute

Present the epic structure to Mark. Once approved:
- Research tasks are closed (planning complete)
- Implementation tasks are open and ready
- `bd ready --parent <epic-id>` shows available work
- Fresh CT session can orchestrate execution

## Plan Document Location

Write plans to: `plans/[feature-name].md` in the project root.

This keeps plans accessible across sessions and provides reference during execution.

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Skip epic creation | Research tasks have no container; workflow not tracked |
| Dispatch researcher without task | No tracking; findings not persisted; like using Explore |
| Use Explore instead of researcher agents | CT consumes context that should be preserved |
| Vague phase descriptions | Tasks won't be actionable; execution will stall |
| Skip plan-to-beads conversion | Plan exists only as markdown; no execution tracking |
| Create tasks as draft | Delays execution; planning should produce ready work |
| Plan without parallelization analysis | Missed optimization; sequential when parallel possible |

## Quick Reference

```bash
# Create containing epic
bd create --title "Feature X" --type epic --priority 1 --json

# Create research task under epic
bd create --title "Research: Y" --type task --parent <epic-id> \
  --description "Investigate [question]" --json

# After planning, check epic structure
bd show <epic-id> --json
bd list --parent <epic-id> --json

# Start execution
bd ready --parent <epic-id> --json
```
