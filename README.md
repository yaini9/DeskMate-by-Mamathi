# DeskMate — AI-Powered IT Helpdesk Assistant

DeskMate is a proof-of-concept AI helpdesk assistant that handles common enterprise IT support requests using a real LLM with tool-calling capabilities.

The system supports:
- Password resets
- VPN diagnostics
- Software access requests
- Ticket status lookups
- Out-of-scope request refusal

DeskMate also provides observable execution traces so requests can be followed end-to-end.

---

# Setup Instructions

## 1. Clone The Repository

```bash
git clone <your-github-repo-url>
cd front-desk-IT-ai-main
```

---

# Backend Setup

## 1. Navigate To Backend

```bash
cd backend
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Create Environment File

Create a `.env` file inside the `backend` folder.

Example:

```env
OPENAI_API_KEY=your_api_key_here(Create a Gemini API key from: https://aistudio.google.com/app/apikey)
OPENAI_MODEL=gemini-2.5-flash
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

---

## 5. Start Backend Server

```bash
uvicorn app.main:app --reload
```

Backend runs on:

```txt
http://localhost:8000
```

---

# Frontend Setup

## 1. Navigate To Frontend

```bash
cd frontend
```

---

## 2. Install Dependencies

```bash
npm install
```

---

## 3. Create Environment File

Create `.env.local` inside the `frontend` folder.

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 4. Start Frontend

```bash
npm run dev
```

Frontend runs on:

```txt
http://localhost:3000
```

---

# Example Queries

Try the following prompts:

```txt
Please reset my password
```

```txt
My VPN keeps disconnecting
```

```txt
I need Adobe Creative Suite access — if I’m not already entitled, raise a high-priority ticket
```

```txt
What is the status of IT-2417?
```

```txt
Order me a pizza
```

---

# Architecture Overview

## Frontend
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui

The frontend provides:
- Chat interface
- Execution trace viewer
- Real-time interaction with the backend

---

## Backend
- FastAPI
- OpenAI-compatible LLM integration
- Tool-calling orchestration loop

The backend:
1. Receives user queries
2. Sends conversation history to the LLM
3. Executes tool calls requested by the model
4. Returns tool outputs back to the model
5. Produces the final response

---

## Mock Internal IT Systems

DeskMate uses mocked enterprise IT systems for:
- Password reset operations
- VPN diagnostics
- Software entitlement checks
- Ticket creation
- Ticket status lookup

---

# Observable Execution

Each request includes an execution trace showing:
- Model reasoning steps
- Tool calls
- Tool results
- Error handling

This makes the workflow fully observable end-to-end.

---

# Demo

A recorded demo video demonstrating multiple query workflows is included in this repository as:

```txt
demo.mp4
```

---

