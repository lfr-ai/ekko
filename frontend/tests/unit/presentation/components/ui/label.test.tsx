import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Label } from "@/presentation/components/ui/label";

describe("Label", () => {
  it("renders its text", () => {
    render(<Label>Email address</Label>);
    expect(screen.getByText("Email address")).toBeInTheDocument();
  });

  it("renders as a label element", () => {
    render(<Label>Name</Label>);
    expect(screen.getByText("Name").tagName).toBe("LABEL");
  });

  it("sets the data-slot attribute", () => {
    render(<Label>Slot</Label>);
    expect(screen.getByText("Slot")).toHaveAttribute("data-slot", "label");
  });

  it("associates with a control via htmlFor", () => {
    render(
      <>
        <Label htmlFor="email">Email</Label>
        <input id="email" />
      </>,
    );
    expect(screen.getByText("Email")).toHaveAttribute("for", "email");
  });

  it("merges a custom className", () => {
    render(<Label className="custom">Styled</Label>);
    expect(screen.getByText("Styled")).toHaveClass("custom");
  });
});
