# GigShield Backend

Complete backend API for GigShield: Database + Blockchain + AI Agents

## Architecture

```
backend/
├── api.py          # FastAPI server (main entry point)
└── database.py     # SQLite database layer

agent/
├── paralegal.py    # Job validation AI
├── eye.py          # Visual verification AI
└── storage.py      # IPFS storage

src/
├── neo_mcp.py      # Neo N3 blockchain wrapper
└── neo_config.py   # Blockchain configuration
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start API Server

```bash
cd backend
python api.py
```

API will be available at: `http://localhost:8000`

## API Endpoints

### Wallet Management

**GET** `/api/wallet/balance/{address}`
- Get GAS balance for any Neo N3 address
- Response time: ~0.5-1s (blockchain RPC call)

Example:
```bash
curl http://localhost:8000/api/wallet/balance/NUQawTAhtXsQ2WYS6MVVeJdErXPCrWJvpV
```

### Job Listing (Fast - from SQLite)

**GET** `/api/jobs/available`
- List all OPEN jobs
- Response time: <10ms

**GET** `/api/jobs/client/{address}`
- Get all jobs created by a client
- Response time: <10ms

**GET** `/api/jobs/worker/{address}`
- Get worker's current job + history + stats
- Response time: <10ms

**GET** `/api/jobs/{job_id}`
- Get detailed job information
- Response time: <10ms

### Job Creation

**POST** `/api/jobs/create`
```json
{
  "client_address": "NUQawTAhtXsQ2WYS6MVVeJdErXPCrWJvpV",
  "description": "Clean garage and organize tools",
  "reference_photos": ["https://ipfs.io/ipfs/Qm..."],
  "amount": 5.0
}
```

Flow:
1. Creates job on blockchain (15s confirmation)
2. Inserts into database with status OPEN
3. Returns job_id + tx_hash

### Worker Assignment

**POST** `/api/jobs/assign`
```json
{
  "job_id": 1234567890,
  "worker_address": "NUQawTAhtXsQ2WYS6MVVeJdErXPCrWJvpV"
}
```

Flow:
1. Checks job is OPEN in database
2. Assigns worker on blockchain
3. Updates database status to LOCKED

### Proof Submission

**POST** `/api/upload/proof`
- Upload proof photo to IPFS
- Returns IPFS URL

**POST** `/api/jobs/submit`
```json
{
  "job_id": 1234567890,
  "proof_photos": ["https://ipfs.io/ipfs/Qm..."]
}
```

Flow:
1. Updates database with proof photos
2. Triggers Eye Agent for AI verification
3. If approved: Releases funds on blockchain
4. Updates status to COMPLETED or DISPUTED

## Database Schema

**jobs table:**
- `job_id` (INTEGER PRIMARY KEY) - Unix timestamp
- `client_address` (TEXT) - Neo N3 address
- `worker_address` (TEXT) - Neo N3 address or NULL
- `description` (TEXT) - Job details
- `reference_photos` (TEXT) - JSON array of IPFS URLs
- `proof_photos` (TEXT) - JSON array of IPFS URLs
- `amount` (REAL) - Amount in GAS
- `status` (TEXT) - OPEN | LOCKED | COMPLETED | DISPUTED
- `created_at` (TIMESTAMP)
- `assigned_at` (TIMESTAMP)
- `completed_at` (TIMESTAMP)
- `tx_hash` (TEXT) - Blockchain transaction hash
- `verification_result` (TEXT) - JSON from Eye Agent

**Indexes:**
- `idx_status` - Fast queries for available jobs
- `idx_client` - Fast queries for client dashboard
- `idx_worker` - Fast queries for worker dashboard

## Performance

**Database queries:** <10ms (indexed SQLite)
**Balance checks:** ~0.5-1s (Neo RPC call)
**Blockchain writes:** ~15s confirmation time

## Why SQLite?

✅ **Fast:** <10ms queries with indexes
✅ **Simple:** File-based, no server setup
✅ **Reliable:** ACID transactions
✅ **Portable:** Single file database

Blockchain is only used for:
- Job creation (funds locked)
- Worker assignment (claim job)
- Fund release (payment)

Database is used for:
- Job listing (fast queries)
- Worker stats
- Job history

## Health Check

```bash
curl http://localhost:8000/api/health
```

Returns:
```json
{
  "status": "healthy",
  "database": "ok",
  "blockchain": "neo-testnet",
  "ai_service": "sudo-ai"
}
```

## Development

**Run with auto-reload:**
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

**Test endpoints:**
```bash
# Get available jobs
curl http://localhost:8000/api/jobs/available

# Get wallet balance
curl http://localhost:8000/api/wallet/balance/YOUR_ADDRESS

# Health check
curl http://localhost:8000/api/health
```

## Integration with Reflex Frontend

Frontend should:
1. Poll `/api/wallet/balance/{address}` every 10 seconds
2. Query `/api/jobs/available` for job listing
3. POST to `/api/jobs/create` for new jobs
4. POST to `/api/jobs/assign` to claim jobs

See `frontend/app/` for Reflex implementation.
