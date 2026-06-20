import type {
  ClaimIntakeInput,
  ClaimIntakeSubmissionResult,
  InsuranceConditionOption,
} from "@/domain/types/claim-intake";
import { getJson, postJson } from "@/infrastructure/api/http-client";

const FALLBACK_INSURANCE_CONDITION_OPTIONS: ReadonlyArray<InsuranceConditionOption> = [
  { id: "p-basic", code: "P_BASIC", label: "P Basic" },
  { id: "p-plus", code: "P_PLUS", label: "P Plus" },
  { id: "p-premium", code: "P_PREMIUM", label: "P Premium" },
];

interface InsuranceConditionOptionsResponse {
  readonly items: ReadonlyArray<InsuranceConditionOption>;
}

export async function fetchInsuranceConditionOptions(): Promise<
  ReadonlyArray<InsuranceConditionOption>
> {
  try {
    const response = await getJson<InsuranceConditionOptionsResponse>(
      "/insurance-conditions/options",
    );

    if (response.items.length === 0) {
      return FALLBACK_INSURANCE_CONDITION_OPTIONS;
    }

    return response.items;
  } catch {
    return FALLBACK_INSURANCE_CONDITION_OPTIONS;
  }
}

export async function submitClaimIntake(
  input: ClaimIntakeInput,
): Promise<ClaimIntakeSubmissionResult> {
  return postJson<ClaimIntakeSubmissionResult>("/claims/intake", input);
}
