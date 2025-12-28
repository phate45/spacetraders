---
name: planning-work
description: Orchestrate full planning workflow from idea to actionable beads epic. Use when Mark wants to plan, build, design, or implement multi-task features.
---

# Planning Work

Orchestrate the full planning workflow: from idea to actionable beads epic with implementation-ready tasks.

## Planning Mode

**THIS SKILL IS YOUR PLANNING MODE.** When you invoke this skill, you enter a planning-focused workflow.

### EnterPlanMode is FORBIDDEN

**YOU MUST NEVER call EnterPlanMode.** This skill provides specialized guidance that replaces Claude Code's built-in plan mode.

EnterPlanMode + this skill = broken subagents. Every time.

The built-in plan mode alters your system prompt in ways that prevent subagents from executing their tasks. They get stuck "waiting for permission" that never comes. This skill gives you the same discipline without the subagent interference.

### Planning Mode Discipline

**While in this workflow, YOU MUST:**
- Focus on exploration and design, not implementation
- NEVER write source code (read-only exploration only)
- NEVER create or modify files outside `plans/`
- Use Read, Grep, Glob for codebase exploration
- Delegate research to agents (they execute normally)
- Use AskUserQuestion for clarifications and approval gates

**Exit planning mode** by completing Phase 8 (present epic for execution decision).

## When to Invoke

Trigger on: "plan", "build", "design", "let's work on X", "implement X", or any request requiring multi-task implementation.

## Critical Context

**Planning consumes significant context.** The resulting plan and epic must be:
- Thorough and self-contained
- Implementation-ready without CT's planning context
- Execution likely happens in a fresh session

Do NOT assume the executing CT will remember planning discussions. Everything goes into the plan document and task fields.

## Workflow

### Phase 1: Initialize Epic

**For new work:** Create the containing epic before any exploration:

```bash
bd create --title "[Feature/Goal Name]" --type epic --priority 2 --json
```

**For refining existing tasks:** Read the task first, then convert to epic:

```bash
bd show <task-id> --json  # Understand current scope
bd update <task-id> --type epic --json  # Convert to epic container
```

This epic will contain:
- Research tasks (during planning)
- Implementation tasks (after planning)

Record the epic ID—all subsequent tasks use `--parent <epic-id>`.

**Note:** To reparent an existing task: `bd update <id> --parent <epic-id>`

### Phase 2: Scope Establishment (Conversational)

**BEFORE deep research**, establish the broad goal and scope with Mark through natural conversation. Research without scope alignment = wasted context. Every time.

**Discuss with Mark:**
- What problem are we solving?
- What are the boundaries (in scope vs out of scope)?
- Are there known constraints or preferences?
- What does success look like?

This is conversational—ask clarifying questions, propose scope boundaries, get confirmation. Do NOT use AskUserQuestion here; save that tool for later phases when you have specific options to present based on research findings.

**Document the agreed scope before deep research.** A few sentences capturing the goal and boundaries is sufficient. Misaligned research wastes agent context and your planning budget.

### Phase 3: Research Phase

Research uses **tracked tasks and specialized agents**, not ad-hoc exploration.

**Two types of research:**

| Type | Agent | Model | Use When |
|------|-------|-------|----------|
| Fact-gathering | researcher | haiku | Quick questions: "Where is X defined?", "What modules use Y?" |
| Design research | plan-researcher | sonnet | Building implementation case: "Design approach for X", "Analyze patterns for Y" |

**For each research question:**

1. **Create the research task under the epic:**
   ```bash
   bd create --title "Research: [specific topic]" --type task --parent <epic-id> \
     --description "Investigate [question]. Document findings for planning." --json
   ```

2. **Dispatch appropriate agent:**

   For fact-gathering (haiku):
   ```
   Task(
     subagent_type: "researcher",
     model: "haiku",
     prompt: "Execute research task <task-id>. Invoke /agent-researching skill first.

   Gather facts efficiently. Answer the research question directly."
   )
   ```

   For design research (sonnet):
   ```
   Task(
     subagent_type: "plan-researcher",
     prompt: "Execute research task <task-id>. Invoke /agent-researching skill first.

   Approach this as a software architect:
   1. Understand requirements from the task
   2. Explore thoroughly - find patterns, conventions, similar features
   3. Design solution considering trade-offs
   4. End notes with Critical Files section (3-5 files for implementation)"
   )
   ```

**Parallelize aggressively** where appropriate. Create multiple research tasks, dispatch multiple agents in a single message.

**Between research rounds**, consult with Mark:
- Use AskUserQuestion to present findings and open questions
- Get direction on which areas need deeper investigation
- Validate assumptions before proceeding

**Example mid-research check-in:**
```
AskUserQuestion([
  {
    question: "Based on initial research, I found [X]. Should we investigate [A] or [B] next?",
    header: "Direction",
    options: [
      { label: "Investigate A", description: "Focus on [reason]" },
      { label: "Investigate B", description: "Focus on [reason]" },
      { label: "Both in parallel", description: "If time permits" }
    ]
  }
])
```

Multiple rounds of research are encouraged. You don't need to find all answers at once.

### Phase 4: Write Plan Document

After research completes, synthesize findings into a plan document.

**Location:** `plans/[feature-name].md`

**Structure each phase for direct beads translation:**

```markdown
# Plan: [Feature Name]

## Summary

[1-3 sentence overview. Becomes epic description.]

## Motivation

[The overall goal and expectations. High level view unifying all phases.]

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
[Can this run concurrently with other phases? Default: no]

### Phase 2: [Title]
...
```

### Phase 5: Scope Validation

Before seeking approval, verify EVERY phase has:
- Actionable description (not "figure out X")
- Clear design approach (not "TBD")
- Verifiable acceptance criteria (not "works correctly")

**If any phase requires "figure it out later" or "depends on unknowns," the scope is wrong.**

Push back:

> "This scope can't be fully planned. Either narrow to [concrete subset] or clarify [specific unknowns] before we proceed."

Do NOT create placeholder tasks for undefined work. Incomplete planning means incomplete scope.

### Phase 6: Plan Approval Gate

**Use AskUserQuestion to get explicit approval:**

```
AskUserQuestion([
  {
    question: "Plan is ready at plans/[name].md. Approve to convert to beads tasks?",
    header: "Approval",
    options: [
      { label: "Approve", description: "Convert plan to epic with implementation tasks" },
      { label: "Revise", description: "Need changes before approval" }
    ]
  }
])
```

If "Revise" selected, discuss changes and update the plan document. Re-validate and re-submit for approval.

**Do NOT proceed to Phase 7 until explicitly approved.** Proceeding without approval = wasted conversion work when Mark requests changes.

### Phase 7: Convert Plan to Tasks

**IMMEDIATELY after approval**, analyze the plan's phase structure and invoke the plan-to-beads agent. Do NOT pause between approval and conversion—momentum matters.

**Determine expected layer structure:**

Before dispatching, analyze your phases:
1. Count total phases
2. Identify which are sequential vs parallel
3. Build expected layer structure

Example for 5 sequential phases:
```
Expected layers:
- Layer 0: [Phase 1] (ready)
- Layer 1: [Phase 2]
- Layer 2: [Phase 3]
- Layer 3: [Phase 4]
- Layer 4: [Phase 5]
MaxLayer: 4
```

Example with parallel phases (3 and 4 parallel after 2):
```
Expected layers:
- Layer 0: [Phase 1] (ready)
- Layer 1: [Phase 2]
- Layer 2: [Phase 3, Phase 4] (parallel)
- Layer 3: [Phase 5]
MaxLayer: 3
```

**Dispatch with verification target:**

```
Task(
  subagent_type: "plan-to-beads",
  prompt: "Convert plan at plans/[name].md to beads tasks under epic <epic-id>.

Expected dependency structure (verify with bd graph):
- Total phases: N
- Layer 0: [Phase 1 title] (ready)
- Layer 1: [Phase 2 title] (depends on Phase 1)
- Layer 2: [Phase 3 title] (depends on Phase 2)
...
- MaxLayer: N-1

Verify the graph matches this structure before reporting success."
)
```

**After agent returns**, verify the structure yourself:

```bash
bd graph <epic-id> --json
bd ready --parent <epic-id> --json
```

Fix any discrepancies before proceeding.

### Phase 8: Present for Execution Decision

Present the completed epic structure to Mark:

```
Epic: [title] (<epic-id>)

Tasks created:
- [Phase 1] (<id>) - ready
- [Phase 2] (<id>) - blocked by <prev>
- ...

Research tasks closed: N
Implementation tasks ready: M

Next steps:
A) Execute now - dispatch agents to begin implementation
B) Start fresh session - orchestrate execution with full context
C) Defer - work is tracked, pick up later
```

**This concludes planning mode.** Mark decides how to proceed with execution.

## Plan Document Location

Write plans to: `plans/[feature-name].md` in the project root.

This keeps plans accessible across sessions and provides reference during execution.

## Anti-Patterns (Failure Modes)

These patterns cause planning failures. Every time.

| Anti-Pattern | What Happens |
|--------------|--------------|
| Call EnterPlanMode | Subagents freeze. They can't execute. Session stalls. |
| Skip epic creation | Research floats untracked. Findings get lost across sessions. |
| Skip scope establishment | Hours of research on wrong problem. Start over. |
| Dispatch researcher without task | No notes field. Findings vanish when agent returns. |
| Use Explore instead of researcher agents | CT context bloats. Planning budget exhausted early. |
| Skip mid-research check-ins | Discover misalignment at Phase 4. Redo everything. |
| Vague phase descriptions | Implementing agent asks "what does this mean?" Blocks. |
| Skip plan approval gate | Mark rejects at execution time. All planning wasted. |
| Skip plan-to-beads conversion | Plan exists in markdown. No one executes it. |
| Skip graph verification | Wrong task unblocks. Parallel work creates conflicts. |

## Quick Reference

```bash
# Create containing epic
bd create --title "Feature X" --type epic --priority 2 --json

# Convert existing task to epic
bd update <task-id> --type epic --json

# Create research task under epic
bd create --title "Research: Y" --type task --parent <epic-id> \
  --description "Investigate [question]" --json

# After planning, verify epic structure
bd graph <epic-id> --json
bd ready --parent <epic-id> --json

# Start execution
bd ready --parent <epic-id> --json
```
