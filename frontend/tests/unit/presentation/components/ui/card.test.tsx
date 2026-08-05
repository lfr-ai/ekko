import { render, screen } from "@testing-library/react";
import { createRef } from "react";
import { describe, expect, it } from "vitest";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/presentation/components/ui/card";

describe("Card", () => {
  describe("Rendering", () => {
    it("renders card content", () => {
      render(<Card>Body</Card>);
      expect(screen.getByText("Body")).toBeInTheDocument();
    });

    it("renders a full composition", () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Title</CardTitle>
            <CardDescription>Description</CardDescription>
          </CardHeader>
          <CardContent>Content</CardContent>
          <CardFooter>Footer</CardFooter>
        </Card>,
      );

      expect(screen.getByText("Title")).toBeInTheDocument();
      expect(screen.getByText("Description")).toBeInTheDocument();
      expect(screen.getByText("Content")).toBeInTheDocument();
      expect(screen.getByText("Footer")).toBeInTheDocument();
    });

    it("renders the title as an h3", () => {
      render(<CardTitle>Heading</CardTitle>);
      expect(screen.getByText("Heading").tagName).toBe("H3");
    });
  });

  describe("Variants", () => {
    it("renders the default variant", () => {
      render(<Card>Default</Card>);
      expect(screen.getByText("Default")).toHaveClass("border-border");
    });

    it("renders the elevated variant", () => {
      render(<Card variant="elevated">Elevated</Card>);
      expect(screen.getByText("Elevated")).toHaveClass("shadow-lg");
    });

    it("renders the ghost variant", () => {
      render(<Card variant="ghost">Ghost</Card>);
      expect(screen.getByText("Ghost")).toHaveClass("border-transparent");
    });
  });

  describe("Behavior", () => {
    it("forwards a ref to the card element", () => {
      const ref = createRef<HTMLDivElement>();
      render(<Card ref={ref}>Ref</Card>);
      expect(ref.current).toBeInstanceOf(HTMLDivElement);
    });

    it("renders as its child element when asChild is set", () => {
      render(
        <Card asChild>
          <section>Section card</section>
        </Card>,
      );
      expect(screen.getByText("Section card").tagName).toBe("SECTION");
    });

    it("merges a custom className", () => {
      render(<Card className="custom">Styled</Card>);
      expect(screen.getByText("Styled")).toHaveClass("custom", "rounded-lg");
    });
  });
});
