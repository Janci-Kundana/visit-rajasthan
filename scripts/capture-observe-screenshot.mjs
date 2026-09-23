/**
 * Screenshots the agents-observe dashboard for the Day 2 observability deliverable.
 *
 *   node scripts/capture-observe-screenshot.mjs <session-id> [outfile]
 *
 * Playwright is installed globally rather than as a project dependency, so this
 * resolves it out of the global npm root instead of node_modules.
 */
import { execSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";

const sessionId = process.argv[2];
const outFile = path.resolve(process.argv[3] || "docs/observability/agents-observe-session.png");

if (!sessionId) {
  console.error("usage: node scripts/capture-observe-screenshot.mjs <session-id> [outfile]");
  process.exit(1);
}

const globalRoot = execSync("npm root -g", { encoding: "utf8" }).trim();
const require = createRequire(path.join(globalRoot, "index.js"));
const { chromium } = require("playwright");

const DASHBOARD = process.env.AGENTS_OBSERVE_URL || "http://127.0.0.1:4981";
const url = `${DASHBOARD}/#/_/${sessionId}`;

fs.mkdirSync(path.dirname(outFile), { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1600, height: 1000 },
  deviceScaleFactor: 2,
});

await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
// The dashboard hydrates from a WebSocket feed, so give the event stream a beat
// to paint the agent tree before the shutter fires.
await page.waitForTimeout(5000);
await page.screenshot({ path: outFile });
await browser.close();

console.log(`captured ${url}`);
console.log(`-> ${outFile}`);
