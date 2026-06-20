import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "@/App";

describe("App", () => {
  it("renders claim intake heading", async () => {
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>,
    );

    expect(await screen.findByText("Insurance claim intake")).toBeInTheDocument();
  });

  it("renders key form labels", async () => {
    const queryClient = new QueryClient();

    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>,
    );

    expect(await screen.findByLabelText("CPR")).toBeInTheDocument();
    expect(screen.getByLabelText("Insurance condition P")).toBeInTheDocument();
    expect(screen.getByLabelText("Coverage period start")).toBeInTheDocument();
    expect(screen.getByLabelText("Coverage period end")).toBeInTheDocument();
  });
});
