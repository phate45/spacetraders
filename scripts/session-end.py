#!/usr/bin/env python3
"""
Session end script for Control Tower.

Handles the mechanical parts of session close:
- Check for uncommitted changes
- Sync beads
- Pull with rebase
- Push to remote
- Verify state

Usage:
    python3 scripts/session-end.py
    python3 scripts/session-end.py --pretty

Output JSON:
    {
        "result": "success" | "conflict" | "dirty",
        "pre_state": {
            "uncommitted_files": [...],
            "beads_pending": true/false
        },
        "operations": {
            "synced": true,
            "pulled": true,
            "pushed": true
        },
        "post_state": {
            "up_to_date": true,
            "branch": "master"
        },
        "session_summary": {
            "in_progress_count": 2,
            "review_count": 1,
            "open_count": 5
        },
        "message": "Session closed cleanly"
    }

Exit codes:
    0: Success
    1: Error (with JSON error message)
    2: Conflicts detected (manual resolution needed)
    3: Dirty state (uncommitted non-beads changes)
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(
    cmd: list[str],
    capture_output: bool = True,
    check: bool = True,
    cwd: Path = None
) -> subprocess.CompletedProcess:
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
        return e
    except FileNotFoundError:
        error_exit(f"Command not found: {cmd[0]}")


def error_exit(message: str, details: str = "") -> None:
    """Exit with error JSON and non-zero exit code."""
    error_obj = {"result": "error", "error": message}
    if details:
        error_obj["details"] = details
    print(json.dumps(error_obj, indent=2))
    sys.exit(1)


def get_project_root() -> Path:
    """Get the project root directory."""
    result = run_command(["git", "rev-parse", "--show-toplevel"])
    if isinstance(result, subprocess.CalledProcessError):
        error_exit("Not in a git repository")
    return Path(result.stdout.strip())


def get_uncommitted_files(project_root: Path) -> list[str]:
    """Get list of uncommitted files."""
    result = run_command(
        ["git", "status", "--porcelain"],
        cwd=project_root,
        check=False
    )
    if isinstance(result, subprocess.CalledProcessError) or not result.stdout.strip():
        return []
    return result.stdout.strip().split("\n")


def has_beads_pending(project_root: Path) -> bool:
    """Check if there are pending beads changes."""
    result = run_command(
        ["bd", "sync", "--status", "--json"],
        check=False
    )
    if isinstance(result, subprocess.CalledProcessError):
        return False

    try:
        data = json.loads(result.stdout)
        # bd sync --status returns info about pending changes
        return data.get("pending", False) or data.get("uncommitted", False)
    except (json.JSONDecodeError, AttributeError):
        return False


def is_beads_only(files: list[str]) -> bool:
    """Check if all changed files are in .beads/ directory."""
    for f in files:
        # Format is "XY path" or "XY path -> newpath"
        parts = f.strip().split()
        if len(parts) >= 2:
            path = parts[-1]  # Last part is the path
            if not path.startswith(".beads/"):
                return False
    return True


def sync_beads() -> bool:
    """Run bd sync. Returns True on success."""
    result = run_command(["bd", "sync"], check=False)
    return not isinstance(result, subprocess.CalledProcessError) and result.returncode == 0


def pull_rebase(project_root: Path) -> tuple[bool, list[str]]:
    """
    Pull with rebase.

    Returns:
        Tuple of (success, conflicting_files)
    """
    result = run_command(
        ["git", "pull", "--rebase"],
        cwd=project_root,
        check=False
    )

    if isinstance(result, subprocess.CalledProcessError) or result.returncode != 0:
        # Check for conflicts
        conflicts_result = run_command(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=project_root,
            check=False
        )

        conflicting_files = []
        if not isinstance(conflicts_result, subprocess.CalledProcessError) and conflicts_result.stdout.strip():
            conflicting_files = conflicts_result.stdout.strip().split("\n")

        if conflicting_files:
            return (False, conflicting_files)

        # Some other pull failure
        error_msg = result.stderr if hasattr(result, 'stderr') else "Unknown error"
        error_exit("git pull --rebase failed", error_msg)

    return (True, [])


def push_changes(project_root: Path) -> bool:
    """Push to remote. Returns True on success."""
    result = run_command(
        ["git", "push"],
        cwd=project_root,
        check=False
    )
    return not isinstance(result, subprocess.CalledProcessError) and result.returncode == 0


def verify_up_to_date(project_root: Path) -> tuple[bool, str]:
    """
    Verify we're up to date with remote.

    Returns:
        Tuple of (up_to_date, current_branch)
    """
    # Get current branch
    branch_result = run_command(
        ["git", "branch", "--show-current"],
        cwd=project_root,
        check=False
    )
    branch = branch_result.stdout.strip() if not isinstance(branch_result, subprocess.CalledProcessError) else "unknown"

    # Check status
    status_result = run_command(
        ["git", "status", "--porcelain", "-b"],
        cwd=project_root,
        check=False
    )

    if isinstance(status_result, subprocess.CalledProcessError):
        return (False, branch)

    # First line shows branch tracking info
    # If we're up to date, it should just show "## branch...origin/branch"
    # If ahead/behind, it shows "## branch...origin/branch [ahead N]" etc.
    first_line = status_result.stdout.split("\n")[0] if status_result.stdout else ""
    up_to_date = "[ahead" not in first_line and "[behind" not in first_line

    return (up_to_date, branch)


def get_session_summary() -> dict:
    """Get counts of issues by status."""
    summary = {
        "in_progress_count": 0,
        "review_count": 0,
        "open_count": 0
    }

    for status, key in [("in_progress", "in_progress_count"),
                        ("review", "review_count"),
                        ("open", "open_count")]:
        result = run_command(
            ["bd", "list", "--status", status, "--json"],
            check=False
        )
        if not isinstance(result, subprocess.CalledProcessError) and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                summary[key] = len(data) if data else 0
            except json.JSONDecodeError:
                pass

    return summary


def main() -> None:
    pretty = "--pretty" in sys.argv

    project_root = get_project_root()

    # Gather pre-state
    uncommitted = get_uncommitted_files(project_root)
    beads_pending = has_beads_pending(project_root)

    pre_state = {
        "uncommitted_files": uncommitted,
        "beads_pending": beads_pending
    }

    # Check for non-beads uncommitted changes
    if uncommitted and not is_beads_only(uncommitted):
        output = {
            "result": "dirty",
            "pre_state": pre_state,
            "message": "Uncommitted non-beads changes detected. Commit or stash before closing session.",
            "session_summary": get_session_summary()
        }
        print(json.dumps(output, indent=2 if pretty else None))
        sys.exit(3)

    operations = {
        "synced": False,
        "pulled": False,
        "pushed": False
    }

    # Sync beads first
    if sync_beads():
        operations["synced"] = True

    # Pull with rebase
    pull_success, conflicts = pull_rebase(project_root)

    if not pull_success:
        output = {
            "result": "conflict",
            "pre_state": pre_state,
            "operations": operations,
            "conflicting_files": conflicts,
            "message": "Rebase conflicts detected. Resolve manually, then run session-end again.",
            "session_summary": get_session_summary()
        }
        print(json.dumps(output, indent=2 if pretty else None))
        sys.exit(2)

    operations["pulled"] = True

    # Sync again after pull (in case pull brought in beads changes)
    sync_beads()

    # Push
    if push_changes(project_root):
        operations["pushed"] = True
    else:
        error_exit("git push failed", "Check remote connectivity and permissions")

    # Final sync after push
    sync_beads()
    operations["synced"] = True

    # Verify state
    up_to_date, branch = verify_up_to_date(project_root)

    post_state = {
        "up_to_date": up_to_date,
        "branch": branch
    }

    output = {
        "result": "success",
        "pre_state": pre_state,
        "operations": operations,
        "post_state": post_state,
        "session_summary": get_session_summary(),
        "message": "Session closed cleanly" if up_to_date else "Pushed but may not be fully up to date"
    }

    print(json.dumps(output, indent=2 if pretty else None))


if __name__ == "__main__":
    main()
