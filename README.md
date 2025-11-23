# GigShield 🛡️

**Decentralized Gig Platform on Neo N3 Blockchain**

AI-powered escrow system for trustless gig work: Smart contracts + Visual verification + Natural language job creation.

## 🎯 What is GigShield?

GigShield connects clients and workers through blockchain-secured gig contracts with AI verification:

- **Client:** Describe job in natural language → AI extracts requirements → Funds locked in smart contract
- **Worker:** Browse available gigs → Claim job → Submit proof photos
- **AI Tribunal:** Verifies work completion → Auto-releases payment if approved

## 🏗️ Architecture

```
┌─────────────────┐
│  Reflex Web UI  │ (Real-time wallet balance, job dashboard)
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
│   ├── api.py           # FastAPI server (main entry point)
│   ├── database.py      # SQLite layer for fast queries
│   └── README.md        # API documentation
│
├── frontend/
│   └── app/             # Reflex web application
│       ├── app.py       # Main app with mode toggle
│       ├── components/  # UI components
│       └── states/      # State management
│
├── agent/
│   ├── paralegal.py     # Job validation AI
│   ├── eye.py           # Visual verification AI
│   └── storage.py       # IPFS storage
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
    ├── generate_wallets.py # Generate Neo wallets
    └── compile_vault.py    # Compile contracts
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
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
python api.py
```

Backend will start on: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 5. Start Frontend (In a new terminal)

```bash
# Install frontend dependencies
cd frontend
pip install -r requirements.txt

# Start Reflex app
reflex run
```

Frontend will be available at:
- **UI:** `http://localhost:3000`
- **Backend:** `http://localhost:8001` (Reflex internal)

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
**Frontend:** Reflex (Python web framework)
**AI:** Sudo AI APIs (Paralegal + Eye agents)
**Storage:** IPFS (Everland/4everland)
**Wallet:** neo3-python library

## 📊 Performance

| Operation | Speed |
|-----------|-------|
| Database queries | <10ms |
| Wallet balance check | ~0.5-1s |
| Blockchain writes | ~15s |
| IPFS upload | ~2-5s |
| AI verification | ~3-5s |

## 🔐 Smart Contract

**Deployed on Neo N3 TestNet:**
```
Contract: 0x2c9090b5eb4639a6c27b0bfeaba4d7680ef89775
Network: Neo N3 TestNet
```

**Methods:**
- `create_job(job_id, client, amount, details, urls)` - Lock funds
- `assign_worker(job_id, worker)` - Claim job
- `release_funds(job_id)` - Pay worker (agent only)
- `get_job_status(job_id)` - Query status

## 📖 Usage Examples

### Create Job (cURL)

```bash
curl -X POST http://localhost:8000/api/jobs/create \
  -H "Content-Type: application/json" \
  -d '{
    "client_address": "NUQawTAhtXsQ2WYS6MVVeJdErXPCrWJvpV",
    "description": "Clean garage and organize tools",
    "reference_photos": ["https://ipfs.io/ipfs/Qm..."],
    "amount": 5.0
  }'
```

### Check Balance

```bash
curl http://localhost:8000/api/wallet/balance/NUQawTAhtXsQ2WYS6MVVeJdErXPCrWJvpV
```

### List Available Jobs

```bash
curl http://localhost:8000/api/jobs/available
```

## 🧪 Testing

```bash
# Check balances
python scripts/check_balances.py --role client

# Test job creation (TestNet)
python scripts/deposit_job.py
```

## 🌐 API Endpoints

See `backend/README.md` for complete API documentation.

**Key endpoints:**
- `GET /api/wallet/balance/{address}` - Get GAS balance
- `GET /api/jobs/available` - List open jobs
- `POST /api/jobs/create` - Create new job
- `POST /api/jobs/assign` - Worker claims job
- `POST /api/jobs/submit` - Submit proof + AI verification

## 🎯 Roadmap

- [x] Smart contract deployed on Neo N3 TestNet
- [x] Blockchain wrapper (NeoMCP)
- [x] AI agents (Paralegal + Eye)
- [x] SQLite database layer
- [x] FastAPI backend with 15+ endpoints
- [x] Reflex frontend with role-based UI
- [x] Real-time wallet integration
- [x] Job creation and claiming
- [x] IPFS photo storage
- [x] AI visual verification
- [ ] Dispute resolution system
- [ ] Multi-signature approvals
- [ ] MainNet deployment

## 📁 Important Files

### Backend
- `backend/api.py` - FastAPI server (15 REST endpoints)
- `backend/database.py` - SQLite ORM layer
- `src/neo_mcp.py` - Neo N3 blockchain interactions
- `agent/paralegal.py` - Job validation AI
- `agent/eye.py` - Visual proof verification

### Frontend
- `frontend/app/app.py` - Main Reflex application
- `frontend/app/states/global_state.py` - State management
- `frontend/app/components/landing.py` - Role selection page
- `frontend/app/components/client_view.py` - Client dashboard
- `frontend/app/components/worker_view.py` - Worker dashboard

### Contracts
- `contracts/gigshield_vault.py` - Neo N3 smart contract (Python)

## 🐛 Troubleshooting

**Backend won't start:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Verify dependencies
pip list | grep -E "fastapi|uvicorn|neo"
```

**Frontend errors:**
```bash
# Clear Reflex cache
cd frontend
rm -rf .web .states

# Reinstall
pip install -r requirements.txt --force-reinstall
```

**Wallet balance shows 0:**
- Ensure backend is running on port 8000
- Check .env has correct CLIENT_ADDR/WORKER_ADDR
- Verify Neo TestNet RPC is accessible

## 🤝 Contributing

This is a demo project for Neo N3 blockchain + AI integration.

## 📄 License

MIT

## 🔗 Resources

- **Neo N3 Docs:** https://docs.neo.org/
- **Reflex Docs:** https://reflex.dev/docs/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

