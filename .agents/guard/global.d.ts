// Minimal ambient declarations for the runtime globals used by
// tool-guardian.ts, so `tsc --noEmit` can type-check this dependency-free
// script without installing `@types/node` or `bun-types`.
declare const process: {
  readonly env: Record<string, string | undefined>;
  cwd(): string;
  exit(code?: number): never;
  readonly stdout: { write(chunk: string): boolean };
  readonly stderr: { write(chunk: string): boolean };
};

declare module "node:fs" {
  function mkdirSync(path: string, options: { recursive: boolean }): void;
  function appendFileSync(path: string, data: string, encoding: string): void;
  function readFileSync(fd: number, encoding: string): string;
  function readFileSync(path: string, encoding: string): string;
  function existsSync(path: string): boolean;
  const _default: {
    mkdirSync: typeof mkdirSync;
    appendFileSync: typeof appendFileSync;
    readFileSync: typeof readFileSync;
    existsSync: typeof existsSync;
  };
  export default _default;
}

declare module "node:path" {
  function resolve(...segments: string[]): string;
  function join(...segments: string[]): string;
  const sep: string;
  const _default: { resolve: typeof resolve; join: typeof join; sep: typeof sep };
  export default _default;
}

declare module "node:child_process" {
  function execFileSync(
    file: string,
    args: readonly string[],
    options: { cwd: string; encoding: string },
  ): string;
  const _default: { execFileSync: typeof execFileSync };
  export default _default;
}
