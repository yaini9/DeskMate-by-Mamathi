"use client";

import { FormEvent, useMemo, useRef, useState } from "react";
import { Bot, CheckCircle2, CircleDot, Loader2, Send, TerminalSquare, UserRound, Wrench } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type TraceStep = {
  kind: "model" | "tool_call" | "tool_result";
  title: string;
  detail: string;
  data?: unknown;
};

const starterMessages: ChatMessage[] = [
  {
    role: "assistant",
    content:
      "Hi, I’m DeskMate. I can help with software access, password resets, VPN diagnostics, and ticket status.",
  },
];

const suggestions = [
  "I need Adobe Creative Suite - if I'm not already entitled, please raise a high-priority ticket.",
  "My VPN keeps dropping. Can you check what is happening?",
  "Please reset my password.",
  "What is the status of IT-2417?",
];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>(starterMessages);
  const [trace, setTrace] = useState<TraceStep[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  const conversationForApi = useMemo(
    () => messages.filter((message) => !(message.role === "assistant" && message === starterMessages[0])),
    [messages],
  );

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;
    const nextMessages: ChatMessage[] = [...messages, { role: "user", content: trimmed }];
    setMessages(nextMessages);
    setInput("");
    setIsLoading(true);
    setTrace([
      {
        kind: "model",
        title: "Request sent",
        detail: "Full conversation history sent to DeskMate API.",
      },
    ]);

    try {
      const apiMessages = nextMessages.filter((message) => message !== starterMessages[0]);
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: apiMessages }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail ?? "DeskMate API request failed.");
      }
      const payload: { reply: string; trace: TraceStep[] } = await response.json();
      setTrace(payload.trace);
      setMessages([...nextMessages, { role: "assistant", content: payload.reply }]);
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Unexpected error";
      setTrace((current) => [
        ...current,
        {
          kind: "tool_result",
          title: "Request failed",
          detail,
        },
      ]);
      setMessages([
        ...nextMessages,
        {
          role: "assistant",
          content: `I could not reach the helpdesk backend: ${detail}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(input);
  }

  return (
    <main className="min-h-screen bg-background p-4 text-foreground md:p-6">
      <div className="mx-auto flex h-[calc(100vh-2rem)] max-w-7xl flex-col gap-4 md:h-[calc(100vh-3rem)]">
        <header className="flex items-center justify-between border-b pb-4">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Bot className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-semibold tracking-normal">DeskMate</h1>
              <p className="text-sm text-muted-foreground">AI-powered IT helpdesk POC</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-md border bg-card px-3 py-2 text-sm text-muted-foreground md:flex">
            <CircleDot className="h-4 w-4 text-emerald-600" />
            OpenAI function calling
          </div>
        </header>

        <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[minmax(0,7fr)_minmax(320px,3fr)]">
          <Card className="flex min-h-0 flex-col overflow-hidden">
            <CardHeader className="border-b">
              <CardTitle>Chat</CardTitle>
            </CardHeader>
            <CardContent className="flex min-h-0 flex-1 flex-col p-0">
              <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-5">
                {messages.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={cn("flex gap-3", message.role === "user" ? "justify-end" : "justify-start")}
                  >
                    {message.role === "assistant" && (
                      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-secondary text-secondary-foreground">
                        <Bot className="h-4 w-4" />
                      </div>
                    )}
                    <div
                      className={cn(
                        "max-w-[78%] rounded-lg px-4 py-3 text-sm leading-6 shadow-sm",
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "border bg-card text-card-foreground",
                      )}
                    >
                      {message.content}
                    </div>
                    {message.role === "user" && (
                      <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-accent text-accent-foreground">
                        <UserRound className="h-4 w-4" />
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    DeskMate is deciding which tools to call.
                  </div>
                )}
              </div>

              <div className="border-t bg-card p-4">
                <div className="mb-3 flex flex-wrap gap-2">
                  {suggestions.map((suggestion) => (
                    <Button
                      key={suggestion}
                      type="button"
                      variant="secondary"
                      className="h-auto max-w-full justify-start whitespace-normal px-3 py-2 text-left text-xs"
                      onClick={() => void sendMessage(suggestion)}
                      disabled={isLoading}
                    >
                      {suggestion}
                    </Button>
                  ))}
                </div>
                <form ref={formRef} onSubmit={onSubmit} className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                    placeholder="Describe your IT request..."
                    disabled={isLoading}
                  />
                  <Button type="submit" size="icon" disabled={isLoading || input.trim().length === 0} title="Send">
                    {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  </Button>
                </form>
              </div>
            </CardContent>
          </Card>

          <Card className="flex min-h-0 flex-col overflow-hidden">
            <CardHeader className="border-b">
              <CardTitle className="flex items-center gap-2">
                <TerminalSquare className="h-5 w-5" />
                Execution Trace
              </CardTitle>
            </CardHeader>
            <CardContent className="min-h-0 flex-1 overflow-y-auto p-4">
              {trace.length === 0 ? (
                <div className="flex h-full items-center justify-center text-center text-sm text-muted-foreground">
                  Tool calls and results appear here after each request.
                </div>
              ) : (
                <ol className="space-y-3">
                  {trace.map((step, index) => (
                    <li key={`${step.title}-${index}`} className="rounded-lg border bg-card p-3">
                      <div className="mb-2 flex items-start gap-2">
                        <TraceIcon kind={step.kind} />
                        <div className="min-w-0">
                          <div className="text-sm font-medium">{step.title}</div>
                          <div className="text-xs leading-5 text-muted-foreground">{step.detail}</div>
                        </div>
                      </div>
                      {step.data !== undefined && step.data !== null && (
                        <pre className="max-h-48 overflow-auto rounded-md bg-muted p-3 text-xs leading-5 text-muted-foreground">
                          {JSON.stringify(step.data, null, 2)}
                        </pre>
                      )}
                    </li>
                  ))}
                </ol>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}

function TraceIcon({ kind }: { kind: TraceStep["kind"] }) {
  if (kind === "tool_call") {
    return (
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-accent text-accent-foreground">
        <Wrench className="h-4 w-4" />
      </div>
    );
  }
  if (kind === "tool_result") {
    return (
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-secondary text-secondary-foreground">
        <CheckCircle2 className="h-4 w-4" />
      </div>
    );
  }
  return (
    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground">
      <Bot className="h-4 w-4" />
    </div>
  );
}
