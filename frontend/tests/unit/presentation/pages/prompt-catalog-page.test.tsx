import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import type { LoadPromptCatalog } from "@/domain/models/prompt-catalog";
import { PromptCatalogPage } from "@/presentation/pages/prompt-catalog-page";

function TestPage({ loadCatalog }: { readonly loadCatalog: LoadPromptCatalog }) {
  const [includeContent, setIncludeContent] = useState(false);
  return (
    <PromptCatalogPage
      includeContent={includeContent}
      loadCatalog={loadCatalog}
      onIncludeContentChange={setIncludeContent}
    />
  );
}

function _renderPage(loadCatalog: LoadPromptCatalog) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <TestPage loadCatalog={loadCatalog} />
    </QueryClientProvider>,
  );
}

describe("PromptCatalogPage", () => {
  it("loads keys first and refetches content when selected", async () => {
    const loadCatalog = vi.fn<LoadPromptCatalog>().mockImplementation(async (includeContent) => ({
      prompts: [
        {
          ...(includeContent ? { content: "Summarize this content" } : {}),
          key: "summary_chunks",
        },
      ],
      versionSet: "experimental",
    }));
    const user = userEvent.setup();
    _renderPage(loadCatalog);

    expect(await screen.findByRole("heading", { name: "Active prompts" })).toBeInTheDocument();
    expect(loadCatalog).toHaveBeenCalledWith(false);
    expect(screen.queryByText("Summarize this content")).not.toBeInTheDocument();

    await user.click(screen.getByRole("checkbox", { name: "Include template content" }));

    expect(await screen.findByText("Summarize this content")).toBeInTheDocument();
    expect(loadCatalog).toHaveBeenLastCalledWith(true);
  });

  it("announces loading failures", async () => {
    const loadCatalog = vi.fn<LoadPromptCatalog>().mockRejectedValue(new Error("Unavailable"));
    _renderPage(loadCatalog);

    expect(await screen.findByRole("alert")).toHaveTextContent("Unavailable");
  });
});
