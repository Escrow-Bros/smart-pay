# 🛡️ GigShield - Smart Pay

**AI-Powered Gig Work Verification Platform**

## 🎯 Project Overview

GigShield uses AI agents and blockchain to protect both workers and employers. Workers submit proof of completed work, AI verifies it, and smart contracts automatically release payment.

## 📁 Project Structure

```
smart-pay/
├── agent/              # AI Agents ONLY
│   ├── paralegal.py       # Job validator & plan generator (TASK-011)
│   ├── eye.py             # Work verifier with vision (TASK-013)
│   ├── hello.py           # SpoonOS demo
│   └── requirements.txt   # Python dependencies
│
├── services/           # Infrastructure Services
│   ├── storage.py         # IPFS uploader (TASK-012)
│   ├── api_server.py      # API endpoints
│   └── config.py          # Configuration helpers
│
├── docs/               # Comprehensive Documentation
│   ├── PARALEGAL_AGENT.md     # Paralegal guide
│   ├── EYE_AGENT.md           # Eye agent guide
│   ├── STORAGE_MODULE.md      # Storage guide
│   ├── AGENT_INTEGRATION.md   # Integration flow
│   └── README.md              # Docs index
│
├── contracts/          # Smart Contracts (Neo N3)
│   └── gigshield_vault.py     # Payment escrow contract
│
├── frontend/           # UI (To be built)
│
├── mcp-server/         # MCP Server (Future)
│
└── scripts/            # Deployment scripts
```

## ✅ Completed Components

### 1. **Paralegal Agent** (TASK-011) ✅
Validates job submissions and generates verification plans.

**Features:**
- Natural language job parsing
- Vision-based image verification (GPT-4V)
- Verification plan generation
- Acceptance criteria creation

**Usage:**
```python
from agent.paralegal import analyze_job_request

result = await analyze_job_request(
    text="Paint wall blue at 123 Main for 50 GAS",
    reference_image=photo_bytes
)
```

### 2. **Eye Agent** (TASK-013) ✅
Verifies worker proof photos with AI vision.

**Features:**
- Universal verification (works for any task type)
- Before/after comparison with GPT-4V
- Multi-layer fraud prevention
- Quality assessment

**Usage:**
```python
from agent.eye import verify_work

verdict = await verify_work(
    proof_photos=["ipfs://Qm.../proof.jpg"],
    job_id="job_12345"
)
```

### 3. **Storage Module** (TASK-012) ✅
Handles IPFS uploads via 4Everland.

**Usage:**
```python
from services.storage import upload_to_ipfs

url = upload_to_ipfs(image_bytes, "proof.jpg")
```

## 🚀 Quick Start

### 1. Setup
```bash
git clone <repo-url>
cd smart-pay

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r agent/requirements.txt
```

### 2. Configure
```bash
# Edit agent/.env with your API keys
nano agent/.env
```

Required:
- Sudo AI key (for Paralegal & Eye)
- 4Everland credentials (for Storage)

### 3. Test Agents
```bash
# Test Paralegal
python agent/paralegal.py

# Test integration
python agent/integration_test.py
```

## 📚 Documentation

See `/docs` folder for comprehensive guides:
- Component documentation
- Integration flows
- Usage examples
- Implementation details

## 🎯 Current Focus

**Focus:** Core AI agents  
**Status:** Paralegal ✅ | Eye ✅ | Storage ✅  
**Next:** Smart contract integration  
**Later:** Frontend orchestration

## 🏗️ Architecture

```
┌─────────────────┐
│  PARALEGAL      │  Validates jobs, generates rules
└────────┬────────┘
         ↓
┌────────▼────────┐
│  SMART CONTRACT │  Stores rules, holds payment
└────────┬────────┘
         ↓
┌────────▼────────┐
│  EYE AGENT      │  Verifies work with vision
└────────┬────────┘
         ↓
┌────────▼────────┐
│  PAYMENT        │  Automatic release if approved
└─────────────────┘
```

## 🔑 Tech Stack

- **AI:** SpoonOS SDK + Sudo AI + GPT-4V
- **Storage:** 4Everland IPFS
- **Blockchain:** Neo N3 (in progress)
- **Language:** Python

## 📝 Tasks Status

- [x] TASK-011: Paralegal Agent
- [x] TASK-012: 4Everland Storage
- [x] TASK-013: Eye Agent
- [ ] TASK-004-006: Smart Contracts
- [ ] TASK-007-010: Frontend
- [ ] TASK-015: MCP Server

## 🤝 Team

- **The Vault:** Smart contracts (Neo N3)
- **The Brain:** AI agents (Paralegal + Eye) ← Current focus
- **The Face:** Frontend (deferred)
- **The Bridge:** Integration & MCP (future)

---

**Status:** Core AI agents complete and production-ready! 🎉  
**Next:** Backend integration with blockchain

