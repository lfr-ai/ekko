import { useQuery } from "@tanstack/react-query";
import type { LoadPromptCatalog, PromptCatalog } from "@/domain/models/prompt-catalog";

const _PROMPT_CATALOG_QUERY_KEY = "prompt-catalog";

export function usePromptCatalog(loadCatalog: LoadPromptCatalog, includeContent: boolean) {
  return useQuery<PromptCatalog>({
    queryFn: () => loadCatalog(includeContent),
    queryKey: [_PROMPT_CATALOG_QUERY_KEY, includeContent],
  });
}
