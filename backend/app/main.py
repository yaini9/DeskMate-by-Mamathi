from __future__ import annotations

import json
import os
import traceback
from typing import Any, Literal

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

from .tools import OPENAI_TOOLS, TOOL_FUNCTIONS

load_dotenv(override=True)

# ---------------- SYSTEM PROMPT ---------------- #

SYSTEM_PROMPT = """
You are DeskMate, an enterprise IT helpdesk assistant.

You handle ONLY IT-related requests:
- password resets
- VPN issues
- software access
- laptop/email/network issues
- ticket status

If the user asks anything outside IT scope, politely refuse in ONE sentence:
"I can only help with IT-related support requests."

You MUST:
- Use tools when needed
- Never guess tool outputs
- Always use tool results if available
- Be concise and factual
"""

# ---------------- MODELS ---------------- #

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


class TraceStep(BaseModel):
    kind: Literal["model", "tool_call", "tool_result"]
    title: str
    detail: str
    data: dict[str, Any] | list[Any] | str | None = None


class ChatResponse(BaseModel):
    reply: str
    trace: list[TraceStep]


# ---------------- APP ---------------- #

app = FastAPI(title="DeskMate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HELPERS ---------------- #

def _conversation(messages: list[ChatMessage]) -> list[dict[str, str]]:
    return [{"role": m.role, "content": m.content} for m in messages]


def _tools_schema():
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
                "strict": t.get("strict", True),
            },
        }
        for t in OPENAI_TOOLS
    ]


def _safe_tool_call(name: str, args: dict[str, Any]):
    if name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool: {name}"}
    try:
        return TOOL_FUNCTIONS[name](**args)
    except Exception as e:
        return {"error": str(e)}


def _parse_args(raw: str | None) -> dict:
    try:
        return json.loads(raw or "{}")
    except Exception:
        return {}


def _error(error: Exception | str, trace: list[TraceStep]):
    return ChatResponse(
        reply=f"Backend error: {str(error)}",
        trace=trace + [
            TraceStep(
                kind="tool_result",
                title="error",
                detail=str(error),
                data={"error": str(error)},
            )
        ],
    )

# ---------------- CORE AGENT ---------------- #

def _openai_response(messages: list[ChatMessage]) -> ChatResponse:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return ChatResponse(reply="Missing OPENAI_API_KEY", trace=[])

    client = OpenAI(api_key=api_key)

    trace: list[TraceStep] = []

    chat = [{"role": "system", "content": SYSTEM_PROMPT}]
    chat += _conversation(messages)

    try:
        while True:
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
                messages=chat,
                tools=_tools_schema(),
                tool_choice="auto",
            )

            msg = response.choices[0].message

            trace.append(
                TraceStep(
                    kind="model",
                    title="LLM step",
                    detail="Model responded",
                )
            )

            # ---------------- FINAL ANSWER ---------------- #
            if not msg.tool_calls:
                return ChatResponse(
                    reply=msg.content or "",
                    trace=trace,
                )

            # add assistant tool request
            chat.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
            })

            # ---------------- TOOL EXECUTION ---------------- #
            for tc in msg.tool_calls:
                name = tc.function.name
                args = _parse_args(tc.function.arguments)

                trace.append(
                    TraceStep(
                        kind="tool_call",
                        title=name,
                        detail="Executing tool",
                        data=args,
                    )
                )

                result = _safe_tool_call(name, args)

                trace.append(
                    TraceStep(
                        kind="tool_result",
                        title=f"{name} result",
                        detail=str(result),
                        data=result,
                    )
                )

                chat.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                })

    except Exception as e:
        traceback.print_exc()
        return _error(e, trace)


# ---------------- ENDPOINTS ---------------- #

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        return _openai_response(req.messages)
    except Exception as e:
        return ChatResponse(reply=str(e), trace=[])