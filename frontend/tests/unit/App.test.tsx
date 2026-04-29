import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "@/App";

describe("App", () => {
  it("renders heading", () => {
    render(<App />);
    expect(screen.getByText("Ekko")).toBeInTheDocument();
  });

  it("renders description", () => {
    render(<App />);
    expect(screen.getByText(/voice assistant/i)).toBeInTheDocument();
  });
});
