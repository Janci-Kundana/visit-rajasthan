#!/usr/bin/env node
/**
 * PostToolUse verifier: runs the test suite immediately after a `git commit`.
 *
 * A commit is the point where a mistake becomes history, so this is the cheapest
 * place to catch one. Failures come back on exit code 2, which is Claude Code's
 * blocking-error channel: the agent sees the output and has to deal with it
 * rather than moving on to the next task.
 */
import { spawnSync } from "node:child_process";
import { readEvent, projectRoot, respond, blockWith, passThrough } from "./lib/hook-io.mjs";

/** Global git options that take a value, so the subcommand scan can step over them. */
const GIT_OPTS_WITH_VALUE = new Set([
  "-C",
  "-c",
  "--exec-path",
  "--git-dir",
  "--work-tree",
  "--namespace",
]);

/**
 * True only when a segment actually invokes the `commit` subcommand. Guards against
 * false positives like `git log --format=%H commit` or `git status`.
 */
function isGitCommit(segment) {
  const tokens = segment.trim().split(/\s+/).filter(Boolean);
  const gitIndex = tokens.findIndex((token) => /(?:^|[/\\])git(?:\.exe)?$/i.test(token));
  if (gitIndex === -1) return false;

  let i = gitIndex + 1;
  while (i < tokens.length) {
    const token = tokens[i];
    if (GIT_OPTS_WITH_VALUE.has(token)) {
      i += 2;
      continue;
    }
    if (token.startsWith("-")) {
      i += 1;
      continue;
    }
    break;
  }
  if (tokens[i] !== "commit") return false;
  return !tokens.slice(i).includes("--dry-run");
}

function commandCommits(command) {
  if (!command) return false;
  return command.split(/&&|\|\||;|\|/).some((segment) => isGitCommit(segment));
}

const event = await readEvent();
if ((event.tool_name || "") !== "Bash") passThrough();

const toolInput = event.tool_input || {};
if (!commandCommits(toolInput.command)) passThrough();

// A no-op commit is not worth a test run.
const responseText = JSON.stringify(event.tool_response || "");
if (/nothing to commit|no changes added to commit/i.test(responseText)) passThrough();

const root = projectRoot(event);
// Node's test runner takes glob patterns, not bare directories. Forward slashes
// work on Windows too, since Node expands the pattern itself without a shell.
const target = process.env.VR_TEST_TARGET || "tests/**/*.test.mjs";

// NODE_TEST_CONTEXT is set whenever this hook is itself launched from a test run.
// Leaving it set would put the child runner in child-process reporter mode, which
// swallows its exit code — so the suite would always look green.
const childEnv = { ...process.env, VR_TEST_TARGET: "" };
delete childEnv.NODE_TEST_CONTEXT;

const result = spawnSync(process.execPath, ["--test", target], {
  cwd: root,
  encoding: "utf8",
  timeout: 120000,
  env: childEnv,
});

const output = `${result.stdout || ""}${result.stderr || ""}`.trim();

if (result.status === 0) {
  // Node's default reporter prefixes the summary with an info glyph, TAP with "#".
  const pass = output.match(/^[#ℹ]\s*pass (\d+)/m)?.[1] ?? "?";
  respond({
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: `Post-commit hook: test suite passed (${pass} tests) against ${target}.`,
    },
    systemMessage: `Tests passed after commit (${pass} tests).`,
  });
}

blockWith(
  `Post-commit hook: the test suite FAILED after your commit.\n` +
    `The commit exists but the tree is red — fix it before doing anything else.\n\n` +
    `${output.slice(-4000)}\n`,
);
