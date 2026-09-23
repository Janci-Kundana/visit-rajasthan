#!/usr/bin/env node
/**
 * PostToolUse formatter: runs Prettier over any source file Claude just wrote.
 *
 * Writing through fs (rather than handing the diff back to the Edit tool) keeps
 * this from re-triggering itself. Claude is told the file changed via
 * additionalContext so its in-memory copy does not drift from disk.
 */
import fs from "node:fs";
import path from "node:path";
import { readEvent, projectRoot, relativePath, respond, passThrough } from "./lib/hook-io.mjs";

const FORMATTABLE = new Set([
  ".ts",
  ".tsx",
  ".js",
  ".mjs",
  ".cjs",
  ".json",
  ".css",
  ".html",
  ".md",
]);
const SKIP_DIRS = ["node_modules/", "dist/", "output/", "blender-output/", ".playwright-cli/"];

const event = await readEvent();
const toolName = event.tool_name || "";
if (!["Edit", "Write", "MultiEdit"].includes(toolName)) passThrough();

const root = projectRoot(event);
const rel = relativePath(root, (event.tool_input || {}).file_path);
if (!rel) passThrough();
if (!FORMATTABLE.has(path.extname(rel))) passThrough();
if (SKIP_DIRS.some((dir) => rel.startsWith(dir))) passThrough();

const absolute = path.join(root, rel);
if (!fs.existsSync(absolute)) passThrough();

let prettier;
try {
  prettier = await import("prettier");
} catch {
  // Prettier not installed in this checkout — formatting is a nicety, never a blocker.
  passThrough();
}

const source = fs.readFileSync(absolute, "utf8");
const fileInfo = await prettier.getFileInfo(absolute, {
  ignorePath: path.join(root, ".prettierignore"),
});
if (fileInfo.ignored || !fileInfo.inferredParser) passThrough();

const config = (await prettier.resolveConfig(absolute)) || {};
let formatted;
try {
  formatted = await prettier.format(source, { ...config, filepath: absolute });
} catch (error) {
  // A syntax error is the author's problem to see, not the hook's to hide.
  respond({
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: `Prettier could not parse ${rel}, so it was left unformatted: ${error.message.split("\n")[0]}`,
    },
  });
}

if (formatted === source) passThrough();

fs.writeFileSync(absolute, formatted, "utf8");
respond({
  hookSpecificOutput: {
    hookEventName: "PostToolUse",
    additionalContext: `Auto-formatted ${rel} with Prettier after your edit. The file on disk now differs from what you wrote — re-read it before editing again.`,
  },
});
