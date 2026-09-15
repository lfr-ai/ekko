import { usePromptCatalog } from "@/application/hooks/use-prompt-catalog";
import type { LoadPromptCatalog } from "@/domain/models/prompt-catalog";

interface PromptCatalogPageProps {
  readonly includeContent: boolean;
  readonly loadCatalog: LoadPromptCatalog;
  readonly onIncludeContentChange: (includeContent: boolean) => void;
}

export function PromptCatalogPage({
  includeContent,
  loadCatalog,
  onIncludeContentChange,
}: PromptCatalogPageProps): React.JSX.Element {
  const catalog = usePromptCatalog(loadCatalog, includeContent);

  return (
    <main className="mx-auto min-h-screen max-w-4xl p-6 sm:p-10">
      <header className="space-y-3">
        <p className="text-sm font-medium text-muted-foreground">GraphQL learning feature</p>
        <h1 className="text-3xl font-semibold tracking-tight">Prompt catalog</h1>
        <p className="max-w-2xl text-muted-foreground">
          Browse the real prompt registry. Toggle template content to see GraphQL fetch only the
          nested fields this view requests.
        </p>
      </header>

      <label className="mt-8 flex w-fit items-center gap-3 rounded-lg border bg-card px-4 py-3">
        <input
          checked={includeContent}
          className="size-4 accent-primary"
          onChange={(event) => onIncludeContentChange(event.currentTarget.checked)}
          type="checkbox"
        />
        Include template content
      </label>

      {catalog.isPending && (
        <p aria-live="polite" className="mt-8 text-muted-foreground" role="status">
          Loading prompt catalog…
        </p>
      )}

      {catalog.isError && (
        <p className="mt-8 rounded-lg border border-destructive p-4 text-destructive" role="alert">
          {catalog.error.message}
        </p>
      )}

      {catalog.data && (
        <section aria-labelledby="catalog-heading" className="mt-8 space-y-4">
          <div className="flex items-baseline justify-between gap-4">
            <h2 className="text-xl font-semibold" id="catalog-heading">
              Active prompts
            </h2>
            <span className="text-sm text-muted-foreground">{catalog.data.versionSet}</span>
          </div>
          <ul className="grid gap-4">
            {catalog.data.prompts.map((prompt) => (
              <li className="rounded-xl border bg-card p-5 shadow-sm" key={prompt.key}>
                <h3 className="font-mono text-sm font-semibold">{prompt.key}</h3>
                {prompt.content !== undefined && (
                  <pre className="mt-4 max-h-72 overflow-auto whitespace-pre-wrap rounded-lg bg-muted p-4 text-sm">
                    {prompt.content}
                  </pre>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
