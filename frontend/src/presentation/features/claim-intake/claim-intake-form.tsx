import { zodResolver } from "@hookform/resolvers/zod";
import { LoaderCircle, Upload, X } from "lucide-react";
import { useId, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { useInsuranceConditionOptions } from "@/application/hooks/use-insurance-condition-options";
import { useSubmitClaimIntake } from "@/application/hooks/use-submit-claim-intake";
import { type ClaimIntakeFormData, claimIntakeSchema } from "@/domain/schemas/claim-intake-schema";
import type { ClaimAttachment, ClaimIntakeInput } from "@/domain/types/claim-intake";
import { cn } from "@/lib/utils";
import { Button } from "@/presentation/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/presentation/components/ui/card";
import { Checkbox } from "@/presentation/components/ui/checkbox";
import { Input } from "@/presentation/components/ui/input";
import { Label } from "@/presentation/components/ui/label";
import { Switch } from "@/presentation/components/ui/switch";
import { Textarea } from "@/presentation/components/ui/textarea";

interface AttachmentListProps {
  readonly attachments: ReadonlyArray<ClaimAttachment>;
  readonly onRemove: (attachmentId: string) => void;
}

function AttachmentList({ attachments, onRemove }: AttachmentListProps) {
  if (attachments.length === 0) {
    return <output className="text-muted-foreground text-sm">No files or URLs added yet.</output>;
  }

  return (
    <ul className="space-y-2">
      {attachments.map((attachment) => (
        <li
          key={attachment.id}
          className="flex items-center justify-between rounded-md border bg-card px-3 py-2"
        >
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center rounded-full border border-transparent bg-secondary px-2.5 py-0.5 font-semibold text-secondary-foreground text-xs">
              {attachment.source.toUpperCase()}
            </span>
            <div>
              <p className="font-medium text-sm">{attachment.name}</p>
              {attachment.url ? (
                <p className="text-muted-foreground text-xs">{attachment.url}</p>
              ) : null}
            </div>
          </div>
          <Button
            aria-label={`Remove ${attachment.name}`}
            onClick={() => onRemove(attachment.id)}
            size="icon"
            type="button"
            variant="ghost"
          >
            <X className="h-4 w-4" />
          </Button>
        </li>
      ))}
    </ul>
  );
}

function makeFileAttachment(file: File): ClaimAttachment {
  return {
    id: crypto.randomUUID(),
    mimeType: file.type,
    name: file.name,
    sizeBytes: file.size,
    source: "file",
  };
}

function makeUrlAttachment(url: string): ClaimAttachment {
  const segments = url.split("/");
  const attachmentName =
    [...segments].reverse().find((segment: string) => segment.length > 0) ?? "remote-document";

  return {
    id: crypto.randomUUID(),
    name: attachmentName,
    source: "url",
    url,
  };
}

export function ClaimIntakeForm(): React.JSX.Element {
  const dropZoneId = useId();
  const [attachmentUrl, setAttachmentUrl] = useState("");
  const [isDragOver, setIsDragOver] = useState(false);
  const [attachments, setAttachments] = useState<ReadonlyArray<ClaimAttachment>>([]);
  const [submitSuccessMessage, setSubmitSuccessMessage] = useState<string | null>(null);

  const optionsQuery = useInsuranceConditionOptions();
  const submitMutation = useSubmitClaimIntake();

  const form = useForm<ClaimIntakeFormData>({
    defaultValues: {
      attachments: [],
      coverageEndDate: "",
      coverageStartDate: "",
      cpr: "",
      hasMultiplePolicies: false,
      hasPaid: false,
      hasPriorCasesInKs: false,
      insuranceConditionId: "",
      notes: "",
      payoutAmount: 0,
    },
    resolver: zodResolver(claimIntakeSchema),
  });

  const optionItems = useMemo(() => optionsQuery.data ?? [], [optionsQuery.data]);

  function syncAttachments(nextAttachments: ReadonlyArray<ClaimAttachment>): void {
    setAttachments(nextAttachments);
    setSubmitSuccessMessage(null);
    form.clearErrors("attachments");
    form.setValue("attachments", [...nextAttachments], {
      shouldDirty: true,
      shouldValidate: true,
    });
  }

  function appendFiles(fileList: FileList | null): void {
    if (!fileList) {
      return;
    }

    const next = [...attachments, ...Array.from(fileList).map(makeFileAttachment)];
    syncAttachments(next);
  }

  function removeAttachment(attachmentId: string): void {
    syncAttachments(attachments.filter((attachment) => attachment.id !== attachmentId));
  }

  function handleDrop(event: React.DragEvent<HTMLLabelElement>): void {
    event.preventDefault();
    setIsDragOver(false);
    appendFiles(event.dataTransfer.files);
  }

  function handleAddUrl(): void {
    const candidate = attachmentUrl.trim();

    try {
      // eslint-disable-next-line no-new
      new URL(candidate);
    } catch {
      form.setError("attachments", {
        type: "manual",
        message: "Please provide a valid URL.",
      });
      return;
    }

    syncAttachments([...attachments, makeUrlAttachment(candidate)]);
    setAttachmentUrl("");
  }

  async function onSubmit(values: ClaimIntakeFormData): Promise<void> {
    const { notes, ...basePayload } = values;
    const payload: ClaimIntakeInput = notes
      ? { ...basePayload, attachments, notes }
      : { ...basePayload, attachments };

    const response = await submitMutation.mutateAsync(payload);

    setSubmitSuccessMessage(`Claim intake submitted. Reference: ${response.referenceId}`);
    form.reset();
    setAttachments([]);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Claim intake</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-6" onSubmit={form.handleSubmit(onSubmit)}>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="cpr">CPR</Label>
              <Input id="cpr" placeholder="DDMMYY-XXXX" {...form.register("cpr")} />
              <p className="text-destructive text-sm">{form.formState.errors.cpr?.message}</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="insurance-condition">Insurance condition P</Label>
              <select
                aria-label="Insurance condition P"
                className="h-9 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
                id="insurance-condition"
                name="insuranceConditionId"
                onChange={(event) => {
                  form.setValue("insuranceConditionId", event.target.value, {
                    shouldDirty: true,
                    shouldValidate: true,
                  });
                }}
                title="Insurance condition P"
                value={form.watch("insuranceConditionId")}
              >
                <option value="">Select condition</option>
                {optionItems.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label}
                  </option>
                ))}
              </select>
              {optionsQuery.isLoading ? (
                <p className="text-muted-foreground text-sm">Loading options…</p>
              ) : null}
              <p className="text-destructive text-sm">
                {form.formState.errors.insuranceConditionId?.message}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="coverage-start-date">Coverage period start</Label>
              <Input id="coverage-start-date" type="date" {...form.register("coverageStartDate")} />
              <p className="text-destructive text-sm">
                {form.formState.errors.coverageStartDate?.message}
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="coverage-end-date">Coverage period end</Label>
              <Input id="coverage-end-date" type="date" {...form.register("coverageEndDate")} />
              <p className="text-destructive text-sm">
                {form.formState.errors.coverageEndDate?.message}
              </p>
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="payout-amount">Payout amount</Label>
              <Input
                id="payout-amount"
                min="0"
                step="0.01"
                type="number"
                {...form.register("payoutAmount", { valueAsNumber: true })}
              />
              <p className="text-destructive text-sm">
                {form.formState.errors.payoutAmount?.message}
              </p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <Label className="flex items-center justify-between rounded-md border px-3 py-2">
              <span className="text-sm">Multiple policies</span>
              <Switch
                checked={form.watch("hasMultiplePolicies")}
                onCheckedChange={(checked) => form.setValue("hasMultiplePolicies", checked)}
              />
            </Label>

            <Label className="flex items-center justify-between rounded-md border px-3 py-2">
              <span className="text-sm">Has paid</span>
              <Switch
                checked={form.watch("hasPaid")}
                onCheckedChange={(checked) => form.setValue("hasPaid", checked)}
              />
            </Label>

            <Label className="flex items-center justify-between rounded-md border px-3 py-2">
              <span className="text-sm">Prior KS cases</span>
              <Checkbox
                checked={form.watch("hasPriorCasesInKs")}
                onCheckedChange={(checked) => form.setValue("hasPriorCasesInKs", checked === true)}
              />
            </Label>
          </div>

          <div className="space-y-3">
            <Label htmlFor={`${dropZoneId}-input`}>Relevant files</Label>
            <label
              className={cn(
                "rounded-lg border border-dashed p-6 text-center transition",
                isDragOver && "border-primary bg-primary/5",
              )}
              htmlFor={`${dropZoneId}-input`}
              id={dropZoneId}
              onDragOver={(event) => {
                event.preventDefault();
                setIsDragOver(true);
              }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
            >
              <Upload className="mx-auto mb-2 h-6 w-6 text-muted-foreground" />
              <p className="font-medium text-sm">Drag and drop files here</p>
              <p className="mb-4 text-muted-foreground text-xs">
                PDF, images, or other claim documents
              </p>
              <span className="inline-flex h-10 items-center justify-center rounded-md border border-input bg-secondary px-4 py-2 font-medium text-secondary-foreground text-sm">
                Select files
              </span>
              <input
                aria-label="Choose claim files"
                className="hidden"
                id={`${dropZoneId}-input`}
                multiple
                onChange={(event) => appendFiles(event.target.files)}
                type="file"
              />
            </label>

            <div className="flex gap-2">
              <Input
                placeholder="Paste file URL (PDF or similar)"
                value={attachmentUrl}
                onChange={(event) => setAttachmentUrl(event.target.value)}
              />
              <Button onClick={handleAddUrl} type="button" variant="outline">
                Add URL
              </Button>
            </div>

            <AttachmentList attachments={attachments} onRemove={removeAttachment} />
            <output className="text-destructive text-sm">
              {form.formState.errors.attachments?.message}
            </output>
            {submitSuccessMessage ? (
              <output className="text-primary text-sm">{submitSuccessMessage}</output>
            ) : null}
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              placeholder="Add any relevant details"
              {...form.register("notes")}
            />
          </div>

          <Button className="w-full" disabled={submitMutation.isPending} type="submit">
            {submitMutation.isPending ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}
            Submit claim intake
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
