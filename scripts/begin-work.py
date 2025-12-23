#!/usr/bin/env python3
"""
begin-work.py - Worktree setup for agent task execution

Creates or detects worktrees for beads tasks and outputs agent-friendly JSON.

Usage:
    begin-work.py <task-id>

Output JSON:
    {
        "task": {
            "id": "spacetraders-xyz",
            "title": "...",
            "description": "...",
            "design": "...",
            "acceptance_criteria": "...",
            "notes": "..."
        },
        "workspace": {
            "worktree_path": "./worktrees/xyz",
            "worktree_name": "xyz",
            "branch_name": "task/xyz"
        },
        "mode": "new" | "resume"
    }

Exit codes:
    0: Success
    1: Error (with JSON error message on stderr)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def error_exit(message: str, details: str = "") -> None:
    """Exit with error JSON on stderr and non-zero exit code."""
    error_obj = {"error": message}
    if details:
        error_obj["details"] = details
    print(json.dumps(error_obj), file=sys.stderr)
    sys.exit(1)


def run_command(cmd: list[str], capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=check
        )
    except subprocess.CalledProcessError as e:
        error_exit(
            f"Command failed: {' '.join(cmd)}",
            f"Exit code: {e.returncode}\nStderr: {e.stderr}"
        )
    except FileNotFoundError:
        error_exit(f"Command not found: {cmd[0]}")


def get_task_info(task_id: str) -> dict:
    """
    Fetch task information from beads.

    Args:
        task_id: Task ID (short or full form)

    Returns:
        Task information dict
    """
    result = run_command(["bd", "show", task_id, "--json"])

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        error_exit("Failed to parse bd show output", str(e))

    if not data or not isinstance(data, list) or len(data) == 0:
        error_exit(f"Task not found: {task_id}")

    task = data[0]

    # Validate task is not closed
    if task.get("status") == "closed":
        error_exit(f"Task {task_id} is already closed")

    return task


def get_project_root() -> Path:
    """Get the project root directory (where .git exists)."""
    result = run_command(["git", "rev-parse", "--show-toplevel"])
    return Path(result.stdout.strip())


def extract_short_id(full_id: str) -> str:
    """Extract short ID from full ID (e.g., 'spacetraders-q4x' -> 'q4x')."""
    parts = full_id.split("-", 1)
    if len(parts) != 2:
        error_exit(f"Invalid task ID format: {full_id}")
    return parts[1]


def check_worktree_exists(worktree_path: Path) -> bool:
    """Check if a worktree exists at the given path."""
    return worktree_path.exists() and worktree_path.is_dir()


def get_branch_name(task: dict, short_id: str) -> str:
    """
    Generate branch name from task type and short ID.

    Format: <type>/<short-id>
    Example: task/q4x, bug/abc, feature/xyz
    """
    issue_type = task.get("issue_type", "task")
    return f"{issue_type}/{short_id}"


def create_worktree(worktree_path: Path, branch_name: str) -> None:
    """
    Create a new worktree and branch.

    Args:
        worktree_path: Path where worktree should be created
        branch_name: Name of the branch to create
    """
    # Ensure worktrees directory exists
    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    # Create worktree with new branch based on master
    run_command([
        "git", "worktree", "add",
        str(worktree_path),
        "-b", branch_name,
        "master"
    ])


def set_task_in_progress(task_id: str) -> None:
    """Set task status to in_progress to claim work."""
    run_command(["bd", "update", task_id, "--status", "in_progress"])


def determine_mode(task: dict, worktree_exists: bool) -> str:
    """
    Determine work mode based on task status and worktree existence.

    Rules:
    - status=in_progress + worktree exists = resume
    - status=review + worktree exists = resume (feedback rework)
    - status=open + no worktree = new
    - Other combinations are errors
    """
    status = task.get("status")

    if status == "in_progress" and worktree_exists:
        return "resume"
    elif status == "review" and worktree_exists:
        return "resume"
    elif status == "open" and not worktree_exists:
        return "new"
    elif status == "in_progress" and not worktree_exists:
        error_exit(
            f"Task {task['id']} is in_progress but worktree doesn't exist",
            "Inconsistent state - task marked as started but no worktree found"
        )
    elif status == "open" and worktree_exists:
        error_exit(
            f"Task {task['id']} is open but worktree already exists",
            "Inconsistent state - worktree exists but task not marked as started"
        )
    elif status == "review" and not worktree_exists:
        error_exit(
            f"Task {task['id']} is in review but worktree doesn't exist",
            "Inconsistent state - can't resume review without worktree"
        )
    else:
        error_exit(
            f"Unexpected task status: {status}",
            f"Worktree exists: {worktree_exists}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Set up worktree for beads task execution"
    )
    parser.add_argument(
        "task_id",
        help="Beads task ID (short form like 'q4x' or full form like 'spacetraders-q4x')"
    )

    args = parser.parse_args()

    # Get task information
    task = get_task_info(args.task_id)

    # Extract IDs
    full_id = task["id"]
    short_id = extract_short_id(full_id)

    # Determine paths
    project_root = get_project_root()
    worktree_path = project_root / "worktrees" / short_id

    # Check worktree existence
    worktree_exists = check_worktree_exists(worktree_path)

    # Capture original status for transition logic
    original_status = task.get("status")

    # Determine mode
    mode = determine_mode(task, worktree_exists)

    # Create worktree if in 'new' mode
    if mode == "new":
        branch_name = get_branch_name(task, short_id)
        create_worktree(worktree_path, branch_name)
        set_task_in_progress(full_id)
    else:
        # Resume mode - transition from review back to in_progress if needed
        if original_status == "review":
            set_task_in_progress(full_id)
        # In resume mode, get the branch name from the worktree
        # Use git worktree list to find the branch
        result = run_command(["git", "worktree", "list", "--porcelain"])
        branch_name = None
        found_worktree = False

        lines = result.stdout.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("worktree ") and str(worktree_path) in line:
                # Found our worktree, look for branch in subsequent lines
                found_worktree = True
                continue

            if found_worktree and line.startswith("branch "):
                # Extract branch name (format: "branch refs/heads/task/q4x")
                branch_ref = line.split(" ", 1)[1]
                if branch_ref.startswith("refs/heads/"):
                    branch_name = branch_ref.replace("refs/heads/", "")
                break

            # Empty line marks end of worktree entry
            if found_worktree and line == "":
                break

        if not branch_name:
            # Fallback: reconstruct from task type
            branch_name = get_branch_name(task, short_id)

    # Build output JSON
    output = {
        "task": {
            "id": task["id"],
            "title": task["title"],
            "description": task.get("description", ""),
            "design": task.get("design", ""),
            "acceptance_criteria": task.get("acceptance_criteria", ""),
            "notes": task.get("notes", "")
        },
        "workspace": {
            "worktree_path": str(worktree_path.relative_to(project_root)),
            "worktree_name": short_id,
            "branch_name": branch_name
        },
        "mode": mode
    }

    # Output JSON to stdout
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
