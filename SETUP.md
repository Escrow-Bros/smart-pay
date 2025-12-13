# GigShield Setup Guide

## 📋 Quick Reference

### Project Structure
```
smart-pay/
├── backend/          # FastAPI server (port 8000)
├── frontend/         # Reflex UI (port 3000)
├── agent/            # AI agents (Paralegal, Eye)
├── contracts/        # Neo N3 smart contracts
├── scripts/          # Utility scripts
└── src/              # Neo blockchain wrapper
```

### Dependencies

**Root `requirements.txt`** (Backend + Blockchain):
- Neo N3 blockchain libraries (neo-mamba, neo3-boa)
- FastAPI + Uvicorn
- AI SDK (spoon-ai-sdk, openai)
- IPFS/Storage (boto3)
- Database (SQLite via Python)

**Frontend `frontend/requirements.txt`**:
- Reflex framework >=0.4.0
- httpx (async HTTP client)
- python-dotenv (env variables)

## 🚀 Running the Application

### Step 1: Backend Setup (Terminal 1)

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Start backend
./start_backend.sh
# Backend runs on http://localhost:8000
```

**Expected Output:**
```
✅ All dependencies already satisfied
🚀 Starting backend on port 8000...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Frontend Setup (Terminal 2)

```bash
# Navigate to frontend
cd frontend

# Install frontend dependencies (first time only)
pip install -r requirements.txt

# Start Reflex
reflex run
```

**Expected Output:**
```
App running at: http://localhost:3000/
Backend running at: http://0.0.0.0:8001
```

### Step 3: Access Application

Open browser: **http://localhost:3000**

## 🔐 Environment Setup

Ensure `.env` file exists in root directory with:

```env
# Neo N3 Configuration
NEO_TESTNET_RPC=https://testnet1.neo.coz.io:443/

# Wallet Addresses
CLIENT_ADDR=NYKdk2LUEngRZNc5hnFvuFJV6n2hpppSVg
CLIENT_WIF=KwHtAwGuYCQNkrerYqx2BSbngzTrJucAQpEGmnmK8H3GbwmgV4Cm

WORKER_ADDR=Nij8VV5N7ehpYvHWYRgE4KUWeCoCt5xzXL
WORKER_WIF=KxAcYFCnMbasEWtomtw9T2Fy2kShRYUMaP9Sgq9XtFjCSmY4CjcB

AGENT_ADDR=NRF64mpLJ8yExn38EjwkxzPGoJ5PLyUbtP
AGENT_WIF=L5j461NAEvD84rWCjphFZSanSPc45kVtapxEC1uAWF7MRNuZJYzr

# Smart Contract
VAULT_CONTRACT_HASH=0x2c9090b5eb4639a6c27b0bfeaba4d7680ef89775

# AI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=https://sudoapp.dev/api/v1

# Pinata IPFS Storage
PINATA_API_KEY=your_api_key
PINATA_SECRET_KEY=your_secret_key
PINATA_JWT=your_jwt_token
PINATA_GROUP_ID=optional_group_id
```

## 📊 Console Logs to Expect

When selecting a role, you should see:

**Client Mode:**
```
🔵 CLIENT MODE - Address: NYKdk2LUEngRZNc5hnFvuFJV6n2hpppSVg
📍 Current User: Alice
📍 Wallet Address: NYKdk2LUEngRZNc5hnFvuFJV6n2hpppSVg
🔄 Fetching balance for: NYKdk2LUEngRZNc5hnFvuFJV6n2hpppSVg
📡 API URL: http://localhost:8000/api/wallet/balance/NYK...
📥 Response Status: 200
💰 Balance fetched: 39.97 GAS
```

**Worker Mode:**
```
🟢 WORKER MODE - Address: Nij8VV5N7ehpYvHWYRgE4KUWeCoCt5xzXL
📍 Current User: Bob
📍 Wallet Address: Nij8VV5N7ehpYvHWYRgE4KUWeCoCt5xzXL
🔄 Fetching balance for: Nij8VV5N7ehpYvHWYRgE4KUWeCoCt5xzXL
📡 API URL: http://localhost:8000/api/wallet/balance/Nij...
📥 Response Status: 200
💰 Balance fetched: 59.49 GAS
```

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

**Dependencies missing:**
```bash
# Reinstall from root
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port 3000 already in use:**
```bash
# Reflex will auto-switch to 3001
# Or manually kill process
lsof -i :3000
kill -9 <PID>
```

**Reflex cache issues:**
```bash
cd frontend
rm -rf .web .states
reflex run
```

**Module import errors:**
```bash
cd frontend
pip install -r requirements.txt
```

### API Connection Issues

**Balance shows 0 GAS:**
- Check backend is running: `curl http://localhost:8000/api/wallet/balance/NYKdk2LUEngRZNc5hnFvuFJV6n2hpppSVg`
- Verify .env has correct addresses
- Check Neo TestNet RPC is accessible

**No jobs showing:**
- Backend might not have any jobs created yet
- Check database: `ls -la backend/gigshield.db`
- Create test job via client UI

## 📁 Important Files

### Configuration
- `.env` - Environment variables (DO NOT commit)
- `.gitignore` - Git ignore patterns
- `start_backend.sh` - Backend startup script

### Backend
- `backend/api.py` - FastAPI server (15 endpoints)
- `backend/database.py` - SQLite database layer
- `backend/gigshield.db` - SQLite database file

### Frontend
- `frontend/app/app.py` - Main Reflex app
- `frontend/app/states/global_state.py` - State management
- `frontend/rxconfig.py` - Reflex configuration

### Blockchain
- `src/neo_mcp.py` - Neo N3 blockchain wrapper
- `contracts/gigshield_vault.py` - Smart contract

## 🎯 User Flows

### Client Flow
1. Select "Login as Client" on landing page
2. Navigate to "Create New Job"
3. Enter job description
4. Upload reference photos
5. Set payment amount (GAS)
6. Click "Create Job & Escrow Funds"
7. View job in "My Jobs"

### Worker Flow
1. Select "Login as Gig Worker" on landing page
2. View "Available Jobs" dashboard
3. Click "Claim Job" on desired gig
4. Navigate to "My Work"
5. See current assignment
6. Upload proof photo
7. Click "Verify Work & Claim Payment"

### Wallet View (Both Roles)
1. Click "Wallet" in sidebar
2. See full Neo address with copy button
3. View current GAS balance
4. Balance updates automatically

## 📦 Git Status

Files tracked:
- Source code (`.py`, `.md`)
- Configuration templates
- Scripts

Files ignored:
- `.env` (secrets)
- `.venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `.web/`, `.states/` (Reflex build)
- `*.db` (databases)
- `uploaded_files/` (user uploads)

## 🔄 Development Workflow

1. **Make changes** to backend or frontend
2. **Backend auto-reloads** (FastAPI with `--reload`)
3. **Frontend auto-compiles** (Reflex hot reload)
4. **Check console** for errors/logs
5. **Test in browser** at localhost:3000

## 📚 Additional Resources

- Backend API Docs: http://localhost:8000/docs
- Neo N3 Docs: https://docs.neo.org/
- Reflex Docs: https://reflex.dev/docs/
- Project README: `README.md`
