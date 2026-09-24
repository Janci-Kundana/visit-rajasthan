#!/usr/bin/env node
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const isWindows = process.platform === "win32";
const serverCommand = isWindows ? process.env.ComSpec || "cmd.exe" : "npx";
const executablePath = process.env.PLAYWRIGHT_EXECUTABLE_PATH;
const browserName = process.env.PLAYWRIGHT_BROWSER;
const playwrightCommand = [
  "npx --yes @playwright/mcp@latest",
  browserName ? `--browser ${browserName}` : "",
  executablePath ? `--executable-path "${path.resolve(executablePath)}"` : "",
].filter(Boolean).join(" ");
const serverArgs = isWindows
  ? ["/d", "/s", "/c", playwrightCommand]
  : [
      "--yes",
      "@playwright/mcp@latest",
      ...(browserName ? ["--browser", browserName] : []),
      ...(executablePath ? ["--executable-path", path.resolve(executablePath)] : []),
    ];
const child = spawn(serverCommand, serverArgs, {
  cwd: process.cwd(),
  stdio: ["pipe", "pipe", "pipe"],
  windowsHide: true,
});

let buffered = "";
let stderr = "";
let nextId = 1;
const pending = new Map();

child.stderr.setEncoding("utf8");
child.stderr.on("data", (chunk) => {
  stderr += chunk;
});

child.stdout.setEncoding("utf8");
child.stdout.on("data", (chunk) => {
  buffered += chunk;
  while (buffered.includes("\n")) {
    const newline = buffered.indexOf("\n");
    const line = buffered.slice(0, newline).trim();
    buffered = buffered.slice(newline + 1);
    if (!line) continue;
    let message;
    try {
      message = JSON.parse(line);
    } catch {
      continue;
    }
    if (message.id !== undefined && pending.has(message.id)) {
      const { resolve, reject, timer } = pending.get(message.id);
      clearTimeout(timer);
      pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message || JSON.stringify(message.error)));
      else resolve(message.result);
    }
  }
});

function request(method, params = {}) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pending.delete(id);
      reject(new Error(`Timed out waiting for ${method}. ${stderr.slice(-1000)}`));
    }, 60_000);
    pending.set(id, { resolve, reject, timer });
    child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", id, method, params })}\n`);
  });
}

function notify(method, params = {}) {
  child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", method, params })}\n`);
}

async function callTool(name, args) {
  const result = await request("tools/call", { name, arguments: args });
  if (result.isError) {
    const detail = result.content?.map((item) => item.text || "").join("\n") || `${name} failed`;
    throw new Error(`${detail}\n${stderr ? `Playwright MCP stderr:\n${stderr.slice(-2000)}` : ""}`);
  }
  return result;
}

try {
  const initialized = await request("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "visit-rajasthan-day3-proof", version: "1.0.0" },
  });
  notify("notifications/initialized");
  const { tools } = await request("tools/list");
  if (process.argv.includes("--list")) {
    process.stdout.write(`${JSON.stringify({ server: initialized.serverInfo, tools: tools.map(({ name }) => name) }, null, 2)}\n`);
  } else {
    const urlIndex = process.argv.indexOf("--url");
    const url = urlIndex === -1 ? "http://127.0.0.1:4173" : process.argv[urlIndex + 1];
    const outIndex = process.argv.indexOf("--out");
    const filename = outIndex === -1 ? "docs/day3-evidence/home-dist.png" : process.argv[outIndex + 1];
    const outPath = path.resolve(process.cwd(), filename);
    const relativeOutPath = path.relative(process.cwd(), outPath);
    if (relativeOutPath.startsWith("..") || path.isAbsolute(relativeOutPath)) {
      throw new Error("Screenshot output must stay inside the project workspace.");
    }
    fs.mkdirSync(path.dirname(outPath), { recursive: true });

    await callTool("browser_resize", { width: 1440, height: 900 });
    const navigation = await callTool("browser_navigate", { url });
    await callTool("browser_wait_for", { time: 1.5 });
    const snapshot = await callTool("browser_snapshot", {});
    const screenshot = await callTool("browser_take_screenshot", {
      filename,
      fullPage: false,
      scale: "css",
    });
    const routeSmoke = [];
    for (const check of [
      { route: "/#/places", hash: "#/places", heading: "Places to Visit", feature: "F3 places grid" },
      { route: "/#/jaipur", hash: "#/jaipur", heading: "Jaipur", feature: "F5 Jaipur detail" },
      { route: "/#/about", hash: "#/about", heading: "About Us", feature: "F6 about page" },
      { route: "/#/unknown-place", hash: "#/unknown-place", heading: "Places to Visit", feature: "F1 unknown-route fallback" },
    ]) {
      await callTool("browser_navigate", { url: new URL(check.route, url).href });
      await callTool("browser_wait_for", { time: 0.5 });
      const state = await callTool("browser_evaluate", {
        function: "() => JSON.stringify({ hash: location.hash, heading: document.querySelector('#page-content .page-heading, #page-content .place-title')?.textContent?.trim() || '' })",
      });
      const text = state.content?.map((item) => item.text || "").join("\n") || "";
      if (!text.includes(check.hash) || !text.includes(check.heading)) {
        throw new Error(`${check.feature} expected hash ${check.hash} and heading ${check.heading}; got ${text}`);
      }
      routeSmoke.push(`${check.feature}: ${check.hash} → ${check.heading}`);
    }
    const consoleMessages = await callTool("browser_console_messages", { level: "error", all: true });
    process.stdout.write(
      `${JSON.stringify({
        server: initialized.serverInfo,
        url,
        output: relativeOutPath.split(path.sep).join("/"),
        navigation: navigation.content?.map((item) => item.text).join("\n"),
        snapshot: snapshot.content?.map((item) => item.text).join("\n").slice(0, 5000),
        routeSmoke,
        consoleErrors: consoleMessages.content?.map((item) => item.text).join("\n"),
        screenshot: screenshot.content?.map((item) => item.text).join("\n"),
      }, null, 2)}\n`,
    );
  }
} finally {
  child.kill();
}
