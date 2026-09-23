/**
 * Shared plumbing for the visit-rajasthan Claude Code hooks.
 *
 * Every hook is a plain Node script: Claude Code pipes a JSON event on stdin and
 * reads a JSON decision back on stdout. Keeping that contract in one place means
 * the individual hooks stay short enough to audit at a glance.
 */
import path from "node:path";

/** Reads the hook event JSON from stdin. Returns {} for empty or malformed input. */
export async function readEvent() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf8").trim();
  if (!raw) return {};
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

/**
 * Project root. CLAUDE_PROJECT_DIR is exported by Claude Code and stays pinned to
 * the original root even inside a worktree, so it wins over the event's cwd.
 */
export function projectRoot(event = {}) {
  return process.env.CLAUDE_PROJECT_DIR || event.cwd || process.cwd();
}

/** Repo-relative POSIX path, or null when the file sits outside the project. */
export function relativePath(root, filePath) {
  if (!filePath) return null;
  const rel = path.relative(root, path.resolve(root, filePath));
  if (rel.startsWith("..") || path.isAbsolute(rel)) return null;
  return rel.split(path.sep).join("/");
}

/** Writes a JSON hook response and exits 0 (the "I handled it" path). */
export function respond(payload) {
  process.stdout.write(JSON.stringify(payload));
  process.exit(0);
}

/** Exit 2 is the blocking-error channel: stderr is fed straight back to Claude. */
export function blockWith(message) {
  process.stderr.write(message);
  process.exit(2);
}

/** Exit quietly. Most hook invocations end here — the event wasn't ours. */
export function passThrough() {
  process.exit(0);
}

/**
 * Minimal glob matcher for the lock list: `*` matches within a path segment,
 * `**` matches across segments. Enough for "src/**" or ".github/workflows/*.yml"
 * without pulling a dependency into a hook that runs on every single edit.
 */
export function matchesGlob(pattern, value) {
  const escaped = pattern.replace(/[.+^${}()|[\]\\]/g, (char) => `\\${char}`);
  const regex = escaped
    .replace(/\*\*\//g, "\u0000SLASHSTAR\u0000")
    .replace(/\*\*/g, "\u0000DOUBLESTAR\u0000")
    .replace(/\*/g, "[^/]*")
    .replace(/\u0000SLASHSTAR\u0000/g, "(?:.*/)?")
    .replace(/\u0000DOUBLESTAR\u0000/g, ".*");
  return new RegExp(`^${regex}$`).test(value);
}
