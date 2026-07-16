import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, within } from "@storybook/test";
import { useEffect, type JSX, type ReactNode } from "react";
import { ClaimIntakeForm } from "@/presentation/features/claim-intake/claim-intake-form";

interface MockApiProviderProps {
  readonly children: ReactNode;
}

function MockApiProvider({ children }: MockApiProviderProps): JSX.Element {
  useEffect(() => {
    const originalFetch = globalThis.fetch;

    globalThis.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      const requestUrl = typeof input === "string" ? input : input.toString();

      if (requestUrl.endsWith("/insurance-conditions/options")) {
        return new Response(
          JSON.stringify({
            items: [
              { id: "p-basic", code: "P_BASIC", label: "P Basic" },
              { id: "p-plus", code: "P_PLUS", label: "P Plus" },
            ],
          }),
          {
            headers: { "Content-Type": "application/json" },
            status: 200,
          },
        );
      }

      if (requestUrl.endsWith("/claims/intake") && init?.method === "POST") {
        return new Response(
          JSON.stringify({
            acceptedAtIso: "2026-06-22T10:30:00Z",
            referenceId: "CLAIM-STORY-001",
          }),
          {
            headers: { "Content-Type": "application/json" },
            status: 200,
          },
        );
      }

      return originalFetch(input, init);
    };

    return () => {
      globalThis.fetch = originalFetch;
    };
  }, []);

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        gcTime: 0,
        retry: false,
      },
    },
  });

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

const meta = {
  title: "Features/Claim Intake/Form",
  component: ClaimIntakeForm,
  tags: ["autodocs", "ai-generated"],
  decorators: [
    (Story) => (
      <MockApiProvider>
        <Story />
      </MockApiProvider>
    ),
  ],
  parameters: {
    layout: "padded",
  },
} satisfies Meta<typeof ClaimIntakeForm>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Use this flow when a claims handler registers a new intake with required metadata
 * and at least one supporting attachment URL.
 *
 * @summary Complete intake submission with URL attachment
 */
export const SubmitWithUrlAttachment: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByLabelText("CPR"), "010190-1234");
    await userEvent.click(canvas.getByLabelText("Insurance condition P"));
    await userEvent.click(canvas.getByRole("option", { name: "P Basic" }));

    await userEvent.type(canvas.getByLabelText("Coverage period start"), "2026-01-01");
    await userEvent.type(canvas.getByLabelText("Coverage period end"), "2026-12-31");
    await userEvent.type(canvas.getByLabelText("Payout amount"), "1500");

    await userEvent.type(
      canvas.getByPlaceholderText("Paste file URL (PDF or similar)"),
      "https://example.com/docs/claim.pdf",
    );
    await userEvent.click(canvas.getByRole("button", { name: "Add URL" }));

    await userEvent.click(canvas.getByRole("button", { name: "Submit claim intake" }));

    await expect(canvas.getByText(/Claim intake submitted\. Reference:/)).toBeVisible();
  },
};

/**
 * Use this when validating client-side URL checks before allowing users
 * to add remote evidence links.
 *
 * @summary Invalid attachment URL validation feedback
 */
export const InvalidUrlFeedback: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByPlaceholderText("Paste file URL (PDF or similar)"), "invalid");
    await userEvent.click(canvas.getByRole("button", { name: "Add URL" }));

    await expect(canvas.getByText("Please provide a valid URL.")).toBeVisible();
  },
};
