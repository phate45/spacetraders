#!/usr/bin/env python3
"""
end-work.py - Clean merge workflow for completed tasks

Handles rebase-then-merge workflow with conflict detection for beads tasks.

Usage:
    end-work.py <task-id>

Output JSON on success:
    {
        "result": "success",
        "task": {
            "id": "spacetraders-xyz",
            "title": "..."
        },
        "operations": {
            "pulled": true,
            "rebased": true,
            "merged": true,
            "worktree_removed": true,
            "branch_deleted": true,
            "task_closed": true,
            "synced": true,
            "pushed": true
        }
    }

Output JSON on conflict:
    {
        "result": "conflict",
        "task": {
            "id": "spacetraders-xyz",
            "title": "..."
        },
        "conflicting_files": ["file1.rs", "file2.py"],
        "message": "Resolve conflicts, then run end-work again"
    }

Exit codes:
    0: Success (merged)
    1: Error (with JSON error message on stderr)
    2: Conflicts (with JSON conflict info on stdout)
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


def run_command(cmd: list[str], capture_output: bool = True, check: bool = True, cwd: Path = None) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=check,
            cwd=cwd
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

    return data[0]


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


def validate_task_status(task: dict) -> None:
    """
    Validate task is in review status.

    Args:
        task: Task information dict
    """
    status = task.get("status")
    if status != "review":
        error_exit(
            f"Task must be in 'review' status, found '{status}'",
            "Run 'bd update <id> --status review' before merging"
        )


def validate_worktree_exists(worktree_path: Path) -> None:
    """
    Validate worktree exists at the expected location.

    Args:
        worktree_path: Expected worktree path
    """
    if not worktree_path.exists() or not worktree_path.is_dir():
        error_exit(
            f"Worktree not found: {worktree_path}",
            "Expected worktree to exist for task in review"
        )


def validate_no_uncommitted_changes(worktree_path: Path) -> None:
    """
    Validate worktree has no uncommitted changes.

    Args:
        worktree_path: Path to worktree
    """
    result = run_command(
        ["git", "status", "--porcelain"],
        cwd=worktree_path
    )

    if result.stdout.strip():
        error_exit(
            "Worktree has uncommitted changes",
            f"Commit or stash changes before merging:\n{result.stdout}"
        )


def pull_master(project_root: Path) -> None:
    """
    Pull latest master from remote with rebase.

    Args:
        project_root: Project root directory
    """
    # Ensure we're on master
    run_command(
        ["git", "checkout", "master"],
        cwd=project_root
    )

    # Pull with rebase to update local master
    run_command(
        ["git", "pull", "--rebase"],
        cwd=project_root
    )


def rebase_onto_master(worktree_path: Path) -> tuple[bool, list[str]]:
    """
    Rebase worktree branch onto master.

    Args:
        worktree_path: Path to worktree

    Returns:
        Tuple of (success: bool, conflicting_files: list[str])
        success=True means rebase completed cleanly
        success=False means conflicts detected, conflicting_files populated
    """
    result = run_command(
        ["git", "rebase", "master"],
        check=False,
        cwd=worktree_path
    )

    if result.returncode == 0:
        return (True, [])

    # Rebase failed - check if it's conflicts
    # Get list of conflicting files
    conflicts_result = run_command(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        check=False,
        cwd=worktree_path
    )

    conflicting_files = []
    if conflicts_result.stdout.strip():
        conflicting_files = conflicts_result.stdout.strip().split("\n")

    # Abort the rebase to leave worktree in clean state
    run_command(
        ["git", "rebase", "--abort"],
        check=False,
        cwd=worktree_path
    )

    return (False, conflicting_files)


def get_branch_name(worktree_path: Path) -> str:
    """
    Get the branch name of the worktree.

    Args:
        worktree_path: Path to worktree

    Returns:
        Branch name (e.g., "task/q4x")
    """
    result = run_command(
        ["git", "branch", "--show-current"],
        cwd=worktree_path
    )
    return result.stdout.strip()


def merge_branch(project_root: Path, branch_name: str) -> None:
    """
    Fast-forward merge branch into master.

    Args:
        project_root: Project root directory
        branch_name: Branch to merge
    """
    # Ensure we're on master
    run_command(
        ["git", "checkout", "master"],
        cwd=project_root
    )

    # Merge with --ff-only to ensure fast-forward
    run_command(
        ["git", "merge", "--ff-only", branch_name],
        cwd=project_root
    )


def remove_worktree(worktree_path: Path) -> None:
    """
    Remove the worktree.

    Args:
        worktree_path: Path to worktree
    """
    run_command(["git", "worktree", "remove", str(worktree_path)])


def delete_branch(branch_name: str) -> None:
    """
    Delete the task branch.

    Args:
        branch_name: Branch to delete
    """
    run_command(["git", "branch", "-d", branch_name])


def close_task(task_id: str) -> None:
    """
    Close the task in beads.

    Args:
        task_id: Task ID to close
    """
    run_command(["bd", "close", task_id, "-r", "Merged to master", "--json"])


def sync_beads() -> None:
    """Sync beads changes to git."""
    run_command(["bd", "sync", "--json"])


def push_changes(project_root: Path) -> None:
    """
    Push changes to remote.

    Args:
        project_root: Project root directory
    """
    run_command(
        ["git", "push"],
        cwd=project_root
    )


def main():
    parser = argparse.ArgumentParser(
        description="Merge completed task with rebase workflow"
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

    # Validation phase
    validate_task_status(task)
    validate_worktree_exists(worktree_path)
    validate_no_uncommitted_changes(worktree_path)

    # Get branch name before we start operations
    branch_name = get_branch_name(worktree_path)

    # Pull latest master from remote
    pull_master(project_root)

    # Rebase onto master
    rebase_success, conflicting_files = rebase_onto_master(worktree_path)

    if not rebase_success:
        # Output conflict info and exit with special code
        conflict_output = {
            "result": "conflict",
            "task": {
                "id": full_id,
                "title": task["title"]
            },
            "conflicting_files": conflicting_files,
            "message": "Resolve conflicts in worktree, commit resolution, then run end-work again"
        }
        print(json.dumps(conflict_output, indent=2))
        sys.exit(2)

    # Rebase successful - proceed with merge and cleanup
    merge_branch(project_root, branch_name)
    remove_worktree(worktree_path)
    delete_branch(branch_name)
    close_task(full_id)
    sync_beads()
    push_changes(project_root)

    # Output success JSON
    success_output = {
        "result": "success",
        "task": {
            "id": full_id,
            "title": task["title"]
        },
        "operations": {
            "pulled": True,
            "rebased": True,
            "merged": True,
            "worktree_removed": True,
            "branch_deleted": True,
            "task_closed": True,
            "synced": True,
            "pushed": True
        }
    }
    print(json.dumps(success_output, indent=2))


if __name__ == "__main__":
    main()
