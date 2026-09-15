import type { LoadPromptCatalog, PromptCatalog } from "@/domain/models/prompt-catalog";
import promptCatalogDocument from "@/infrastructure/graphql/operations/queries/prompt-catalog.graphql?raw";

const _GRAPHQL_ENDPOINT = "/graphql";
const _OPERATION_NAME = "PromptCatalog";

interface PromptCatalogData {
  readonly promptCatalog: PromptCatalog;
}

interface GraphQLErrorResult {
  readonly message: string;
}

interface GraphQLResult {
  readonly data?: PromptCatalogData;
  readonly errors?: ReadonlyArray<GraphQLErrorResult>;
}

export const loadPromptCatalog: LoadPromptCatalog = async (includeContent) => {
  const response = await fetch(_GRAPHQL_ENDPOINT, {
    body: JSON.stringify({
      operationName: _OPERATION_NAME,
      query: promptCatalogDocument,
      variables: { includeContent },
    }),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`Prompt catalog request failed with status ${response.status}.`);
  }

  const result = (await response.json()) as GraphQLResult;
  const error = result.errors?.[0];
  if (error) {
    throw new Error(error.message);
  }
  if (!result.data) {
    throw new Error("Prompt catalog response did not include data.");
  }
  return result.data.promptCatalog;
};
