#!/usr/bin/env python3
"""
Session start script for Control Tower.

Gathers session state in a single invocation:
- Ready work (unblocked, not in progress)
- In-progress work (currently claimed)
- Review work (awaiting review)
- Draft issues (need refinement)
- Orphaned issues (mentioned in commits but never closed)
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


def get_meta_task_ids() -> set[str]:
    """
    Get IDs of all tasks under the meta-work epic (spacetraders-m7y).

    Uses single `bd list --parent` call instead of per-task lookups.
    """
    meta_tasks = run_bd(["list", "--parent", "spacetraders-m7y"])
    return {task["id"] for task in meta_tasks}


TASK_DISPLAY_FIELDS = {"id", "title", "status", "priority", "issue_type"}


def slim_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter tasks to display fields only."""
    return [{k: v for k, v in t.items() if k in TASK_DISPLAY_FIELDS} for t in tasks]


def categorize_tasks(
    tasks: list[dict[str, Any]], meta_ids: set[str]
) -> list[dict[str, Any]]:
    """Add 'category' field and filter to display fields only."""
    categorized = []
    for task in tasks:
        slim_task = {k: v for k, v in task.items() if k in TASK_DISPLAY_FIELDS}
        slim_task["category"] = "meta" if task["id"] in meta_ids else "game"
        categorized.append(slim_task)
    return categorized


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


def check_orphans() -> dict[str, Any]:
    """
    Check for orphaned issues (mentioned in commits but never closed).

    Note: `bd orphans --json` currently returns null (bug), so we parse human output.
    Baseline: "✓ No orphaned issues found"

    Returns dict with:
        - found: bool indicating if orphans were detected
        - count: number of orphans (0 if none)
        - message: human-readable output
        - raw_output: original output for debugging when format changes
    """
    result = subprocess.run(
        ["bd", "orphans"],
        capture_output=True,
        text=True,
    )

    output = result.stdout.strip()

    # Known baseline: no orphans
    if "No orphaned issues found" in output:
        return {"found": False, "count": 0, "message": "No orphaned issues"}

    # If output differs from baseline, orphans likely exist
    # Flag for CT to surface to Mark for implementation
    return {
        "found": True,
        "count": -1,  # Unknown count, needs parsing implementation
        "message": "Orphaned issues detected - output format needs implementation",
        "raw_output": output,
    }


def main() -> None:
    pretty = "--pretty" in sys.argv

    # Evaluate gates first (may unblock work)
    gates_result = evaluate_gates()

    # Check for orphaned issues
    orphans_result = check_orphans()

    # Get meta-work task IDs (single bd call)
    meta_ids = get_meta_task_ids()

    # Fetch task lists
    ready_tasks = run_bd(["ready"])
    # Filter out container tasks (epics that aren't directly actionable)
    ready_tasks = [t for t in ready_tasks if "container" not in t.get("labels", [])]
    in_progress_tasks = run_bd(["list", "--status", "in_progress"])
    review_tasks = run_bd(["list", "--status", "review"])
    drafts_tasks = run_bd(["list", "--status", "draft"])

    # Categorize tasks as meta or game work
    categorized_ready = categorize_tasks(ready_tasks, meta_ids)
    categorized_in_progress = categorize_tasks(in_progress_tasks, meta_ids)
    categorized_review = categorize_tasks(review_tasks, meta_ids)

    session_state = {
        "gates": gates_result,
        "orphans": orphans_result,
        "ready": categorized_ready,
        "in_progress": categorized_in_progress,
        "review": categorized_review,
        "drafts": slim_tasks(drafts_tasks),
    }

    # Check for beads updates
    beads_update = check_beads_update()

    # Calculate meta/game breakdown
    meta_ready = sum(1 for t in categorized_ready if t["category"] == "meta")
    game_ready = sum(1 for t in categorized_ready if t["category"] == "game")
    meta_in_progress = sum(
        1 for t in categorized_in_progress if t["category"] == "meta"
    )
    game_in_progress = sum(
        1 for t in categorized_in_progress if t["category"] == "game"
    )
    meta_review = sum(1 for t in categorized_review if t["category"] == "meta")
    game_review = sum(1 for t in categorized_review if t["category"] == "game")

    # Add summary counts (compact one-liner format for meta/game/total)
    session_state["summary"] = {
        "meta": f"RDY: {meta_ready}, PG: {meta_in_progress}, RW: {meta_review}",
        "game": f"RDY: {game_ready}, PG: {game_in_progress}, RW: {game_review}",
        "total": f"RDY: {len(categorized_ready)}, PG: {len(categorized_in_progress)}, RW: {len(categorized_review)}",
        "draft_count": len(drafts_tasks),
        "beads_update_available": beads_update,
        "gates_closed": len(gates_result.get("closed", [])),
        "orphans_found": orphans_result.get("found", False),
    }

    if pretty:
        print(json.dumps(session_state, indent=2))
    else:
        print(json.dumps(session_state))


if __name__ == "__main__":
    main()
