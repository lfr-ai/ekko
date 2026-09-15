import { afterEach, describe, expect, it, vi } from "vitest";
import { loadPromptCatalog } from "@/infrastructure/graphql/prompt-catalog-client";

describe("loadPromptCatalog", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends the exact named query and field-selection variable", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          data: {
            promptCatalog: {
              prompts: [{ content: "Template", key: "summary_chunks" }],
              versionSet: "experimental",
            },
          },
        }),
        { headers: { "Content-Type": "application/json" }, status: 200 },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const catalog = await loadPromptCatalog(true);

    expect(catalog.prompts[0]?.content).toBe("Template");
    const [, options] = fetchMock.mock.calls[0] ?? [];
    expect(JSON.parse(String(options?.body))).toMatchObject({
      operationName: "PromptCatalog",
      variables: { includeContent: true },
    });
  });

  it("surfaces GraphQL errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ errors: [{ message: "Prompt registry unavailable" }] }), {
          headers: { "Content-Type": "application/json" },
          status: 200,
        }),
      ),
    );

    await expect(loadPromptCatalog(false)).rejects.toThrow("Prompt registry unavailable");
  });
});
