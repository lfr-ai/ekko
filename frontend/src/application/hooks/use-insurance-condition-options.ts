import { useQuery } from "@tanstack/react-query";
import { fetchInsuranceConditionOptions } from "@/infrastructure/api/claim-intake-api";

export function useInsuranceConditionOptions() {
  return useQuery({
    queryFn: fetchInsuranceConditionOptions,
    queryKey: ["insurance-condition-options"],
  });
}
