import { render, screen } from "@testing-library/react";
import { createRef } from "react";
import { describe, expect, it } from "vitest";
import { Separator } from "@/presentation/components/ui/separator";

describe("Separator", () => {
  it("renders a decorative separator by default", () => {
    const { container } = render(<Separator />);
    expect(container.firstChild).toHaveAttribute("role", "none");
  });

  it("renders horizontal orientation classes by default", () => {
    const { container } = render(<Separator />);
    expect(container.firstChild).toHaveClass("h-px", "w-full");
  });

  it("renders vertical orientation classes", () => {
    const { container } = render(<Separator orientation="vertical" />);
    expect(container.firstChild).toHaveClass("h-full", "w-px");
  });

  it("exposes the separator role when non-decorative", () => {
    render(<Separator decorative={false} />);
    expect(screen.getByRole("separator")).toBeInTheDocument();
  });

  it("sets aria-orientation when non-decorative", () => {
    render(<Separator decorative={false} orientation="vertical" />);
    expect(screen.getByRole("separator")).toHaveAttribute("aria-orientation", "vertical");
  });

  it("merges a custom className", () => {
    const { container } = render(<Separator className="custom" />);
    expect(container.firstChild).toHaveClass("custom", "bg-border");
  });

  it("forwards a ref", () => {
    const ref = createRef<HTMLDivElement>();
    render(<Separator ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });
});
