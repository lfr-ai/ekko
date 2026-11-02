import { afterEach, describe, expect, it, vi } from "vitest";
import { summarizeChunks } from "@/infrastructure/api/summarize-client";

describe("summarizeChunks", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("posts the chunks and returns the summary", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        new Response(JSON.stringify({ summary: "A concise summary." }), { status: 200 }),
      );
    vi.stubGlobal("fetch", fetchMock);

    const result = await summarizeChunks(["First chunk.", "Second chunk."]);

    expect(result.summary).toBe("A concise summary.");
    const [url, options] = fetchMock.mock.calls[0] ?? [];
    expect(url).toBe("/summarize");
    expect(JSON.parse(String(options?.body))).toEqual({
      chunks: ["First chunk.", "Second chunk."],
    });
  });

  it("surfaces the server-provided error detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Request could not be processed" }), {
          status: 422,
        }),
      ),
    );

    await expect(summarizeChunks(["Some text"])).rejects.toThrow("Request could not be processed");
  });
});
