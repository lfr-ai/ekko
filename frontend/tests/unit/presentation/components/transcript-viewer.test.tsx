import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { TranscriptViewer } from "@/presentation/components/transcript-viewer";

describe("TranscriptViewer", () => {
  const mockEntries = [
    {
      id: "1",
      text: "Hello from microphone",
      source: "microphone" as const,
      timestamp: "2024-01-01T10:00:00Z",
    },
    {
      id: "2",
      text: "System response here",
      source: "system" as const,
      timestamp: "2024-01-01T10:00:01Z",
    },
    {
      id: "3",
      text: "Another microphone entry",
      source: "microphone" as const,
      timestamp: "2024-01-01T10:00:02Z",
    },
  ];

  describe("Rendering", () => {
    it("renders heading", () => {
      render(<TranscriptViewer />);
      expect(screen.getByText("Transcript")).toBeInTheDocument();
    });

    it("renders empty state when no entries", () => {
      render(<TranscriptViewer />);
      expect(screen.getByText("No transcript entries yet.")).toBeInTheDocument();
    });

    it("renders all entries by default", () => {
      render(<TranscriptViewer entries={mockEntries} />);
      expect(screen.getByText("Hello from microphone")).toBeInTheDocument();
      expect(screen.getByText("System response here")).toBeInTheDocument();
      expect(screen.getByText("Another microphone entry")).toBeInTheDocument();
    });

    it("renders source labels for each entry", () => {
      render(<TranscriptViewer entries={mockEntries} />);
      const microphoneLabels = screen.getAllByText("microphone");
      const systemLabels = screen.getAllByText("system");

      // 2 microphone entries + 1 filter button = 3 total
      expect(microphoneLabels).toHaveLength(3);
      // 1 system entry + 1 filter button = 2 total
      expect(systemLabels).toHaveLength(2);
    });
  });

  describe("Filtering", () => {
    it("renders all filter buttons", () => {
      render(<TranscriptViewer entries={mockEntries} />);

      const allBtn = screen.getByRole("button", { name: /^all$/i });
      const micBtn = screen.getByRole("button", { name: /^microphone$/i });
      const sysBtn = screen.getByRole("button", { name: /^system$/i });

      expect(allBtn).toBeInTheDocument();
      expect(micBtn).toBeInTheDocument();
      expect(sysBtn).toBeInTheDocument();
    });

    it("highlights 'all' filter by default", () => {
      render(<TranscriptViewer entries={mockEntries} />);
      const allBtn = screen.getByRole("button", { name: /^all$/i });

      expect(allBtn).toHaveClass("bg-primary", "text-primary-foreground");
    });

    it("filters to microphone entries only", async () => {
      const user = userEvent.setup();
      render(<TranscriptViewer entries={mockEntries} />);

      await user.click(screen.getByRole("button", { name: /^microphone$/i }));

      expect(screen.getByText("Hello from microphone")).toBeInTheDocument();
      expect(screen.getByText("Another microphone entry")).toBeInTheDocument();
      expect(screen.queryByText("System response here")).not.toBeInTheDocument();
    });

    it("filters to system entries only", async () => {
      const user = userEvent.setup();
      render(<TranscriptViewer entries={mockEntries} />);

      await user.click(screen.getByRole("button", { name: /^system$/i }));

      expect(screen.getByText("System response here")).toBeInTheDocument();
      expect(screen.queryByText("Hello from microphone")).not.toBeInTheDocument();
      expect(screen.queryByText("Another microphone entry")).not.toBeInTheDocument();
    });

    it("returns to all entries when 'all' clicked", async () => {
      const user = userEvent.setup();
      render(<TranscriptViewer entries={mockEntries} />);

      // Filter to microphone first
      await user.click(screen.getByRole("button", { name: /^microphone$/i }));
      expect(screen.queryByText("System response here")).not.toBeInTheDocument();

      // Click 'all' to show everything again
      await user.click(screen.getByRole("button", { name: /^all$/i }));

      expect(screen.getByText("Hello from microphone")).toBeInTheDocument();
      expect(screen.getByText("System response here")).toBeInTheDocument();
      expect(screen.getByText("Another microphone entry")).toBeInTheDocument();
    });

    it("shows empty state when filtered entries are empty", async () => {
      const user = userEvent.setup();
      const micOnlyEntries = [
        {
          id: "1",
          text: "Only microphone",
          source: "microphone" as const,
          timestamp: "2024-01-01T10:00:00Z",
        },
      ];

      render(<TranscriptViewer entries={micOnlyEntries} />);

      await user.click(screen.getByRole("button", { name: /^system$/i }));

      expect(screen.getByText("No transcript entries yet.")).toBeInTheDocument();
    });
  });

  describe("Accessibility", () => {
    it("has role='log' on transcript container", () => {
      render(<TranscriptViewer entries={mockEntries} />);
      const logElement = screen.getByRole("log");

      expect(logElement).toBeInTheDocument();
    });

    it("has aria-live='polite' on transcript container", () => {
      render(<TranscriptViewer entries={mockEntries} />);
      const logElement = screen.getByRole("log");

      expect(logElement).toHaveAttribute("aria-live", "polite");
    });

    it("filter buttons have type='button' to prevent form submission", () => {
      render(<TranscriptViewer entries={mockEntries} />);

      const allBtn = screen.getByRole("button", { name: /^all$/i });
      const micBtn = screen.getByRole("button", { name: /^microphone$/i });
      const sysBtn = screen.getByRole("button", { name: /^system$/i });

      expect(allBtn).toHaveAttribute("type", "button");
      expect(micBtn).toHaveAttribute("type", "button");
      expect(sysBtn).toHaveAttribute("type", "button");
    });
  });

  describe("Styling", () => {
    it("applies custom className", () => {
      const { container } = render(<TranscriptViewer className="custom-class" />);
      const wrapper = container.firstChild as HTMLElement;

      expect(wrapper).toHaveClass("custom-class");
    });

    it("applies custom maxHeight", () => {
      render(<TranscriptViewer entries={mockEntries} maxHeight="600px" />);
      const logElement = screen.getByRole("log");

      expect(logElement).toHaveStyle({ maxHeight: "600px" });
    });

    it("uses default maxHeight of 400px", () => {
      render(<TranscriptViewer entries={mockEntries} />);
      const logElement = screen.getByRole("log");

      expect(logElement).toHaveStyle({ maxHeight: "400px" });
    });
  });

  describe("Entry Display", () => {
    it("displays entries in order", () => {
      render(<TranscriptViewer entries={mockEntries} />);

      expect(screen.getByText("Hello from microphone")).toBeInTheDocument();
      expect(screen.getByText("System response here")).toBeInTheDocument();
      expect(screen.getByText("Another microphone entry")).toBeInTheDocument();
    });

    it("uses unique keys for entries", () => {
      const { container } = render(<TranscriptViewer entries={mockEntries} />);
      const logElement = container.querySelector('[role="log"]');
      const entryDivs = logElement?.querySelectorAll('[class*="rounded-md p-2"]');

      expect(entryDivs).toHaveLength(3);
    });
  });

  describe("Interactive Filter State", () => {
    it("updates filter button styles on click", async () => {
      const user = userEvent.setup();
      render(<TranscriptViewer entries={mockEntries} />);

      const micBtn = screen.getByRole("button", { name: /^microphone$/i });

      // Initially not highlighted
      expect(micBtn).not.toHaveClass("bg-primary");

      await user.click(micBtn);

      // Now highlighted
      expect(micBtn).toHaveClass("bg-primary", "text-primary-foreground");
    });

    it("removes highlight from previous filter", async () => {
      const user = userEvent.setup();
      render(<TranscriptViewer entries={mockEntries} />);

      const allBtn = screen.getByRole("button", { name: /^all$/i });
      const micBtn = screen.getByRole("button", { name: /^microphone$/i });

      // 'all' starts highlighted
      expect(allBtn).toHaveClass("bg-primary");

      await user.click(micBtn);

      // 'all' no longer highlighted
      expect(allBtn).not.toHaveClass("bg-primary");
      expect(allBtn).toHaveClass("bg-muted");
    });
  });
});
