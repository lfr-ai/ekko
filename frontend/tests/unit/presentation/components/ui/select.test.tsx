import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/presentation/components/ui/select";

interface RenderOptions {
  readonly disabled?: boolean;
  readonly defaultValue?: string;
  readonly open?: boolean;
}

function renderSelect(options: RenderOptions = {}) {
  return render(
    <Select disabled={options.disabled} defaultValue={options.defaultValue} open={options.open}>
      <SelectTrigger aria-label="fruit" className="custom-trigger">
        <SelectValue placeholder="Pick a fruit" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="apple">Apple</SelectItem>
        <SelectItem value="banana">Banana</SelectItem>
      </SelectContent>
    </Select>,
  );
}

describe("Select", () => {
  it("renders a closed trigger with the combobox role", () => {
    renderSelect();
    expect(screen.getByRole("combobox", { name: "fruit" })).toBeInTheDocument();
  });

  it("shows the placeholder when no value is selected", () => {
    renderSelect();
    expect(screen.getByText("Pick a fruit")).toBeInTheDocument();
  });

  it("merges a custom className on the trigger", () => {
    renderSelect();
    expect(screen.getByRole("combobox")).toHaveClass("custom-trigger");
  });

  it("sets the data-slot attribute on the trigger", () => {
    renderSelect();
    expect(screen.getByRole("combobox")).toHaveAttribute("data-slot", "select-trigger");
  });

  it("renders the selected value", () => {
    renderSelect({ defaultValue: "apple" });
    expect(screen.getByRole("combobox")).toHaveTextContent("Apple");
  });

  it("disables the trigger when disabled", () => {
    renderSelect({ disabled: true });
    expect(screen.getByRole("combobox")).toBeDisabled();
  });

  it("renders the options when open", () => {
    renderSelect({ open: true });
    expect(screen.getByRole("option", { name: "Apple" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Banana" })).toBeInTheDocument();
  });
});
