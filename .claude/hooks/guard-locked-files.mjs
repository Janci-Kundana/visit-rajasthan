#!/usr/bin/env node
/**
 * PreToolUse guard: refuses agent writes to human-owned config.
 *
 * Fires on Edit / Write / NotebookEdit (direct file writes) and on Bash, where it
 * looks for shell constructs that would clobber a locked file behind the file
 * tools' back (`>`, `>>`, `sed -i`, `tee`, `rm`, `mv`, `cp`).
 *
 * Reading locked files is always fine; only mutation is blocked.
 */
import fs from "node:fs";
import path from "node:path";
import {
  readEvent,
  projectRoot,
  relativePath,
  respond,
  passThrough,
  matchesGlob,
} from "./lib/hook-io.mjs";

const FILE_TOOLS = new Set(["Edit", "Write", "NotebookEdit", "MultiEdit"]);

function loadLockList(root) {
  try {
    const raw = fs.readFileSync(path.join(root, ".claude", "locked-files.json"), "utf8");
    const parsed = JSON.parse(raw);
    return {
      locked: Array.isArray(parsed.locked) ? parsed.locked : [],
      reason: parsed.reason || "This file is locked by project policy.",
    };
  } catch {
    return { locked: [], reason: "" };
  }
}

function deny(target, reason) {
  respond({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason:
        `Blocked by the locked-files hook: ${target} is protected.\n${reason}\n` +
        `Locked paths live in .claude/locked-files.json. If this edit is genuinely ` +
        `intended, ask the user to make it, or re-run with VR_ALLOW_LOCKED_EDITS=1.`,
    },
  });
}

/**
 * Bash side of the guard. Deliberately conservative: it only trips on tokens that
 * clearly write, so `cat package.json` or `grep three package.json` stay allowed.
 */
function lockedTargetInCommand(command, locked, root) {
  if (!command) return null;
  const writeRedirect = /(?:^|[^>\d])>>?\s*("[^"]+"|'[^']+'|[^\s;&|]+)/g;
  const candidates = [];

  for (const match of command.matchAll(writeRedirect)) {
    candidates.push(match[1]);
  }
  const mutators =
    /\b(?:sed\s+-i[^\s]*|tee(?:\s+-a)?|rm(?:\s+-[^\s]+)*|mv|cp|truncate[^\s]*)\s+([^;&|]+)/g;
  for (const match of command.matchAll(mutators)) {
    for (const token of match[1].split(/\s+/)) {
      if (token && !token.startsWith("-")) candidates.push(token);
    }
  }

  for (const rawToken of candidates) {
    const token = rawToken.replace(/^["']|["']$/g, "").trim();
    if (!token) continue;
    const rel = relativePath(root, token);
    if (!rel) continue;
    if (locked.some((pattern) => matchesGlob(pattern, rel))) return rel;
  }
  return null;
}

const event = await readEvent();

if (process.env.VR_ALLOW_LOCKED_EDITS === "1") passThrough();

const root = projectRoot(event);
const { locked, reason } = loadLockList(root);
if (locked.length === 0) passThrough();

const toolName = event.tool_name || "";
const toolInput = event.tool_input || {};

if (FILE_TOOLS.has(toolName)) {
  const rel = relativePath(root, toolInput.file_path || toolInput.notebook_path);
  if (rel && locked.some((pattern) => matchesGlob(pattern, rel))) deny(rel, reason);
  passThrough();
}

if (toolName === "Bash" || toolName === "PowerShell") {
  const hit = lockedTargetInCommand(toolInput.command, locked, root);
  if (hit) deny(hit, reason);
}

passThrough();
