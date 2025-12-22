# Dependency Direction

**WARNING: Temporal language causes dependency inversion**

When adding dependencies between tasks, think in terms of **requirements**, not **sequence**.

## The Cognitive Trap

Temporal thinking leads to backwards dependencies:

```bash
# WRONG - temporal thinking: "phase1 comes before phase2"
bd dep add phase1 phase2  # Says phase1 DEPENDS ON phase2 (backwards!)
```

Requirement thinking produces correct dependencies:

```bash
# RIGHT - requirement thinking: "api NEEDS schema first"
bd dep add api schema  # api depends on schema (schema blocks api)
```

## Mental Model

The command `bd dep add A B` means:
- **A depends on B**
- **B blocks A**
- **B must complete before A can start**

## Verification

After adding dependencies, verify they make sense:

```bash
bd blocked  # Shows what's blocked and why
bd show <id>  # Shows dependencies for specific issue
```

If the blocked list looks inverted (things that should be available are blocked), the dependencies are backwards.
