import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Switch } from "@/presentation/components/ui/switch";

describe("Switch", () => {
  it("renders with the switch role", () => {
    render(<Switch aria-label="notifications" />);
    expect(screen.getByRole("switch", { name: "notifications" })).toBeInTheDocument();
  });

  it("is off by default", () => {
    render(<Switch aria-label="off" />);
    expect(screen.getByRole("switch")).toHaveAttribute("aria-checked", "false");
  });

  it("renders on when defaultChecked is set", () => {
    render(<Switch aria-label="on" defaultChecked />);
    expect(screen.getByRole("switch")).toHaveAttribute("aria-checked", "true");
  });

  it("uses the default size", () => {
    render(<Switch aria-label="default-size" />);
    expect(screen.getByRole("switch")).toHaveAttribute("data-size", "default");
  });

  it("supports the small size", () => {
    render(<Switch aria-label="small" size="sm" />);
    expect(screen.getByRole("switch")).toHaveAttribute("data-size", "sm");
  });

  it("toggles when clicked", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(<Switch aria-label="toggle" onCheckedChange={handleChange} />);
    const toggle = screen.getByRole("switch");

    await user.click(toggle);

    expect(handleChange).toHaveBeenCalledWith(true);
    expect(toggle).toHaveAttribute("aria-checked", "true");
  });

  it("does not toggle when disabled", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();
    render(<Switch aria-label="disabled" disabled onCheckedChange={handleChange} />);

    await user.click(screen.getByRole("switch"));

    expect(handleChange).not.toHaveBeenCalled();
  });

  it("merges a custom className", () => {
    render(<Switch aria-label="styled" className="custom" />);
    expect(screen.getByRole("switch")).toHaveClass("custom");
  });
});
