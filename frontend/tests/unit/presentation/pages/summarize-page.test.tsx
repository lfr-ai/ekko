import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { SummarizeChunks } from "@/domain/models/summary";
import { SummarizePage } from "@/presentation/pages/summarize-page";

function _renderPage(summarize: SummarizeChunks) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <SummarizePage summarize={summarize} />
    </QueryClientProvider>,
  );
}

describe("SummarizePage", () => {
  it("submits the pasted transcript and renders the summary", async () => {
    const summarize = vi.fn<SummarizeChunks>().mockResolvedValue({ summary: "A concise summary." });
    const user = userEvent.setup();
    _renderPage(summarize);

    await user.type(screen.getByLabelText("Transcript text"), "Hello there, this is a transcript.");
    await user.click(screen.getByRole("button", { name: "Summarize" }));

    expect(await screen.findByRole("heading", { name: "Summary" })).toBeInTheDocument();
    expect(screen.getByText("A concise summary.")).toBeInTheDocument();
    expect(summarize).toHaveBeenCalledWith(["Hello there, this is a transcript."]);
  });

  it("disables submission until there is transcript text", () => {
    _renderPage(vi.fn());

    expect(screen.getByRole("button", { name: "Summarize" })).toBeDisabled();
  });

  it("announces failures", async () => {
    const summarize = vi
      .fn<SummarizeChunks>()
      .mockRejectedValue(new Error("Request could not be processed"));
    const user = userEvent.setup();
    _renderPage(summarize);

    await user.type(screen.getByLabelText("Transcript text"), "Some transcript text.");
    await user.click(screen.getByRole("button", { name: "Summarize" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Request could not be processed");
  });
});
