# Worktree File Path Requirements

Agents work in isolated worktrees at `./worktrees/<task-id>`. After entering the worktree, different tools have different path requirements.

## Worktree ↔ Branch Name Correspondence

The worktree directory name, task ID, and branch name suffix are all the same:
- **Task ID:** `spacetraders-4dl.6`
- **Worktree:** `./worktrees/4dl.6`
- **Branch:** `feature/4dl.6`

This redundancy is intentional. Use it to verify you're in the right place. If `git branch` shows `feature/4dl.6` but you're trying to navigate to `worktrees/4dl`, you have a typo.

## Tool Path Behavior

| Tool Type | Path Style | Example |
|-----------|------------|---------|
| Shell commands (rg, git, ls) | Relative from cwd | `rg "pattern" src/` |
| Read/Edit/Write tools | Full absolute path | `Read("/home/.../worktrees/abc/src/main.rs")` |
| Grep/Glob tools | Full absolute path | `Grep(path="/home/.../worktrees/abc", ...)` |
| bd commands | Run anywhere | `bd show abc --json` (finds .beads/ automatically) |
| `cargo` and `bun` only | Via host-executor MCP | `mcp__host-executor__execute_command(tool="cargo", args="check", worktree="abc")` |

## Why This Matters

After `cd worktrees/<id>`, your shell's working directory changes. Shell commands inherit this and use relative paths correctly.

But Claude Code tools (Read, Edit, Write, Grep, Glob) don't inherit shell cwd—they resolve paths from the project root. If you use a relative path or main repo path, you'll read/edit the **wrong files**.

## Correct vs Wrong

```
After: cd /home/user/project/worktrees/abc && pwd

Shell command (correct):
  rg "TODO" src/           # Searches worktree/src/

Read tool:
  ✅ Read("/home/user/project/worktrees/abc/src/main.rs")  # Worktree file
  ❌ Read("src/main.rs")                                    # Wrong: relative path
  ❌ Read("/home/user/project/src/main.rs")                 # Wrong: main repo path

Grep tool:
  ✅ Grep(path="/home/user/project/worktrees/abc", pattern="TODO")
  ❌ Grep(path="/home/user/project", pattern="TODO")        # Wrong: main repo
```

## Quick Rule

**Shell tools:** relative paths work after `cd`.

**Claude tools (Read/Edit/Write/Grep/Glob):** always use full path including `/worktrees/<id>/`.

**bd:** works from anywhere—no path needed.
