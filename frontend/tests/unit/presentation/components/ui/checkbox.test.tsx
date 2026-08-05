import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Checkbox } from "@/presentation/components/ui/checkbox";

describe("Checkbox", () => {
  it("renders with the checkbox role", () => {
    render(<Checkbox aria-label="accept" />);
    expect(screen.getByRole("checkbox", { name: "accept" })).toBeInTheDocument();
  });

  it("is unchecked by default", () => {
    render(<Checkbox aria-label="unchecked" />);
    expect(screen.getByRole("checkbox")).toHaveAttribute("aria-checked", "false");
  });

  it("renders checked when defaultChecked is set", () => {
    render(<Checkbox aria-label="checked" defaultChecked />);
    expect(screen.getByRole("checkbox")).toHaveAttribute("aria-checked", "true");
  });

  it("sets the data-slot attribute", () => {
    render(<Checkbox aria-label="slot" />);
    expect(screen.getByRole("checkbox")).toHaveAttribute("data-slot", "checkbox");
  });

  it("toggles when clicked", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(<Checkbox aria-label="toggle" onCheckedChange={handleChange} />);
    const checkbox = screen.getByRole("checkbox");

    await user.click(checkbox);

    expect(handleChange).toHaveBeenCalledWith(true);
    expect(checkbox).toHaveAttribute("aria-checked", "true");
  });

  it("does not toggle when disabled", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(<Checkbox aria-label="disabled" disabled onCheckedChange={handleChange} />);
    const checkbox = screen.getByRole("checkbox");

    expect(checkbox).toBeDisabled();
    await user.click(checkbox);

    expect(handleChange).not.toHaveBeenCalled();
  });

  it("merges a custom className", () => {
    render(<Checkbox aria-label="styled" className="custom" />);
    expect(screen.getByRole("checkbox")).toHaveClass("custom");
  });
});
