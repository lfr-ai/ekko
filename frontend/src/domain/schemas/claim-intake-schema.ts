import { z } from "zod";

const cprRegex = /^\d{6}-?\d{4}$/;

export const claimAttachmentSchema = z.object({
  id: z.string().min(1),
  source: z.enum(["file", "url"]),
  name: z.string().min(1),
  mimeType: z.string().optional(),
  sizeBytes: z.number().int().nonnegative().optional(),
  url: z.string().url().optional(),
});

export const claimIntakeSchema = z
  .object({
    cpr: z.string().trim().regex(cprRegex, "CPR must be formatted as DDMMYY-XXXX or DDMMYYXXXX."),
    insuranceConditionId: z.string().min(1, "Choose an insurance condition."),
    coverageStartDate: z.string().date(),
    coverageEndDate: z.string().date(),
    payoutAmount: z
      .number({
        coerce: true,
      })
      .nonnegative("Payout amount must be 0 or greater."),
    hasMultiplePolicies: z.boolean(),
    hasPaid: z.boolean(),
    hasPriorCasesInKs: z.boolean(),
    notes: z.string().trim().max(5000).optional(),
    attachments: z.array(claimAttachmentSchema).min(1, "Add at least one file or URL."),
  })
  .superRefine((value, ctx) => {
    if (value.coverageEndDate < value.coverageStartDate) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["coverageEndDate"],
        message: "Coverage end date must be the same as or after start date.",
      });
    }
  });

export type ClaimIntakeFormData = z.infer<typeof claimIntakeSchema>;
