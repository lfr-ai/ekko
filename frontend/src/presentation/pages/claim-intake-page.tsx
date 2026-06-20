import { ShieldCheck } from "lucide-react";
import { ClaimIntakeForm } from "@/presentation/features/claim-intake/claim-intake-form";

export function ClaimIntakePage(): React.JSX.Element {
  return (
    <main className="mx-auto max-w-4xl space-y-6 px-4 py-8 md:px-6">
      <header className="space-y-2">
        <p className="inline-flex items-center gap-2 rounded-full border px-3 py-1 font-medium text-sm">
          <ShieldCheck className="h-4 w-4" />
          Claims automation frontend
        </p>
        <h1 className="font-semibold text-3xl tracking-tight">Insurance claim intake</h1>
        <p className="text-muted-foreground">
          Register a case with CPR, condition, period, payout, policy/payment flags, prior KS
          context, and supporting documents.
        </p>
      </header>

      <ClaimIntakeForm />
    </main>
  );
}
