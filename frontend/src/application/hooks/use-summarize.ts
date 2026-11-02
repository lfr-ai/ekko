import { useMutation } from "@tanstack/react-query";
import type { SummarizeChunks } from "@/domain/models/summary";

export function useSummarize(summarize: SummarizeChunks) {
  return useMutation({
    mutationFn: (chunks: ReadonlyArray<string>) => summarize(chunks),
  });
}
