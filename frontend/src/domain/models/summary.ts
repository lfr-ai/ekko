export interface SummarizeResult {
  readonly summary: string;
}

export type SummarizeChunks = (chunks: ReadonlyArray<string>) => Promise<SummarizeResult>;
