# GigSmartPay Backend

The unified backend for GigSmartPay, powering the AI agents, blockchain interactions, and real-time data sync.

## Technologies
- **Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Blockchain:** Neo N3 (via `neo-mcp`)
- **AI:** OpenAI GPT-4o / GPT-4.1 (via Sudo AI)
- **Storage:** IPFS (for proof photos)

## Core Components

### 1. API Server (`api.py`)
- **REST Endpoints:** Manage jobs, users, and disputes.
- **WebSocket Manager:** Broadcasts real-time events (`JOB_COMPLETED`, `DISPUTE_RAISED`, `PAYMENT_RECEIVED`) to connected clients.
- **Background Tasks:** Monitors blockchain transactions for confirmation.

### 2. AI Agents (`agent/`)
- **Conversational Job Creator:** A stateful chat agent that helps clients define job requirements naturally. Extracts structured JSON from conversation.
- **Universal Eye Agent:** A vision-based agent that verifies work by comparing "Before" and "After" photos against the job description.
- **Paralegal:** validation logic ensuring jobs meet safety and policy guidelines.

### 3. Database Layer (`database.py`)
- Connects to Supabase PostgreSQL.
- Handles atomic updates for job status transitions (OPEN -> LOCKED -> IN_PROGRESS -> COMPLETED).

## Setup via Supabase

This project uses Supabase for the database.
Please refer to the root [SUPABASE_SETUP.md](../SUPABASE_SETUP.md) for initialization instructions.

## Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **GET** | `/api/jobs/available` | List open jobs |
| **POST** | `/api/jobs/create/chat` | Chat with Job Creator Agent |
| **POST** | `/api/jobs/submit` | Submit proof (triggers AI verification) |
| **POST** | `/api/resolve_dispute` | Resolve a dispute (Admin/Arbiter) |
| **GET** | `/api/wallet/balance/{addr}` | Get Neo N3 GAS balance |
| **WS** | `/ws/{address}` | Real-time event stream |

## Running the Server

```bash
# Make sure you are in the root or backend directory
# and have your .venv activated

python api.py
```

Server runs on `http://localhost:8000`.
Docs available at `http://localhost:8000/docs`.
