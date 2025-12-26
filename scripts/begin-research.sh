#!/usr/bin/env bash
# begin-research.sh - Wrapper for researcher agent
#
# Usage: begin-research <task-id>
#
# Calls begin-work.py --research to set up research context without
# creating worktree (researcher operates read-only on main repo).

set -euo pipefail

# Resolve symlinks to find the actual script directory
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
exec python3 "$SCRIPT_DIR/begin-work.py" --research "$@"
