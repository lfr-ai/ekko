import { Activity, ChevronRight, Circle, Mic, MicOff, Settings, Volume2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Badge } from "@/presentation/components/ui/badge";
import { Button } from "@/presentation/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/presentation/components/ui/card";
import { Separator } from "@/presentation/components/ui/separator";

const VISUALIZATION_BARS = Array.from({ length: 20 }, (_, i) => ({
  id: `viz-bar-${i}`,
  delay: i * 50,
}));

interface TranscriptEntry {
  id: string;
  text: string;
  source: "user" | "assistant" | "system";
  timestamp: Date;
}

export default function App() {
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState<"idle" | "listening" | "processing">("idle");
  const [transcripts, _setTranscripts] = useState<TranscriptEntry[]>([
    {
      id: "1",
      text: "Welcome to Ekko — your AI-powered voice assistant.",
      source: "system",
      timestamp: new Date(),
    },
  ]);

  const toggleListening = () => {
    setIsListening(!isListening);
    setStatus(isListening ? "idle" : "listening");
  };

  return (
    <div className="flex h-screen bg-background" data-testid="app-shell">
      {/* Sidebar */}
      <aside className="flex w-16 flex-col items-center border-r bg-card py-4">
        <div className="mb-8 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
          <Activity className="h-6 w-6 text-primary" />
        </div>

        <nav className="flex flex-1 flex-col gap-4">
          <Button
            variant="ghost"
            size="icon"
            aria-label={isListening ? "Stop listening" : "Start listening"}
            className={cn("relative", status === "listening" && "bg-primary/10 text-primary")}
            onClick={toggleListening}
          >
            {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            {status === "listening" && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-primary" />
              </span>
            )}
          </Button>

          <Button variant="ghost" size="icon" aria-label="Audio output">
            <Volume2 className="h-5 w-5" />
          </Button>
        </nav>

        <Button variant="ghost" size="icon" aria-label="Settings">
          <Settings className="h-5 w-5" />
        </Button>
      </aside>

      {/* Main Content */}
      <main className="flex flex-1 flex-col">
        {/* Header */}
        <header className="flex items-center justify-between border-b px-6 py-4">
          <div className="flex items-center gap-3">
            <h1 className="font-semibold text-2xl tracking-tight">Ekko</h1>
            <Badge
              data-testid="assistant-status-badge"
              variant={
                status === "idle" ? "secondary" : status === "listening" ? "success" : "warning"
              }
            >
              <Circle className="mr-1.5 h-2 w-2 fill-current" />
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Badge>
          </div>

          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <span>Azure Speech Services</span>
            <span className="text-muted-foreground/50">•</span>
            <span>GPT-4</span>
            <span className="text-muted-foreground/50">•</span>
            <span>da-DK</span>
          </div>
        </header>

        {/* Content Area */}
        <div className="grid flex-1 grid-cols-3 gap-6 overflow-hidden p-6">
          {/* Transcript Viewer */}
          <Card className="col-span-2 flex flex-col">
            <CardHeader>
              <CardTitle>Transcript</CardTitle>
              <CardDescription>
                Real-time voice transcription with AI-powered responses
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto">
              <div className="space-y-4">
                {transcripts.map((entry) => (
                  <div
                    key={entry.id}
                    className={cn("flex gap-3", entry.source === "user" && "flex-row-reverse")}
                  >
                    <div
                      className={cn(
                        "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                        entry.source === "user" && "bg-primary text-primary-foreground",
                        entry.source === "assistant" && "bg-secondary text-secondary-foreground",
                        entry.source === "system" && "bg-muted text-foreground",
                      )}
                    >
                      {entry.source === "user" && "U"}
                      {entry.source === "assistant" && "AI"}
                      {entry.source === "system" && "S"}
                    </div>
                    <div
                      className={cn(
                        "flex-1 rounded-lg px-4 py-3",
                        entry.source === "user" && "bg-primary text-primary-foreground",
                        entry.source === "assistant" && "bg-secondary text-secondary-foreground",
                        entry.source === "system" && "bg-muted text-foreground",
                      )}
                    >
                      <p className="text-sm">{entry.text}</p>
                      <span className="mt-1 text-xs opacity-90">
                        {entry.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Side Panel */}
          <div className="flex flex-col gap-6">
            {/* Audio Visualization */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Audio Input</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex h-24 items-end justify-center gap-1">
                  {VISUALIZATION_BARS.map((bar) => (
                    <div
                      key={bar.id}
                      data-testid="audio-visualizer-bar"
                      className={cn(
                        "w-2 rounded-t-sm bg-primary/20 transition-all",
                        isListening && "animate-pulse bg-primary/40",
                      )}
                      style={{
                        height: `${Math.random() * 100}%`,
                        animationDelay: `${bar.delay}ms`,
                      }}
                    />
                  ))}
                </div>
                <Separator className="my-4" />
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Sample Rate</span>
                    <span className="font-medium">16 kHz</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Channels</span>
                    <span className="font-medium">Mono</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Format</span>
                    <span className="font-medium">PCM 16-bit</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Status */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">System Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground text-sm">Speech-to-Text</span>
                  <Badge variant="success">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground text-sm">LLM Engine</span>
                  <Badge variant="success">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground text-sm">Audio Input</span>
                  <Badge variant={isListening ? "success" : "secondary"}>
                    {isListening ? "Active" : "Standby"}
                  </Badge>
                </div>
                <Separator />
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Latency</span>
                    <span className="font-medium">~300ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Uptime</span>
                    <span className="font-medium">2h 34m</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start" size="sm">
                  <ChevronRight className="mr-2 h-4 w-4" />
                  Clear Transcript
                </Button>
                <Button variant="outline" className="w-full justify-start" size="sm">
                  <ChevronRight className="mr-2 h-4 w-4" />
                  Export Conversation
                </Button>
                <Button variant="outline" className="w-full justify-start" size="sm">
                  <ChevronRight className="mr-2 h-4 w-4" />
                  Language Settings
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex items-center justify-between border-t px-6 py-3 text-muted-foreground text-sm">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            <span>Ekko v0.1.0</span>
          </div>
          <div className="flex items-center gap-4">
            <span>Clean Architecture</span>
            <span className="text-muted-foreground/50">•</span>
            <span>Python 3.12</span>
            <span className="text-muted-foreground/50">•</span>
            <span>React 19</span>
          </div>
        </footer>
      </main>
    </div>
  );
}
