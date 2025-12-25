# Worktree File Path Requirements

Agents work in isolated worktrees at `./worktrees/<task-id>`. After entering the worktree, different tools have different path requirements.

## Tool Path Behavior

| Tool Type | Path Style | Example |
|-----------|------------|---------|
| Shell commands (rg, git, ls) | Relative from cwd | `rg "pattern" src/` |
| Read/Edit/Write tools | Full absolute path | `Read("/home/.../worktrees/abc/src/main.rs")` |
| Grep/Glob tools | Full absolute path | `Grep(path="/home/.../worktrees/abc", ...)` |
| bd commands | Run anywhere | `bd show abc --json` (finds .beads/ automatically) |
| Heavy tools (cargo, bun) | Via host-executor | `mcp__host-executor__execute_command(..., worktree="abc")` |

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
