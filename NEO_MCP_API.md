# GigShield Neo N3 MCP API Documentation

## For AI Agent Team

This document describes how to interact with the GigShield smart contract on Neo N3 blockchain through the NeoMCP Python wrapper.

---

## Contract Information

**Network:** Neo N3 TestNet  
**RPC Endpoint:** `https://testnet1.neo.coz.io:443/`

**Explorer:** https://testnet.neotube.io/contract/0x2c9090b5eb4639a6c27b0bfeaba4d7680ef89775

---

## Setup

```python
from src.neo_mcp import NeoMCP

# Initialize (loads config from .env automatically)
neo = NeoMCP()
```

---

## API Methods

### 1. Get Job Details (READ - For AI Verification)

**Use Case:** AI Agent reads job details from blockchain to verify task completion.

```python
job_details = await neo.get_job_details(job_id=1001)
```

**Returns:**
```python
{
    "job_id": 1001,
    "status_code": 2,
    "status_name": "LOCKED",
    "client_address": "NYKdk2LUEngRZNc5hnFvuFJV6n2hpppSVg",
    "worker_address": "Nij8VV5N7ehpYvHWYRgE4KUWeCoCt5xzXL",
    "amount_locked": 1000000000,
    "amount_gas": 10.0,
    "details": "Build a simple landing page with responsive design",
    "reference_urls": ["ipfs://QmTest123", "ipfs://QmTest456"]
}
```

**Status Codes:**
- `0` = NONE (job doesn't exist)
- `1` = OPEN (waiting for worker)
- `2` = LOCKED (worker assigned, work in progress)
- `3` = COMPLETED (funds released)
- `4` = DISPUTED (conflict resolution)

**Response Time:** ~0.7 seconds (fast, no gas cost)

---

### 2. Release Funds (WRITE - AI Agent Action)

**Use Case:** After AI verifies task completion, release payment to worker.

```python
result = await neo.release_funds_on_chain(job_id=1001)
```

**Pre-conditions:**
- Job status must be `LOCKED` (worker assigned)
- Only AGENT wallet can call this
- AI must have verified task completion

**Returns on Success:**
```python
{
    "success": True,
    "tx_hash": "0xdf1f07517e9327de5d895375bee777778df5d91e3d5f7afee83a4525d2cae36c",
    "job_id": 1001,
    "worker": "Nij8VV5N7ehpYvHWYRgE4KUWeCoCt5xzXL",
    "worker_paid_gas": 9.5,
    "fee_collected_gas": 0.5,
    "treasury": "NXpN8dzPnXaVYqRTiS6dXPXG8NmaqoeqjY",
    "note": "Transaction sent. Funds will be transferred once confirmed.",
    "job_details": { ... }
}
```

**Returns on Failure:**
```python
{
    "success": False,
    "error": "Job must be LOCKED to release funds. Current: OPEN",
    "job_id": 1001,
    "current_status": "OPEN",
    "job_details": { ... }
}
```

**Response Time:** ~1 second (transaction sent), ~15-20 seconds for blockchain confirmation

---

### 3. Get Job Status (READ - Quick Status Check)

**Use Case:** Quick check of job status without full details.

```python
status = await neo.get_job_status(job_id=1001)
```

**Returns:**
```python
{
    "job_id": 1001,
    "status_code": 2,
    "status_name": "LOCKED"
}
```

**Response Time:** ~0.5 seconds

---

### 4. Get Contract Configuration (READ)

**Use Case:** Check contract settings (agent address, fee, treasury).

```python
config = await neo.get_contract_config()
```

**Returns:**
```python
{
    "owner": "NddzCAoj13xgtBvFZ1Wp8eRdETsjpNTbyz",
    "agent": "NRF64mpLJ8yExn38EjwkxzPGoJ5PLyUbtP",
    "treasury": "NXpN8dzPnXaVYqRTiS6dXPXG8NmaqoeqjY",
    "fee_bps": 500,
    "fee_percentage": 5.0
}
```

---

## AI Agent Workflow

### Typical Flow for Task Verification & Payment:

```python
# 1. AI receives notification that task is submitted
job_id = 1001

# 2. Read job details from blockchain (NOT from database!)
job_details = await neo.get_job_details(job_id)

print(f"Verifying job: {job_details['details']}")
print(f"Client: {job_details['client_address']}")
print(f"Worker: {job_details['worker_address']}")
print(f"Amount: {job_details['amount_gas']} GAS")
print(f"Status: {job_details['status_name']}")

# 3. Verify job is in LOCKED state (worker assigned)
if job_details['status_name'] != 'LOCKED':
    print(f"❌ Cannot verify - job must be LOCKED, current: {job_details['status_name']}")
    return

# 4. AI performs verification (your ML/AI logic here)
# - Check reference images from IPFS URLs
# - Verify task completion against acceptance criteria
# - Check quality standards
verification_passed = your_ai_verification_logic(
    task_details=job_details['details'],
    reference_urls=job_details['reference_urls'],
    submitted_work_url="worker_submission_url"
)

# 5. If verification passes, release funds
if verification_passed:
    print("✅ Verification passed - releasing funds...")
    result = await neo.release_funds_on_chain(job_id)
    
    if result['success']:
        print(f"💰 Payment released:")
        print(f"   Worker: {result['worker_paid_gas']} GAS")
        print(f"   Treasury: {result['fee_collected_gas']} GAS")
        print(f"   TX: {result['tx_hash']}")
    else:
        print(f"❌ Payment failed: {result['error']}")
else:
    print("❌ Verification failed - work does not meet criteria")
    # Handle dispute resolution
```

---

## Important Notes for AI Team

### 1. **Source of Truth = Blockchain**
- Always read job details from blockchain using `get_job_details()`
- Do NOT trust data from your database - blockchain is the source of truth
- Database is only for caching/indexing

### 2. **Transaction Timing**
- Write operations (`release_funds`) return immediately with TX hash
- Actual blockchain confirmation takes ~15-20 seconds
- Read operations are instant (~0.5-1 second)

### 3. **Error Handling**
- Check `result['success']` before proceeding
- Handle `error` field when `success: False`
- Pre-validation happens automatically (job status check)

### 4. **Gas Costs**
- Read operations: **FREE** (no GAS cost)
- Write operations: **~0.003 GAS** (paid by agent wallet)
- Agent wallet needs GAS balance for transactions

### 5. **Agent Wallet**
- Only the configured AGENT wallet can call `release_funds()`
- This is enforced by smart contract
- Agent address: `NRF64mpLJ8yExn38EjwkxzPGoJ5PLyUbtP`

### 6. **Payment Split**
- Worker receives: **95%** of locked amount
- Treasury receives: **5%** platform fee
- Split happens automatically in smart contract

---

## Integration Example

```python
import asyncio
from src.neo_mcp import NeoMCP

async def ai_agent_main():
    # Initialize
    neo = NeoMCP()
    
    # Your AI agent logic here
    job_id = 1001
    
    # Read from blockchain
    job = await neo.get_job_details(job_id)
    
    # Verify task (your AI logic)
    if job['status_name'] == 'LOCKED':
        # ... your verification code ...
        
        # Release payment
        result = await neo.release_funds_on_chain(job_id)
        print(result)

if __name__ == "__main__":
    asyncio.run(ai_agent_main())
```

---

## Questions?

Contact the blockchain team if you need:
- Different wallet configuration
- Additional read/write methods
- Help with async/await patterns
- Contract ABI details

**Remember:** You're working with REAL blockchain - all transactions are permanent and cost GAS!
