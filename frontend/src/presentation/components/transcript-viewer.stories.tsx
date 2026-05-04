import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "@storybook/test";
import { TranscriptViewer } from "./transcript-viewer";

const sampleEntries = [
  {
    id: "1",
    text: "Hej, jeg vil gerne høre om mine pensionsordninger.",
    source: "microphone" as const,
    timestamp: "2026-04-29T10:00:00Z",
  },
  {
    id: "2",
    text: "Selvfølgelig! Lad mig hente dine oplysninger.",
    source: "system" as const,
    timestamp: "2026-04-29T10:00:02Z",
  },
  {
    id: "3",
    text: "Jeg har tre active ordninger hos AP Pension.",
    source: "system" as const,
    timestamp: "2026-04-29T10:00:05Z",
  },
  {
    id: "4",
    text: "Kan du fortælle mig mere om den største?",
    source: "microphone" as const,
    timestamp: "2026-04-29T10:00:08Z",
  },
];

const meta = {
  title: "Components/TranscriptViewer",
  component: TranscriptViewer,
  parameters: {
    layout: "padded",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof TranscriptViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Empty: Story = {
  args: {
    entries: [],
  },
};

export const WithEntries: Story = {
  args: {
    entries: sampleEntries,
  },
};

export const FilterInteraction: Story = {
  args: {
    entries: sampleEntries,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Click "microphone" filter
    await userEvent.click(canvas.getByText("microphone"));

    // Should only show microphone entries
    const entries = canvas.getAllByText(/pensionsordninger|fortælle/);
    await expect(entries.length).toBe(2);

    // Click "all" to reset
    await userEvent.click(canvas.getByText("all"));
    const allEntries = canvas.getAllByText(/microphone|system/i);
    await expect(allEntries.length).toBeGreaterThanOrEqual(4);
  },
};
