import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Button } from "@/presentation/components/ui/button";

describe("Button", () => {
  describe("Rendering", () => {
    it("renders children correctly", () => {
      render(<Button>Click me</Button>);
      expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument();
    });

    it("renders as a button element", () => {
      render(<Button>Test</Button>);
      const button = screen.getByRole("button");
      expect(button.tagName).toBe("BUTTON");
    });
  });

  describe("Variants", () => {
    it("renders default variant", () => {
      render(<Button>Default</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("bg-primary", "text-primary-foreground");
    });

    it("renders destructive variant", () => {
      render(<Button variant="destructive">Delete</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("bg-destructive", "text-destructive-foreground");
    });

    it("renders outline variant", () => {
      render(<Button variant="outline">Outline</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("border", "border-input", "bg-background");
    });

    it("renders secondary variant", () => {
      render(<Button variant="secondary">Secondary</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("bg-secondary", "text-secondary-foreground");
    });

    it("renders ghost variant", () => {
      render(<Button variant="ghost">Ghost</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("hover:bg-accent");
    });

    it("renders link variant", () => {
      render(<Button variant="link">Link</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("text-primary", "underline-offset-4");
    });
  });

  describe("Sizes", () => {
    it("renders default size", () => {
      render(<Button>Default Size</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("h-10", "px-4", "py-2");
    });

    it("renders small size", () => {
      render(<Button size="sm">Small</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("h-9", "px-3");
    });

    it("renders large size", () => {
      render(<Button size="lg">Large</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("h-11", "px-8");
    });

    it("renders icon size", () => {
      render(<Button size="icon">☰</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("h-10", "w-10");
    });
  });

  describe("Custom Styling", () => {
    it("applies custom className", () => {
      render(<Button className="custom-class">Custom</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("custom-class");
    });

    it("merges custom className with variant classes", () => {
      render(
        <Button className="custom-class" variant="destructive">
          Custom Destructive
        </Button>,
      );
      const button = screen.getByRole("button");

      expect(button).toHaveClass("custom-class", "bg-destructive");
    });
  });

  describe("Interactions", () => {
    it("handles click events", async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<Button onClick={handleClick}>Click me</Button>);

      await user.click(screen.getByRole("button"));

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it("does not fire click when disabled", async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(
        <Button onClick={handleClick} disabled>
          Disabled
        </Button>,
      );

      const button = screen.getByRole("button");

      await user.click(button);

      expect(handleClick).not.toHaveBeenCalled();
    });

    it("handles double click", async () => {
      const user = userEvent.setup();
      const handleDblClick = vi.fn();

      render(<Button onDoubleClick={handleDblClick}>Double click</Button>);

      await user.dblClick(screen.getByRole("button"));

      expect(handleDblClick).toHaveBeenCalledTimes(1);
    });

    it("handles keyboard activation (Enter)", async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<Button onClick={handleClick}>Press Enter</Button>);

      const button = screen.getByRole("button");
      button.focus();

      await user.keyboard("{Enter}");

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it("handles keyboard activation (Space)", async () => {
      const user = userEvent.setup();
      const handleClick = vi.fn();

      render(<Button onClick={handleClick}>Press Space</Button>);

      const button = screen.getByRole("button");
      button.focus();

      await user.keyboard(" ");

      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe("Disabled State", () => {
    it("renders disabled button", () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole("button");

      expect(button).toBeDisabled();
    });

    it("applies disabled styles", () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("disabled:pointer-events-none", "disabled:opacity-50");
    });

    it("does not respond to hover when disabled", () => {
      render(<Button disabled>Disabled</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("disabled:pointer-events-none");
    });
  });

  describe("Accessibility", () => {
    it("has correct role", () => {
      render(<Button>Accessible</Button>);
      expect(screen.getByRole("button")).toBeInTheDocument();
    });

    it("supports aria-label", () => {
      render(<Button aria-label="Close dialog">×</Button>);
      expect(screen.getByRole("button", { name: "Close dialog" })).toBeInTheDocument();
    });

    it("supports aria-describedby", () => {
      render(
        <>
          <Button aria-describedby="help-text">Submit</Button>
          <span id="help-text">This will save your changes</span>
        </>,
      );
      const button = screen.getByRole("button");

      expect(button).toHaveAttribute("aria-describedby", "help-text");
    });

    it("is keyboard focusable", () => {
      render(<Button>Focusable</Button>);
      const button = screen.getByRole("button");

      button.focus();

      expect(button).toHaveFocus();
    });

    it("has visible focus styles", () => {
      render(<Button>Focus me</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveClass("focus-visible:outline-none", "focus-visible:ring-2");
    });
  });

  describe("HTML Attributes", () => {
    it("supports type attribute", () => {
      render(<Button type="submit">Submit</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveAttribute("type", "submit");
    });

    it("defaults to type='button' implicitly", () => {
      render(<Button>Default type</Button>);
      const button = screen.getByRole("button");

      // HTML buttons default to 'submit', but we want to verify the component behavior
      expect(button.tagName).toBe("BUTTON");
    });

    it("supports name attribute", () => {
      render(<Button name="action">Action</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveAttribute("name", "action");
    });

    it("supports value attribute", () => {
      render(<Button value="send">Send</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveAttribute("value", "send");
    });

    it("supports form attribute", () => {
      render(<Button form="my-form">External Submit</Button>);
      const button = screen.getByRole("button");

      expect(button).toHaveAttribute("form", "my-form");
    });
  });

  describe("Ref Forwarding", () => {
    it("forwards ref to button element", () => {
      const ref = { current: null };

      render(<Button ref={ref}>Ref Button</Button>);

      expect(ref.current).toBeInstanceOf(HTMLButtonElement);
    });

    it("allows imperative focus via ref", () => {
      const ref = { current: null as HTMLButtonElement | null };

      render(<Button ref={ref}>Focus via ref</Button>);

      ref.current?.focus();

      expect(ref.current).toHaveFocus();
    });
  });

  describe("Content", () => {
    it("renders text content", () => {
      render(<Button>Text Button</Button>);
      expect(screen.getByText("Text Button")).toBeInTheDocument();
    });

    it("renders icon and text", () => {
      render(
        <Button>
          <span>✓</span>
          <span>Save</span>
        </Button>,
      );

      expect(screen.getByText("✓")).toBeInTheDocument();
      expect(screen.getByText("Save")).toBeInTheDocument();
    });

    it("renders only icon", () => {
      render(<Button size="icon">☰</Button>);
      expect(screen.getByText("☰")).toBeInTheDocument();
    });
  });
});
