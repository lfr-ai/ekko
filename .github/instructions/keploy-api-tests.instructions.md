---
description: >-
  No-MCP, log-driven Keploy record/replay loop, driven by `keploy status` NEXT blocks.
applyTo: '{keploy/**,keploy.yml,Taskfile.yml,tasks/**/*.yml}'
---

# Keploy API test loop

Use this whenever the dev wants to set up, add, run, fix, or re-record API / contract
tests for a service with Keploy. Keploy here is the **record/replay** flow: it captures
real API traffic plus the downstream calls it triggers (DB, cache, HTTP) into
repo-resident YAML, then replays them with those dependencies mocked.

## The loop

1. From the service directory, run `keploy status`. It prints a `NEXT` block.
2. `keploy status`, `keploy record`, and `keploy test` each end with a NEXT block:
   `{ phase, summary, ask?, run, options, agent_todo? }`.
   - If `ask` is present, **relay it to the dev verbatim and WAIT.** Do not answer it yourself.
   - On the dev's yes/choice, do `agent_todo` first (if present), then run `NEXT.run`. Read the
     new NEXT block. Loop until the suite rests green: `phase: verified_green`, or
     `phase: ci_wired` once CI is set up.
3. Never ask the dev for an app id, command, or base URL — they come from `keploy.yml`
   at the repo root (Keploy's existing config). The dev's whole vocabulary is:
   yes / no / swap / later / stop.

## Recording — you are the traffic generator

When a NEXT step asks you to record:
- Write a **seed script** that exercises the service's endpoints in CRUD order
  (create → read → update → delete), chaining the id returned by `POST` into the later
  `GET`/`PUT`/`DELETE`.
- Bring up the app and its **real** dependencies (e.g. `docker compose up -d`).
- Run the record command from the NEXT block while the seed script drives traffic.
- **Always name the test-set** with `--metadata 'name=<descriptive-name>'` (e.g.
  `name=orders-crud`), so its `config.yaml` documents what the suite covers. Add more
  key=value pairs if useful (e.g. `'name=orders-crud,description=create→read→update→delete'`).
  The folder itself stays the auto-numbered `test-set-N` (a fixed Keploy convention) — the
  descriptive name lives in the metadata, not the folder name.
- **Commit the seed script inside the recorded test-set's own folder**, as
  `keploy/<test-set>/seed.sh`. `<test-set>` is whatever the recording is named
  (`test-set-0`, or a name you chose) — it is NOT a fixed "resource" name. Keep the
  filename constant (`seed.sh`); never create a new sibling folder under `keploy/` for
  seeds — any non-reserved folder there is treated as a test-set by `keploy test`.
- If a re-record is needed later and `seed.sh` is gone: reconstruct it from the recorded
  test cases — read `keploy/<test-set>/tests/*.yaml`, sort by `reqTimestampMock`, emit each
  request in order, and re-chain ids using the recorded responses.

## Calibrate noise — run the test TWICE right after recording

Before trusting a freshly recorded suite, separate non-deterministic fields from real diffs.
The code and mocks are unchanged between the two runs, so anything that differs is noise:

1. Run `keploy test` (pass 1), then run `keploy test` AGAIN (pass 2) — no changes in between.
2. Compare the two runs. **Any field whose value differs between pass 1 and pass 2 is
   non-deterministic** (timestamps, generated ids, ordering, …). Add each such field to that
   test case's `noise` list so it's ignored on compare.
3. Run `keploy test` once more to confirm:
   - **Green** → the suite is calibrated and trustworthy. Proceed.
   - **Still failing** → those fields did NOT differ between identical runs, so they are NOT
     noise. Treat them as **legit failures** (a real regression or an intended change) — heal
     them per the next section. Never silence them as noise.

Do this once, at record time. Later runs (after code changes) are a single `keploy test`: noise
is already filtered, so any failure then is real.

## gRPC services — always provide the proto files

Keploy can only apply field-level noise (and produce readable diffs) on a gRPC body when
it can decode it to JSON — and that requires the service's protos. Without them, gRPC
bodies are compared as opaque canonicalized text and the noise config is **ignored**: a
non-deterministic field (a signed JWT, a timestamp, a generated id) fails on every replay
and cannot be denoised, no matter how many times you mark it as noise.

- Provide them on replay: `keploy test … --proto-dir <dir>` (or `--proto-file <main.proto>`
  plus `--proto-include <import-dirs>`), or persist them in `keploy.yml` under
  `test: { protoDir: …, protoFile: …, protoInclude: […] }` so every run gets them.
- On a gRPC service, do this BEFORE noise calibration — otherwise marking noise silently
  does nothing for the gRPC tests.
- A gRPC body diff that is a signed token (`iat`/`exp` baked in) still changes every
  replay even with protos; protos + noise handles the volatile fields, and a token that
  must be byte-identical needs time-freezing (below).

## Time-freezing — setup differs by app type (Go vs non-Go) and how it runs

Time-freezing makes recorded JWTs / time-sensitive tokens validate on replay even though
their `exp` has passed wall-clock. It is **REPLAY-ONLY**: record always runs the normal
prod artifact — NEVER record with `--freezeTime` or a faketime build (it silently corrupts
the recording's timestamps; recovery = re-record from scratch).

| App    | Runs as          | What replay needs |
|--------|------------------|-------------------|
| Non-Go | native binary    | just add `--freezeTime` — the CLI injects the LD_PRELOAD time shim itself |
| Non-Go | Docker / Compose | add keploy's freeze `.so` + `LD_PRELOAD` env via a sibling `Dockerfile.keploy` / compose override — never edit the prod Dockerfile |
| Go     | native binary    | Go reads time via vDSO and **ignores LD_PRELOAD**: fetch keploy's `go_freeze_time` helper, patch GOROOT with it, build a **sibling** binary with `-tags=faketime`, replay THAT with `--freezeTime`. Never overwrite the prod binary (gitignore the sibling). |
| Go     | Docker / Compose | faketime build inside a sibling `Dockerfile.keploy` loaded via a compose override; prod Dockerfile untouched |

The NEXT block's `freeze_time` remedy prints the exact commands for your detected
quadrant — follow those instead of reconstructing them from memory. Banned "fixes":
never bump `JWT_EXPIRY` to mask it, never edit recorded tokens, never set the system clock.

## Healing a failing replay — there is NO `keploy heal` command; you do it

Read the structured diff in the NEXT block's `failures[]` and the full report at
`keploy/reports/<run>/<set>-report.yaml`, plus the handler source and the IDE/GitNexus change set. Then:
- **Stale downstream mocks** (mock-mismatch dominant) → re-record: re-run the seed script
  under `keploy record`.
- **Wrong row / unexpected 401 from a stateful DB** (replay returns a different record's data,
  or a login 401s though the recorded creds are right) → this is mock *matching*, not a code
  bug. Always replay with `keploy test --mappings` so each test gets only the mocks it recorded
  (pins ambiguous `SELECT … WHERE id = ?` / repeated-query / INSERT-then-SELECT read-backs). If
  it still happens, make the seed use **distinct data per request** (unique usernames/ids) so
  every query is unambiguous, then re-record. Do NOT edit the expected body to match the wrong row.
- **Auth / time-sensitive failure** (a 2xx became 401/403, or a JWT `exp`/`iat` or date field
  differs) → enable time-freezing on replay (enterprise). Setup depends on your quadrant —
  see "Time-freezing" above; for Go apps `--freezeTime` alone is a no-op without the
  faketime sibling build.
- **Flaky / non-deterministic field** (timestamp, uuid, ordering) → noise should already be
  calibrated at record time (see above); only mark a NEW field as noise if its value actually
  differs between two back-to-back `keploy test` runs. A field that fails with the SAME value
  every run is not noise — it's a real diff.
- **A response change that matches a deliberate code change** → update the expected value in the
  test YAML, and CONFIRM with the dev (flag it as a breaking change).
- **A response change with no matching code change** → likely a real regression; tell the dev,
  do not edit the test.

GUARDRAIL: never silently rewrite an expected value to make a red test green.

## Putting the tests in CI — mocks are NEVER committed

- `mocks.yaml` files are huge and gitignored on purpose (keploy itself adds
  `/*/mocks.yaml` to `.gitignore`). **Never commit them, never remove that ignore.**
  What IS committed: `tests/`, `seed.sh`, and the test-set's `config.yaml` — which
  carries the mock content-hash (`mockRegistry.mock`). CI downloads the mock blobs from
  the Keploy registry by that hash (`KEPLOY_API_KEY` required in CI).
- **Upload is automatic on green:** when a test-set PASSES, `keploy test` uploads its
  mocks to the registry by itself (opt out with `--disableMockUpload`). So the normal
  order is: make the suite green → mocks are already uploaded → wire CI → commit
  tests + config.yaml.
- **If the dev insists on wiring CI while tests are still FAILING:** say clearly this is
  NOT recommended — CI will be red and gates PRs on a broken suite; fix the tests first.
  If they confirm anyway, the mocks were never auto-uploaded (upload only happens on
  green), so first upload them manually — `keploy mock upload -t "<test-set>"` — so CI
  can fetch them, then commit tests + config.yaml. Still never `mocks.yaml`.

## Constraints
- `keploy record`/`test` use eBPF and usually need `sudo` + Linux. Real dependencies must be up
  during record; replay needs none (that is the CI win).
