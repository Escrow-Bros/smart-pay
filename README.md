# GigSmartPay

<img width="1046" height="558" alt="image" src="https://github.com/user-attachments/assets/fe16c104-6ba7-4718-8714-cdb955fd7bb8" />

**Decentralized Gig Platform on Neo N3 Blockchain**

AI-powered escrow system for trustless gig work: Smart contracts + Visual verification + Natural language job creation.

## 🎯 What is GigSmartPay?

GigSmartPay connects clients and workers through blockchain-secured gig contracts with AI verification:

- **Client:** Describe job in natural language → AI extracts requirements → Funds locked in smart contract
- **Worker:** Browse available gigs → Claim job → Submit proof photos
- **AI Tribunal:** Verifies work completion → Auto-releases payment if approved

## 🏗️ Architecture

```
┌─────────────────┐
│  Next.js Web UI │ (Real-time wallet balance, job dashboard)
└────────┬────────┘
         │
┌────────▼────────┐
│  FastAPI Backend│ (Database + Blockchain + AI)
└────────┬────────┘
         │
    ┌────┴────────────────┐
    │                     │
┌───▼────┐          ┌─────▼─────┐
│ SQLite │          │ Neo N3    │
│Database│          │Blockchain │
│(Listing)│         │(Payments) │
└────────┘          └───────────┘
         │                │
    ┌────┴────────────────┘
    │
┌───▼──────┐
│AI Agents │ (Paralegal: Job validation, Eye: Visual verification)
└──────────┘
```

## 📦 Project Structure

```
smart-pay/
├── backend/
│   ├── app.py           # FastAPI server (main entry point)
│   ├── database.py      # SQLite layer for fast queries
│   └── agent/           # AI Agents (Eye, Paralegal)
│
├── web/                 # Next.js Frontend
│   ├── app/             # App router pages
│   ├── components/      # React components
│   └── lib/             # API and utilities
│
├── src/
│   ├── neo_mcp.py       # Neo N3 blockchain wrapper
│   └── neo_config.py    # Blockchain configuration
│
├── contracts/
│   └── gigshield_vault.py  # Neo N3 smart contract
│
└── scripts/
    ├── check_balances.py   # Wallet balance checker
    └── generate_wallets.py # Generate Neo wallets
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm
- Neo N3 TestNet access (automatic)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd smart-pay
```

### 2. Install Backend Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```bash
# Neo N3 Configuration
NEO_TESTNET_RPC=https://testnet1.neo.coz.io:443/

# Wallet Addresses (Generate your own using scripts/generate_wallets.py)
CLIENT_ADDR=
CLIENT_WIF=

WORKER_ADDR=
WORKER_WIF=

AGENT_ADDR=
AGENT_WIF=

# Contract Hash
VAULT_CONTRACT_HASH=0x2c9090b5eb4639a6c27b0bfeaba4d7680ef89775

# AI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://sudoapp.dev/api/v1

# IPFS Storage (4everland)
EVERLAND_BUCKET_NAME=super-pay
EVERLAND_ACCESS_KEY=your_access_key
EVERLAND_SECRET_KEY=your_secret_key
EVERLAND_ENDPOINT=https://endpoint.4everland.co/
```

### 4. Start Backend API

```bash
# Using start script (recommended)
./start_backend.sh

# OR manually
cd backend
python app.py
```

Backend will start on: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 5. Start Frontend (In a new terminal)

```bash
# Install frontend dependencies
cd web
npm install

# Start Next.js app
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### 6. Access the Application

1. Open browser: `http://localhost:3000`
2. Select role: **Client** or **Worker**
3. Wallet auto-connects based on .env configuration

**Client Flow:**
- Navigate to "Create New Job"
- Enter job description and upload reference photos
- Set amount in GAS
- Submit to create escrow contract

**Worker Flow:**
- Browse "Available Jobs"
- Click "Claim Job" to accept
- Navigate to "My Work"
- Upload proof photo and submit for verification

## 🔑 Key Features

### For Clients
- ✅ Natural language job creation (AI-powered)
- ✅ Automatic fund escrow in smart contract
- ✅ Job history and status tracking
- ✅ Real-time wallet balance

### For Workers
- ✅ Browse available gigs
- ✅ Auto-claim (first-come-first-served)
- ✅ Submit proof photos via IPFS
- ✅ Earnings dashboard + stats

### System Features
- ✅ AI visual verification (Eye Agent)
- ✅ <10ms job queries (SQLite)
- ✅ ~15s blockchain confirmations
- ✅ Automatic payment release
- ✅ Dispute handling

## 🛠️ Technology Stack

**Blockchain:** Neo N3 TestNet (Smart contracts in Python)
**Backend:** FastAPI + SQLite (Fast queries)
**Frontend:** Next.js + Tailwind CSS
**AI:** Sudo AI APIs (Paralegal + Eye agents)
**Storage:** IPFS (Everland/4everland)
**Wallet:** neo3-python library

## 🔐 Smart Contract

**Deployed on Neo N3 TestNet:**
```
Contract: 0x2c9090b5eb4639a6c27b0bfeaba4d7680ef89775
Network: Neo N3 TestNet
```
<img width="1511" height="771" alt="image" src="https://github.com/user-attachments/assets/60c17679-3ca7-43cd-9968-f236c4a88e37" />

<img width="1022" height="713" alt="image" src="https://github.com/user-attachments/assets/09953052-d885-4e50-a9d9-594205720c97" />

**Test Wallet Status**

<img width="1278" height="625" alt="image" src="https://github.com/user-attachments/assets/f61e21d7-9101-4c0a-9c1c-526e0c6bf934" />

<img width="1276" height="699" alt="image" src="https://github.com/user-attachments/assets/db25f6fe-8170-48ab-9357-20e7d5285814" />

<img width="1269" height="677" alt="image" src="https://github.com/user-attachments/assets/cac9f430-0081-4a5b-83d6-9cf9398d59c4" />


## 🌐 API Endpoints

See `http://localhost:8000/docs` for complete API documentation.

**Key endpoints:**
- `GET /api/wallet/balance/{address}` - Get GAS balance
- `GET /api/jobs/available` - List open jobs
- `POST /api/jobs/create` - Create new job
- `POST /api/jobs/assign` - Worker claims job
- `POST /api/jobs/submit` - Submit proof + AI verification

## 📄 License

MIT
