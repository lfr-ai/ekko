import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ClaimIntakeForm } from "@/presentation/features/claim-intake/claim-intake-form";

const mutateAsyncMock = vi.fn();

vi.mock("@/application/hooks/use-insurance-condition-options", () => ({
  useInsuranceConditionOptions: () => ({
    data: [
      {
        id: "p-basic",
        code: "P_BASIC",
        label: "P Basic",
      },
    ],
    isLoading: false,
  }),
}));

vi.mock("@/application/hooks/use-submit-claim-intake", () => ({
  useSubmitClaimIntake: () => ({
    isPending: false,
    mutateAsync: mutateAsyncMock,
  }),
}));

describe("ClaimIntakeForm", () => {
  beforeEach(() => {
    mutateAsyncMock.mockReset();
    mutateAsyncMock.mockResolvedValue({
      acceptedAtIso: "2026-06-20T09:00:00Z",
      referenceId: "CLAIM-123",
    });
  });

  it("renders key intake fields", () => {
    render(<ClaimIntakeForm />);

    expect(screen.getByLabelText("CPR")).toBeInTheDocument();
    expect(screen.getByLabelText("Insurance condition P")).toBeInTheDocument();
    expect(screen.getByLabelText("Coverage period start")).toBeInTheDocument();
    expect(screen.getByLabelText("Coverage period end")).toBeInTheDocument();
    expect(screen.getByLabelText("Payout amount")).toBeInTheDocument();
  });

  it("shows validation when URL attachment is invalid", async () => {
    const user = userEvent.setup();

    render(<ClaimIntakeForm />);

    await user.type(screen.getByPlaceholderText("Paste file URL (PDF or similar)"), "not-a-url");
    await user.click(screen.getByRole("button", { name: "Add URL" }));

    expect(await screen.findByText("Please provide a valid URL.")).toBeInTheDocument();
  });

  it("adds URL attachment to the attachment list", async () => {
    const user = userEvent.setup();

    render(<ClaimIntakeForm />);

    await user.type(
      screen.getByPlaceholderText("Paste file URL (PDF or similar)"),
      "https://example.com/claim.pdf",
    );
    await user.click(screen.getByRole("button", { name: "Add URL" }));

    expect(await screen.findByText("claim.pdf")).toBeInTheDocument();
    expect(screen.getByText("https://example.com/claim.pdf")).toBeInTheDocument();
    expect(mutateAsyncMock).not.toHaveBeenCalled();
  });
});
