#!/usr/bin/env node
/**
 * SubagentStart / SubagentStop recorder.
 *
 * Appends one JSON line per subagent lifecycle event to .claude/logs/subagents.jsonl.
 * This is the in-repo counterpart to the agents-observe dashboard: the dashboard is
 * the live view, this file is the durable record that survives the session.
 */
import fs from "node:fs";
import path from "node:path";
import { readEvent, projectRoot, respond, passThrough } from "./lib/hook-io.mjs";

const event = await readEvent();
const hookEvent = event.hook_event_name || "";
if (!["SubagentStart", "SubagentStop"].includes(hookEvent)) passThrough();

const root = projectRoot(event);
const logDir = path.join(root, ".claude", "logs");
fs.mkdirSync(logDir, { recursive: true });

const entry = {
  ts: new Date().toISOString(),
  event: hookEvent,
  agent_type: event.agent_type || "unknown",
  agent_id: event.agent_id || null,
  session_id: event.session_id || null,
  description: event.description || event.prompt?.slice(0, 200) || null,
};

fs.appendFileSync(path.join(logDir, "subagents.jsonl"), `${JSON.stringify(entry)}\n`, "utf8");

respond({
  hookSpecificOutput: {
    hookEventName: hookEvent,
    additionalContext: `Recorded ${hookEvent} for subagent "${entry.agent_type}" in .claude/logs/subagents.jsonl`,
  },
});
