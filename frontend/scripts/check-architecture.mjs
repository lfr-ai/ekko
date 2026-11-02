#!/usr/bin/env node
// Frontend Clean Architecture boundary checker.
//
// Mirrors the backend's tools/security/check_architecture_boundaries.py: the
// backend enforces layer boundaries with import-linter, and this is the
// frontend equivalent. It is intentionally dependency-free (pure Node) so it
// runs in CI and locally even when node_modules is degraded.
//
// Dependencies flow inward. Each layer may import from itself, from the layers
// in its allowed set, and from `lib` (shared leaf utilities). Any other
// cross-layer import is a violation.
//
// Usage: node ./scripts/check-architecture.mjs   (exit 0 = clean, 1 = violations)

import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const SRC = resolve(SCRIPT_DIR, "..", "src");

/**
 * Allowed inward dependency targets per layer.
 * Read as: files in <key> may import from any layer listed in the value set.
 */
const ALLOWED = {
  domain: new Set(["domain", "lib"]),
  infrastructure: new Set(["infrastructure", "domain", "lib"]),
  application: new Set(["application", "infrastructure", "domain", "lib"]),
  presentation: new Set(["presentation", "application", "domain", "lib"]),
  router: new Set(["router", "presentation", "application", "domain", "lib"]),
  lib: new Set(["lib"]),
};
const LAYERS = new Set(Object.keys(ALLOWED));

const SOURCE_PATTERNS = [
  /\bfrom\s*["']([^"']+)["']/g, // import ... from "x" / export ... from "x"
  /\bimport\s*\(\s*["']([^"']+)["']/g, // dynamic import("x")
  /^\s*import\s+["']([^"']+)["']/gm, // side-effect import "x"
];

/** Recursively collect .ts/.tsx files under a directory, skipping tests/stories. */
function collectSourceFiles(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      out.push(...collectSourceFiles(full));
      continue;
    }
    if (!/\.tsx?$/.test(entry)) continue;
    if (/\.(test|spec|stories)\.tsx?$/.test(entry)) continue;
    if (/\.d\.ts$/.test(entry)) continue;
    out.push(full);
  }
  return out;
}

/** Return the layer of a path relative to src/, or null for composition-root files. */
function layerOf(relPathFromSrc) {
  const first = relPathFromSrc.split(sep)[0];
  return LAYERS.has(first) ? first : null;
}

/** Resolve an import specifier to a target layer, or null when out of scope. */
function targetLayerOf(spec, fileDir) {
  let relPath;
  if (spec.startsWith("@/")) {
    relPath = spec.slice(2);
  } else if (spec.startsWith(".")) {
    relPath = relative(SRC, resolve(fileDir, spec));
    if (relPath.startsWith("..")) return null; // escapes src/
  } else {
    return null; // external dependency
  }
  const first = relPath.split(/[\\/]/)[0];
  return LAYERS.has(first) ? first : null;
}

function extractSpecifiers(text) {
  const specs = new Set();
  for (const pattern of SOURCE_PATTERNS) {
    pattern.lastIndex = 0;
    let match;
    while ((match = pattern.exec(text)) !== null) specs.add(match[1]);
  }
  return specs;
}

function main() {
  const violations = [];
  for (const file of collectSourceFiles(SRC)) {
    const relFromSrc = relative(SRC, file);
    const sourceLayer = layerOf(relFromSrc);
    if (sourceLayer === null) continue; // App.tsx / main.tsx composition root

    const text = readFileSync(file, "utf8");
    for (const spec of extractSpecifiers(text)) {
      const targetLayer = targetLayerOf(spec, dirname(file));
      if (targetLayer === null || targetLayer === sourceLayer) continue;
      if (ALLOWED[sourceLayer].has(targetLayer)) continue;
      violations.push({
        file: relative(resolve(SRC, ".."), file).replace(/\\/g, "/"),
        sourceLayer,
        targetLayer,
        spec,
      });
    }
  }

  if (violations.length === 0) {
    console.log("Clean Architecture boundaries KEPT (frontend).");
    return 0;
  }

  console.error(`Clean Architecture boundary violations (frontend): ${violations.length}`);
  for (const v of violations) {
    console.error(`  ${v.file}: '${v.sourceLayer}' must not import '${v.targetLayer}' (${v.spec})`);
  }
  return 1;
}

process.exit(main());
