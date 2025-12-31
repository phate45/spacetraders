#!/usr/bin/env python3
"""
Beads (bd) installer script.

Downloads the latest release from GitHub, extracts it, and installs to ~/.local/bin.
Can also check for updates and upgrade an existing installation.

Usage:
    python install_beads.py                 # Install or upgrade
    python install_beads.py --check         # Check if update available
    python install_beads.py --check --quiet # Output JSON snippet for scripting
    python install_beads.py --force         # Force reinstall even if up to date
    python install_beads.py --doctor        # Run bd doctor with filtered output
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path


GITHUB_API_URL = "https://api.github.com/repos/steveyegge/beads/releases/latest"
INSTALL_DIR = Path.home() / ".local" / "bin"
BINARY_NAME = "bd"
BEADS_REPO_PATH = Path("/tmp/beads")

# Doctor check statuses that indicate issues (filter out "ok")
DOCTOR_ISSUE_STATUSES = {"warning", "error", "fail"}

# Doctor warnings we ignore (local divergence from upstream expectations)
IGNORED_DOCTOR_WARNINGS = {
    "Claude Plugin",
    "Claude Integration",
    "Issues Tracking",  # Expected with sync-branch workflow
}


def get_platform() -> str:
    """Detect OS and architecture, return platform string like 'linux_amd64'."""
    system = platform.system().lower()
    if system not in ("linux", "darwin"):
        raise RuntimeError(f"Unsupported OS: {system}")

    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        arch = "amd64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    return f"{system}_{arch}"


def fetch_latest_release(quiet: bool = False) -> dict:
    """Fetch latest release info from GitHub API."""
    if not quiet:
        print("Fetching latest release info...")

    request = urllib.request.Request(
        GITHUB_API_URL,
        headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "beads-installer"}
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API error: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error: {e.reason}")


def get_installed_version() -> str | None:
    """Get currently installed bd version, or None if not installed."""
    bd_path = INSTALL_DIR / BINARY_NAME
    if not bd_path.exists():
        return None

    try:
        result = subprocess.run(
            [str(bd_path), "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse version from output like "bd version 1.2.3"
            output = result.stdout.strip()
            import re
            return "v" + re.match(r"bd version ([\d.]+).*", output).groups()[0]
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return None


def download_file(url: str, dest: Path) -> None:
    """Download a file with progress indication."""
    print(f"Downloading {url}...")

    request = urllib.request.Request(url, headers={"User-Agent": "beads-installer"})

    with urllib.request.urlopen(request, timeout=60) as response:
        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0
        block_size = 8192

        with open(dest, "wb") as f:
            while True:
                chunk = response.read(block_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                if total_size:
                    percent = (downloaded / total_size) * 100
                    print(f"\r  Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end="", flush=True)

        if total_size:
            print()  # Newline after progress


def extract_and_install(archive_path: Path) -> None:
    """Extract archive and install binary to INSTALL_DIR."""
    print(f"Extracting and installing to {INSTALL_DIR}...")

    INSTALL_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_extract:
        tmp_extract_path = Path(tmp_extract)

        with tarfile.open(archive_path, "r:gz") as tar:
            # Security: check for path traversal
            for member in tar.getmembers():
                if member.name.startswith("/") or ".." in member.name:
                    raise RuntimeError(f"Suspicious path in archive: {member.name}")
            tar.extractall(tmp_extract_path)

        # Find the bd binary
        bd_src = tmp_extract_path / BINARY_NAME
        if not bd_src.exists():
            # Check if it's in a subdirectory
            for item in tmp_extract_path.rglob(BINARY_NAME):
                if item.is_file():
                    bd_src = item
                    break

        if not bd_src.exists():
            raise RuntimeError("Could not find 'bd' binary in archive")

        # Install
        bd_dest = INSTALL_DIR / BINARY_NAME
        shutil.copy2(bd_src, bd_dest)
        bd_dest.chmod(0o755)

        print(f"Installed to {bd_dest}")


def verify_installation() -> bool:
    """Verify the installation works."""
    bd_path = INSTALL_DIR / BINARY_NAME

    if not bd_path.exists():
        print("ERROR: Binary not found after installation")
        return False

    try:
        result = subprocess.run(
            [str(bd_path), "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"Verified: {result.stdout.strip()}")
            return True
        else:
            print(f"ERROR: bd returned non-zero: {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: Could not run bd: {e}")
        return False


def check_path() -> None:
    """Check if INSTALL_DIR is in PATH and warn if not."""
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    install_str = str(INSTALL_DIR)

    if install_str not in path_dirs:
        print(f"\nWARNING: {INSTALL_DIR} is not in your PATH")
        print("Add this to your shell profile (~/.bashrc, ~/.zshrc):")
        print(f'  export PATH="$PATH:{INSTALL_DIR}"')
        print()


def check_beads_repo() -> dict:
    """Check if /tmp/beads repo exists and return status info."""
    exists = BEADS_REPO_PATH.exists() and (BEADS_REPO_PATH / ".git").exists()
    return {
        "exists": exists,
        "path": str(BEADS_REPO_PATH),
        "message": "Ready for changelog review" if exists else "Clone repo to review changelog",
    }


def run_doctor() -> int:
    """Run bd doctor with filtered output for our local setup.

    Filters to show only warning/error/fail statuses, excluding known
    ignorable warnings specific to our sync-branch workflow.
    """
    bd_path = INSTALL_DIR / BINARY_NAME
    if not bd_path.exists():
        print("ERROR: bd not installed")
        return 1

    try:
        result = subprocess.run(
            [str(bd_path), "doctor", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Parse JSON output (doctor outputs to stdout even on warnings)
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fall back to stderr if stdout isn't valid JSON
            print("ERROR: Could not parse doctor output")
            print(result.stdout)
            print(result.stderr)
            return 1

        # Filter checks to only show issues, excluding ignored warnings
        checks = data.get("checks", [])
        issues = [
            check for check in checks
            if check.get("status") in DOCTOR_ISSUE_STATUSES
            and check.get("name") not in IGNORED_DOCTOR_WARNINGS
        ]

        # Output filtered result
        if issues:
            print(json.dumps({"issues": issues}, indent=2))
            return 1
        else:
            print(json.dumps({"issues": [], "message": "All checks passed (or ignorable)"}))
            return 0

    except subprocess.TimeoutExpired:
        print("ERROR: bd doctor timed out")
        return 1
    except FileNotFoundError:
        print("ERROR: bd not found")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Install or update beads (bd)")
    parser.add_argument("--check", action="store_true", help="Only check if update available")
    parser.add_argument("--quiet", action="store_true", help="With --check, output JSON snippet only")
    parser.add_argument("--force", action="store_true", help="Force reinstall even if up to date")
    parser.add_argument("--doctor", action="store_true", help="Run bd doctor with filtered output")
    args = parser.parse_args()

    # Handle --doctor separately (standalone operation)
    if args.doctor:
        return run_doctor()

    quiet = args.quiet and args.check

    def log(msg: str) -> None:
        if not quiet:
            print(msg)

    log("Beads (bd) Installer")
    log("=" * 40)

    try:
        # Detect platform
        plat = get_platform()
        log(f"Platform: {plat}")

        # Get current version
        current = get_installed_version()
        if current:
            log(f"Installed version: {current}")
        else:
            log("Not currently installed")

        # Fetch latest release
        release = fetch_latest_release(quiet=quiet)
        latest = release["tag_name"]
        log(f"Latest version: {latest}")

        # Check if update needed
        update_available = current != latest

        if args.check:
            # Include beads repo status for changelog review
            repo_status = check_beads_repo()

            if quiet:
                print(f'"beads_update_available": {str(update_available).lower()}')
            else:
                if update_available:
                    print(f"\nUpdate available: {current} -> {latest}")
                else:
                    print("\nAlready up to date!")
                print(f"\nChangelog repo: {repo_status['path']}")
                print(f"  Status: {repo_status['message']}")
                if repo_status['exists']:
                    print("  Run: git -C /tmp/beads pull")
            return 1 if update_available else 0

        if not update_available and not args.force:
            log("\nAlready up to date!")
            return 0

        # Find download URL
        archive_name = f"beads_{latest.lstrip('v')}_{plat}.tar.gz"
        download_url = None

        for asset in release.get("assets", []):
            if asset["name"] == archive_name:
                download_url = asset["browser_download_url"]
                break

        if not download_url:
            available = [a["name"] for a in release.get("assets", [])]
            raise RuntimeError(
                f"Could not find {archive_name} in release assets.\n"
                f"Available: {available}"
            )

        # Download and install
        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_path = Path(tmp_dir) / archive_name
            download_file(download_url, archive_path)
            extract_and_install(archive_path)

        # Verify
        if not verify_installation():
            return 1

        check_path()

        print("\nInstallation complete!")
        print("\nGet started:")
        print("  cd your-project")
        print("  bd init")
        print("  bd quickstart")

        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
