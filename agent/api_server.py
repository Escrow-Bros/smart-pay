from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
from paralegal import analyze_job_request
from storage import upload_to_ipfs
from eye import UniversalEyeAgent

app = FastAPI(
    title="Smart-Pay API",
    description="AI-powered job validation with image verification",
    version="2.0.0"
)

eye_agent = UniversalEyeAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ValidationResult(BaseModel):
    clarity_issues: List[str]
    image_mismatch: bool
    mismatch_details: Optional[str]
    image_shows: Optional[str] = None

class JobAnalysisResponse(BaseModel):
    success: bool
    status: str
    data: dict
    validation: ValidationResult
    task_description: List[str]
    clarifying_questions: List[str]
    message: str

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Smart-Pay API",
        "version": "2.0.0",
        "endpoints": {
            "POST /api/jobs/analyze": "Analyze job with image",
            "POST /api/eye/verify": "Verify work completion",
            "POST /api/eye/verify-complete": "Upload and verify in one step",
            "GET /api/health": "Health check"
        }
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_service": "Sudo AI",
        "text_model": "gpt-4",
        "vision_model": "gpt-4o",
        "validation_mode": "strict"
    }


@app.post("/api/jobs/analyze")
async def analyze_job(
    message: str = Form(...),
    reference_image: UploadFile = File(...)
):
    try:
        image_bytes = await reference_image.read()
        
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image too large. Maximum size is 10MB")
        
        if not reference_image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Invalid file type. Must be an image")
        
        result = await analyze_job_request(message, image_bytes)
        
        if result["status"] == "needs_clarification":
            message_text = "Job description is unclear. Please provide more details."
        elif result["status"] == "mismatch":
            message_text = "Image doesn't match the description. Please check and resubmit."
        else:
            message_text = "Job analyzed successfully! Ready to create contract."
        
        return JobAnalysisResponse(
            success=True,
            status=result["status"],
            data=result["data"],
            validation=ValidationResult(**result["validation"]),
            task_description=result["task_description"],
            clarifying_questions=result["clarifying_questions"],
            message=message_text
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze job: {str(e)}")


@app.post("/api/eye/verify-work")
async def verify_work(
    job_id: str = Form(...),
    reference_image_url: str = Form(...),
    proof_image: UploadFile = File(...),
    task_description: str = Form(...),
    job_location: str = Form(...),
    worker_location: str = Form(...),
    verification_plan: Optional[str] = Form(None)
):
    """
    Verify worker's completed work using Eye Agent
    
    Required:
    - job_id: Job identifier
    - reference_image_url: IPFS URL of reference photo
    - proof_image: Worker's proof photo (file upload)
    - task_description: What needs to be done
    - job_location: Job GPS location as JSON {"latitude": float, "longitude": float}
    - worker_location: Worker GPS location as JSON {"latitude": float, "longitude": float}
    - verification_plan: Optional verification plan as JSON
    """
    try:
        # Parse locations
        try:
            job_loc = json.loads(job_location)
            worker_loc = json.loads(worker_location)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid location format. Must be JSON with latitude/longitude")
        
        # Validate location data
        if not all(k in job_loc for k in ["latitude", "longitude"]):
            raise HTTPException(status_code=400, detail="Job location must include latitude and longitude")
        
        if not all(k in worker_loc for k in ["latitude", "longitude"]):
            raise HTTPException(status_code=400, detail="Worker location must include latitude and longitude")
        
        # Upload proof image to IPFS
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
                "verification_checklist": ["Work completed as described"]
            }
        
        # Run Eye verification
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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)