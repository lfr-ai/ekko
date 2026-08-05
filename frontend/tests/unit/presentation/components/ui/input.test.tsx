import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Input } from "@/presentation/components/ui/input";

describe("Input", () => {
  it("renders an input element", () => {
    render(<Input placeholder="Email" />);
    expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
  });

  it("applies the provided type", () => {
    render(<Input type="password" aria-label="pw" />);
    expect(screen.getByLabelText("pw")).toHaveAttribute("type", "password");
  });

  it("sets the data-slot attribute", () => {
    render(<Input aria-label="field" />);
    expect(screen.getByLabelText("field")).toHaveAttribute("data-slot", "input");
  });

  it("merges a custom className", () => {
    render(<Input aria-label="styled" className="custom" />);
    expect(screen.getByLabelText("styled")).toHaveClass("custom");
  });

  it("accepts user typing", async () => {
    const user = userEvent.setup();
    render(<Input aria-label="name" />);
    const input = screen.getByLabelText("name");

    await user.type(input, "hello");

    expect(input).toHaveValue("hello");
  });

  it("does not accept input when disabled", async () => {
    const user = userEvent.setup();
    render(<Input aria-label="disabled-field" disabled />);
    const input = screen.getByLabelText("disabled-field");

    expect(input).toBeDisabled();
    await user.type(input, "x");

    expect(input).toHaveValue("");
  });

  it("fires the onChange handler", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(<Input aria-label="change" onChange={handleChange} />);

    await user.type(screen.getByLabelText("change"), "a");

    expect(handleChange).toHaveBeenCalled();
  });
});
