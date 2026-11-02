// Shared stdin/JSON/audit-log primitives for the Bun-executed hook scripts in
// this directory (tool-guardian, license-guardian, session-context). Kept
// dependency-free so every hook stays a single file Bun can run directly.
import fs from "node:fs";
import path from "node:path";

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Parses the hook payload from stdin; `undefined` on invalid JSON. */
export function readStdinJson(): unknown {
  try {
    return JSON.parse(fs.readFileSync(0, "utf8"));
  } catch {
    return undefined;
  }
}

export function cwdFrom(payload: unknown): string {
  return isRecord(payload) && typeof payload.cwd === "string" && payload.cwd
    ? payload.cwd
    : process.cwd();
}

export function commandFrom(toolInput: unknown): string {
  if (typeof toolInput === "string") {
    return toolInput;
  }
  if (!isRecord(toolInput)) {
    return "";
  }
  return typeof toolInput.command === "string" ? toolInput.command : "";
}

/** Appends one JSON-line audit entry; silently no-ops on write failure. */
export function appendAuditLog(
  logDir: string,
  entry: Record<string, unknown>,
): void {
  try {
    fs.mkdirSync(logDir, { recursive: true });
    fs.appendFileSync(
      path.join(logDir, "guard.log"),
      `${JSON.stringify({ timestamp: new Date().toISOString(), ...entry })}\n`,
      "utf8",
    );
  } catch {
    // Policy/feedback decisions must not depend on optional audit logging.
  }
}
