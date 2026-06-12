---
name: gitnexus-debugging
description: "Use when the user is debugging a bug, tracing an error, or asking why something fails. Examples: \"Why is X failing?\", \"Where does this error come from?\", \"Trace this bug\""
---

# Debugging with GitNexus

## When to Use

- "Why is this function failing?"
- "Trace where this error comes from"
- "Who calls this method?"
- "This endpoint returns 500"
- Investigating bugs, errors, or unexpected behavior

## Workflow

```
1. gitnexus_query({query: "<error or symptom>"})            → Find related execution flows
2. gitnexus_context({name: "<suspect>"})                    → See callers/callees/processes
3. READ gitnexus://repo/{name}/process/{name}                → Trace execution flow
4. gitnexus_cypher({query: "MATCH path..."})                 → Custom traces if needed
```

> If "Index is stale" → run `npx gitnexus analyze` in terminal.

## Checklist

```
- [ ] Understand the symptom (error message, unexpected behavior)
- [ ] gitnexus_query for error text or related code
- [ ] Identify the suspect function from returned processes
- [ ] gitnexus_context to see callers and callees
- [ ] Trace execution flow via process resource if applicable
- [ ] gitnexus_cypher for custom call chain traces if needed
- [ ] Read source files to confirm root cause
```

## Debugging Patterns

| Symptom              | GitNexus Approach                                          |
| -------------------- | ---------------------------------------------------------- |
| Error message        | `gitnexus_query` for error text → `context` on throw sites |
| Wrong return value   | `context` on the function → trace callees for data flow    |
| Intermittent failure | `context` → look for external calls, async deps            |
| Performance issue    | `context` → find symbols with many callers (hot paths)     |
| Recent regression    | `detect_changes` to see what your changes affect           |

## Tools

**gitnexus_query** — find code related to error:

```
gitnexus_query({query: "audio transcription error"})
→ Processes: AudioPipeline, TranscriptionFlow
→ Symbols: transcribe_audio, handle_stt_error, STTException
```

**gitnexus_context** — full context for a suspect:

```
gitnexus_context({name: "transcribe_audio"})
→ Incoming calls: audio_handler, stream_processor
→ Outgoing calls: faster_whisper_transcribe, normalize_text
→ Processes: AudioPipeline (step 3/7)
```

**gitnexus_cypher** — custom call chain traces:

```cypher
MATCH path = (a)-[:CodeRelation {type: 'CALLS'}*1..2]->(b:Function {name: "transcribe_audio"})
RETURN [n IN nodes(path) | n.name] AS chain
```

## Example: "STT endpoint returns empty transcript intermittently"

```
1. gitnexus_query({query: "transcription error handling"})
   → Processes: AudioPipeline, ErrorHandling
   → Symbols: transcribe_audio, handle_stt_error

2. gitnexus_context({name: "transcribe_audio"})
   → Outgoing calls: faster_whisper_transcribe, audio_buffer.read()

3. READ gitnexus://repo/ekko/process/AudioPipeline
   → Step 3: transcribe_audio → calls audio_buffer.read()

4. Root cause: audio_buffer.read() can return empty when queue drains
```
