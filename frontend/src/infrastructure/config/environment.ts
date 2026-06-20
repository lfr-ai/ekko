const DEFAULT_API_BASE_URL = "/api";

export interface FrontendEnvironment {
  readonly apiBaseUrl: string;
}

export const frontendEnvironment: FrontendEnvironment = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL,
};
