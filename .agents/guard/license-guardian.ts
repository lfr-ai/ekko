// License Guardian: PostToolUse feedback that reruns a repository-owned license
// policy immediately after uv or Bun changes the dependency set, so a
// disallowed license surfaces in the same turn instead of at the next quality
// gate. Bun executes this file directly (no build step);
// wired from both .claude/settings.json and
// .github/hooks/license-guardian.json.
import childProcess from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { appendAuditLog, commandFrom, cwdFrom, isRecord, readStdinJson } from "./lib/hook-io.ts";

const _UV_DEPENDENCY_COMMAND_PATTERN =
  /\buv\s+(?:add|remove|sync|lock)\b|\buv\s+pip\s+(?:install|uninstall)\b/i;
const _BUN_DEPENDENCY_COMMAND_PATTERN = /\bbun\s+(?:add|install|remove|update)\b/i;
const _UV_LICENSE_CHECK_COMMAND = ["run", "--with", "pip-licenses", "pip-licenses"];

interface LicenseCheck {
  readonly executable: string;
  readonly args: readonly string[];
  readonly manager: "bun" | "uv";
}

function hasBunLicenseScript(cwd: string): boolean {
  try {
    const manifest: unknown = JSON.parse(
      fs.readFileSync(path.join(cwd, "package.json"), "utf8"),
    );
    if (!isRecord(manifest) || !isRecord(manifest.scripts)) {
      return false;
    }
    return typeof manifest.scripts["license:check"] === "string";
  } catch {
    return false;
  }
}

function licenseCheckFor(command: string, cwd: string): LicenseCheck | null {
  if (_UV_DEPENDENCY_COMMAND_PATTERN.test(command)) {
    return { executable: "uv", args: _UV_LICENSE_CHECK_COMMAND, manager: "uv" };
  }
  if (_BUN_DEPENDENCY_COMMAND_PATTERN.test(command) && hasBunLicenseScript(cwd)) {
    return { executable: "bun", args: ["run", "license:check"], manager: "bun" };
  }
  return null;
}

function runLicenseCheck(check: LicenseCheck, cwd: string): { failed: boolean; output: string } {
  try {
    const output = childProcess.execFileSync(check.executable, check.args, {
      cwd,
      encoding: "utf8",
    });
    return { failed: false, output };
  } catch (error) {
    const output = isRecord(error) && typeof error.stdout === "string" ? error.stdout : "";
    const stderrOutput = isRecord(error) && typeof error.stderr === "string" ? error.stderr : "";
    return { failed: true, output: `${output}${stderrOutput}` };
  }
}

function appendAudit(outcome: "skipped" | "clean" | "denied", detail: string): void {
  const logDir = process.env.LICENSE_GUARD_LOG_DIR || "logs/copilot/tool-guardian";
  appendAuditLog(logDir, { tool: "license-guardian", outcome, reason: detail });
}

const payload: unknown = readStdinJson();
if (payload === undefined) {
  process.exit(0); // Non-JSON input: nothing to react to, stay silent.
}

const toolInput = isRecord(payload) ? (payload.tool_input ?? payload.toolArgs) : undefined;
const command = commandFrom(toolInput);
const cwd = cwdFrom(payload);
const check = licenseCheckFor(command, cwd);
if (check === null) {
  process.exit(0);
}

const { failed, output } = runLicenseCheck(check, cwd);
if (!failed) {
  appendAudit("clean", `${check.manager}: ${command} passed the dependency license policy`);
  process.exit(0);
}

const reason =
  `The dependency change from \`${command}\` fails the repository's ` +
  `${check.manager} license policy:\n${output.trim()}\n` +
  "Replace the package, or add an explicit, documented allow-only/ignore-packages " +
  "entry once the license risk has been reviewed.";
appendAudit("denied", reason);
process.stderr.write(`${reason}\n`);
process.exit(2);

