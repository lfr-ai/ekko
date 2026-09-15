import { QueryClient } from "@tanstack/react-query";

const MUTATION_RETRY_COUNT = 0;
const QUERY_RETRY_COUNT = 1;
const STALE_TIME_MS = 60_000;
const GC_TIME_MS = 300_000;

export const applicationQueryClient = new QueryClient({
  defaultOptions: {
    mutations: {
      retry: MUTATION_RETRY_COUNT,
    },
    queries: {
      gcTime: GC_TIME_MS,
      refetchOnWindowFocus: false,
      retry: QUERY_RETRY_COUNT,
      staleTime: STALE_TIME_MS,
    },
  },
});
