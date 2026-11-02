import { useState } from "react";
import { useSummarize } from "@/application/hooks/use-summarize";
import type { SummarizeChunks } from "@/domain/models/summary";

const _CHUNK_SEPARATOR = /\n{2,}/;

interface SummarizePageProps {
  readonly summarize: SummarizeChunks;
}

function splitIntoChunks(transcript: string): ReadonlyArray<string> {
  return transcript
    .split(_CHUNK_SEPARATOR)
    .map((chunk) => chunk.trim())
    .filter((chunk) => chunk.length > 0);
}

export function SummarizePage({ summarize }: SummarizePageProps): React.JSX.Element {
  const [transcript, setTranscript] = useState("");
  const mutation = useSummarize(summarize);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>): void {
    event.preventDefault();
    const chunks = splitIntoChunks(transcript);
    if (chunks.length > 0) {
      mutation.mutate(chunks);
    }
  }

  return (
    <section aria-labelledby="summarize-heading" className="mx-auto max-w-4xl p-6 sm:p-10">
      <header className="space-y-3">
        <h2 className="text-3xl font-semibold tracking-tight" id="summarize-heading">
          Summarize a transcript
        </h2>
        <p className="max-w-2xl text-muted-foreground">
          Paste transcript text below. It is anonymized before it reaches the LLM.
        </p>
      </header>

      <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
        <label className="block" htmlFor="transcript-input">
          <span className="sr-only">Transcript text</span>
          <textarea
            className="min-h-40 w-full rounded-lg border bg-card p-4 text-sm"
            id="transcript-input"
            onChange={(event) => setTranscript(event.currentTarget.value)}
            placeholder="Paste transcript text…"
            value={transcript}
          />
        </label>
        <button
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
          disabled={mutation.isPending || splitIntoChunks(transcript).length === 0}
          type="submit"
        >
          {mutation.isPending ? "Summarizing…" : "Summarize"}
        </button>
      </form>

      {mutation.isPending && (
        <p aria-live="polite" className="mt-8 text-muted-foreground" role="status">
          Summarizing…
        </p>
      )}

      {mutation.isError && (
        <p className="mt-8 rounded-lg border border-destructive p-4 text-destructive" role="alert">
          {mutation.error.message}
        </p>
      )}

      {mutation.isSuccess && (
        <section
          aria-labelledby="summary-heading"
          className="mt-8 rounded-xl border bg-card p-5 shadow-sm"
        >
          <h3 className="font-semibold" id="summary-heading">
            Summary
          </h3>
          <p className="mt-2 whitespace-pre-wrap text-sm">{mutation.data.summary}</p>
        </section>
      )}
    </section>
  );
}
