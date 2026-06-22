import { describe, expect, it } from "vitest";
import { claimIntakeSchema } from "@/domain/schemas/claim-intake-schema";

describe("claimIntakeSchema", () => {
  it("accepts valid claim intake payload", () => {
    const result = claimIntakeSchema.safeParse({
      cpr: "010190-1234",
      insuranceConditionId: "p-basic",
      coverageStartDate: "2026-01-01",
      coverageEndDate: "2026-12-31",
      payoutAmount: 3200,
      hasMultiplePolicies: true,
      hasPaid: false,
      hasPriorCasesInKs: true,
      notes: "Customer submitted complete documentation",
      attachments: [
        {
          id: "att-1",
          source: "url",
          name: "policy.pdf",
          url: "https://example.com/policy.pdf",
        },
      ],
    });

    expect(result.success).toBe(true);
  });

  it("rejects when coverage end date is before start date", () => {
    const result = claimIntakeSchema.safeParse({
      cpr: "010190-1234",
      insuranceConditionId: "p-basic",
      coverageStartDate: "2026-12-31",
      coverageEndDate: "2026-01-01",
      payoutAmount: 100,
      hasMultiplePolicies: false,
      hasPaid: false,
      hasPriorCasesInKs: false,
      attachments: [
        {
          id: "att-1",
          source: "file",
          name: "evidence.pdf",
          mimeType: "application/pdf",
          sizeBytes: 1200,
        },
      ],
    });

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues.some((issue) => issue.path.includes("coverageEndDate"))).toBe(
        true,
      );
    }
  });

  it("requires at least one attachment", () => {
    const result = claimIntakeSchema.safeParse({
      cpr: "010190-1234",
      insuranceConditionId: "p-basic",
      coverageStartDate: "2026-01-01",
      coverageEndDate: "2026-01-15",
      payoutAmount: 100,
      hasMultiplePolicies: false,
      hasPaid: false,
      hasPriorCasesInKs: false,
      attachments: [],
    });

    expect(result.success).toBe(false);
  });
});
