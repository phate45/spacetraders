#!/usr/bin/env bash

# load-control-tower-context.sh
#
# Loads Control Tower-specific context at session start.
# This context is NOT inherited by subagents - it's CT-only.
#
# Purpose:
# - Inject communication style, collaboration guidelines, proactiveness rules
# - Keep agent context clean (they get CLAUDE.md + agent.md, not CT personality)
#
# How it works:
# - Runs at start of every Claude Code session
# - Skips execution for subagent sessions
# - Reads control-tower-context.md and injects as system-reminder

# Skip for subagent sessions
if [[ "$CLAUDE_PROJECT_DIR" == *"/.claude/agents/"* ]] || [[ -n "$CLAUDE_AGENT_TYPE" ]]; then
    exit 0
fi

CT_CONTEXT_PATH="$CLAUDE_PROJECT_DIR/.claude/control-tower-context.md"

# Verify context file exists
if [[ ! -f "$CT_CONTEXT_PATH" ]]; then
    echo "Warning: Control Tower context not found at: $CT_CONTEXT_PATH" >&2
    exit 0
fi

# Read and inject the context
CT_CONTENT=$(cat "$CT_CONTEXT_PATH")

cat <<EOF
<system-reminder>
CONTROL TOWER CONTEXT (Auto-loaded at Session Start)

The following Control Tower-specific context applies to this session.
Subagents do NOT receive this context - they get CLAUDE.md + their agent.md only.

---
$CT_CONTENT
---
</system-reminder>
EOF
