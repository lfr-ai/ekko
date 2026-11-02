import type { SummarizeChunks, SummarizeResult } from "@/domain/models/summary";

const _SUMMARIZE_ENDPOINT = "/summarize";

interface ErrorResponse {
  readonly detail?: string;
}

export const summarizeChunks: SummarizeChunks = async (chunks) => {
  const response = await fetch(_SUMMARIZE_ENDPOINT, {
    body: JSON.stringify({ chunks }),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ErrorResponse | null;
    throw new Error(body?.detail ?? `Summarize request failed with status ${response.status}.`);
  }

  return (await response.json()) as SummarizeResult;
};
