import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Textarea } from "@/presentation/components/ui/textarea";

describe("Textarea", () => {
  it("renders a textarea element", () => {
    render(<Textarea placeholder="Notes" />);
    expect(screen.getByPlaceholderText("Notes")).toBeInTheDocument();
  });

  it("sets the data-slot attribute", () => {
    render(<Textarea aria-label="ta" />);
    expect(screen.getByLabelText("ta")).toHaveAttribute("data-slot", "textarea");
  });

  it("merges a custom className", () => {
    render(<Textarea aria-label="styled" className="custom" />);
    expect(screen.getByLabelText("styled")).toHaveClass("custom");
  });

  it("accepts user typing", async () => {
    const user = userEvent.setup();
    render(<Textarea aria-label="body" />);
    const textarea = screen.getByLabelText("body");

    await user.type(textarea, "multi line");

    expect(textarea).toHaveValue("multi line");
  });

  it("respects the disabled state", async () => {
    const user = userEvent.setup();
    render(<Textarea aria-label="disabled-ta" disabled />);
    const textarea = screen.getByLabelText("disabled-ta");

    expect(textarea).toBeDisabled();
    await user.type(textarea, "x");

    expect(textarea).toHaveValue("");
  });

  it("fires the onChange handler", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(<Textarea aria-label="change" onChange={handleChange} />);

    await user.type(screen.getByLabelText("change"), "a");

    expect(handleChange).toHaveBeenCalled();
  });
});
