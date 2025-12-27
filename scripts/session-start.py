#!/usr/bin/env python3
"""
Session start script for Control Tower.

Gathers session state in a single invocation:
- Ready work (unblocked, not in progress)
- In-progress work (currently claimed)
- Review work (awaiting review)
- Draft issues (need refinement)
- Beads update availability

Usage:
    python3 scripts/session-start.py
    python3 scripts/session-start.py --pretty
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent


def check_beads_update() -> bool | None:
    """Check if beads update is available. Returns None on error."""
    try:
        result = subprocess.run(
            ["python3", str(SCRIPT_DIR / "install_beads.py"), "--check", "--quiet"],
            capture_output=True,
            text=True,
            timeout=35,  # GitHub API can be slow; install_beads.py has 30s urllib timeout
        )
        output = result.stdout.strip()
        if '"beads_update_available": true' in output:
            return True
        if '"beads_update_available": false' in output:
            return False
        return None  # Unexpected output or error
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


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


def evaluate_gates() -> dict[str, Any]:
    """
    Evaluate timer gates and return results.

    Returns dict with:
        - evaluated: number of gates checked
        - closed: list of gate IDs that were closed
        - message: human-readable summary
    """
    result = subprocess.run(
        ["bd", "gate", "eval"],
        capture_output=True,
        text=True,
    )

    output = result.stdout.strip()

    # Parse the output format:
    # - "No open gates to evaluate"
    # - "Evaluated N gates, none ready to close"
    # - "✓ Closed N gate(s)" followed by gate IDs
    if "No open gates" in output:
        return {"evaluated": 0, "closed": [], "message": "No open gates"}

    if "none ready to close" in output:
        # Extract count from "Evaluated N gates, none ready to close"
        parts = output.split()
        count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return {"evaluated": count, "closed": [], "message": output}

    if "Closed" in output:
        # Parse "✓ Closed N gate(s)" and extract IDs from following lines
        lines = output.split("\n")
        closed_ids = [line.strip() for line in lines[1:] if line.strip()]
        return {
            "evaluated": len(closed_ids),
            "closed": closed_ids,
            "message": f"Closed {len(closed_ids)} gate(s)",
        }

    # Fallback for unexpected output
    return {"evaluated": 0, "closed": [], "message": output or "Unknown"}


def main() -> None:
    pretty = "--pretty" in sys.argv

    # Evaluate gates first (may unblock work)
    gates_result = evaluate_gates()

    session_state = {
        "gates": gates_result,
        "ready": run_bd(["ready"]),
        "in_progress": run_bd(["list", "--status", "in_progress"]),
        "review": run_bd(["list", "--status", "review"]),
        "drafts": run_bd(["list", "--status", "draft"]),
    }

    # Check for beads updates
    beads_update = check_beads_update()

    # Add summary counts
    session_state["summary"] = {
        "ready_count": len(session_state["ready"]),
        "in_progress_count": len(session_state["in_progress"]),
        "review_count": len(session_state["review"]),
        "draft_count": len(session_state["drafts"]),
        "beads_update_available": beads_update,
        "gates_closed": len(gates_result.get("closed", [])),
    }

    if pretty:
        print(json.dumps(session_state, indent=2))
    else:
        print(json.dumps(session_state))


if __name__ == "__main__":
    main()
