import { afterEach, describe, expect, it, vi } from "vitest";
import {
  fetchInsuranceConditionOptions,
  submitClaimIntake,
} from "@/infrastructure/api/claim-intake-api";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("claim-intake-api", () => {
  it("returns insurance condition options from API", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        items: [{ code: "P_BASIC", id: "p-basic", label: "P Basic" }],
      }),
      status: 200,
    });

    vi.stubGlobal("fetch", fetchMock);

    const result = await fetchInsuranceConditionOptions();

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/insurance-conditions/options"),
      expect.objectContaining({ method: "GET" }),
    );
    expect(result).toEqual([{ code: "P_BASIC", id: "p-basic", label: "P Basic" }]);
  });

  it("throws when insurance condition options request fails", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
    });

    vi.stubGlobal("fetch", fetchMock);

    await expect(fetchInsuranceConditionOptions()).rejects.toThrow(
      "GET /insurance-conditions/options failed with status 503.",
    );
  });

  it("submits claim intake payload", async () => {
    const payload = {
      attachments: [{ id: "att-1", name: "claim.pdf", source: "url" as const, url: "https://example.com/claim.pdf" }],
      cpr: "010190-1234",
      coverageEndDate: "2026-12-31",
      coverageStartDate: "2026-01-01",
      hasMultiplePolicies: false,
      hasPaid: false,
      hasPriorCasesInKs: false,
      insuranceConditionId: "p-basic",
      payoutAmount: 1234,
    };

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ acceptedAtIso: "2026-06-22T10:30:00Z", referenceId: "CLAIM-42" }),
      status: 200,
    });

    vi.stubGlobal("fetch", fetchMock);

    const result = await submitClaimIntake(payload);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/claims/intake"),
      expect.objectContaining({
        body: JSON.stringify(payload),
        method: "POST",
      }),
    );
    expect(result.referenceId).toBe("CLAIM-42");
  });
});
