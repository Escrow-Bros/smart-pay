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

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Backend API

```bash
./start_backend.sh
# OR manually:
cd backend && python api.py
```

API available at: `http://localhost:8000`
Documentation: `http://localhost:8000/docs`

### 4. Start Frontend (Coming Soon)

```bash
cd frontend/app
reflex run
```

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

- [x] Smart contract deployed
- [x] Blockchain wrapper (NeoMCP)
- [x] AI agents (Paralegal + Eye)
- [x] SQLite database layer
- [x] FastAPI backend
- [ ] Reflex frontend integration
- [ ] Real-time polling (10s refresh)
- [ ] MainNet deployment

## 🤝 Contributing

This is a demo project for Neo N3 blockchain + AI integration.

## 📄 License

MIT

## 🔗 Resources

- **Neo N3 Docs:** https://docs.neo.org/
- **Reflex Docs:** https://reflex.dev/docs/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

