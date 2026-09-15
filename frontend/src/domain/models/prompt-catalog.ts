export interface PromptCatalogEntry {
  readonly content?: string;
  readonly key: string;
}

export interface PromptCatalog {
  readonly prompts: ReadonlyArray<PromptCatalogEntry>;
  readonly versionSet: string;
}

export type LoadPromptCatalog = (includeContent: boolean) => Promise<PromptCatalog>;
