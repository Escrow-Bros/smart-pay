# GigShield Project Structure

Clean, organized structure separating AI agents from infrastructure services.

## 📁 Directory Organization

```
smart-pay/
├── agent/              ← AI AGENTS ONLY (SpoonOS + LLMs)
│   ├── paralegal.py       🤖 Job validator & plan generator
│   ├── eye.py             👁️ Work verifier with vision
│   ├── hello.py           🚀 SpoonOS demo
│   ├── __init__.py        📦 Package exports
│   └── requirements.txt   📋 Dependencies
│
├── services/           ← INFRASTRUCTURE SERVICES
│   ├── storage.py         ☁️ IPFS uploader (4Everland)
│   ├── api_server.py      🔌 Flask API endpoints
│   ├── config.py          ⚙️ Configuration utilities
│   ├── __init__.py        📦 Package exports
│   └── README.md          📖 Services documentation
│
├── contracts/          ← SMART CONTRACTS (Neo N3)
│   ├── gigshield_vault.py 💰 Payment escrow
│   └── requirements.txt   📋 Dependencies
│
├── docs/               ← COMPREHENSIVE DOCUMENTATION
│   ├── README.md              📋 Documentation index
│   ├── PARALEGAL_AGENT.md     📖 Paralegal guide
│   ├── EYE_AGENT.md           📖 Eye agent guide
│   ├── STORAGE_MODULE.md      📖 Storage guide
│   ├── AGENT_INTEGRATION.md   📖 Integration flow
│   ├── INTEGRATION_GUIDE.md   📖 Detailed integration
│   ├── PARALEGAL_FIXES.md     📖 Technical fixes
│   ├── VISION_UPGRADE.md      📖 Vision details
│   └── README_EYE.md          📖 Extended Eye guide
│
├── frontend/           ← USER INTERFACE (Future)
│   └── client_view.py     (partial implementation)
│
├── scripts/            ← DEPLOYMENT & UTILITY SCRIPTS
│   ├── generate_wallets.py    💼 Wallet creation
│   ├── check_balances.py      💵 Balance checker
│   ├── compile_vault.py       🔨 Contract compiler
│   ├── deploy_contract.py     🚀 Contract deployment
│   ├── initialize_contract.py ⚙️ Contract initialization
│   └── verify_contract.py     ✅ Contract verifier
│
├── mcp-server/         ← MCP SERVER (Future)
│
├── README.md           ← PROJECT OVERVIEW
├── STRUCTURE.md        ← THIS FILE
└── requirements.txt    📋 Root dependencies
```

## 🎯 Design Principles

### `/agent` - AI Agents Only
**Rule:** Files here MUST use LLMs and make intelligent decisions

**Includes:**
- ✅ Paralegal (validates jobs, generates plans)
- ✅ Eye (verifies work, makes decisions)
- ✅ Hello (SpoonOS demo)

**Does NOT include:**
- ❌ Storage (no AI, just IPFS upload)
- ❌ API server (routing only)
- ❌ Config (utilities)

### `/services` - Infrastructure Services
**Rule:** Files here provide utility functions WITHOUT AI

**Includes:**
- ✅ Storage (IPFS upload)
- ✅ API server (endpoints)
- ✅ Config (helpers)

**Characteristics:**
- No LLM calls
- No intelligent decisions
- Reusable utilities
- External integrations

### `/contracts` - Smart Contracts
Blockchain logic (Neo N3).

### `/docs` - Documentation
All guides, implementation details, and integration docs.

### `/frontend` - User Interface
To be built (deferred for now).

### `/scripts` - Deployment Scripts
Wallet creation, contract deployment, utilities.

## 📦 Import Patterns

### Agents:
```python
from agent.paralegal import analyze_job_request
from agent.eye import verify_work
```

### Services:
```python
from services.storage import upload_to_ipfs
from services.config import get_setting
```

### Cross-Module:
```python
# Agents can use Services:
from services.storage import upload_to_ipfs  # ✅ OK

# Services should NOT use Agents:
from agent.eye import verify_work  # ❌ Avoid (creates circular dependency)
```

## 🎯 Separation Benefits

### 1. Clarity
```
"Where's the AI logic?" → /agent
"Where's the IPFS upload?" → /services
"Where's the documentation?" → /docs
```

### 2. Team Organization
```
Brain Team → /agent (AI logic)
Vault Team → /contracts (blockchain)
Bridge Team → /services (integrations)
Face Team → /frontend (UI)
```

### 3. Reusability
```
Services can be used by:
- Agents
- Frontend
- Scripts
- Tests
- External tools
```

### 4. Testing
```
# Test agents independently
python agent/paralegal.py

# Test services independently
python -c "from services.storage import upload_to_ipfs"

# Test integration
python scripts/test_integration.py
```

## ✅ Current Status

| Component | Location | Status |
|-----------|----------|--------|
| Paralegal Agent | `/agent` | ✅ Complete |
| Eye Agent | `/agent` | ✅ Complete |
| Storage Service | `/services` | ✅ Complete |
| Documentation | `/docs` | ✅ Organized |
| Smart Contracts | `/contracts` | 🚧 In progress |
| Frontend | `/frontend` | 🚧 Deferred |

## 🚀 Next Steps

1. **Smart Contract Integration**
   - Update Eye agent to fetch from Neo N3
   - Replace placeholder storage

2. **Testing**
   - Update test imports (agent.storage → services.storage)
   - Integration tests with actual contract

3. **Frontend** (Later)
   - Build on top of stable agents
   - Import from both /agent and /services

---

**Clean structure = Happy developers!** 🎉

