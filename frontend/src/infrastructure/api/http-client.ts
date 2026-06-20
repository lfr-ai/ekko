import { frontendEnvironment } from "@/infrastructure/config/environment";

const JSON_HEADERS: HeadersInit = {
  "Content-Type": "application/json",
};

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
