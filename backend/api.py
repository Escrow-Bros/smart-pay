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
import os

# Internal imports
from backend.database import get_db
from backend.agent.paralegal import analyze_job_request
from backend.agent.eye import UniversalEyeAgent, verify_work
from backend.agent.storage import upload_to_ipfs
from backend.agent.banker import check_balance
from src.neo_mcp import NeoMCP
from scripts.check_balances import get_gas_balance


# ==================== MODELS ====================

class CreateJobRequest(BaseModel):
    client_address: str
    description: str
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    reference_photos: List[str]  # IPFS URLs
    verification_plan: dict
    amount: float

class AssignJobRequest(BaseModel):
    job_id: int
    worker_address: str

class SubmitProofRequest(BaseModel):
    job_id: int
    proof_photos: List[str]  # IPFS URLs
    worker_location: Optional[Dict[str, float]] = None  # {lat: float, lng: float, accuracy: float}

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
    title="GigShield Unified Backend API",
    description="Complete backend for GigShield - Database + Blockchain + AI",
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
eye_agent = UniversalEyeAgent()


# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "GigShield Unified Backend API",
        "version": "4.0.0",
        "components": {
            "database": "SQLite",
            "blockchain": "Neo N3",
            "ai_agents": ["Paralegal", "Eye", "Banker"]
        },
        "endpoints": {
            "GET /api/health": "Detailed health check",
            "GET /api/wallet/balance/{address}": "Get wallet balance",
            "GET /api/jobs/available": "List available jobs",
            "GET /api/jobs/client/{address}": "Get client's jobs",
            "GET /api/jobs/worker/{address}": "Get worker's jobs",
            "GET /api/jobs/{job_id}": "Get job details",
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


# ==================== JOB LISTING ENDPOINTS ====================

@app.get("/api/jobs/available")
async def list_available_jobs():
    """Get all open jobs (filtered for worker public view)"""
    try:
        jobs = db.get_available_jobs()
        # Filter sensitive data for public worker view
        filtered_jobs = [db._filter_for_worker_view(job) for job in jobs]
        return {
            "success": True,
            "count": len(filtered_jobs),
            "jobs": filtered_jobs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/client/{address}")
async def get_client_jobs(address: str):
    """Get all jobs created by a client (with full details for owner)"""
    try:
        jobs = db.get_client_jobs(address)
        # Filter to show summary verification only
        filtered_jobs = [db._filter_for_client_view(job) for job in jobs]
        return {
            "success": True,
            "count": len(filtered_jobs),
            "jobs": filtered_jobs
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
        file_bytes = await file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
            
        # Generate a unique filename
        filename = f"upload_{os.urandom(4).hex()}.{file.filename.split('.')[-1]}"
        
        ipfs_url = upload_to_ipfs(file_bytes, filename)
        if not ipfs_url:
            raise HTTPException(status_code=500, detail="Failed to upload to IPFS")
            
        return {"success": True, "url": ipfs_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IPFS upload failed: {str(e)}")


# ==================== JOB CREATION ====================

@app.post("/api/jobs/create")
async def create_job(request: CreateJobRequest):
    """
    Create new job: Database + Blockchain
    
    Flow:
    1. Create on blockchain first
    2. Insert into DB with tx_hash
    """
    try:
        print("\n📝 CREATE JOB REQUEST:")
        print(f"   Client: {request.client_address}")
        print(f"   Description: {request.description[:100]}...")
        print(f"   Location: {request.location}")
        print(f"   Coordinates: ({request.latitude}, {request.longitude})")
        print(f"   Amount: {request.amount} GAS")
        print(f"   Reference Photos: {len(request.reference_photos)} images")
        
        # STRICT VALIDATION: Ensure all verification fields are present
        if not request.description or len(request.description.strip()) < 10:
            raise HTTPException(status_code=400, detail="Job description is required and must be at least 10 characters.")
            
        if not request.reference_photos:
            raise HTTPException(status_code=400, detail="At least one reference photo is required for verification.")
            
        if not request.verification_plan:
            raise HTTPException(status_code=400, detail="Verification plan is required. Please ensure AI analysis completed successfully.")
        
        # Format details for on-chain storage (Description + Verification Plan)
        # This ensures the Eye agent has all context on-chain
        full_details = request.description + "\n\n"
        
        vp = request.verification_plan
        full_details += f"VERIFICATION PLAN:\n"
        full_details += f"Category: {vp.get('task_category', 'General')}\n"
        
        if 'expected_transformation' in vp:
            et = vp['expected_transformation']
            full_details += f"Transformation:\n  Before: {et.get('before', 'N/A')}\n  After: {et.get('after', 'N/A')}\n"
            
        if 'verification_checklist' in vp:
            full_details += "Checklist:\n" + "\n".join([f"  - {item}" for item in vp['verification_checklist']]) + "\n"
            
        if 'quality_indicators' in vp:
            full_details += "Quality Indicators:\n" + "\n".join([f"  - {item}" for item in vp['quality_indicators']]) + "\n"
        
        # Step 1: Create on blockchain first
        result = await mcp.create_job_on_chain(
            client_address=request.client_address,
            description=full_details,
            reference_photos=request.reference_photos,
            amount=request.amount
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Blockchain creation failed"))
        
        job_id = result["job_id"]
        tx_hash = result["tx_hash"]
        
        print(f"\n✅ Blockchain job created:")
        print(f"   Job ID: {job_id} (Type: {type(job_id)})")
        print(f"   TX Hash: {tx_hash}")
        
        # Step 2: Insert into database
        job = db.create_job(
            job_id=job_id,
            client_address=request.client_address,
            description=request.description,  # Store original description in DB
            reference_photos=request.reference_photos,
            amount=request.amount,
            tx_hash=tx_hash,
            location=request.location,
            latitude=request.latitude,
            longitude=request.longitude,
            verification_plan=request.verification_plan
        )
        
        print(f"\n✅ Database job created successfully")
        print(f"   Job Object: {job}")
        
        return {
            "success": True,
            "message": "Job created successfully",
            "job": job,
            "tx_hash": tx_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ Job creation error: {str(e)}")
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


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GigShield Unified Backend API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
