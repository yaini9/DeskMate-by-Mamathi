# DeskMate — Production Design Note

## Goal

The current DeskMate implementation is a proof-of-concept focused on:
- LLM orchestration
- tool calling
- execution visibility
- enterprise IT workflows

For production, the system would need stronger:
- security
- reliability
- observability
- scalability
- governance

This document focuses only on the decisions I consider load-bearing.

---

# Proposed Azure Architecture

## Frontend
- Next.js frontend hosted on Azure Static Web Apps

## Backend API
- FastAPI service hosted on Azure Container Apps or AKS

## LLM Layer
- Azure OpenAI or Gemini API abstraction layer
- Centralized prompt/version management

## Data Layer
- Azure SQL or Cosmos DB
- Ticket persistence
- Conversation storage
- Audit logs

## Internal Enterprise Integrations
Production integrations would connect to:
- Active Directory / Entra ID
- ServiceNow / Jira
- VPN monitoring systems
- Software entitlement systems
- Email systems

---

# Authentication & Authorization

The current POC has no authentication.

Production would require:
- Entra ID authentication
- RBAC (role-based access control)
- per-user authorization checks
- secure tool access boundaries

The assistant should never execute actions for users without identity verification.

---

# Tool Execution Safety

The highest-risk area is unauthorized or hallucinated actions.

Production protections would include:
- strict tool schemas
- server-side validation
- approval workflows for sensitive actions
- human-in-the-loop escalation
- action logging

The LLM should never directly perform privileged operations without verification.

---

# Prompt Injection Protection

Prompt injection is a major risk for enterprise AI systems.

Mitigations:
- strict system prompts
- server-side scope enforcement
- input sanitization
- tool allowlists
- separating user input from tool instructions

The backend should enforce security boundaries even if the model behaves unexpectedly.

---

# Observability & Monitoring

Production systems require:
- centralized logging
- request tracing
- tool execution monitoring
- token usage tracking
- failure dashboards
- alerting

I would integrate:
- Azure Monitor
- Application Insights
- structured JSON logs

---

# Reliability & Resilience

The current POC assumes happy-path execution.

Production systems need:
- retries
- timeouts
- fallback behavior
- rate-limit handling
- circuit breakers
- queue-based processing for long-running tasks

---

# Cost Control

LLM cost can grow quickly.

Mitigations:
- caching
- request limits
- smaller models for simple tasks
- routing logic based on complexity
- token monitoring

Not every request should require a large model.

---

# Deployment Strategy

I would containerize:
- frontend
- backend

using Docker.

CI/CD would run through:
- GitHub Actions
- automated tests
- staging deployments
- production approval gates

---

# Biggest Risks

The biggest production concerns are:

## Unauthorized Actions
Preventing the assistant from executing actions for the wrong user.

## Hallucinated Responses
Ensuring the model never invents ticket statuses or system state.

## Prompt Injection
Preventing malicious prompts from bypassing security rules.

## Operational Reliability
Handling outages, retries, and degraded services gracefully.

---

# Final Thoughts

For production, I would prioritize:
1. security boundaries
2. observability
3. auditability
4. safe tool execution

before expanding feature breadth.

A smaller but trustworthy system is more valuable than a broader but unsafe one.