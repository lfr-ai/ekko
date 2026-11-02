// Tool Guardian: deterministic PreToolUse policy shared by every agent runtime.
// Bun executes this file directly (no build step); wired from both
// .claude/settings.json and .github/hooks/tool-guardian.json.
//
// Agents may read and edit local workspace files freely, including deleting
// them, as long as the target stays inside the workspace (never '.git', a
// drive/home root, or a path resolving outside it). Database, Azure, and other
// external-resource mutations stay denied regardless of workspace scoping.
import path from "node:path";
import { appendAuditLog, commandFrom, cwdFrom, isRecord, readStdinJson } from "./lib/hook-io.ts";

const _DATABASE_MARKERS = ["database", "mssql", "mysql", "pgsql", "postgres"];
const _MUTATING_SQL_WORDS = new Set([
  "alter", "analyze", "call", "comment", "copy", "create", "delete", "do",
  "drop", "grant", "insert", "lock", "merge", "refresh", "reindex", "revoke",
  "set", "truncate", "update", "upsert", "vacuum",
]);
const _CYPHER_MARKER = "cypher";
const _MUTATING_CYPHER_WORDS = new Set([
  "create", "delete", "detach", "drop", "foreach", "load", "merge", "remove",
  "set",
]);
const _DATABASE_MUTATION_MARKERS = [
  "bulk_load", "create", "delete", "drop", "execute", "import", "insert",
  "modify", "remove", "restore", "truncate", "update", "upsert", "write",
];
const _DATABASE_READ_MARKERS = [
  "capabilit", "change_database", "connect", "context", "describe", "disconnect",
  "export", "get", "list", "open_script", "query_plan", "schema", "visualize",
];
const _AZURE_MUTATION_WORDS = new Set([
  "add", "apply", "assign", "cancel", "create", "delete", "deploy", "disable",
  "enable", "import", "invoke", "migrate", "modify", "patch", "post", "provision",
  "purge", "put", "remove", "restart", "run", "scale", "set", "start", "stop",
  "update", "upload", "write",
]);
const _AZURE_READ_WORDS = new Set([
  "advisor", "bestpractices", "build", "build-params", "capabilities", "check",
  "decompile", "describe", "diagnostics", "export", "format", "get", "health",
  "learn", "list", "logs", "metrics", "preview", "query", "read", "schema",
  "search", "show", "status", "validate", "what-if",
]);
const _DELETE_COMMANDS = new Set([
  "del", "erase", "rd", "rmdir", "rm", "unlink", "remove-item",
]);
const _DATABASE_CLIENTS = new Set(["mysql", "pgcli", "psql", "sqlcmd", "sqlite3"]);
const _INFRASTRUCTURE_MUTATIONS = new Map<string, ReadonlySet<string>>([
  ["azd", new Set(["deploy", "provision", "up"])],
  ["helm", new Set(["install", "rollback", "uninstall", "upgrade"])],
  ["kubectl", new Set(["annotate", "apply", "autoscale", "cordon", "create", "delete", "drain", "edit", "label", "patch", "replace", "scale", "set", "taint"])],
  ["pulumi", new Set(["cancel", "destroy", "import", "refresh", "up"])],
  ["terraform", new Set(["apply", "destroy", "import", "taint", "untaint"])],
]);

interface GuardDecision {
  readonly malformed: boolean;
  readonly reason: string | null;
}

function normalizeToolName(value: unknown): string {
  return typeof value === "string" ? value.toLowerCase().replaceAll("-", "_") : "";
}

function words(value: string): string[] {
  return value.toLowerCase().match(/[a-z][a-z0-9_-]*/g) ?? [];
}

function includesMarker(value: string, markers: readonly string[]): boolean {
  return markers.some((marker) => value.includes(marker));
}

function includesWord(value: string, candidates: ReadonlySet<string>): boolean {
  return words(value).some((word) => candidates.has(word));
}

function commandSegments(command: string): string[] {
  return command.split(/[;&|\r\n]+/).map((segment) => segment.trim()).filter(Boolean);
}

function executableName(token: string): string {
  return token.toLowerCase().replace(/\.(?:cmd|exe)$/, "");
}

function collectStrings(value: unknown): string[] {
  if (typeof value === "string") {
    return [value];
  }
  if (Array.isArray(value)) {
    return value.flatMap(collectStrings);
  }
  if (isRecord(value)) {
    return Object.values(value).flatMap(collectStrings);
  }
  return [];
}

function stripSqlNoise(value: string): string {
  return value
    .replace(/\/\*[\s\S]*?\*\//g, " ")
    .replace(/--[^\r\n]*/g, " ")
    .replace(/'(?:''|[^'])*'/g, " ");
}

function hasBoolean(toolInput: unknown, key: string): boolean {
  return isRecord(toolInput) && toolInput[key] === true;
}

function databaseDenial(toolName: string, toolInput: unknown): string | null {
  if (!includesMarker(toolName, _DATABASE_MARKERS)) {
    return null;
  }
  if (includesMarker(toolName, _DATABASE_MUTATION_MARKERS)) {
    return "Database mutation tools are disabled; use a read-only query tool and read-only credentials.";
  }
  if (toolName.includes("query")) {
    const sql = stripSqlNoise(collectStrings(toolInput).join("\n"));
    if (includesWord(sql, _MUTATING_SQL_WORDS) || /\bfor\s+(?:no\s+key\s+)?update\b/i.test(sql)) {
      return "Mutating SQL is disabled; agents may execute read-only queries only.";
    }
    if (!/^\s*(?:describe|explain|pragma|select|show|with)\b/i.test(sql)) {
      return "The database query could not be proven read-only and was denied.";
    }
    return null;
  }
  if (includesMarker(toolName, _DATABASE_READ_MARKERS)) {
    return null;
  }
  return "Unknown database operations are denied by the read-only agent policy.";
}

function cypherDenial(toolName: string, toolInput: unknown): string | null {
  if (!toolName.includes(_CYPHER_MARKER)) {
    return null;
  }
  const query = collectStrings(toolInput).join("\n");
  if (includesWord(query, _MUTATING_CYPHER_WORDS)) {
    return "Mutating Cypher is disabled; agents may run read-only graph queries only.";
  }
  if (!/^\s*(?:call\s*\{|explain|match|profile|return|unwind|with)\b/i.test(query)) {
    return "The Cypher query could not be proven read-only and was denied.";
  }
  return null;
}

function azureDenial(toolName: string, toolInput: unknown): string | null {
  const isAzureTool = toolName.includes("azure") || toolName.includes("azureresources");
  if (!isAzureTool) {
    return null;
  }
  if (toolName === "azure_auth_set_auth_context") {
    return null;
  }
  if (hasBoolean(toolInput, "learn")) {
    return null;
  }
  const operation = isRecord(toolInput) && typeof toolInput.command === "string"
    ? toolInput.command
    : toolName;
  if (includesWord(operation, _AZURE_MUTATION_WORDS)) {
    return "Azure mutations are disabled; agents may inspect resources and validate local artifacts only.";
  }
  if (includesWord(operation, _AZURE_READ_WORDS)) {
    return null;
  }
  return "Unknown Azure operations are denied by the read-only agent policy.";
}

function isReadOnlyAzSegment(segment: string): boolean {
  const tokens = words(segment);
  if (tokens.some((token) => _AZURE_MUTATION_WORDS.has(token) && token !== "set")) {
    return false;
  }
  const isAccountSet = tokens[1] === "account" && tokens[2] === "set";
  return isAccountSet || tokens[1] === "login" || tokens.some((token) => _AZURE_READ_WORDS.has(token));
}

function azureShellDenial(command: string): string | null {
  const azureSegments = commandSegments(command).filter((segment) => {
    const [first = ""] = words(segment);
    return executableName(first) === "az";
  });
  if (azureSegments.some((segment) => !isReadOnlyAzSegment(segment.trim()))) {
    return "Azure CLI operations must be provably read-only; resource mutations are disabled.";
  }
  return null;
}

function deletesFiles(command: string): boolean {
  return /\b(?:Directory|File)\.Delete\s*\(|\b(?:fs\.rmSync|os\.remove|shutil\.rmtree)\s*\(/i.test(command);
}

function isProtectedDeletionTarget(target: string): boolean {
  let normalized = target.replaceAll("\\", "/").toLowerCase();
  while (normalized.length > 1 && normalized.endsWith("/")) {
    normalized = normalized.slice(0, -1);
  }
  if (normalized === "" || normalized === "/" || normalized === "~" || normalized === ".git") {
    return true;
  }
  if (normalized.endsWith("/.git") || normalized.includes("/.git/")) {
    return true;
  }
  return /^[a-z]:\/?$/.test(normalized) || normalized === "$home" || normalized === "%userprofile%";
}

function isWithinWorkspace(target: string, cwd: string): boolean {
  const resolved = path.resolve(cwd, target);
  const root = path.resolve(cwd);
  return resolved === root || resolved.startsWith(root + path.sep);
}

function deletionArgs(segment: string): string[] {
  return segment
    .trim()
    .split(/\s+/)
    .slice(1)
    .filter((token) => token && !token.startsWith("-"));
}

function deletesOutsideWorkspace(command: string, cwd: string): boolean {
  return commandSegments(command).some((segment) => {
    const [first = ""] = words(segment);
    if (!_DELETE_COMMANDS.has(executableName(first))) {
      return false;
    }
    const targets = deletionArgs(segment);
    if (targets.length === 0) {
      return true;
    }
    return targets.some(
      (target) => isProtectedDeletionTarget(target) || !isWithinWorkspace(target, cwd),
    );
  });
}

function mutatesInfrastructure(command: string): boolean {
  return commandSegments(command).some((segment) => {
    const tokens = words(segment);
    const program = executableName(tokens[0] ?? "");
    if (program === "func") {
      return tokens.includes("publish");
    }
    const mutations = _INFRASTRUCTURE_MUTATIONS.get(program);
    return mutations !== undefined && tokens.some((token) => mutations.has(token));
  });
}

function destroysDockerState(command: string): boolean {
  return commandSegments(command).some((segment) => {
    const tokens = words(segment);
    if (executableName(tokens[0] ?? "") !== "docker") {
      return false;
    }
    const operation = (tokens[1] === "compose" ? tokens[2] : tokens[1]) ?? "";
    return ["down", "prune", "rm"].includes(operation) && (operation !== "down" || tokens.includes("v") || tokens.includes("volumes"));
  });
}

function usesDatabaseShell(command: string): boolean {
  const normalized = command.toLowerCase();
  const tokens = words(normalized);
  const invokesClient = tokens.some((token) => _DATABASE_CLIENTS.has(executableName(token)));
  const mutatesWithAlembic = normalized.includes("alembic upgrade") || normalized.includes("alembic downgrade") || normalized.includes("alembic stamp");
  const mutatesWithTask = normalized.includes("task db:migrate") || normalized.includes("task db:stamp") || normalized.includes("task db:conditions:sync");
  return invokesClient || mutatesWithAlembic || mutatesWithTask;
}

function invokesGit(command: string): boolean {
  return commandSegments(command).some((segment) => {
    const [first = ""] = words(segment);
    return executableName(first) === "git";
  });
}

function shellDenial(command: string, cwd: string): string | null {
  if (!command) {
    return null;
  }
  if (invokesGit(command)) {
    return "Git commands are disabled for agents in this repository.";
  }
  if (deletesFiles(command)) {
    return "Deletions via inline code (fs/os/shutil/.NET APIs) are disabled; use a direct shell delete command scoped to the workspace instead.";
  }
  if (deletesOutsideWorkspace(command, cwd)) {
    return "Deletion targets must resolve inside the current workspace; refusing paths outside it, '.git', or drive/home roots.";
  }
  if (usesDatabaseShell(command)) {
    return "Database mutations and database shell clients are disabled for agents.";
  }
  if (mutatesInfrastructure(command)) {
    return "External infrastructure mutations are disabled for agents.";
  }
  if (destroysDockerState(command)) {
    return "Destructive Docker operations are disabled for agents.";
  }
  return azureShellDenial(command);
}

function evaluate(payload: unknown): GuardDecision {
  if (!isRecord(payload)) {
    return { malformed: true, reason: "Tool Guardian received a non-object payload." };
  }
  const toolName = normalizeToolName(payload.tool_name ?? payload.toolName);
  const toolInput = payload.tool_input ?? payload.toolArgs;
  if (!toolName || toolInput === undefined) {
    return { malformed: true, reason: "Tool Guardian payload is missing tool name or tool input." };
  }

  const databaseReason = databaseDenial(toolName, toolInput);
  if (databaseReason) {
    return { malformed: false, reason: databaseReason };
  }
  const cypherReason = cypherDenial(toolName, toolInput);
  if (cypherReason) {
    return { malformed: false, reason: cypherReason };
  }
  const azureReason = azureDenial(toolName, toolInput);
  if (azureReason) {
    return { malformed: false, reason: azureReason };
  }
  const commandReason = shellDenial(commandFrom(toolInput), cwdFrom(payload));
  return { malformed: false, reason: commandReason };
}

function appendAudit(toolName: string, outcome: "allowed" | "denied", reason: string): void {
  const logDir = process.env.TOOL_GUARD_LOG_DIR || "logs/copilot/tool-guardian";
  appendAuditLog(logDir, { tool: toolName, outcome, reason });
}

function deny(reason: string): void {
  const output = {
    permissionDecision: "deny",
    permissionDecisionReason: reason,
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: reason,
    },
  };
  process.stdout.write(`${JSON.stringify(output)}\n`);
}

const payload = readStdinJson();
if (payload === undefined) {
  process.stderr.write("Tool Guardian denied the operation because its input was not valid JSON.\n");
  process.exit(2);
}

const decision = evaluate(payload);
const toolName = isRecord(payload) ? normalizeToolName(payload.tool_name ?? payload.toolName) : "unknown";
if (decision.malformed) {
  appendAudit(toolName, "denied", decision.reason ?? "malformed payload");
  process.stderr.write(`${decision.reason}\n`);
  process.exit(2);
}
if (decision.reason) {
  appendAudit(toolName, "denied", decision.reason);
  deny(decision.reason);
} else {
  appendAudit(toolName, "allowed", "read-only or workspace-local operation");
}
