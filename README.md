# GigSmartPay

<img width="1512" height="741" alt="image" src="https://github.com/user-attachments/assets/35985bb2-cbec-455a-b6d3-9078f9c205e3" />

**Decentralized Gig Platform on Neo N3 Blockchain**

AI-powered escrow system for trustless gig work.  
Combines **Smart Contracts**, **AI Visual Verification**, and **Natural Language Job Creation** to automate the entire gig lifecycle.

---

## 🎯 What is GigSmartPay?

GigSmartPay automates the trust layer between clients and gig workers:

1.  **Client:** Chats with an AI to describe the job. The AI extracts requirements, sets a price, and locks funds in a smart contract.
2.  **Worker:** Accepts the job, performs the work, and uses the **in-app camera** to take proof photos.
3.  **AI Tribunal:** The "Eye Agent" (GPT-4o Vision) analyzes the proof against the requirements.
    - **Pass:** Payment is auto-released instantly via blockchain.
    - **Fail:** Dispute is raised for arbitration.

## 🏗️ Architecture

```mermaid
graph TD
    subgraph Frontend [Next.js Web App]
        UI[User Interface]
        Chat[Conversational Job Creator]
        Cam[In-App Camera / ImageUpload]
        Toast[Payment Toasts]
        SocketClient[WebSocket Client]
    end

    subgraph Backend [FastAPI Server]
        API[REST API]
        SocketServer[WebSocket Server]
        
        subgraph Agents [AI Agents]
            Planner[Conversational Agent]
            Eye[Eye Agent (Vision)]
            Paralegal[Paralegal (Contracts)]
        end
    end

    subgraph Infrastructure
        DB[(Supabase PostgreSQL)]
        IPFS[IPFS Storage]
        Neo[Neo N3 Blockchain]
        LLM[Sudo AI / GPT-4o]
    end

    UI --> Chat
    UI --> Cam
    Chat -->|Plan Job| Planner
    Cam -->|Upload Proof| IPFS
    
    Planner -->|Generate Plan| LLM
    Eye -->|Verify Photos| LLM
    
    API -->|Manage Data| DB
    API -->|Lock/Release Funds| Neo
    API -->|Trigger Verification| Eye
    
    SocketServer -->|Real-time Updates| SocketClient
    Eye -->|Verdict| API
```

## 🚀 Key Features

### 🤖 Generative Job Creation
- Chat with an AI assistant to create standard gig contracts.
- AI extracts **Tasks**, **Location**, **Price**, and **Verification Criteria**.
- No forms to fill out—just natural conversation.

### 📸 Real-Time Verification
- **In-App Camera:** Workers capture secure, time-stamped proof photos directly in the browser.
- **AI Vision:** The "Eye Agent" analyzes before/after photos to verify work quality.
- **Location Check:** GPS verification ensures the worker was at the job site.

### 💸 Instant Smart Payments
- **Escrow:** Funds are locked on the Neo N3 blockchain upon job creation.
- **Auto-Release:** Payment is released immediately when AI verifies the work.
- **Real-Time Notifications:** WebSocket events notify users of payments, disputes, and completions instantly.

### ⚖️ Dispute Resolution
- If AI verification fails, a dispute is raised.
- **Arbitration:** Manual or system-based dispute resolution.
- **Fairness:** Funds are returned to client or released to worker based on the verdict.

## 📦 Project Structure

```bash
smart-pay/
├── backend/
│   ├── api.py           # FastAPI server + WebSocket
│   ├── database.py      # Supabase connection
│   └── agent/           # AI Agents (Eye, Paralegal, Conversational)
│
├── web/                 # Next.js Frontend
│   ├── app/             # App Router pages
│   ├── components/      # UI Components (ImageUpload, Chat, etc.)
│   └── context/         # Global State & WebSocket logic
│
├── contracts/
│   └── gigshield_vault.py  # Neo N3 Smart Contract
│
└── src/
    └── neo_mcp.py       # Neo Blockchain Wrapper
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Neo N3 TestNet Wallet (or local private net)
- Supabase Account (for database)

### 1. Database Setup (Supabase)
We use Supabase (PostgreSQL) for production-grade persistence.
See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for detailed instructions.

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your keys (Supabase, Neo, OpenAI/SudoAI)

python api.py
```

### 3. Frontend Setup
```bash
cd web
npm install
npm run dev
```

Visit `http://localhost:3000` to start using the app.

## 🔗 Documentation
- [Backend API Docs](./backend/README.md)
- [Supabase Setup Guide](./SUPABASE_SETUP.md)
