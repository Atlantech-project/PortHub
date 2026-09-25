## Main idea

Git submodules let you embed one Git repository inside another as a subdirectory, while keeping their histories completely separate. This solves the problem of using a third-party or shared library inside your project without losing the ability to customize it or cleanly track upstream updates (unlike vendoring/copying code, or plain package managers). The parent repo doesn't track the submodule's file contents — it just records a pointer to a specific commit SHA of the submodule.

## Key commands

**Setting up**
| Command | Use / Cause |
|---|---|
| `git submodule add <url> [path]` | Add a repo as a submodule; creates `.gitmodules` mapping path→URL |
| `git clone --recurse-submodules <url>` | Clone a project and auto-populate its submodules in one step |
| `git submodule init` | Register submodule config locally (after a plain clone) |
| `git submodule update` | Fetch and checkout the exact commit the superproject expects |
| `git submodule update --init --recursive` | Combo: init + fetch + checkout, including nested submodules |

**Inspecting**
| Command | Use / Cause |
|---|---|
| `git diff --submodule` (or `git config --global diff.submodule log`) | Show which submodule commits changed, not just the SHA |
| `git status` (with `git config status.submodulesummary 1`) | Show submodule commit summary in status output |
| `git log -p --submodule` | Include submodule commit logs in history view |

**Updating from upstream**
| Command | Use / Cause |
|---|---|
| `git submodule update --remote [name]` | Pull the latest commit from the submodule's tracked branch (default: remote HEAD, or set via `submodule.<name>.branch`) |
| `git submodule update --remote --merge` | Same, but merge into your local submodule branch instead of detaching HEAD |
| `git submodule update --remote --rebase` | Same, but rebase your local submodule work on top |
| `git submodule sync --recursive` | Fix local config if the submodule's URL changed upstream |
| `git config submodule.recurse true` | Make Git auto-recurse into submodules for supported commands (checkout, pull, etc.) |

**Publishing your changes**
| Command | Use / Cause |
|---|---|
| `git push --recurse-submodules=check` | Abort push if submodule commits weren't pushed first (prevents others getting broken refs) |
| `git push --recurse-submodules=on-demand` | Auto-push submodule changes before pushing the parent repo |
| `git config push.recurseSubmodules on-demand`/`check` | Make either behavior the default |

**Bulk operations**
| Command | Use / Cause |
|---|---|
| `git submodule foreach '<cmd>'` | Run any Git command across all submodules (e.g. `git stash`, `git checkout -b featureA`) |

## Key causes/gotchas to know
- **Detached HEAD**: `git submodule update` by default leaves the submodule in detached HEAD — you must `git checkout <branch>` inside it before committing local work, or changes can be lost.
- **Merge conflicts on submodule pointers**: if two branches record diverging submodule commits, Git can't auto-merge; you resolve it manually inside the submodule directory, then re-add/commit the resulting SHA in the parent.
- **Branch switching**: older Git (<2.13) leaves stale/untracked submodule directories when switching branches; use `git checkout --recurse-submodules` (Git ≥2.13) to avoid this.
- **Subdirectory → submodule conversion**: you must `git rm -r <dir>` before `git submodule add` on the same path, or Git refuses (index already tracks it).