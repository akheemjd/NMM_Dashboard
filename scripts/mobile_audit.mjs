#!/usr/bin/env node
/**
 * Mobile audit via Chrome DevTools Protocol.
 *
 * Chrome's --window-size has a ~500px minimum on Windows, so headless
 * screenshots cannot simulate a phone viewport that way. CDP's
 * Emulation.setDeviceMetricsOverride has no such limit, and also lets us
 * evaluate real layout metrics (horizontal overflow being the big one).
 *
 * Usage:
 *   node scripts/mobile_audit.mjs <outdir> <url> [<url> ...]
 *
 * Prints a report per URL:
 *   innerWidth / scrollWidth / overflowPx / overflowing elements
 */

import { spawn } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const PORT = 9333;

// iPhone X-ish
const DEVICE = { width: 375, height: 812, deviceScaleFactor: 2, mobile: true };
// A recent Android mid-range
const ANDROID = { width: 412, height: 915, deviceScaleFactor: 2.6, mobile: true };

const [, , outdirArg = ".", ...urls] = process.argv;
if (!urls.length) {
  console.error("usage: mobile_audit.mjs <outdir> <url> [...]");
  process.exit(2);
}
const outdir = resolve(outdirArg);
mkdirSync(outdir, { recursive: true });

// Chrome needs an absolute Windows-style path for the profile dir; a relative
// or MSYS-style path makes it exit immediately and the debug port never opens.
const profileDir = resolve(outdir, "chrome-profile").replace(/\//g, "\\");

const chrome = spawn(CHROME, [
  "--headless=new",
  "--disable-gpu",
  "--no-sandbox",
  "--hide-scrollbars",
  "--no-first-run",
  "--disable-extensions",
  `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profileDir}`,
  "about:blank",
], { stdio: ["ignore", "pipe", "pipe"] });

let chromeErr = "";
chrome.stderr.on("data", d => { chromeErr += d.toString(); });
chrome.on("exit", code => {
  if (code !== null && code !== 0) {
    console.error(`Chrome exited early (code ${code})`);
    if (chromeErr) console.error(chromeErr.split("\n").slice(0, 8).join("\n"));
  }
});

async function cdpTarget() {
  // Chrome's /json/new needs PUT and some builds reject it; fall back to
  // an existing page target from /json/list, which is always available.
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" });
      if (r.ok) {
        const t = await r.json();
        if (t.webSocketDebuggerUrl) return t;
      }
    } catch { /* not up yet, or PUT unsupported */ }

    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      if (r.ok) {
        const list = await r.json();
        const page = list.find(t => t.type === "page" && t.webSocketDebuggerUrl);
        if (page) return page;
      }
    } catch { /* still starting */ }

    await sleep(300);
  }
  throw new Error("Chrome debugging endpoint never came up");
}

function connect(wsUrl) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);
    let id = 0;
    const pending = new Map();
    ws.addEventListener("open", () => resolve({
      send(method, params = {}) {
        return new Promise((res, rej) => {
          const mid = ++id;
          pending.set(mid, { res, rej });
          ws.send(JSON.stringify({ id: mid, method, params }));
        });
      },
      close: () => ws.close(),
    }));
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && pending.has(msg.id)) {
        const { res, rej } = pending.get(msg.id);
        pending.delete(msg.id);
        msg.error ? rej(new Error(JSON.stringify(msg.error))) : res(msg.result);
      }
    });
    ws.addEventListener("error", reject);
  });
}

const MEASURE = `(() => {
  const de = document.documentElement;
  const vw = window.innerWidth;
  const offenders = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    if (r.right > vw + 1) {
      const cs = getComputedStyle(el);
      if (cs.position === 'fixed' || cs.visibility === 'hidden') continue;
      offenders.push({
        tag: el.tagName.toLowerCase(),
        cls: (el.className && String(el.className).slice(0, 40)) || '',
        right: Math.round(r.right),
        width: Math.round(r.width),
      });
    }
  }
  // Dedupe by tag+class, keep widest
  const seen = new Map();
  for (const o of offenders) {
    const k = o.tag + '.' + o.cls;
    if (!seen.has(k) || seen.get(k).width < o.width) seen.set(k, o);
  }
  return JSON.stringify({
    innerWidth: vw,
    clientWidth: de.clientWidth,
    scrollWidth: de.scrollWidth,
    overflowPx: Math.max(0, de.scrollWidth - vw),
    bodyScrollWidth: document.body.scrollWidth,
    offenders: [...seen.values()].sort((a,b) => b.width - a.width).slice(0, 12),
  });
})()`;

function slugify(u) {
  return u.replace(/^https?:\/\//, "").replace(/[^a-z0-9]+/gi, "-").replace(/-+$/, "").slice(0, 60);
}

const target = await cdpTarget();
const client = await connect(target.webSocketDebuggerUrl);
await client.send("Page.enable");
await client.send("Runtime.enable");

const report = [];

for (const url of urls) {
  for (const [label, dev] of [["iphone", DEVICE], ["android", ANDROID]]) {
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: dev.width,
      height: dev.height,
      deviceScaleFactor: dev.deviceScaleFactor,
      mobile: dev.mobile,
    });

    await client.send("Page.navigate", { url });
    await sleep(3800);

    const m = await client.send("Runtime.evaluate", {
      expression: MEASURE,
      returnByValue: true,
    });
    const data = JSON.parse(m.result.value);

    const shot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: true,
    });
    const file = `${outdir}/${slugify(url)}--${label}.png`;
    writeFileSync(file, Buffer.from(shot.data, "base64"));

    const entry = { url, device: label, ...data, file };
    report.push(entry);

    const flag = data.overflowPx > 1 ? "OVERFLOW" : "ok";
    console.log(`\n${flag}  ${url}`);
    console.log(`     device=${label} (${dev.width}x${dev.height} @${dev.deviceScaleFactor}x)`);
    console.log(`     innerWidth=${data.innerWidth}  scrollWidth=${data.scrollWidth}  overflow=${data.overflowPx}px`);
    if (data.offenders?.length) {
      console.log(`     ${data.offenders.length} element(s) past the right edge:`);
      for (const o of data.offenders.slice(0, 6)) {
        console.log(`       - <${o.tag} class="${o.cls}"> width=${o.width} right=${o.right}`);
      }
    }
  }
}

writeFileSync(`${outdir}/report.json`, JSON.stringify(report, null, 2));

const bad = report.filter(r => r.overflowPx > 1);
console.log(`\n${"=".repeat(60)}`);
console.log(`${report.length} renders checked, ${bad.length} with horizontal overflow`);
if (bad.length) {
  for (const b of bad) {
    console.log(`  ${b.overflowPx}px overflow  ${b.device}  ${b.url}`);
  }
}

client.close();
chrome.kill();
process.exit(0);
