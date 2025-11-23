import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import json

# Internal imports
from backend.database import get_db
from agent.paralegal import analyze_job_request
from agent.eye import verify_work
from agent.storage import upload_to_ipfs
from src.neo_mcp import NeoMCP
from scripts.check_balances import get_gas_balance


# ==================== MODELS ====================

class CreateJobRequest(BaseModel):
    client_address: str
    description: str
    reference_photos: List[str]  # IPFS URLs
    amount: float

class AssignJobRequest(BaseModel):
    job_id: int
    worker_address: str

class SubmitProofRequest(BaseModel):
    job_id: int
    proof_photos: List[str]  # IPFS URLs


# ==================== APP SETUP ====================

app = FastAPI(
    title="GigShield Backend API",
    description="Complete backend for GigShield - Database + Blockchain + AI",
    version="3.0.0"
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


# ==================== WALLET ENDPOINTS ====================

@app.get("/api/wallet/balance/{address}")
async def get_wallet_balance(address: str):
    """
    Get GAS balance for Neo N3 address
    Uses check_balances.py logic
    """
    try:
        import os
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


# ==================== JOB LISTING ENDPOINTS ====================

@app.get("/api/jobs/available")
async def list_available_jobs():
    """Get all open jobs (fast query from DB)"""
    try:
        jobs = db.get_available_jobs()
        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/client/{address}")
async def get_client_jobs(address: str):
    """Get all jobs created by a client"""
    try:
        jobs = db.get_client_jobs(address)
        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/worker/{address}")
async def get_worker_jobs(address: str):
    """Get all jobs for a worker (history + current)"""
    try:
        current = db.get_worker_current_job(address)
        history = db.get_worker_jobs(address)
        stats = db.get_worker_stats(address)
        
        return {
            "success": True,
            "current_job": current,
            "history": history,
            "stats": stats
        }
    except Exception as e:
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


# ==================== JOB CREATION ====================

@app.post("/api/jobs/create")
async def create_job(request: CreateJobRequest):
    """
    Create new job: Database + Blockchain
    
    Flow:
    1. Insert into DB (status: OPEN)
    2. Create on blockchain
    3. Update DB with tx_hash
    """
    try:
        # Step 1: Create on blockchain first
        result = await mcp.create_job_on_chain(
            client_address=request.client_address,
            description=request.description,
            reference_photos=request.reference_photos,
            amount=request.amount
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Blockchain creation failed"))
        
        job_id = result["job_id"]
        tx_hash = result["tx_hash"]
        
        # Step 2: Insert into database
        job = db.create_job(
            job_id=job_id,
            client_address=request.client_address,
            description=request.description,
            reference_photos=request.reference_photos,
            amount=request.amount,
            tx_hash=tx_hash
        )
        
        return {
            "success": True,
            "message": "Job created successfully",
            "job": job,
            "tx_hash": tx_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job creation failed: {str(e)}")


# ==================== WORKER ASSIGNMENT ====================

@app.post("/api/jobs/assign")
async def assign_job(request: AssignJobRequest):
    """
    Worker claims job (auto-assign, first-come-first-served)
    
    Flow:
    1. Check if job is OPEN
    2. Call blockchain to assign worker
    3. Update DB status to LOCKED
    """
    try:
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
        raise HTTPException(status_code=500, detail=f"Assignment failed: {str(e)}")


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
    1. Update DB with proof photos
    2. Call Eye Agent for verification
    3. If approved: Release funds on blockchain
    4. Update DB status
    """
    try:
        # Check job exists and is LOCKED
        job = db.get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job["status"] != "LOCKED":
            raise HTTPException(status_code=400, detail=f"Job is {job['status']}, cannot submit proof")
        
        # Update with proof photos
        db.submit_proof(request.job_id, request.proof_photos)
        
        # Run Eye Agent verification
        verification = await verify_work(
            proof_photos=request.proof_photos,
            job_id=str(request.job_id)
        )
        
        if verification.get("verified"):
            # Approved - Release funds
            release_result = await mcp.release_funds_on_chain(job_id=request.job_id)
            
            if release_result["success"]:
                # Update DB to COMPLETED
                job = db.complete_job(
                    job_id=request.job_id,
                    verification_result=verification,
                    tx_hash=release_result["tx_hash"]
                )
                
                return {
                    "success": True,
                    "message": "Work approved! Payment released.",
                    "verification": verification,
                    "job": job,
                    "tx_hash": release_result["tx_hash"]
                }
            else:
                raise HTTPException(status_code=500, detail="Payment release failed")
        else:
            # Rejected - Mark as disputed or allow retry
            job = db.dispute_job(
                job_id=request.job_id,
                reason=verification.get("reason", "Work did not meet requirements")
            )
            
            return {
                "success": False,
                "message": "Work rejected",
                "verification": verification,
                "job": job
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")


# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "GigShield Backend API",
        "version": "3.0.0",
        "components": {
            "database": "SQLite",
            "blockchain": "Neo N3",
            "ai_agents": ["Paralegal", "Eye"]
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
            "ai_service": "sudo-ai"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
