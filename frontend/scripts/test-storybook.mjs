#!/usr/bin/env node

import { spawn } from "node:child_process";
import { createReadStream, existsSync, readFileSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, relative, resolve, sep } from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const HOST = "127.0.0.1";
const PORT = 6006;
const READY_URL = `http://${HOST}:${PORT}/index.html`;
const READY_TIMEOUT_MS = 15_000;
const READY_POLL_MS = 100;
const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const FRONTEND_DIR = resolve(SCRIPT_DIR, "..");
const STATIC_DIR = join(FRONTEND_DIR, "storybook-static");
const MIME_TYPES = new Map([
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".ico", "image/x-icon"],
  [".jpeg", "image/jpeg"],
  [".jpg", "image/jpeg"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".mjs", "text/javascript; charset=utf-8"],
  [".png", "image/png"],
  [".svg", "image/svg+xml"],
  [".ttf", "font/ttf"],
  [".txt", "text/plain; charset=utf-8"],
  [".webp", "image/webp"],
  [".woff", "font/woff"],
  [".woff2", "font/woff2"],
]);

function resolveRequestPath(requestUrl) {
  const pathname = decodeURIComponent(new URL(requestUrl ?? "/", READY_URL).pathname);
  const requestedPath = pathname.endsWith("/") ? `${pathname}index.html` : pathname;
  const filePath = resolve(STATIC_DIR, `.${requestedPath}`);
  const relativePath = relative(STATIC_DIR, filePath);
  if (relativePath.startsWith(`..${sep}`) || relativePath === "..") return null;
  return filePath;
}

function createStaticServer() {
  return createServer((request, response) => {
    let filePath;
    try {
      filePath = resolveRequestPath(request.url);
    } catch {
      response.writeHead(400).end("Bad request");
      return;
    }

    if (filePath === null || !existsSync(filePath) || !statSync(filePath).isFile()) {
      response.writeHead(404).end("Not found");
      return;
    }

    response.writeHead(200, {
      "Content-Type": MIME_TYPES.get(extname(filePath).toLowerCase()) ?? "application/octet-stream",
    });
    if (request.method === "HEAD") {
      response.end();
      return;
    }
    createReadStream(filePath).pipe(response);
  });
}

function listen(server) {
  return new Promise((resolvePromise, reject) => {
    server.once("error", reject);
    server.listen(PORT, HOST, () => {
      server.off("error", reject);
      resolvePromise();
    });
  });
}

function close(server) {
  return new Promise((resolvePromise, reject) => {
    server.close((error) => (error ? reject(error) : resolvePromise()));
  });
}

async function waitUntilReady() {
  const deadline = Date.now() + READY_TIMEOUT_MS;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(READY_URL);
      if (response.ok) return;
    } catch {
      // The bounded retry loop handles startup races.
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, READY_POLL_MS));
  }
  throw new Error(`Storybook did not become ready at ${READY_URL}.`);
}

function resolveTestRunner() {
  const require = createRequire(import.meta.url);
  const packagePath = require.resolve("@storybook/test-runner/package.json");
  const packageJson = JSON.parse(readFileSync(packagePath, "utf-8"));
  const binaryPath = packageJson.bin?.["test-storybook"];
  if (typeof binaryPath !== "string") throw new Error("Unable to resolve the test-storybook binary.");
  return resolve(dirname(packagePath), binaryPath);
}

function runTests() {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(process.execPath, [resolveTestRunner(), "--url", READY_URL, "--maxWorkers", "1"], {
      cwd: FRONTEND_DIR,
      env: { ...process.env, TARGET_URL: READY_URL },
      stdio: "inherit",
    });
    child.once("error", reject);
    child.once("exit", (code, signal) => {
      if (signal !== null) {
        reject(new Error(`Storybook tests terminated by signal ${signal}.`));
        return;
      }
      resolvePromise(code ?? 1);
    });
  });
}

async function main() {
  if (!existsSync(join(STATIC_DIR, "index.html"))) {
    throw new Error("storybook-static/index.html is missing; run the Storybook build first.");
  }

  const server = createStaticServer();
  await listen(server);
  try {
    await waitUntilReady();
    process.exitCode = await runTests();
  } finally {
    await close(server);
  }
}

await main();
