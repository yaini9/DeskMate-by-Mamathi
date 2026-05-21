# DeskMate — Design Notes

## Why I Chose This Architecture

I intentionally kept the system small and easy to reason about because this is a POC, not a production system.

The goal was to demonstrate:
- LLM tool orchestration
- Agent-style reasoning
- Observable execution
- Safe scope handling
- Clear system boundaries

without overengineering infrastructure.

---

# High-Level Architecture

Frontend:
- Next.js + TypeScript
- Chat UI
- Execution trace panel

Backend:
- FastAPI service
- LLM orchestration loop
- Tool execution layer

LLM:
- Gemini 2.5 Flash
- Function/tool calling

Internal Systems:
- Mock Python tool functions
- Simulated IT system responses

---

# Key Design Decisions

## 1. Tool Calling Instead of Hardcoded Logic

The LLM decides when tools should be called.

This was important because the exercise specifically asked for:
- natural language handling
- multi-step reasoning
- conditional decisions

Instead of manually routing every request with if/else chains, the model dynamically chooses tools based on user intent.

Example:
- User requests Adobe access
- Model checks entitlement tool
- If not entitled:
  - creates a ticket
- Then generates a final response

This demonstrates agent-like behavior rather than scripted flows.

---

## 2. Observable Execution

Every request produces an execution trace visible in the UI.

The trace shows:
- model reasoning steps
- tool calls
- tool inputs
- tool outputs
- failures/errors

This makes the system debuggable and interview-friendly.

I considered this load-bearing because AI systems become difficult to trust when actions are hidden.

---

# 3. Mock Internal IT Systems

The exercise requested internal systems with realistic data.

I implemented:
- password reset service
- VPN diagnostics
- entitlement checking
- ticket management

These are mocked using Python functions returning structured data.

This allowed:
- deterministic behavior
- realistic enterprise workflows
- function-calling demonstrations

without requiring external enterprise integrations.

---

# 4. Strict Scope Restriction

DeskMate is intentionally limited to IT support requests.

The system prompt strongly restricts:
- food orders
- shopping
- travel
- personal assistant tasks

This matters because uncontrolled assistants can easily drift outside intended enterprise scope.

I also added explicit refusal behavior for non-IT requests.

---

# 5. Graceful Error Handling

The backend handles:
- missing API keys
- malformed tool arguments
- tool failures
- model failures
- invalid requests

Errors are surfaced both:
- in API responses
- in execution traces

instead of silently failing.

---

# 6. Why FastAPI + Next.js

I chose:
- FastAPI for lightweight API development and async support
- Next.js for a fast interactive frontend

This stack allowed rapid iteration while still feeling production-adjacent.

---

# What I Would Improve Next

If given more time, I would add:
- persistent ticket storage
- authentication
- streaming responses
- retry handling
- conversation memory
- role-based permissions
- real enterprise integrations
- Docker deployment
- automated testing

---

# Production Concerns I Consider Important

The biggest production risks are:

## Hallucinated Actions
The model should never execute actions without tool verification.

## Prompt Injection
User prompts should not override system behavior or security boundaries.

## Access Control
Real enterprise systems require strict identity verification and authorization.

## Auditability
All tool actions should be logged and traceable.

## Reliability
Production systems need retries, monitoring, and fallback behavior.

---

# Tradeoffs

I intentionally optimized for:
- clarity
- explainability
- observability
- speed of iteration

over:
- scalability
- security hardening
- infrastructure complexity

because the exercise explicitly described this as a proof-of-concept system.