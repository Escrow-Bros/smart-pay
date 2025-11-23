"""
GigShield API Server
REST API for testing Paralegal and Eye agents via Postman

Run: uvicorn api_server:app --reload --port 8000
Test: http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.paralegal import analyze_job_request
from agent.eye import verify_work

# Initialize FastAPI
app = FastAPI(
    title="GigShield API",
    description="Test Paralegal and Eye agents via REST API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated contract storage (replace with real Neo N3 later)
JOB_DATABASE = {}

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class JobCreateResponse(BaseModel):
    success: bool
    status: str
    job_id: Optional[str] = None
    data: dict
    verification_plan: dict
    acceptance_criteria: List[str]
    clarifying_questions: List[str]
    message: str

class VerifyWorkRequest(BaseModel):
    job_id: str
    proof_photos: List[str]
    worker_id: Optional[str] = None

class VerifyWorkResponse(BaseModel):
    success: bool
    verified: bool
    confidence: float
    reason: str
    category: str
    quality_score: Optional[float] = None
    issues: Optional[str] = None
    suggestions: Optional[List[str]] = None

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API info"""
    return {
        "service": "GigShield API",
        "version": "1.0.0",
        "status": "online",
        "agents": {
            "paralegal": "Job validation & plan generation",
            "eye": "Work verification with vision"
        },
        "endpoints": {
            "POST /api/jobs/create": "Create job with Paralegal",
            "POST /api/jobs/verify": "Verify work with Eye",
            "GET /api/jobs/{job_id}": "Get job details",
            "GET /api/health": "Health check",
            "GET /docs": "API documentation (Swagger)"
        },
        "docs": "http://localhost:8000/docs"
    }

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "paralegal": "ready",
        "eye": "ready",
        "storage": "ready",
        "ai_provider": "Sudo AI",
        "vision_model": "GPT-4V (gpt-4o)"
    }

@app.post("/api/jobs/create", response_model=JobCreateResponse)
async def create_job(
    description: str = Form(..., description="Job description (e.g., 'Paint wall blue at 123 Main for 50 GAS')"),
    reference_image: UploadFile = File(..., description="Photo of current state (BEFORE)")
):
    """
    Create a job using Paralegal agent
    
    **Paralegal validates:**
    - Extracts task, location, price
    - Validates clarity
    - Verifies image matches description (GPT-4V)
    - Generates verification plan
    - Creates acceptance criteria
    
    **Returns:**
    - Job ID (if validation passed)
    - Verification plan (for Eye agent)
    - Status and any clarifying questions
    """
    try:
        # Read image
        image_bytes = await reference_image.read()
        
        # Validate image size
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "Image too large (max 10MB)")
        
        # Call Paralegal agent
        result = await analyze_job_request(description, image_bytes)
        
        # Generate response based on status
        if result["status"] == "complete":
            # Create job in database
            job_id = f"job_{len(JOB_DATABASE) + 1:03d}"
            
            JOB_DATABASE[job_id] = {
                "job_id": job_id,
                "description": description,
                "reference_photos": [f"ipfs://test/{job_id}_ref.jpg"],  # Mock IPFS
                "verification_plan": result["verification_plan"],
                "acceptance_criteria": result["acceptance_criteria"],
                "reference_analysis": result["reference_analysis"],
                "data": result["data"],
                "status": "OPEN",
                "client": "0xClient...",  # Mock address
                "amount": result["data"].get("price_amount"),
                "currency": result["data"].get("price_currency")
            }
            
            return JobCreateResponse(
                success=True,
                status=result["status"],
                job_id=job_id,
                data=result["data"],
                verification_plan=result["verification_plan"],
                acceptance_criteria=result["acceptance_criteria"],
                clarifying_questions=[],
                message=f"Job created successfully! Job ID: {job_id}"
            )
            
        elif result["status"] == "needs_clarification":
            return JobCreateResponse(
                success=False,
                status=result["status"],
                job_id=None,
                data=result["data"],
                verification_plan={},
                acceptance_criteria=[],
                clarifying_questions=result["clarifying_questions"],
                message="Job description needs clarification"
            )
            
        elif result["status"] == "mismatch":
            return JobCreateResponse(
                success=False,
                status=result["status"],
                job_id=None,
                data=result["data"],
                verification_plan={},
                acceptance_criteria=[],
                clarifying_questions=[],
                message=f"Image mismatch: {result['validation'].get('mismatch_details')}"
            )
            
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

@app.post("/api/jobs/verify", response_model=VerifyWorkResponse)
async def verify_job(request: VerifyWorkRequest):
    """
    Verify work using Eye agent
    
    **Eye verifies:**
    - Compares before/after photos (GPT-4V)
    - Checks location match (fraud detection)
    - Verifies quality requirements
    - Makes approval/rejection decision
    
    **Request body:**
    ```json
    {
        "job_id": "job_001",
        "proof_photos": ["ipfs://Qm.../proof.jpg"],
        "worker_id": "0xWorker..." (optional)
    }
    ```
    
    **Returns:**
    - verified: true/false
    - confidence: 0.0-1.0
    - reason: explanation
    - category: APPROVED/REJECTED/etc
    """
    try:
        # Check job exists
        if request.job_id not in JOB_DATABASE:
            raise HTTPException(404, f"Job {request.job_id} not found")
        
        # Update job status
        JOB_DATABASE[request.job_id]['status'] = 'VERIFYING'
        if request.worker_id:
            JOB_DATABASE[request.job_id]['worker'] = request.worker_id
        
        # Temporarily patch Eye agent to use our database
        import agent.eye as eye_module
        original_placeholder = eye_module.UniversalEyeAgent._get_job_data_placeholder
        
        def mock_get_job(self, job_id):
            if job_id in JOB_DATABASE:
                return JOB_DATABASE[job_id]
            return original_placeholder(self, job_id)
        
        eye_module.UniversalEyeAgent._get_job_data_placeholder = mock_get_job
        
        # Call Eye agent
        verdict = await verify_work(
            proof_photos=request.proof_photos,
            job_id=request.job_id,
            worker_id=request.worker_id
        )
        
        # Restore original
        eye_module.UniversalEyeAgent._get_job_data_placeholder = original_placeholder
        
        # Update job status
        if verdict["verified"]:
            JOB_DATABASE[request.job_id]['status'] = 'COMPLETED'
        else:
            JOB_DATABASE[request.job_id]['status'] = 'REJECTED'
        
        return VerifyWorkResponse(
            success=True,
            verified=verdict["verified"],
            confidence=verdict["confidence"],
            reason=verdict["reason"],
            category=verdict["category"],
            quality_score=verdict.get("quality_score"),
            issues=verdict.get("issues"),
            suggestions=verdict.get("suggestions")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Verification error: {str(e)}")

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job details"""
    if job_id not in JOB_DATABASE:
        raise HTTPException(404, f"Job {job_id} not found")
    
    return {
        "success": True,
        "job": JOB_DATABASE[job_id]
    }

@app.get("/api/jobs")
async def list_jobs():
    """List all jobs"""
    return {
        "success": True,
        "count": len(JOB_DATABASE),
        "jobs": list(JOB_DATABASE.values())
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🛡️  GIGSHIELD API SERVER")
    print("=" * 70)
    print()
    print("🚀 Starting server...")
    print()
    print("📡 API Endpoints:")
    print("   - POST http://localhost:8000/api/jobs/create   (Test Paralegal)")
    print("   - POST http://localhost:8000/api/jobs/verify   (Test Eye)")
    print("   - GET  http://localhost:8000/api/jobs          (List jobs)")
    print()
    print("📖 Interactive Docs:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print()
    print("🔧 Test with Postman:")
    print("   1. Import collection from /postman folder")
    print("   2. Or manually create requests to endpoints above")
    print()
    print("=" * 70)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

