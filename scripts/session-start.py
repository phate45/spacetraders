#!/usr/bin/env python3
"""
Session start script for Control Tower.

Gathers session state in a single invocation:
- Ready work (unblocked, not in progress)
- In-progress work (currently claimed)
- Draft issues (need refinement)

Usage:
    python scripts/session-start.py
    python scripts/session-start.py --pretty
"""

import json
import subprocess
import sys
from typing import Any


def run_bd(args: list[str]) -> list[dict[str, Any]]:
    """Run bd command and return parsed JSON."""
    result = subprocess.run(
        ["bd", *args, "--json"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # bd may write errors to stderr but still return empty list
        return []

    output = result.stdout.strip()
    if not output:
        return []

    return json.loads(output)


def main() -> None:
    pretty = "--pretty" in sys.argv

    session_state = {
        "ready": run_bd(["ready"]),
        "in_progress": run_bd(["list", "--status", "in_progress"]),
        "drafts": run_bd(["list", "--status", "draft"]),
    }

    # Add summary counts
    session_state["summary"] = {
        "ready_count": len(session_state["ready"]),
        "in_progress_count": len(session_state["in_progress"]),
        "draft_count": len(session_state["drafts"]),
    }

    if pretty:
        print(json.dumps(session_state, indent=2))
    else:
        print(json.dumps(session_state))


if __name__ == "__main__":
    main()
