export interface InsuranceConditionOption {
  readonly id: string;
  readonly code: string;
  readonly label: string;
}

export interface ClaimAttachment {
  readonly id: string;
  readonly source: "file" | "url";
  readonly name: string;
  readonly mimeType?: string;
  readonly sizeBytes?: number;
  readonly url?: string;
}

export interface ClaimIntakeInput {
  readonly cpr: string;
  readonly insuranceConditionId: string;
  readonly coverageStartDate: string;
  readonly coverageEndDate: string;
  readonly payoutAmount: number;
  readonly hasMultiplePolicies: boolean;
  readonly hasPaid: boolean;
  readonly hasPriorCasesInKs: boolean;
  readonly notes?: string;
  readonly attachments: ReadonlyArray<ClaimAttachment>;
}

export interface ClaimIntakeSubmissionResult {
  readonly referenceId: string;
  readonly acceptedAtIso: string;
}
