# Project hooks

Four hooks, wired in [`.claude/settings.json`](../settings.json). Each is a plain
Node script: Claude Code pipes a JSON event on stdin and reads a JSON decision back
on stdout. Shared plumbing lives in [`lib/hook-io.mjs`](lib/hook-io.mjs).

They are registered in **exec form** (`"command": "node"`, `"args": [...]`) rather
than shell form. On Windows that matters — exec form skips the shell entirely, so
paths with spaces (`C:\Users\...\AI Software Dev\...`) need no quoting gymnastics.

| Hook                                               | Event                           | Matcher                                                  | What it does                              |
| -------------------------------------------------- | ------------------------------- | -------------------------------------------------------- | ----------------------------------------- |
| [`guard-locked-files.mjs`](guard-locked-files.mjs) | `PreToolUse`                    | `Edit\|Write\|NotebookEdit\|MultiEdit\|Bash\|PowerShell` | Denies writes to human-owned config       |
| [`format-after-edit.mjs`](format-after-edit.mjs)   | `PostToolUse`                   | `Edit\|Write\|MultiEdit`                                 | Runs Prettier on the file just written    |
| [`test-after-commit.mjs`](test-after-commit.mjs)   | `PostToolUse`                   | `Bash`                                                   | Runs `npm test` after a `git commit`      |
| [`log-subagent.mjs`](log-subagent.mjs)             | `SubagentStart`, `SubagentStop` | `*`                                                      | Records subagent lifecycle to a JSONL log |

## guard-locked-files

Blocks mutation of the files listed in [`.claude/locked-files.json`](../locked-files.json):
`package.json`, `package-lock.json`, `tsconfig.json`, `vite.config.ts`,
`.github/workflows/*.yml`, and the hook config itself. Patterns support `*` (within
a segment) and `**` (across segments).

Reading a locked file is always allowed; only writes are refused. It covers Bash as
well as the file tools, so `echo x > vite.config.ts`, `sed -i … tsconfig.json` and
`tee package.json` are caught too — otherwise the lock would be one shell command
wide. The Bash patterns are deliberately narrow, so `cat package.json` and
`grep three package.json` still pass.

Escape hatch: `VR_ALLOW_LOCKED_EDITS=1`.

## format-after-edit

Runs Prettier over `.ts .tsx .js .mjs .cjs .json .css .html .md` files after an
edit, skipping `node_modules/`, `dist/`, `output/`, `blender-output/` and anything
in `.prettierignore`. It writes through `fs` rather than handing a diff back to the
Edit tool, so it cannot re-trigger itself.

When it reformats, it returns `additionalContext` telling Claude the file on disk
now differs from what it wrote — without that, Claude's next `Edit` would fail on a
stale `old_string`.

## test-after-commit

Watches Bash calls and runs the suite whenever one actually commits. Detection
tokenises each `&&`/`||`/`;`/`|` segment and steps over git's global options, so
`git -C . commit -m …` counts while `git log --format=%H`, `git commit --dry-run`
and `npm run commit-helper` do not. Empty commits are skipped.

A red suite exits **2**, which is Claude Code's blocking-error channel: stderr goes
straight back into the conversation, so the agent has to deal with a broken tree
rather than moving on to the next task.

Override the target with `VR_TEST_TARGET` (a glob — Node's test runner does not
accept bare directories).

## log-subagent

Appends one JSON line per subagent lifecycle event to `.claude/logs/subagents.jsonl`
(gitignored). This is the durable, in-repo counterpart to the agents-observe
dashboard — see [`docs/day2-hooks-and-observability.md`](../../docs/day2-hooks-and-observability.md).

Note: `SubagentStop` fires once per subagent **turn**, not once per subagent. A
single Explore agent produced nine `SubagentStop` events in testing. Treat
`SubagentStart` as the reliable spawn signal and de-duplicate stops by `agent_id`.

## Tests

```bash
npm test
```

[`tests/hooks.test.mjs`](../../tests/hooks.test.mjs) drives every hook the way
Claude Code drives it — spawn the script, pipe an event on stdin, assert on
stdout/stderr and the exit code. Nothing is mocked. Each hook is checked both for
firing on its own event and for staying silent on everything else.

The post-commit hook's own tests point `VR_TEST_TARGET` at fixtures in
`__fixtures__/` (one green, one red) so the suite does not recurse into itself.
Those fixtures live outside `tests/` so that `npm test` never collects them.

## Known gaps

- Files written by a shell command (`cat > src/foo.ts`) are not formatted; only the
  file tools are matched.
- `guard-locked-files` reads shell commands with regex, not a real parser. It
  catches the common write forms, not every possible one. It raises the cost of an
  accidental edit; it is not a security boundary.
