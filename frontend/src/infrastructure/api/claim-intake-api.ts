import type {
  ClaimIntakeInput,
  ClaimIntakeSubmissionResult,
  InsuranceConditionOption,
} from "@/domain/types/claim-intake";
import { getJson, postJson } from "@/infrastructure/api/http-client";

interface InsuranceConditionOptionsResponse {
  readonly items: ReadonlyArray<InsuranceConditionOption>;
}

export async function fetchInsuranceConditionOptions(): Promise<
  ReadonlyArray<InsuranceConditionOption>
> {
  const response = await getJson<InsuranceConditionOptionsResponse>("/insurance-conditions/options");
  return response.items;
}

export async function submitClaimIntake(
  input: ClaimIntakeInput,
): Promise<ClaimIntakeSubmissionResult> {
  return postJson<ClaimIntakeSubmissionResult>("/claims/intake", input);
}
