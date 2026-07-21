import { frontendEnvironment } from "@/infrastructure/config/environment";

const JSON_HEADERS: HeadersInit = {
  "Content-Type": "application/json",
};

const DEFAULT_GRAPHQL_ENDPOINT = "/graphql";

interface GraphQLResponse<TData> {
  readonly data?: TData;
  readonly errors?: ReadonlyArray<{ readonly message: string }>;
}

export async function getJson<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${frontendEnvironment.apiBaseUrl}${path}`, {
    headers: JSON_HEADERS,
    method: "GET",
  });

  if (!response.ok) {
    throw new Error(`GET ${path} failed with status ${response.status}.`);
  }

  return (await response.json()) as TResponse;
}

export async function postJson<TResponse>(path: string, body: unknown): Promise<TResponse> {
  const response = await fetch(`${frontendEnvironment.apiBaseUrl}${path}`, {
    body: JSON.stringify(body),
    headers: JSON_HEADERS,
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`POST ${path} failed with status ${response.status}.`);
  }

  return (await response.json()) as TResponse;
}

export async function postGraphql<TData>(
  query: string,
  variables?: Record<string, unknown>,
): Promise<TData> {
  const response = await fetch(DEFAULT_GRAPHQL_ENDPOINT, {
    body: JSON.stringify({ query, variables }),
    headers: JSON_HEADERS,
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`POST ${DEFAULT_GRAPHQL_ENDPOINT} failed with status ${response.status}.`);
  }

  const payload = (await response.json()) as GraphQLResponse<TData>;
  if (payload.errors && payload.errors.length > 0) {
    throw new Error(payload.errors[0]?.message ?? "GraphQL request failed.");
  }

  if (!payload.data) {
    throw new Error("GraphQL response did not include data.");
  }

  return payload.data;
}
