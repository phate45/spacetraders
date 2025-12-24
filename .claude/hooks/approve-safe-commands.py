#!/usr/bin/env python3
"""
Auto-approve safe commands for subagents.

Subagents don't inherit the parent's permission allow-list.
This hook extends those permissions via PreToolUse approval.
"""

import json
import re
import sys

# Commands that are safe to auto-approve
# These mirror the allow-list in settings.json but work for subagents
SAFE_PATTERNS = [
    # Beads task management
    r"^bd\s+",                    # All bd commands
    r"^begin-work\s+",            # Worktree initialization

    # Git read operations
    r"^git\s+status",
    r"^git\s+log",
    r"^git\s+branch",
    r"^git\s+diff",
    r"^git\s+show",
    r"^git\s+ls-tree",
    r"^git\s+check-ignore",

    # Git write operations (already in allow-list)
    r"^git\s+add",
    r"^git\s+commit",
    r"^git\s+restore",
    r"^git\s+pull",
    r"^git\s+push$",              # Exact match, no force flags
    r"^git\s+worktree",

    # Safe shell commands
    r"^pwd$",
    r"^ls\s",
    r"^ls$",
    r"^cat\s",
    r"^head\s",
    r"^tail\s",
    r"^wc\s",
    r"^sort\s",
    r"^find\s",
    r"^fd\s",
    r"^rg\s",
    r"^grep\s",
    r"^eza\s",
    r"^tree\s",
    r"^mkdir\s",
    r"^chmod\s",
    r"^test\s",
    r"^date",
    r"^jq\s",
    r"^awk\s",

    # Python scripts (uv-managed)
    r"^python3?\s+scripts/",
]

# Patterns that should NEVER be auto-approved, even if they match above
DENY_PATTERNS = [
    # Force flags
    r"--force",
    # r"-f\s",  # too generic?
    # General protection
    r"rm\s+-rf",
    # Git ops
    r"git\s+push\s+.*--force",
    r"git\s+reset\s+--hard",
]


def should_approve(command: str) -> tuple[bool, str]:
    """
    Check if a command should be auto-approved.

    Returns (should_approve, reason)
    """
    if not command:
        return None, "Empty command"

    # Check deny patterns first
    for pattern in DENY_PATTERNS:
        if re.search(pattern, command):
            return False, f"Matched deny pattern: {pattern}"

    # Check safe patterns
    for pattern in SAFE_PATTERNS:
        if re.match(pattern, command):
            return True, f"Matched safe pattern: {pattern}"

    return None, "No matching pattern"


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Can't parse input, don't interfere
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only process Bash tool calls
    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")
    approve, reason = should_approve(command)

    if approve:
        # Return JSON to auto-approve
        response = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": f"Auto-approved: {reason}"
            }
        }
        print(json.dumps(response))

    if approve is False:
        # None is for 'fall-through'
        response = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Auto-denied: {reason}"
            }
        }
        print(json.dumps(response))

    # Exit 0 regardless - don't block, just approve or pass through
    sys.exit(0)


if __name__ == "__main__":
    main()
