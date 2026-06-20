import { useMutation } from "@tanstack/react-query";
import type { ClaimIntakeInput } from "@/domain/types/claim-intake";
import { submitClaimIntake } from "@/infrastructure/api/claim-intake-api";

export function useSubmitClaimIntake() {
  return useMutation({
    mutationFn: (input: ClaimIntakeInput) => submitClaimIntake(input),
  });
}
