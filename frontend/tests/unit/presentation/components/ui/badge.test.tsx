import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge } from "@/presentation/components/ui/badge";

describe("Badge", () => {
  describe("Rendering", () => {
    it("renders children", () => {
      render(<Badge>New</Badge>);
      expect(screen.getByText("New")).toBeInTheDocument();
    });

    it("renders as a div element", () => {
      render(<Badge>Tag</Badge>);
      expect(screen.getByText("Tag").tagName).toBe("DIV");
    });
  });

  describe("Variants", () => {
    it("renders the default variant", () => {
      render(<Badge>Default</Badge>);
      expect(screen.getByText("Default")).toHaveClass("bg-primary", "text-primary-foreground");
    });

    it("renders the secondary variant", () => {
      render(<Badge variant="secondary">Secondary</Badge>);
      expect(screen.getByText("Secondary")).toHaveClass("bg-secondary");
    });

    it("renders the destructive variant", () => {
      render(<Badge variant="destructive">Destructive</Badge>);
      expect(screen.getByText("Destructive")).toHaveClass("bg-destructive");
    });

    it("renders the outline variant", () => {
      render(<Badge variant="outline">Outline</Badge>);
      expect(screen.getByText("Outline")).toHaveClass("text-foreground");
    });

    it("renders the success variant", () => {
      render(<Badge variant="success">Success</Badge>);
      expect(screen.getByText("Success")).toHaveClass("bg-success");
    });

    it("renders the warning variant", () => {
      render(<Badge variant="warning">Warning</Badge>);
      expect(screen.getByText("Warning")).toHaveClass("bg-warning");
    });
  });

  describe("Custom styling", () => {
    it("merges a custom className", () => {
      render(<Badge className="custom">Custom</Badge>);
      expect(screen.getByText("Custom")).toHaveClass("custom", "rounded-full");
    });

    it("forwards HTML attributes", () => {
      render(
        <Badge data-testid="badge-el" title="hint">
          A
        </Badge>,
      );
      expect(screen.getByTestId("badge-el")).toHaveAttribute("title", "hint");
    });
  });
});
