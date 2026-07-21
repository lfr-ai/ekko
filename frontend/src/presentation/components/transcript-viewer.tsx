import { useState } from "react";
import { cn } from "@/lib/utils";

interface TranscriptEntry {
  id: string;
  text: string;
  source: "microphone" | "system";
  timestamp: string;
}

interface TranscriptViewerProps {
  entries?: TranscriptEntry[];
  className?: string;
  maxHeight?: string;
}

export function TranscriptViewer({
  entries = [],
  className,
  maxHeight = "400px",
}: TranscriptViewerProps) {
  const [filter, setFilter] = useState<"all" | "microphone" | "system">("all");

  const filtered = filter === "all" ? entries : entries.filter((e) => e.source === filter);

  return (
    <div className={cn("rounded-lg border bg-card p-4", className)}>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold text-card-foreground text-sm">Transcript</h3>
        <div className="flex gap-1">
          {(["all", "microphone", "system"] as const).map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => setFilter(f)}
              className={cn(
                "rounded-md px-2 py-1 text-xs capitalize transition-colors",
                filter === f
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-accent",
              )}
            >
              {f}
            </button>
          ))}
        </div>
      </div>
      <div
        className="space-y-2 overflow-y-auto"
        style={{ maxHeight }}
        role="log"
        aria-live="polite"
      >
        {filtered.length === 0 ? (
          <p className="text-muted-foreground text-sm">No transcript entries yet.</p>
        ) : (
          filtered.map((entry) => (
            <div
              key={entry.id}
              className={cn(
                "rounded-md p-2 text-sm",
                entry.source === "microphone"
                  ? "bg-blue-50 dark:bg-blue-950"
                  : "bg-gray-50 dark:bg-gray-900",
              )}
            >
              <span className="font-medium text-muted-foreground text-xs uppercase">
                {entry.source}
              </span>
              <p className="mt-0.5">{entry.text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
