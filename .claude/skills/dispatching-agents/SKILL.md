---
name: dispatching-agents
description: Decision logic for agent dispatch. Invoke BEFORE dispatching any agent to ensure correct agent type, model, execution mode, and prompt construction. Control Tower only.
---

<objective>
Codify the decision process for dispatching agents to beads tasks. Invoke this skill each time before dispatching to refresh context and make informed choices.

This skill is for Control Tower only. Agents do not use this skill.
</objective>

<quick_start>
**Before every dispatch, answer these questions:**

1. **Which agent?** → See Agent Selection
2. **Which model?** → See Model Selection
3. **Background or foreground?** → Background (default)
4. **Is task complete?** → description, design, acceptance_criteria all populated?
5. **Resume or fresh?** → See Resume Patterns

**Standard dispatch pattern:**
```
Task(
  subagent_type: "rust-implementer",
  model: "sonnet",
  run_in_background: true,
  prompt: "Work on task spacetraders-xyz. [Brief motivation—the why.]"
)
```

Context lives in beads fields. Prompt provides motivation.
</quick_start>

<agent_selection>
## Agent Selection

| Task Type | Agent | Why |
|-----------|-------|-----|
| Rust implementation | `rust-implementer` | Has 2024 edition context, Rust coding standards |
| General implementation | `task-executor` | Language-agnostic implementation workflow |
| First-gate code review | `task-reviewer` | Verification methodology, comment-based feedback |
| Codebase exploration | `Explore` (built-in) | Fast context gathering, no task creation needed |
| Research/scouting | `rust-implementer` or `task-executor` | Creates task, writes findings to notes |

**Decision tree:**

```
Is this Rust code?
├─ Yes → rust-implementer
└─ No
   ├─ Is it code review? → task-reviewer
   ├─ Is it quick exploration (no task needed)? → Explore (built-in)
   └─ Otherwise → task-executor
```

**Research tasks:** Use implementation agents (rust-implementer/task-executor) with haiku model. They create worktrees, write findings to task notes, and follow the standard workflow. The only difference is model choice and that CT can close directly (no code to review).
</agent_selection>

<model_selection>
## Model Selection

| Task Nature | Model | Rationale |
|-------------|-------|-----------|
| Research, scouting, exploration | `haiku` | Fast, cheap, sufficient for reading and summarizing |
| Code implementation | `sonnet` | Better code quality, worth the cost for production code |
| First-gate review | `sonnet` | Catches subtle issues (schema mismatches, missing fields) |
| Uncertain | `sonnet` | Default to higher capability when unsure |

**Observed:** Haiku reviewer missed a schema mismatch (`expiration` field). Sonnet caught it. For code review, sonnet is worth the cost.

**Override:** If Mark specifies a model, use that.
</model_selection>

<execution_mode>
## Execution Mode

**Background is preferred.** Launch with `run_in_background: true`.

Benefits:
- CT can prepare next task, update notes, discuss with Mark
- Returns agent ID immediately for later resume if needed
- Check progress with `TaskOutput(block=false)`
- Wait for completion with `TaskOutput(block=true)` when needed

**Foreground (blocking) when:**
- CT has nothing else to do
- Result needed immediately to continue conversation
- Sequential dependency on this agent's output

**In practice:** For sequential task flows, CT often just waits. But background execution keeps options open.
</execution_mode>

<prompt_construction>
## Prompt Construction

**Lean on beads.** The task fields are the source of truth:
- `description` — WHY and WHAT (the problem)
- `design` — HOW (approach, file pointers, schemas to check)
- `acceptance_criteria` — WHAT SUCCESS LOOKS LIKE
- `notes` — Current state, checkpoints, prior findings
- `comments` — External feedback, review results

Agents run `begin-work <task-id>` which loads all of this automatically.

**The prompt provides motivation, not context.**

Good prompt:
```
Work on task spacetraders-xyz.
This implements the contracts API, our first step toward mission automation.
Follow up tasks will integrate this implementation into the CLI interface, keep that in mind.
```

The "why" helps the agent prioritize and make judgment calls. The "what" and "how" are in the task fields.

**Do NOT put in the prompt:**
- File paths or pointers → put in task `design` field
- Schemas or API details → put in task `design` field
- Prior findings → should already be in task `notes`
- Review feedback → should be in task `comments`

**If context is missing from task fields:** Add it via `bd update` or `bd comment` BEFORE dispatch. The task record is persistent; the prompt is ephemeral.
</prompt_construction>

<resume_patterns>
## Resume Patterns

**Core principle:** Beads fields should be complete enough that ANY agent (resumed or fresh) can pick up the work. The prompt doesn't change based on whether it's a resume or fresh dispatch.

### Normal Resume

Agent checkpointed and returned. Resume with Task tool:

```
Task(
  subagent_type: "rust-implementer",
  resume: "<agent-id-from-previous-dispatch>",
  prompt: "Continue work on spacetraders-xyz. Blocker resolved."
)
```

The agent retains conversation history. Task notes contain checkpoint state.

### Post-Review Resume

If reviewer found issues, the agent writes findings to task comments automatically. Just dispatch:

```
Task(
  subagent_type: "rust-implementer",
  prompt: "Work on task spacetraders-xyz. Address review feedback in comments."
)
```

### Resume Failure Fallback

If Task tool resume fails (API error, etc.), dispatch a fresh agent:

```
Task(
  subagent_type: "rust-implementer",
  prompt: "Work on task spacetraders-xyz. [Brief motivation and/or nudge towards feedback in comments]"
)
```

**Same prompt as any fresh dispatch.** If the task notes are complete (COMPLETED, IN_PROGRESS, BLOCKERS sections), a fresh agent can resume seamlessly. If you find yourself needing to invent special context for the prompt, that's a signal the task notes are incomplete—fix the notes, not the prompt.

**Do NOT manually update status before dispatch.** The `begin-work` script handles status transitions automatically.
</resume_patterns>

<sequential_vs_parallel>
## Sequential vs Parallel Execution

**Sequential when:**
- Tasks touch the same files (especially entry points like `main.rs`, `index.ts`)
- One task's output is another's input
- Merge conflicts are likely

**Parallel when:**
- Tasks are in completely separate areas of codebase
- No file overlap
- Independent deliverables

**Example:**
- Waypoint endpoint + Contracts endpoint → Both modify `main.rs` → **Sequential**
- Frontend feature + Backend API → Different directories → **Parallel OK**

**When uncertain:** Sequential is safer. Parallel saves time but costs more if merge conflicts occur.
</sequential_vs_parallel>

<research_vs_implementation>
## Research vs Implementation Tasks

**Research tasks** (scouting, exploration, context gathering):
- Use haiku model (fast, cheap)
- Agent writes findings to task notes
- No code changes expected
- CT can review and close directly (no code to review)
- Still creates worktree (standard workflow), but no merge needed

**Implementation tasks** (code changes):
- Use sonnet model (better code quality)
- Agent commits code in worktree
- First-gate review by task-reviewer
- Second-gate review by Mark
- Merge via `end-work <id>`

**Key insight:** Research tasks skip the review cycle because there's nothing to review. CT reads the notes, validates findings, closes the task.
</research_vs_implementation>

<anti_patterns>
## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Manually run `bd update --status in_progress` before dispatch | Just dispatch; `begin-work` handles status |
| Read files and paste content into prompt | Put pointers in task `design` field; agent reads themselves |
| Put file paths or pointers in prompt | Put them in task `design` field |
| Invent special context for resume prompts | Ensure task notes are complete; use same prompt as fresh |
| Use foreground for everything | Default to `run_in_background: true` |
| Dispatch without invoking this skill | Invoke `/dispatching-agents` every time |
| Guess at model selection | Follow the model selection table |
| Dispatch parallel when tasks touch same files | Use sequential execution |
| Skip task creation for significant work | Everything flows through task graph |

**The IC trap:** Personally gathering context, figuring out patterns, then creating "perfectly-scoped" tasks. This is still IC behavior with extra steps. Context gathering is a task. Delegate it.
</anti_patterns>

<checklist>
## Pre-Dispatch Checklist

- [ ] Task exists in beads with description, design, acceptance_criteria populated
- [ ] Agent type selected (rust-implementer / task-executor / task-reviewer)
- [ ] Model selected (haiku for research, sonnet for implementation/review)
- [ ] Execution mode decided (background preferred)
- [ ] Prompt is lean (task ID + motivation only)
- [ ] No manual status update (begin-work handles it)
- [ ] Sequential/parallel decision made if multiple agents
</checklist>

<success_criteria>
Dispatch is well-formed when:

- [ ] Correct agent for task type
- [ ] Appropriate model for task nature
- [ ] Background execution unless blocked on result
- [ ] Prompt contains task ID and motivation only (context in beads fields)
- [ ] No redundant status updates
- [ ] Task fields complete enough for fresh agent to resume
</success_criteria>
