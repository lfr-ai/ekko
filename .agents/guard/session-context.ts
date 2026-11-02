// Session Start: verifies the small agent-context entry set and reports the
// active working directory without running Git or another project command.
// Bun executes this file
// directly (no build step); wired from both .claude/settings.json and
// .github/hooks/session-context.json, mirroring tool-guardian.ts's pattern.
// Never blocks the session: missing files become context for the agent to act
// on, while malformed stdin falls back to the process working directory.
import fs from "node:fs";
import path from "node:path";
import { cwdFrom, readStdinJson } from "./lib/hook-io.ts";

const _CONTEXT_FILES = ["AGENTS.md", "PROJECT.md", "llms.txt"] as const;

function buildContext(cwd: string): string {
  const missing = _CONTEXT_FILES.filter(
    (fileName) => !fs.existsSync(path.join(cwd, fileName)),
  );
  const lines = [
    `Active workspace: ${cwd}`,
    "Agent entry points: AGENTS.md, PROJECT.md, llms.txt.",
  ];
  if (missing.length > 0) {
    lines.push(`Missing agent context files: ${missing.join(", ")}.`);
  }
  return lines.join("\n");
}

function readCwd(): string {
  return cwdFrom(readStdinJson());
}

const context = buildContext(readCwd());
const output = {
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: context,
  },
};
process.stdout.write(`${JSON.stringify(output)}\n`);
