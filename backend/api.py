import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables at application entry point
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
import asyncio
import json
import os
import time
import logging
from collections import defaultdict
from threading import Lock

# Internal imports
from backend.database import Database

# Database instance - Supabase PostgreSQL only
db = Database()

def get_db():
    """Dependency to get database instance"""
    return db

from backend.agent.paralegal import analyze_job_request
from backend.agent.eye import UniversalEyeAgent, verify_work
from backend.agent.storage import upload_to_ipfs
from backend.agent.banker import check_balance
from backend.agent.conversational_job_creator import get_conversation_engine
from src.neo_mcp import NeoMCP
from scripts.check_balances import get_gas_balance


# ==================== RATE LIMITING ====================

class RateLimiter:
    """Simple in-memory rate limiter"""
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier (IP/wallet)"""
        with self.lock:
            now = time.time()
            # Clean old requests outside the window
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if now - req_time < self.window_seconds
            ]
            
            # Check if limit exceeded
            if len(self.requests[identifier]) >= self.max_requests:
                return False
            
            # Record this request and allow it
            self.requests[identifier].append(now)
            return True

rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

# Arbiter rate limiter (stricter limits for sensitive operations)
arbiter_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

# ==================== ARBITER CONFIGURATION ====================

# Arbiter whitelist - authorized addresses that can resolve disputes
# In production, this should be stored in database with role management
ARBITER_WHITELIST = set()

# Task tracking for recovery and background jobs
recovery_tasks: set = set()

def load_arbiter_whitelist():
    """Load arbiter addresses from environment variables"""
    # Default arbiter address (fallback for development)
    DEFAULT_ARBITER = 'NRF64mpLJ8yExn38EjwkxzPGoJ5PLyUbtP'
    
    agent_addr = os.getenv('AGENT_ADDR', '')
    if agent_addr:
        ARBITER_WHITELIST.add(agent_addr)
    else:
        # If no AGENT_ADDR set, use default for development
        print(f"ℹ️  No AGENT_ADDR in environment, using default arbiter: {DEFAULT_ARBITER}")
        ARBITER_WHITELIST.add(DEFAULT_ARBITER)
    
    # Add additional arbiters from comma-separated env var
    extra_arbiters = os.getenv('ARBITER_ADDRESSES', '')
    if extra_arbiters:
        for addr in extra_arbiters.split(','):
            addr = addr.strip()
            if addr:
                ARBITER_WHITELIST.add(addr)
    
    # Fail-safe: warn if no arbiters configured (shouldn't happen with default)
    if not ARBITER_WHITELIST:
        print("⚠️  WARNING: No arbiters configured in ARBITER_WHITELIST!")
        print("   Set AGENT_ADDR or ARBITER_ADDRESSES in .env to enable dispute resolution")
        print("   All dispute resolution attempts will be rejected with 403")

# Audit log storage (in production, use proper database table)
AUDIT_LOGS = []

def log_arbiter_action(
    arbiter_address: str,
    job_id: int,
    dispute_id: int,
    decision: str,
    client_ip: str = "unknown",
    request_id: str = "unknown"
):
    """Record arbiter resolution action for audit trail"""
    import datetime
    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "arbiter_address": arbiter_address,
        "job_id": job_id,
        "dispute_id": dispute_id,
        "decision": decision,
        "client_ip": client_ip,
        "request_id": request_id
    }
    AUDIT_LOGS.append(log_entry)
    print(f"🔍 AUDIT LOG: {log_entry}")
    # In production: write to database audit table

# ==================== ADDRESS VALIDATION ====================

def validate_neo_address(address: str) -> str:
    """Validate Neo N3 address format and return it if valid"""
    if not address.startswith('N') or len(address) != 34:
        raise HTTPException(status_code=400, detail="Invalid Neo N3 address format")
    return address

def get_validated_address(address: str) -> str:
    """FastAPI dependency for validated Neo N3 address"""
    return validate_neo_address(address)

# ==================== VALIDATION MODELS ====================

class VerificationPlan(BaseModel):
    """Structured verification plan for AI Eye agent"""
    task_category: str = Field(..., description="Category of task (e.g., 'cleaning', 'delivery', 'repair')")
    success_criteria: List[str] = Field(default_factory=list, description="List of criteria for success")
    rejection_criteria: List[str] = Field(default_factory=list, description="List of criteria for rejection")
    visual_checks: List[str] = Field(default_factory=list, description="Specific visual elements to verify")
    location_required: bool = Field(default=False, description="Whether GPS verification is required")
    comparison_mode: str = Field(default="before_after", description="before_after, reference_match, or checklist")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "task_category": "cleaning",
                "success_criteria": ["Area is visibly clean", "No debris present"],
                "rejection_criteria": ["Visible dirt", "Task incomplete"],
                "visual_checks": ["Floor surface", "Corners", "Overall cleanliness"],
                "location_required": True,
                "comparison_mode": "before_after"
            }
        }
    }

class CreateJobRequest(BaseModel):
    client_address: str = Field(..., min_length=34, max_length=34, description="Neo N3 address (34 chars starting with N)")
    description: str = Field(..., min_length=10, max_length=5000, description="Job description (10-5000 chars)")
    location: str = Field("", max_length=500)
    latitude: float = Field(0.0, ge=-90, le=90)
    longitude: float = Field(0.0, ge=-180, le=180)
    reference_photos: List[str] = Field(..., min_length=1, max_length=10, description="IPFS URLs")
    verification_plan: VerificationPlan = Field(..., description="Structured verification plan")
    amount: float = Field(..., gt=0, le=10000, description="Payment amount in GAS (0-10000)")
    
    @field_validator('client_address')
    @classmethod
    def validate_neo_address(cls, v):
        if not v.startswith('N'):
            raise ValueError('Neo N3 address must start with N')
        return v
    
    @field_validator('reference_photos')
    @classmethod
    def validate_ipfs_urls(cls, v):
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid IPFS URL: {url}')
        return v

class AssignJobRequest(BaseModel):
    job_id: int = Field(..., gt=0, description="Job ID (positive integer)")
    worker_address: str = Field(..., min_length=34, max_length=34, description="Worker's Neo N3 address")
    
    @field_validator('worker_address')
    @classmethod
    def validate_neo_address(cls, v):
        if not v.startswith('N'):
            raise ValueError('Neo N3 address must start with N')
        return v

class SubmitProofRequest(BaseModel):
    job_id: int = Field(..., gt=0)
    proof_photos: List[str] = Field(..., min_length=1, max_length=10)
    worker_location: Optional[Dict[str, float]] = Field(
        None, 
        description="GPS coordinates with keys: 'lat' (latitude, -90 to 90), 'lng' (longitude, -180 to 180), 'accuracy' (meters)"
    )
    
    @field_validator('proof_photos')
    @classmethod
    def validate_ipfs_urls(cls, v):
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid IPFS URL: {url}')
        return v
    
    @field_validator('worker_location')
    @classmethod
    def validate_gps(cls, v):
        if v is not None:
            required = ['lat', 'lng']
            for key in required:
                if key not in v:
                    raise ValueError(f'Worker location missing {key}')
            if not (-90 <= v['lat'] <= 90):
                raise ValueError('Invalid latitude')
            if not (-180 <= v['lng'] <= 180):
                raise ValueError('Invalid longitude')
        return v

class ValidationResult(BaseModel):
    clarity_issues: List[str]
    image_mismatch: bool
    mismatch_details: Optional[str]
    image_shows: Optional[str] = None

class BalanceCheck(BaseModel):
    sufficient: bool
    balance: float
    required: float
    error: Optional[str] = None

class JobAnalysisResponse(BaseModel):
    success: bool
    status: str
    data: dict
    validation: ValidationResult
    task_description: List[str]
    clarifying_questions: List[str]
    message: str
    balance_check: Optional[BalanceCheck] = None
    verification_plan: Optional[dict] = None


# ==================== APP SETUP ====================

app = FastAPI(
    title="GigSmartPay Unified Backend API",
    description="Complete backend for GigSmartPay - Database + Blockchain + AI",
    version="4.0.0"
)

# Enable CORS for Reflex frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = get_db()
mcp = NeoMCP()

# Load arbiter whitelist on startup
load_arbiter_whitelist()
print(f"✅ Loaded {len(ARBITER_WHITELIST)} authorized arbiters: {ARBITER_WHITELIST}")
eye_agent = UniversalEyeAgent()

# ==================== WEBSOCKET CONNECTION MANAGER ====================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)
        self.lock = Lock()
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """Connect a client to receive updates"""
        await websocket.accept()
        with self.lock:
            self.active_connections[client_id].append(websocket)
        print(f"🔌 WebSocket connected: {client_id} (total: {len(self.active_connections[client_id])})")
    
    def disconnect(self, client_id: str, websocket: WebSocket):
        """Disconnect a client"""
        with self.lock:
            if client_id in self.active_connections:
                try:
                    self.active_connections[client_id].remove(websocket)
                except ValueError:
                    # Already removed, ignore
                    pass
                # Delete key only if list is empty
                if not self.active_connections[client_id]:
                    del self.active_connections[client_id]
        print(f"🔌 WebSocket disconnected: {client_id}")
    
    async def broadcast_to_client(self, client_id: str, message: dict):
        """Send message to all connections for a specific client"""
        with self.lock:
            connections = self.active_connections.get(client_id, []).copy()
        
        disconnected = []
        for connection in connections:
            try:
                await connection.send_json(message)
            except (WebSocketDisconnect, RuntimeError) as e:
                print(f"⚠️  {type(e).__name__} sending to {client_id}: {e}")
                disconnected.append(connection)
            # Intentionally catch all exceptions to handle unexpected send errors gracefully
            except Exception as e:  # noqa: BLE001
                print(f"⚠️  Unexpected {type(e).__name__} sending to {client_id}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected sockets
        if disconnected:
            with self.lock:
                for conn in disconnected:
                    if conn in self.active_connections.get(client_id, []):
                        try:
                            self.active_connections[client_id].remove(conn)
                        except ValueError:
                            # Already removed by another thread
                            pass

websocket_manager = ConnectionManager()

# ==================== STARTUP RECOVERY ====================

@app.on_event("startup")
async def startup_recovery():
    """
    Recover pending jobs after server restart.
    Restarts blockchain monitors for any jobs stuck in PAYMENT_PENDING.
    """
    print("🔄 Starting recovery scan for pending jobs...")
    
    try:
        pending_jobs = db.get_jobs_by_status("PAYMENT_PENDING")
        print(f"   Found {len(pending_jobs)} jobs in PAYMENT_PENDING state")
        
        recovered = 0
        for job in pending_jobs:
            tx_hash = job.get('tx_hash')
            job_id = job.get('job_id')
            
            if tx_hash and job_id:
                print(f"   ↳ Restarting monitor for Job #{job_id} (tx: {tx_hash[:16]}...)")
                # Restart the background monitor task
                task = asyncio.create_task(
                    monitor_transaction_confirmation(job_id, tx_hash)
                )
                # Track task for lifecycle management
                recovery_tasks.add(task)
                task.add_done_callback(recovery_tasks.discard)
                # Add exception handler (capture job_id by value to avoid closure issue)
                task.add_done_callback(
                    lambda t, jid=job_id: logging.error(f"Recovery task exception for job {jid}", exc_info=t.exception()) if t.exception() else None
                )
                recovered += 1
            else:
                print(f"   ⚠️  Job #{job_id} missing tx_hash, cannot recover")
        
        if recovered > 0:
            print(f"✅ Recovery complete: Restarted {recovered} transaction monitors")
        else:
            print("✅ Recovery complete: No jobs needed recovery")
            
    except Exception:
        # Use logging.exception for better stack trace visibility
        logging.exception("Recovery failed")
        # Don't crash the server on recovery failure

# ==================== BACKGROUND TASK: TX MONITORING ====================

async def monitor_transaction_confirmation(job_id: int, tx_hash: str, max_attempts: int = 15):
    """
    Background task to monitor blockchain transaction confirmation.
    Polls the blockchain every 20 seconds for up to 5 minutes.
    Updates job status from PAYMENT_PENDING to COMPLETED once confirmed.
    Broadcasts updates via WebSocket to connected clients.
    """
    print(f"🔄 Starting transaction monitor for job #{job_id}, tx: {tx_hash}")
    
    # Get job to find client and worker addresses for WebSocket notifications
    job = db.get_job(job_id)
    if not job:
        print(f"⚠️  Job #{job_id} not found, cannot monitor")
        return
    
    for attempt in range(max_attempts):
        await asyncio.sleep(20)  # Wait 20 seconds between checks
        
        try:
            # Check on-chain job status
            job_status = await mcp.get_job_status(job_id)
            print(f"📊 Job #{job_id} blockchain status check (attempt {attempt + 1}/{max_attempts}): {job_status.get('status_name')} (code: {job_status.get('status_code')})")
            
            # Broadcast pending status update via WebSocket
            if job.get("worker_address"):
                await websocket_manager.broadcast_to_client(
                    job["worker_address"],
                    {
                        "type": "PAYMENT_PENDING",
                        "job_id": job_id,
                        "status": "PAYMENT_PENDING",
                        "message": f"Confirming transaction... (attempt {attempt + 1}/{max_attempts})",
                        "tx_hash": tx_hash,
                        "blockchain_status": job_status.get('status_name')
                    }
                )
            
            if job_status.get("status_name") == "COMPLETED":
                print(f"✅ Transaction confirmed for job #{job_id} after {(attempt + 1) * 20}s")
                # Update database to COMPLETED
                db.complete_job(job_id=job_id)
                
                # Broadcast completion to both client and worker
                completion_message = {
                    "type": "JOB_COMPLETED",
                    "job_id": job_id,
                    "status": "COMPLETED",
                    "message": "Payment confirmed! Job completed successfully.",
                    "tx_hash": tx_hash
                }
                
                if job.get("worker_address"):
                    await websocket_manager.broadcast_to_client(job["worker_address"], completion_message)
                if job.get("client_address"):
                    await websocket_manager.broadcast_to_client(job["client_address"], completion_message)
                
                return
            
            print(f"⏳ Job #{job_id} still pending... (attempt {attempt + 1}/{max_attempts}, elapsed: {(attempt + 1) * 20}s)")
            
        except Exception as e:
            print(f"⚠️  Error checking job #{job_id} status: {e}")
            continue
    
    # If we get here, transaction didn't confirm in time
    print(f"⚠️  WARNING: Job #{job_id} transaction {tx_hash} not confirmed after {max_attempts * 20}s")
    print("   Job remains in PAYMENT_PENDING status. Manual verification recommended.")
    
    # Notify worker of timeout
    if job.get("worker_address"):
        await websocket_manager.broadcast_to_client(
            job["worker_address"],
            {
                "type": "PAYMENT_TIMEOUT",
                "job_id": job_id,
                "status": "PAYMENT_PENDING",
                "message": "Transaction confirmation taking longer than expected. Please check status manually.",
                "tx_hash": tx_hash
            }
        )


# ==================== WEBSOCKET ====================

@app.websocket("/ws/{client_address}")
async def websocket_endpoint(websocket: WebSocket, client_address: str):
    """
    WebSocket endpoint for real-time job updates.
    Clients connect with their Neo address to receive:
    - Job status changes
    - Payment confirmations
    - Dispute resolutions
    - System notifications
    """
    await websocket_manager.connect(client_address, websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {"type": "error", "message": "Invalid JSON payload"}
                )
                continue
            
            # Handle ping/pong for connection health
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
            
            # Handle subscription requests
            elif message.get("type") == "subscribe":
                job_ids = message.get("job_ids", [])
                await websocket.send_json({
                    "type": "subscribed",
                    "job_ids": job_ids,
                    "message": f"Subscribed to updates for {len(job_ids)} jobs"
                })
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_address, websocket)
    except Exception as e:
        print(f"❌ WebSocket {type(e).__name__} for {client_address}: {e}")
        websocket_manager.disconnect(client_address, websocket)
        raise


# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "GigSmartPay Unified Backend API",
        "version": "4.0.0",
        "components": {
            "database": "SQLite",
            "blockchain": "Neo N3",
            "ai_agents": ["Paralegal", "Eye", "Banker"]
        },
        "endpoints": {
            "GET /api/health": "Detailed health check",
            "GET /api/wallet/balance/{address}": "Get wallet balance",
            "GET /api/jobs/available": "List available jobs (OPEN status)",
            "GET /api/jobs/client/{address}": "Get all client's jobs (all statuses)",
            "GET /api/jobs/worker/{address}/all": "Get all worker's jobs (all statuses)",
            "GET /api/jobs/worker/{address}/current": "Get worker's active jobs (LOCKED, PAYMENT_PENDING, DISPUTED)",
            "GET /api/jobs/worker/{address}/history": "Get worker's completed jobs",
            "GET /api/jobs/worker/{address}/stats": "Get worker statistics",
            "GET /api/jobs/{job_id}": "Get job details by ID",
            "POST /api/jobs/analyze": "Analyze job with AI (Paralegal)",
            "POST /api/jobs/create": "Create new job",
            "POST /api/jobs/assign": "Assign job to worker",
            "POST /api/upload/proof": "Upload proof image to IPFS",
            "POST /api/jobs/submit": "Submit proof and verify",
            "POST /api/eye/verify-work": "Direct Eye verification endpoint"
        }
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Check DB
        db_ok = db.get_available_jobs() is not None
        
        return {
            "status": "healthy",
            "database": "ok" if db_ok else "error",
            "blockchain": "neo-testnet",
            "ai_service": "sudo-ai",
            "text_model": "gpt-4",
            "vision_model": "gpt-4o"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


# ==================== WALLET ENDPOINTS ====================

@app.get("/api/wallet/balance/{address}")
async def get_wallet_balance(address: str):
    """Get GAS balance for Neo N3 address"""
    try:
        rpc_url = os.getenv("NEO_TESTNET_RPC", "https://testnet1.neo.coz.io:443/")
        balance = get_gas_balance(rpc_url, address)
        
        return {
            "success": True,
            "address": address,
            "balance": round(balance, 2),
            "currency": "GAS"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GasEstimateRequest(BaseModel):
    """Request model for gas estimation"""
    client_address: str = Field(..., description="Client's Neo N3 address")
    amount: float = Field(..., gt=0, description="Job payment amount in GAS")
    operation: str = Field(..., description="Operation to estimate: 'create_job', 'assign_job', 'release_funds'")
    
    @field_validator('client_address')
    @classmethod
    def validate_neo_address(cls, v: str) -> str:
        """Validate Neo N3 address format"""
        if not v or not isinstance(v, str):
            raise ValueError("Neo address must be a non-empty string")
        # Neo N3 addresses start with 'N' and are 34 characters long
        if not v.startswith('N') or len(v) != 34:
            raise ValueError("Invalid Neo N3 address format: must start with 'N' and be 34 characters long")
        return v


@app.post("/api/wallet/estimate-gas")
async def estimate_gas_cost(request: GasEstimateRequest):
    """
    Pre-flight check: Estimate total GAS cost for blockchain operation.
    Helps clients ensure they have sufficient balance before creating jobs.
    
    Returns:
        - operation_cost: GAS needed for the blockchain transaction
        - platform_fee: Platform fee (5% of job amount)
        - total_required: Total GAS needed (amount + fee + operation cost)
        - current_balance: Client's current GAS balance
        - sufficient: Whether client has enough GAS
    """
    try:
        # Get current balance
        rpc_url = os.getenv("NEO_TESTNET_RPC", "https://testnet1.neo.coz.io:443/")
        current_balance = get_gas_balance(rpc_url, request.client_address)
        
        # Platform fee calculation (5%)
        platform_fee = round(request.amount * 0.05, 2)
        
        # Estimate operation cost (blockchain transaction fees)
        # These are rough estimates based on typical Neo N3 transaction costs
        operation_costs = {
            "create_job": 0.02,      # ~0.02 GAS for contract invocation
            "assign_job": 0.01,      # ~0.01 GAS for assignment
            "release_funds": 0.015,  # ~0.015 GAS for release
            "dispute": 0.01,         # ~0.01 GAS for dispute creation
            "resolve": 0.015         # ~0.015 GAS for resolution
        }
        
        # Reject unsupported operations instead of silently defaulting
        if request.operation not in operation_costs:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported operation for gas estimation: {request.operation!r}",
            )
        operation_cost = operation_costs[request.operation]
        
        # Total required = job amount + platform fee + transaction cost
        total_required = request.amount + platform_fee + operation_cost
        
        # Check if sufficient
        sufficient = current_balance >= total_required
        shortfall = max(0, total_required - current_balance)
        
        return {
            "success": True,
            "estimate": {
                "operation": request.operation,
                "job_amount": round(request.amount, 2),
                "platform_fee": platform_fee,
                "operation_cost": operation_cost,
                "total_required": round(total_required, 4),
                "current_balance": round(current_balance, 4),
                "sufficient": sufficient,
                "shortfall": round(shortfall, 4) if not sufficient else 0,
                "message": "Sufficient balance" if sufficient else f"Need {round(shortfall, 4)} more GAS"
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"❌ Gas estimation error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to estimate gas: {e!s}",
        ) from e


# ==================== JOB LISTING ENDPOINTS ====================

@app.get("/api/jobs/available")
async def list_available_jobs():
    """Get all open jobs (filtered for worker public view)"""
    try:
        jobs = db.get_available_jobs()
        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }
    except Exception as e:
        print(f"❌ Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve available jobs")


@app.get("/api/jobs/client/{address}")
async def get_client_jobs(address: str = Depends(get_validated_address)):
    """Get all jobs created by a client (with full details for owner)"""
    try:
        jobs = db.get_client_jobs(address)
        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting client jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve client jobs")



@app.get("/api/jobs/worker/{worker_address}/current")
async def get_worker_active_jobs(worker_address: str):
    """Get all active jobs for a worker (LOCKED + DISPUTED)"""
    try:
        # Validate address
        if not worker_address or not worker_address.startswith('N') or len(worker_address) != 34:
            return {"jobs": []}  # Return empty instead of error
        
        jobs = db.get_worker_active_jobs(worker_address)
        return {"jobs": jobs}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting worker active jobs: {str(e)}")
        return {"jobs": []}  # Return empty on error


@app.get("/api/jobs/worker/{worker_address}/history")
async def get_worker_history(worker_address: str):
    """Get all completed jobs for a worker"""
    try:
        # Validate address
        if not worker_address or not worker_address.startswith('N') or len(worker_address) != 34:
            return {"jobs": []}  # Return empty instead of error
        
        jobs = db.get_worker_completed_jobs(worker_address)
        return {"jobs": jobs}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting worker history: {str(e)}")
        return {"jobs": []}  # Return empty on error


@app.get("/api/jobs/worker/{worker_address}/all")
async def get_all_worker_jobs(worker_address: str):
    """Get all jobs for a worker (active + completed + all statuses)"""
    try:
        # Validate address
        if not worker_address or not worker_address.startswith('N') or len(worker_address) != 34:
            return {"jobs": []}  # Return empty instead of error
        
        jobs = db.get_all_worker_jobs(worker_address)
        return {"jobs": jobs}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting all worker jobs: {str(e)}")
        return {"jobs": []}  # Return empty on error


@app.get("/api/jobs/worker/{worker_address}/stats")
async def get_worker_stats(worker_address: str):
    """Get worker statistics"""
    try:
        # Validate address format
        if not worker_address or not worker_address.startswith('N') or len(worker_address) != 34:
            return {
                "total_jobs": 0,
                "completed_jobs": 0,
                "total_earnings": 0
            }
        
        stats = db.get_worker_stats(worker_address)
        
        # Explicitly map to ensure consistent response schema
        return {
            "total_jobs": stats["total_jobs"],
            "completed_jobs": stats["completed_jobs"],
            "total_earnings": stats["total_earnings"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting worker stats: {str(e)}")
        return {
            "total_jobs": 0,
            "completed_jobs": 0,
            "total_earnings": 0
        }


@app.post("/api/jobs/{job_id}/verify-payment")
async def verify_payment_status(job_id: int):
    """
    Manually verify and fix stuck payment jobs.
    Checks blockchain status and syncs with database if needed.
    
    Use this endpoint when a job is stuck in PAYMENT_PENDING.
    """
    try:
        job = db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        print(f"\n🔍 ===== MANUAL PAYMENT VERIFICATION =====")
        print(f"   Job ID: #{job_id}")
        print(f"   DB Status: {job['status']}")
        print(f"   TX Hash: {job.get('tx_hash', 'N/A')}")
        print(f"   Worker: {job.get('worker_address', 'N/A')}")
        print(f"   Amount: {job.get('amount', 0)} GAS")
        
        # Check blockchain status
        blockchain_status = await mcp.get_job_status(job_id)
        print(f"   Blockchain Status: {blockchain_status.get('status_name')} (code: {blockchain_status.get('status_code')})")
        
        # Get detailed blockchain info
        try:
            blockchain_details = await mcp.get_job_details(job_id)
            print(f"   Blockchain Amount: {blockchain_details.get('amount_locked', 0) / 100_000_000} GAS")
            print(f"   Blockchain Worker: {blockchain_details.get('worker_address', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️  Could not fetch blockchain details: {e}")
            blockchain_details = None
        
        diagnosis = {
            "job_id": job_id,
            "db_status": job["status"],
            "blockchain_status": blockchain_status.get("status_name"),
            "blockchain_code": blockchain_status.get("status_code"),
            "tx_hash": job.get("tx_hash"),
            "explorer_url": f"https://dora.coz.io/transaction/neo3/testnet/{job.get('tx_hash')}" if job.get("tx_hash") else None,
            "synced": False,
            "action_taken": None,
            "blockchain_details": blockchain_details
        }
        
        # If blockchain shows COMPLETED but DB doesn't, sync them
        if blockchain_status.get("status_name") == "COMPLETED" and job["status"] == "PAYMENT_PENDING":
            print(f"   ✅ Blockchain shows COMPLETED but DB shows PAYMENT_PENDING. Syncing...")
            db.complete_job(job_id=job_id)
            
            # Notify worker of completion
            if job.get("worker_address"):
                await websocket_manager.broadcast_to_client(
                    job["worker_address"],
                    {
                        "type": "JOB_COMPLETED",
                        "job_id": job_id,
                        "status": "COMPLETED",
                        "message": "Payment confirmed! Job completed successfully.",
                        "tx_hash": job.get("tx_hash")
                    }
                )
            
            diagnosis["synced"] = True
            diagnosis["action_taken"] = "Successfully synced DB status to COMPLETED"
            print(f"   ✅ Job #{job_id} synced to COMPLETED")
        
        elif job["status"] == "PAYMENT_PENDING":
            # Still pending on blockchain
            if blockchain_status.get("status_name") == "LOCKED":
                diagnosis["action_taken"] = "Transaction still processing on blockchain. Payment was broadcasted but not yet confirmed."
                print(f"   ⏳ Job #{job_id} transaction still processing on blockchain")
            elif blockchain_status.get("status_name") == "OPEN":
                diagnosis["action_taken"] = "ERROR: Blockchain shows OPEN but should be LOCKED. Payment transaction may have failed."
                print(f"   ❌ Job #{job_id} has incorrect blockchain status - payment transaction may have failed!")
            else:
                diagnosis["action_taken"] = f"Unexpected blockchain status: {blockchain_status.get('status_name')}. Manual investigation needed."
                print(f"   ⚠️  Job #{job_id} has unexpected status: {blockchain_status.get('status_name')}")
        
        elif job["status"] == "COMPLETED":
            diagnosis["synced"] = True
            diagnosis["action_taken"] = "Job already completed successfully"
        
        else:
            diagnosis["action_taken"] = f"Job is in {job['status']} status, not related to payment processing"
        
        print(f"   Action: {diagnosis['action_taken']}")
        print(f"========================================\n")
        
        return diagnosis
        
    except Exception as e:
        print(f"❌ Error verifying payment for job #{job_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to verify payment: {e!s}") from e


@app.get("/api/jobs/{job_id}/status")
async def get_job_status(job_id: int):
    """
    Poll job status - checks both database and blockchain.
    Used by frontend to monitor PAYMENT_PENDING jobs.
    
    Returns:
        - db_status: Current database status
        - chain_status: Current blockchain status (if available)
        - synced: Whether DB and blockchain are in sync
    """
    try:
        # Get database status
        job = db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        db_status = job.get("status")
        response = {
            "job_id": job_id,
            "db_status": db_status,
            "tx_hash": job.get("tx_hash"),
            "updated_at": job.get("completed_at") or job.get("assigned_at") or job.get("created_at")
        }
        
        # If PAYMENT_PENDING, check blockchain status
        if db_status == "PAYMENT_PENDING":
            try:
                chain_status = await mcp.get_job_status(job_id)
                chain_status_name = chain_status.get("status_name")
                response["chain_status"] = chain_status_name
                response["synced"] = chain_status_name == db_status
                
                # If blockchain shows COMPLETED but DB doesn't, update it
                if chain_status_name == "COMPLETED":
                    print(f"🔄 Syncing job #{job_id}: blockchain is COMPLETED, updating DB")
                    db.complete_job(job_id=job_id)
                    response["db_status"] = "COMPLETED"
                    response["synced"] = True
            except Exception as e:
                print(f"⚠️  Could not fetch blockchain status for job #{job_id}: {e}")
                response["chain_status"] = "UNKNOWN"
                response["synced"] = False
        else:
            response["chain_status"] = db_status
            response["synced"] = True
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}")
async def get_job_details(job_id: int):
    """Get detailed job information"""
    try:
        job = db.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "job": job
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AI ANALYSIS (Paralegal Agent) ====================

@app.post("/api/jobs/analyze")
async def analyze_job(
    message: str = Form(...),
    reference_image: UploadFile = File(...),
    location: Optional[str] = Form(None),
    client_address: Optional[str] = Form(None),
    amount: Optional[float] = Form(None),
):
    """
    Analyze job description + image using AI agents:
    - Paralegal: Validates description, image match, and location
    - Banker: Checks if client has sufficient balance
    
    Returns structured task breakdown, validation, and balance check
    """
    try:
        image_bytes = await reference_image.read()

        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large. Maximum size is 10MB")

        if not reference_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Must be an image")

        # 1. Paralegal analysis with location
        result = await analyze_job_request(
            message, 
            image_bytes, 
            location=location,
            mime_type=reference_image.content_type
        )
        
        # 2. Balance check (if client address and amount provided)
        balance_check = None
        if client_address and amount:
            balance_result = await check_balance(client_address, amount)
            balance_check = BalanceCheck(**balance_result)

        # Determine status and message
        if result["status"] == "needs_clarification":
            message_text = "Job description is unclear. Please provide more details."
        elif result["status"] == "mismatch":
            message_text = "Image doesn't match the description. Please check and resubmit."
        else:
            # Check balance issues
            if balance_check and not balance_check.sufficient:
                if balance_check.error:
                    message_text = f"⚠️ Balance check failed: {balance_check.error}"
                else:
                    message_text = f"⚠️ Insufficient balance. You have {balance_check.balance:.2f} GAS but need {balance_check.required:.2f} GAS."
            else:
                message_text = "Job analyzed successfully! Ready to create contract."

        return JobAnalysisResponse(
            success=True,
            status=result["status"],
            data=result["data"],
            validation=ValidationResult(**result["validation"]),
            task_description=result["task_description"],
            clarifying_questions=result["clarifying_questions"],
            message=message_text,
            balance_check=balance_check,
            verification_plan=result.get("verification_plan")
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze job: {str(e)}")


@app.post("/api/ipfs/upload")
async def upload_to_ipfs_endpoint(file: UploadFile = File(...)):
    """Upload a file to IPFS and return the hash URL"""
    try:
        print(f"\n📤 ===== IPFS UPLOAD REQUEST =====")
        print(f"   Filename: {file.filename}")
        print(f"   Content-Type: {file.content_type}")
        
        file_bytes = await file.read()
        file_size_mb = len(file_bytes) / (1024 * 1024)
        
        print(f"   File size: {file_size_mb:.2f} MB ({len(file_bytes)} bytes)")
        
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
        
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
            
        # Generate a unique filename with timestamp to reduce collision probability
        extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"upload_{int(time.time())}_{os.urandom(4).hex()}.{extension}"
        print(f"   Generated filename: {filename}")
        
        # Check credentials
        print(f"   Checking 4Everland credentials...")
        bucket = os.getenv("EVERLAND_BUCKET_NAME")
        access_key = os.getenv("EVERLAND_ACCESS_KEY")
        has_secret = bool(os.getenv("EVERLAND_SECRET_KEY"))
        print(f"   Bucket: {bucket}, Access Key: {access_key[:8]}..., Secret Key: {'✓' if has_secret else '✗'}")
        
        print(f"   Calling upload_to_ipfs()...")
        ipfs_url = upload_to_ipfs(file_bytes, filename)
        
        if not ipfs_url:
            print(f"❌ IPFS upload returned None for {filename}")
            raise HTTPException(status_code=500, detail="Failed to upload to IPFS - upload_to_ipfs() returned None")
        
        print(f"✅ IPFS upload successful: {ipfs_url}")
        print(f"===================================\n")
        return {"success": True, "url": ipfs_url}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ IPFS upload exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"IPFS upload failed: {str(e)}")


# ==================== JOB CREATION ====================

@app.post("/api/jobs/create")
async def create_job(request: CreateJobRequest):
    """
    Create new job: Database + Blockchain
    
    Flow:
    1. Rate limit check
    2. Validate input (Pydantic)
    3. Create on blockchain first
    4. Insert into DB with tx_hash
    """
    try:
        # Rate limiting
        if not rate_limiter.is_allowed(request.client_address):
            raise HTTPException(status_code=429, detail="Too many requests. Please wait before creating another job.")
        
        print(f"\n📝 CREATE JOB REQUEST: Client: {request.client_address}, Amount: {request.amount} GAS")
        
        # Format details for on-chain storage (Description + Verification Plan)
        full_details = request.description + "\n\n"
        
        vp = request.verification_plan
        full_details += f"VERIFICATION PLAN:\n"
        full_details += f"Category: {vp.task_category}\n"
        full_details += f"Comparison Mode: {vp.comparison_mode}\n"
        
        if vp.success_criteria:
            full_details += "Success Criteria:\n" + "\n".join([f"  - {item}" for item in vp.success_criteria]) + "\n"
        
        if vp.rejection_criteria:
            full_details += "Rejection Criteria:\n" + "\n".join([f"  - {item}" for item in vp.rejection_criteria]) + "\n"
            
        if vp.visual_checks:
            full_details += "Visual Checks:\n" + "\n".join([f"  - {item}" for item in vp.visual_checks]) + "\n"
        
        if vp.location_required:
            full_details += "GPS Verification: Required\n"
        
        # Step 1: Create on blockchain first
        result = await mcp.create_job_on_chain(
            client_address=request.client_address,
            description=full_details,
            reference_photos=request.reference_photos,
            amount=request.amount,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Blockchain creation failed"))
        
        job_id = result["job_id"]
        tx_hash = result["tx_hash"]
        
        print(f"✅ Blockchain job created: Job ID: {job_id}, TX: {tx_hash}")
        
        # Step 2: Insert into database
        job = db.create_job(
            job_id=job_id,
            client_address=request.client_address,
            description=request.description,
            reference_photos=request.reference_photos,
            amount=request.amount,
            tx_hash=tx_hash,
            location=request.location,
            latitude=request.latitude,
            longitude=request.longitude,
            verification_plan=request.verification_plan.model_dump()
        )
        
        print("✅ Database job created successfully")
        
        return {
            "success": True,
            "message": "Job created successfully",
            "job": job,
            "tx_hash": tx_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Job creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create job. Please try again.")


# ==================== WORKER ASSIGNMENT ====================

@app.post("/api/jobs/assign")
async def assign_job(request: AssignJobRequest):
    """
    Worker claims job (auto-assign, first-come-first-served)
    
    Flow:
    1. Rate limit check
    2. Check if job is OPEN
    3. Call blockchain to assign worker
    4. Update DB status to LOCKED
    """
    try:
        # Rate limiting
        if not rate_limiter.is_allowed(request.worker_address):
            raise HTTPException(status_code=429, detail="Too many requests. Please wait before claiming another job.")
        
        # Check job exists and is OPEN
        job = db.get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job["status"] != "OPEN":
            raise HTTPException(status_code=400, detail=f"Job is {job['status']}, cannot assign")
        
        # Assign on blockchain
        result = await mcp.assign_worker_on_chain(
            job_id=request.job_id,
            worker_address=request.worker_address
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Assignment failed"))
        
        # Update database
        job = db.assign_job(request.job_id, request.worker_address)
        
        return {
            "success": True,
            "message": "Job assigned successfully",
            "job": job
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Assignment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to assign job. Please try again.")


# ==================== PROOF SUBMISSION ====================

@app.post("/api/upload/proof")
async def upload_proof_image(file: UploadFile = File(...)):
    """Upload proof photo to IPFS"""
    try:
        image_bytes = await file.read()
        ipfs_url = upload_to_ipfs(image_bytes, filename=file.filename)
        
        if not ipfs_url:
            raise HTTPException(status_code=500, detail="IPFS upload failed")
        
        return {
            "success": True,
            "ipfs_url": ipfs_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/jobs/submit")
async def submit_proof(request: SubmitProofRequest):
    """
    Submit proof and trigger AI verification
    
    Flow:
    1. Rate limit check
    2. Update DB with proof photos
    3. Call Eye Agent for verification
    4. If approved: Release funds on blockchain
    5. Update DB status
    
    Workers can resubmit for DISPUTED jobs to attempt reverification.
    """
    try:
        # Check job exists and is LOCKED or DISPUTED
        job = db.get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job["status"] not in ["LOCKED", "DISPUTED"]:
            raise HTTPException(status_code=400, detail=f"Job is {job['status']}, cannot submit proof")
        
        # Rate limiting (by worker address)
        worker_addr = job.get("worker_address")
        if worker_addr and not rate_limiter.is_allowed(worker_addr):
            raise HTTPException(status_code=429, detail="Too many proof submissions. Please wait before trying again.")
        
        # Update with proof photos
        db.submit_proof(request.job_id, request.proof_photos)
        
        print(f"🔍 Running Eye Agent verification for job #{request.job_id}...")
        
        # Run Eye Agent verification
        verification = await verify_work(
            proof_photos=request.proof_photos,
            job_id=str(request.job_id),
            worker_location=request.worker_location
        )
        
        if verification.get("verified"):
            # Approved - Release funds (broadcast transaction)
            print(f"✅ Work approved for job #{request.job_id}, releasing funds...")
            release_result = await mcp.release_funds_on_chain(job_id=request.job_id)
            
            print(f"📤 Release result: {release_result}")
            
            if release_result["success"]:
                # Update DB to PAYMENT_PENDING (not COMPLETED yet)
                tx_hash = release_result["tx_hash"]
                print(f"💰 Payment TX broadcasted: {tx_hash}")
                print(f"   Worker will receive: {release_result.get('worker_paid_gas', 'N/A')} GAS")
                print(f"   Fee collected: {release_result.get('fee_collected_gas', 'N/A')} GAS")
                print(f"   🔗 View TX: https://dora.coz.io/transaction/neo3/testnet/{tx_hash}")
                
                job = db.set_payment_pending(
                    job_id=request.job_id,
                    verification_result=verification,
                    tx_hash=tx_hash
                )
                
                # Broadcast verification success to worker and client
                verification_message = {
                    "type": "JOB_STATUS_UPDATE",
                    "job_id": request.job_id,
                    "status": "PAYMENT_PENDING",
                    "message": "✅ Work approved! Payment transaction broadcast.",
                    "tx_hash": tx_hash,
                    "verification": verification
                }
                if job.get("worker_address"):
                    await websocket_manager.broadcast_to_client(job["worker_address"], verification_message)
                if job.get("client_address"):
                    await websocket_manager.broadcast_to_client(job["client_address"], verification_message)
                
                # Start background task to monitor confirmation
                # Store reference to prevent silent exception loss
                task = asyncio.create_task(
                    monitor_transaction_confirmation(
                        job_id=request.job_id,
                        tx_hash=tx_hash
                    )
                )
                # Log any unhandled exceptions in the background task
                task.add_done_callback(
                    lambda t: print(f"❌ Background task exception: {t.exception()}") if not t.cancelled() and t.exception() else None
                )
                
                return {
                    "success": True,
                    "message": "Work approved! Payment transaction broadcast. Waiting for blockchain confirmation...",
                    "verification": verification,
                    "job": job,
                    "tx_hash": tx_hash,
                    "status": "PAYMENT_PENDING"
                }
            else:
                raise HTTPException(status_code=500, detail="Work approved but payment release failed. Please contact support.")
        else:
            # Rejected - Mark as disputed and create dispute record
            print(f"❌ Work rejected for job #{request.job_id}")
            
            # Extract AI-generated rejection reason
            ai_reason = verification.get("reason", "Work did not meet requirements")
            
            # Build detailed dispute reason from verification breakdown
            dispute_reason_parts = [ai_reason]
            
            # Add specific issues if available
            if verification.get("issues"):
                issues = verification["issues"]
                if isinstance(issues, list) and len(issues) > 0:
                    dispute_reason_parts.append("\n\nSpecific issues:")
                    for issue in issues[:3]:  # Limit to top 3 issues
                        dispute_reason_parts.append(f"• {issue}")
            
            # Add breakdown summary if available
            breakdown = verification.get("breakdown", {})
            if breakdown:
                failed_checks = []
                
                # Check each component score (lower scores indicate failures)
                # GPS Quality: max 25 points, failing if < 10
                if breakdown.get("gps_quality", 25) < 10:
                    failed_checks.append("GPS quality failed")
                
                # Visual Location: max 20 points, failing if < 8
                if breakdown.get("visual_location", 20) < 8:
                    failed_checks.append("Location verification failed")
                
                # Transformation: max 25 points, failing if < 15
                if breakdown.get("transformation", 25) < 15:
                    failed_checks.append("No visible work transformation")
                
                # Coverage: max 15 points, failing if < 7
                if breakdown.get("coverage", 15) < 7:
                    failed_checks.append("Incomplete coverage of work area")
                
                # Requirements: max 15 points, failing if < 7
                if breakdown.get("requirements", 15) < 7:
                    failed_checks.append("Requirements not met")
                
                if failed_checks:
                    dispute_reason_parts.append("\n\nFailed checks:")
                    for check in failed_checks:
                        dispute_reason_parts.append(f"• {check}")
            
            dispute_reason = "\n".join(dispute_reason_parts)
            
            job = db.dispute_job(
                job_id=request.job_id,
                reason=dispute_reason,
                ai_verdict=verification,
                raised_by="system"  # AI-triggered dispute
            )
            
            # Broadcast dispute to worker and client
            dispute_message = {
                "type": "DISPUTE_RAISED",
                "job_id": request.job_id,
                "status": "DISPUTED",
                "message": f"❌ Work rejected: {ai_reason}",
                "verification": verification
            }
            if job.get("worker_address"):
                await websocket_manager.broadcast_to_client(job["worker_address"], dispute_message)
            if job.get("client_address"):
                await websocket_manager.broadcast_to_client(job["client_address"], dispute_message)
            
            return {
                "success": False,
                "message": "Work rejected",
                "verification": verification,
                "job": job
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Submission error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit proof. Please try again.")


# ==================== EYE VERIFICATION (Direct Endpoint) ====================

@app.post("/api/eye/verify-work")
async def verify_work_endpoint(
    job_id: str = Form(...),
    reference_image_url: str = Form(...),
    proof_image: UploadFile = File(...),
    task_description: str = Form(...),
    job_location: str = Form(...),
    worker_location: str = Form(...),
    verification_plan: Optional[str] = Form(None),
):
    """
    Direct Eye Agent verification endpoint
    Verify worker's completed work using before/after photos + GPS
    """
    try:
        # Parse locations
        try:
            job_loc = json.loads(job_location)
            worker_loc = json.loads(worker_location)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid location format. Must be JSON with latitude/longitude")

        if not all(k in job_loc for k in ["latitude", "longitude"]):
            raise HTTPException(status_code=400, detail="Job location must include latitude and longitude")
        if not all(k in worker_loc for k in ["latitude", "longitude"]):
            raise HTTPException(status_code=400, detail="Worker location must include latitude and longitude")

        # Upload proof image
        proof_bytes = await proof_image.read()
        if len(proof_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Proof image too large. Maximum 10MB")

        proof_url = upload_to_ipfs(proof_bytes, f"proof_{job_id}.jpg")
        if not proof_url:
            raise HTTPException(status_code=500, detail="Failed to upload proof image to IPFS")

        # Parse verification plan
        if verification_plan:
            try:
                plan = json.loads(verification_plan)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid verification plan JSON")
        else:
            plan = {
                "task_category": "general",
                "expected_transformation": {"before": "incomplete", "after": "completed"},
                "verification_checklist": ["Work completed as described"],
            }

        # Run Eye Agent
        comparison = await eye_agent.compare_before_after(
            reference_photos=[reference_image_url],
            proof_photos=[proof_url],
            verification_plan=plan,
            job_location=job_loc,
            worker_location=worker_loc
        )
        
        verification = await eye_agent.verify_requirements(
            proof_photos=[proof_url],
            task_description=task_description,
            verification_plan=plan,
            comparison=comparison
        )
        
        decision = eye_agent.make_final_decision(
            verification_plan=plan,
            comparison=comparison,
            verification=verification
        )

        return {
            "success": True,
            "job_id": job_id,
            "verified": decision.get("verified", False),
            "verdict": decision.get("verdict", "UNKNOWN"),
            "confidence": decision.get("confidence", 0.0),
            "reason": decision.get("reason", ""),
            "location_check": {
                "distance_meters": comparison.get("gps_verification", {}).get("distance_meters"),
                "passed": comparison.get("gps_verification", {}).get("location_match", False),
                "max_allowed": 50.0
            },
            "proof_image_url": proof_url,
            "payment_recommended": decision.get("payment_recommended", False)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


# ==================== CONVERSATIONAL JOB CREATION ====================

@app.post("/api/chat/job-creation")
async def chat_job_creation(
    session_id: str = Form(...),
    message: str = Form(...),
    image_uploaded: bool = Form(False)
):
    """
    Conversational AI endpoint for job creation.
    Uses multi-turn dialogue to guide users through job posting.
    
    Args:
        session_id: Unique conversation identifier (generate on frontend)
        message: User's text input
        image_uploaded: Whether user just uploaded a reference image
    
    Returns:
        AI response with extracted data and next step guidance
    """
    try:
        # Rate limiting check
        if not rate_limiter.is_allowed(session_id):
            raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
        
        # Get conversation engine
        engine = get_conversation_engine()
        
        # Process message
        response = await engine.process_message(
            session_id=session_id,
            user_message=message,
            image_uploaded=image_uploaded
        )
        
        return {
            "success": True,
            **response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat processing failed")


@app.get("/api/chat/session/{session_id}")
async def get_chat_session(session_id: str):
    """Get current state of a conversation session"""
    try:
        engine = get_conversation_engine()
        state = engine.get_session_state(session_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session": state
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")


@app.delete("/api/chat/session/{session_id}")
async def clear_chat_session(session_id: str):
    """Clear a conversation session"""
    try:
        engine = get_conversation_engine()
        engine.clear_session(session_id)
        
        return {
            "success": True,
            "message": "Session cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear session: {str(e)}")


# ==================== TRIBUNAL / DISPUTE RESOLUTION ====================

class DisputeCreate(BaseModel):
    job_id: int = Field(..., gt=0)
    raised_by: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=10)

class DisputeResolve(BaseModel):
    dispute_id: int = Field(..., gt=0)
    approve_worker: bool = Field(..., description="True to approve worker payment, False to refund client")
    arbiter_address: Optional[str] = None  # Optional, will use AGENT_ADDR from config if not provided
    resolution_notes: str = ""

@app.get("/api/disputes")
async def get_disputes(status: Optional[str] = None):
    """
    Get all disputes, optionally filtered by status.
    
    Query params:
        status: PENDING | UNDER_REVIEW | RESOLVED (optional)
    
    Returns:
        List of disputes with job details
    """
    try:
        db = get_db()
        
        # Validate status if provided
        if status and status not in ['PENDING', 'UNDER_REVIEW', 'RESOLVED']:
            raise HTTPException(status_code=400, detail="Invalid status. Must be PENDING, UNDER_REVIEW, or RESOLVED")
        
        disputes = db.get_all_disputes(status)
        
        return {
            "success": True,
            "disputes": disputes,
            "count": len(disputes)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching disputes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch disputes: {str(e)}")

@app.get("/api/disputes/{dispute_id}")
async def get_dispute_details(dispute_id: int):
    """
    Get detailed information about a specific dispute.
    Includes full job details, AI verdict, and evidence photos.
    """
    try:
        db = get_db()
        dispute = db.get_dispute(dispute_id)
        
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")
        
        return {
            "success": True,
            "dispute": dispute
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching dispute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dispute: {str(e)}")

@app.get("/api/jobs/{job_id}/dispute")
async def get_job_dispute(job_id: int):
    """Get the most recent dispute for a specific job"""
    try:
        db = get_db()
        dispute = db.get_dispute_by_job(job_id)
        
        if not dispute:
            raise HTTPException(status_code=404, detail="No dispute found for this job")
        
        return {
            "success": True,
            "dispute": dispute
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching job dispute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch job dispute: {str(e)}")

@app.post("/api/disputes/create")
async def create_dispute(request: DisputeCreate):
    """
    Manually create a dispute.
    Used for:
    - Worker appeals after AI rejection
    - Client complaints about completed work
    - Manual escalation by either party
    """
    try:
        db = get_db()
        
        # Validate job exists
        job = db.get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Validate raised_by is either client or worker
        if request.raised_by not in [job['client_address'], job.get('worker_address')]:
            raise HTTPException(
                status_code=403, 
                detail="Only the client or assigned worker can create a dispute"
            )
        
        # Get AI verdict and evidence from job
        ai_verdict = job.get('verification_result')
        evidence_photos = job.get('proof_photos', [])
        
        dispute = db.create_dispute(
            job_id=request.job_id,
            raised_by=request.raised_by,
            reason=request.reason,
            ai_verdict=ai_verdict,
            evidence_photos=evidence_photos
        )
        
        return {
            "success": True,
            "dispute": dispute,
            "message": "Dispute created successfully. An arbiter will review your case."
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error creating dispute: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create dispute: {str(e)}")

@app.post("/api/disputes/resolve")
async def resolve_dispute(request: DisputeResolve):
    """
    Resolve a dispute by approving payment to worker or refunding client.
    
    Security: In production, this should require:
    - Arbiter role verification (JWT, OAuth, or Neo signature)
    - Multi-signature for high-value disputes
    - Rate limiting and audit logging
    
    Process:
    1. Validate dispute exists and is unresolved
    2. Call blockchain arbiter_resolve function
    3. Update database with resolution
    4. Emit notifications (future enhancement)
    """
    try:
        db = get_db()
        
        # Get dispute details
        dispute = db.get_dispute(request.dispute_id)
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")
        
        if dispute['status'] == 'RESOLVED':
            raise HTTPException(status_code=400, detail="Dispute already resolved")
        
        # Get arbiter address from request or use default from config
        arbiter_address = request.arbiter_address
        if not arbiter_address:
            # Use AGENT_ADDR as default arbiter
            arbiter_address = os.getenv('AGENT_ADDR', 'NRF64mpLJ8yExn38EjwkxzPGoJ5PLyUbtP')
        
        # Authorization: Check arbiter whitelist
        if arbiter_address not in ARBITER_WHITELIST:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized: Address not in arbiter whitelist. Only authorized arbiters can resolve disputes."
            )
        
        # Rate limiting: Check per-address rate limit for arbiter operations
        if not arbiter_rate_limiter.is_allowed(arbiter_address):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Too many resolution requests from this arbiter address."
            )
        
        # Derive resolution string from boolean
        resolution = 'APPROVED' if request.approve_worker else 'REFUNDED'
        
        # Audit log: Record resolution attempt before blockchain call
        log_arbiter_action(
            arbiter_address=arbiter_address,
            job_id=dispute['job_id'],
            dispute_id=request.dispute_id,
            decision=resolution,
            client_ip="unknown",  # In production: extract from request headers
            request_id=f"dispute_{request.dispute_id}_{int(time.time())}"
        )
        
        # Execute blockchain resolution
        neo = NeoMCP()
        
        blockchain_result = await neo.arbiter_resolve_on_chain(
            job_id=dispute['job_id'],
            approve_worker=request.approve_worker,
            arbiter_role='agent'  # Using agent role as arbiter for MVP
        )
        
        if not blockchain_result['success']:
            raise HTTPException(
                status_code=500, 
                detail=f"Blockchain resolution failed: {blockchain_result.get('error', 'Unknown error')}"
            )
        
        # Update database
        resolved_dispute = db.resolve_dispute(
            dispute_id=request.dispute_id,
            resolution=resolution,
            resolved_by=arbiter_address,
            resolution_notes=request.resolution_notes
        )
        
        return {
            "success": True,
            "message": f"Dispute resolved - {resolution}",
            "dispute": resolved_dispute,
            "transaction": blockchain_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Dispute resolution error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve dispute: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GigSmartPay Unified Backend API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
