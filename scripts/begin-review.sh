#!/usr/bin/env bash
# begin-review.sh - Wrapper for task-reviewer agent
#
# Usage: begin-review <task-id>
#
# Calls begin-work.py --review to set up review context without
# changing task status (reviewer inspects, doesn't claim work).

set -euo pipefail

# Resolve symlinks to find the actual script directory
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
exec python3 "$SCRIPT_DIR/begin-work.py" --review "$@"
