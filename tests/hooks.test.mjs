/**
 * Proof that each hook in .claude/hooks fires on the event it is meant to fire on,
 * and stays out of the way on every other event.
 *
 * Each case drives a hook exactly the way Claude Code drives it: spawn the script,
 * pipe a hook event JSON on stdin, read the decision off stdout/stderr plus the
 * exit code. Nothing is mocked, so a passing run here means the real hook works.
 */
import { test, describe, before, after } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const HOOKS = path.join(ROOT, ".claude", "hooks");
const FIXTURES = path.join(HOOKS, "__fixtures__");
const TMP = path.join(ROOT, "tests", ".tmp");

/** Node's test runner wants a forward-slash glob, even on Windows. */
const fixtureGlob = (name) => `${path.join(FIXTURES, name).split(path.sep).join("/")}/*.test.mjs`;

/** Runs a hook the way Claude Code does and normalises the result. */
function runHook(script, event, env = {}) {
  const result = spawnSync(process.execPath, [path.join(HOOKS, script)], {
    input: JSON.stringify(event),
    encoding: "utf8",
    env: {
      ...process.env,
      CLAUDE_PROJECT_DIR: ROOT,
      VR_ALLOW_LOCKED_EDITS: "",
      VR_TEST_TARGET: "",
      ...env,
    },
  });
  const stdout = (result.stdout || "").trim();
  let json = null;
  if (stdout.startsWith("{")) {
    try {
      json = JSON.parse(stdout);
    } catch {
      json = null;
    }
  }
  return { status: result.status, stdout, stderr: (result.stderr || "").trim(), json };
}

const decisionOf = (result) => result.json?.hookSpecificOutput?.permissionDecision ?? null;
const reasonOf = (result) => result.json?.hookSpecificOutput?.permissionDecisionReason ?? "";
const contextOf = (result) => result.json?.hookSpecificOutput?.additionalContext ?? "";

before(() => fs.mkdirSync(TMP, { recursive: true }));
after(() => fs.rmSync(TMP, { recursive: true, force: true }));

describe("guard-locked-files (PreToolUse)", () => {
  test("denies a Write to package.json", () => {
    const result = runHook("guard-locked-files.mjs", {
      hook_event_name: "PreToolUse",
      tool_name: "Write",
      tool_input: { file_path: path.join(ROOT, "package.json"), content: "{}" },
    });
    assert.equal(decisionOf(result), "deny");
    assert.match(reasonOf(result), /package\.json is protected/);
  });

  test("denies an Edit matched by a glob pattern (.github/workflows/*.yml)", () => {
    const result = runHook("guard-locked-files.mjs", {
      hook_event_name: "PreToolUse",
      tool_name: "Edit",
      tool_input: { file_path: path.join(ROOT, ".github", "workflows", "deploy.yml") },
    });
    assert.equal(decisionOf(result), "deny");
  });

  test("allows edits to ordinary source files", () => {
    for (const file of ["src/data/places.ts", "src/three/TileCard.ts", "src/style.css"]) {
      const result = runHook("guard-locked-files.mjs", {
        hook_event_name: "PreToolUse",
        tool_name: "Edit",
        tool_input: { file_path: path.join(ROOT, file) },
      });
      assert.equal(result.status, 0, `${file} should not be blocked`);
      assert.equal(result.stdout, "", `${file} should produce no decision`);
    }
  });

  test("catches a shell redirect that would clobber a locked file", () => {
    const result = runHook("guard-locked-files.mjs", {
      hook_event_name: "PreToolUse",
      tool_name: "Bash",
      tool_input: { command: 'echo "{}" > vite.config.ts' },
    });
    assert.equal(decisionOf(result), "deny");
    assert.match(reasonOf(result), /vite\.config\.ts/);
  });

  test("catches in-place edits via sed and tee", () => {
    const commands = ["sed -i 's/strict/loose/' tsconfig.json", "cat x | tee package.json"];
    for (const command of commands) {
      const result = runHook("guard-locked-files.mjs", {
        hook_event_name: "PreToolUse",
        tool_name: "Bash",
        tool_input: { command },
      });
      assert.equal(decisionOf(result), "deny", `should block: ${command}`);
    }
  });

  test("leaves read-only shell commands alone", () => {
    const commands = ["cat package.json", "grep three package.json", "npm run build", "git status"];
    for (const command of commands) {
      const result = runHook("guard-locked-files.mjs", {
        hook_event_name: "PreToolUse",
        tool_name: "Bash",
        tool_input: { command },
      });
      assert.equal(result.stdout, "", `should allow: ${command}`);
    }
  });

  test("honours the VR_ALLOW_LOCKED_EDITS escape hatch", () => {
    const result = runHook(
      "guard-locked-files.mjs",
      {
        hook_event_name: "PreToolUse",
        tool_name: "Write",
        tool_input: { file_path: path.join(ROOT, "package.json") },
      },
      { VR_ALLOW_LOCKED_EDITS: "1" },
    );
    assert.equal(result.status, 0);
    assert.equal(result.stdout, "");
  });

  test("ignores tools it does not guard", () => {
    const result = runHook("guard-locked-files.mjs", {
      hook_event_name: "PreToolUse",
      tool_name: "Read",
      tool_input: { file_path: path.join(ROOT, "package.json") },
    });
    assert.equal(result.stdout, "");
  });
});

describe("format-after-edit (PostToolUse)", () => {
  test("reformats a badly formatted file Claude just wrote", () => {
    const file = path.join(TMP, "messy.ts");
    fs.writeFileSync(file, "const   place='jaipur'   ;\n\n\n\nexport    {place}\n");
    const result = runHook("format-after-edit.mjs", {
      hook_event_name: "PostToolUse",
      tool_name: "Edit",
      tool_input: { file_path: file },
    });
    const after = fs.readFileSync(file, "utf8");
    assert.equal(after, 'const place = "jaipur";\n\nexport { place };\n');
    assert.match(contextOf(result), /Auto-formatted/);
  });

  test("stays silent when the file is already formatted", () => {
    const file = path.join(TMP, "clean.ts");
    const clean = 'export const city = "udaipur";\n';
    fs.writeFileSync(file, clean);
    const result = runHook("format-after-edit.mjs", {
      hook_event_name: "PostToolUse",
      tool_name: "Write",
      tool_input: { file_path: file },
    });
    assert.equal(result.status, 0);
    assert.equal(result.stdout, "");
    assert.equal(fs.readFileSync(file, "utf8"), clean);
  });

  test("ignores files Prettier has no business touching", () => {
    const file = path.join(TMP, "tile.glb");
    fs.writeFileSync(file, "binary-ish");
    const result = runHook("format-after-edit.mjs", {
      hook_event_name: "PostToolUse",
      tool_name: "Write",
      tool_input: { file_path: file },
    });
    assert.equal(result.stdout, "");
    assert.equal(fs.readFileSync(file, "utf8"), "binary-ish");
  });

  test("ignores paths under build output directories", () => {
    const distDir = path.join(ROOT, "dist");
    fs.mkdirSync(distDir, { recursive: true });
    const file = path.join(distDir, "hook-probe.ts");
    fs.writeFileSync(file, "const   x=1\n");
    try {
      const result = runHook("format-after-edit.mjs", {
        hook_event_name: "PostToolUse",
        tool_name: "Write",
        tool_input: { file_path: file },
      });
      assert.equal(result.stdout, "");
      assert.equal(fs.readFileSync(file, "utf8"), "const   x=1\n");
    } finally {
      fs.rmSync(file, { force: true });
    }
  });

  test("does not run for non-edit tools", () => {
    const file = path.join(TMP, "untouched.ts");
    fs.writeFileSync(file, "const   y=2\n");
    const result = runHook("format-after-edit.mjs", {
      hook_event_name: "PostToolUse",
      tool_name: "Bash",
      tool_input: { command: "ls" },
    });
    assert.equal(result.stdout, "");
    assert.equal(fs.readFileSync(file, "utf8"), "const   y=2\n");
  });
});

describe("test-after-commit (PostToolUse)", () => {
  const commitEvent = (command) => ({
    hook_event_name: "PostToolUse",
    tool_name: "Bash",
    tool_input: { command },
    tool_response: { type: "text", text: "[main abc1234] feat: add tile" },
  });

  test("runs the suite after a real commit and reports success", () => {
    const result = runHook(
      "test-after-commit.mjs",
      commitEvent('git commit -m "feat: add jawai tile"'),
      { VR_TEST_TARGET: fixtureGlob("passing") },
    );
    assert.equal(result.status, 0);
    assert.match(contextOf(result), /test suite passed \(1 tests\)/);
  });

  test("blocks with exit code 2 when the suite is red", () => {
    const result = runHook("test-after-commit.mjs", commitEvent('git commit -m "feat: break it"'), {
      VR_TEST_TARGET: fixtureGlob("failing"),
    });
    assert.equal(result.status, 2, "exit 2 is the channel Claude actually reads");
    assert.match(result.stderr, /test suite FAILED/);
    assert.match(result.stderr, /fixture suite fails on purpose/);
  });

  test("sees through global git options and command chains", () => {
    const commands = ['git -C . commit -m "x"', 'git add -A && git commit -m "x"'];
    for (const command of commands) {
      const result = runHook("test-after-commit.mjs", commitEvent(command), {
        VR_TEST_TARGET: fixtureGlob("passing"),
      });
      assert.match(contextOf(result), /test suite passed/, `should have run for: ${command}`);
    }
  });

  test("does not fire on git commands that are not commits", () => {
    const commands = [
      "git status",
      "git log --oneline -5",
      "git show --format=%H",
      "git diff --cached",
    ];
    for (const command of commands) {
      const result = runHook("test-after-commit.mjs", commitEvent(command), {
        VR_TEST_TARGET: fixtureGlob("failing"),
      });
      assert.equal(result.status, 0, `should not fire for: ${command}`);
      assert.equal(result.stdout, "", `should stay silent for: ${command}`);
    }
  });

  test("does not fire on a dry run, or on non-git commands containing the word commit", () => {
    const commands = ['git commit --dry-run -m "x"', "npm run commit-helper", "echo commit"];
    for (const command of commands) {
      const result = runHook("test-after-commit.mjs", commitEvent(command), {
        VR_TEST_TARGET: fixtureGlob("failing"),
      });
      assert.equal(result.status, 0, `should not fire for: ${command}`);
    }
  });

  test("skips an empty commit", () => {
    const result = runHook(
      "test-after-commit.mjs",
      {
        hook_event_name: "PostToolUse",
        tool_name: "Bash",
        tool_input: { command: 'git commit -m "x"' },
        tool_response: { type: "text", text: "nothing to commit, working tree clean" },
      },
      { VR_TEST_TARGET: fixtureGlob("failing") },
    );
    assert.equal(result.status, 0);
  });

  test("ignores non-Bash tools", () => {
    const result = runHook(
      "test-after-commit.mjs",
      {
        hook_event_name: "PostToolUse",
        tool_name: "Edit",
        tool_input: { file_path: "src/main.ts" },
      },
      { VR_TEST_TARGET: fixtureGlob("failing") },
    );
    assert.equal(result.status, 0);
    assert.equal(result.stdout, "");
  });
});

describe("log-subagent (SubagentStart / SubagentStop)", () => {
  test("records an Explore subagent's start and stop", () => {
    const sandbox = path.join(TMP, "agent-sandbox");
    fs.mkdirSync(sandbox, { recursive: true });
    const logFile = path.join(sandbox, ".claude", "logs", "subagents.jsonl");

    for (const hookEventName of ["SubagentStart", "SubagentStop"]) {
      const result = runHook(
        "log-subagent.mjs",
        {
          hook_event_name: hookEventName,
          agent_type: "Explore",
          agent_id: "sub-1234",
          session_id: "sess-abcd",
          description: "investigate how tiles are loaded",
        },
        { CLAUDE_PROJECT_DIR: sandbox },
      );
      assert.match(contextOf(result), new RegExp(hookEventName));
    }

    const lines = fs
      .readFileSync(logFile, "utf8")
      .trim()
      .split("\n")
      .map((line) => JSON.parse(line));
    assert.equal(lines.length, 2);
    assert.deepEqual(
      lines.map((line) => line.event),
      ["SubagentStart", "SubagentStop"],
    );
    assert.equal(lines[0].agent_type, "Explore");
    assert.equal(lines[0].agent_id, "sub-1234");
    assert.match(lines[0].ts, /^\d{4}-\d{2}-\d{2}T/);
  });

  test("ignores unrelated hook events", () => {
    const sandbox = path.join(TMP, "agent-sandbox-quiet");
    fs.mkdirSync(sandbox, { recursive: true });
    const result = runHook(
      "log-subagent.mjs",
      { hook_event_name: "PreToolUse", tool_name: "Bash", tool_input: { command: "ls" } },
      { CLAUDE_PROJECT_DIR: sandbox },
    );
    assert.equal(result.status, 0);
    assert.equal(result.stdout, "");
    assert.equal(fs.existsSync(path.join(sandbox, ".claude", "logs", "subagents.jsonl")), false);
  });
});
