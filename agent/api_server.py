"""
GigShield Paralegal API - Job Architect (Upgraded)
Handles image uploads and intelligent job validation

Run with: uvicorn api_server_v2:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from paralegal import analyze_job_request
import os
import shutil
import tempfile
# from detective import DetectiveAgent  # Skipped for now
from storage import upload_to_ipfs
from eye import UniversalEyeAgent

# Initialize FastAPI app
app = FastAPI(
    title="GigShield Paralegal API - Job Architect",
    description="AI-powered job validation with image verification",
    version="2.0.0"
)

# Initialize Agents
# detective = DetectiveAgent() # Skipped for now
eye_agent = UniversalEyeAgent()

# Request Models
class EyeVerifyRequest(BaseModel):
    proof_url: str
    reference_url: str
    task_description: str
    job_id: Optional[str] = "test_job"
    verification_plan: Optional[dict] = None  # Allow manual plan injection

# --- TASK-013: EYE AGENT ENDPOINTS ---

@app.post("/api/eye/verify")
async def verify_visuals(request: EyeVerifyRequest):
    """
    Verify work visually using Eye Agent (TASK-013)
    Compares proof URL vs reference URL
    """
    try:
        # Use provided plan OR default fallback
        verification_plan = request.verification_plan or {
            "task_category": "general",
            "expected_transformation": {
                "before": "incomplete task",
                "after": "completed task"
            },
            "verification_checklist": [
                "Is the work completed as described?",
                "Is the quality acceptable?"
            ]
        }
        
        # Run comparison
        comparison = await eye_agent.compare_before_after(
            reference_photos=[request.reference_url],
            proof_photos=[request.proof_url],
            verification_plan=verification_plan
        )
        
        # Run verification
        verification = await eye_agent.verify_requirements(
            proof_photos=[request.proof_url],
            task_description=request.task_description,
            verification_plan=verification_plan,
            comparison=comparison
        )
        
        # Make decision
        decision = eye_agent.make_final_decision(
            verification_plan,
            comparison,
            verification
        )
        
        return {
            "success": True,
            "decision": decision,
            "details": {
                "comparison": comparison,
                "verification": verification
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/eye/verify-complete")
async def verify_complete(
    reference_image: UploadFile = File(...),
    proof_image: UploadFile = File(...),
    task_description: str = Form(...),
    verification_plan_json: Optional[str] = Form(None)
):
    """
    Unified Endpoint: Uploads images AND verifies work in one step.
    
    Args:
        reference_image: File (Before)
        proof_image: File (After)
        task_description: Text
        verification_plan_json: Optional JSON string
    """
    import json
    try:
        # 1. Upload Reference Image
        ref_bytes = await reference_image.read()
        ref_filename = reference_image.filename or "ref.jpg"
        ref_url = upload_to_ipfs(ref_bytes, ref_filename)
        if not ref_url:
            raise HTTPException(status_code=500, detail="Failed to upload reference image")

        # 2. Upload Proof Image
        proof_bytes = await proof_image.read()
        proof_filename = proof_image.filename or "proof.jpg"
        proof_url = upload_to_ipfs(proof_bytes, proof_filename)
        if not proof_url:
            raise HTTPException(status_code=500, detail="Failed to upload proof image")

        # 3. Parse Verification Plan
        if verification_plan_json:
            try:
                verification_plan = json.loads(verification_plan_json)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in verification_plan_json")
        else:
            verification_plan = {
                "task_category": "general",
                "expected_transformation": {
                    "before": "incomplete task",
                    "after": "completed task"
                },
                "verification_checklist": [
                    "Is the work completed as described?",
                    "Is the quality acceptable?"
                ]
            }

        # 4. Run Verification (Reuse existing logic)
        comparison = await eye_agent.compare_before_after(
            reference_photos=[ref_url],
            proof_photos=[proof_url],
            verification_plan=verification_plan
        )
        
        verification = await eye_agent.verify_requirements(
            proof_photos=[proof_url],
            task_description=task_description,
            verification_plan=verification_plan,
            comparison=comparison
        )
        
        decision = eye_agent.make_final_decision(
            verification_plan,
            comparison,
            verification
        )
        
        return {
            "success": True,
            "decision": decision,
            "images": {
                "reference_url": ref_url,
                "proof_url": proof_url
            },
            "details": {
                "comparison": comparison,
                "verification": verification
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response Models
class ValidationResult(BaseModel):
    clarity_issues: List[str]
    image_mismatch: bool
    mismatch_details: Optional[str]
    image_shows: Optional[str] = None

class JobAnalysisResponse(BaseModel):
    success: bool
    status: str  # "complete" | "needs_clarification" | "mismatch"
    data: dict
    validation: ValidationResult
    acceptance_criteria: List[str]
    clarifying_questions: List[str]
    message: str

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "GigShield Paralegal API - Job Architect",
        "version": "2.0.0",
        "features": [
            "Clarity validation",
            "Image verification (Sodu Vision)",
            "Acceptance criteria generation"
        ],
        "endpoints": {
            "POST /api/jobs/analyze": "Analyze job with image (REQUIRED)",
            "GET /api/health": "Health check"
        }
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ai_service": "Sudo AI",
        "text_model": "gpt-4.1-mini",
        "vision_model": "gpt-4-vision",
        "validation_mode": "strict"
    }

@app.post("/api/jobs/analyze")
async def analyze_job(
    message: str = Form(..., description="Job description text"),
    reference_image: UploadFile = File(..., description="Photo of current state (REQUIRED)")
):
    """
    Intelligent job analysis with validation and criteria generation
    
    **Required:**
    - message: Job description (e.g., "Clean graffiti at 555 Market St for 10 GAS")
    - reference_image: Photo showing current state
    
    **Returns:**
    - status: "complete" | "needs_clarification" | "mismatch"
    - data: Extracted task, location, price
    - validation: Clarity and image verification results
    - acceptance_criteria: Auto-generated success criteria
    - clarifying_questions: Questions if description is vague
    
    **Validation Mode:** STRICT (blocks submission if validation fails)
    """
    try:
        # Read image bytes
        image_bytes = await reference_image.read()
        
        # Validate image size (max 10MB)
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image too large. Maximum size is 10MB"
            )
        
        # Validate image type
        if not reference_image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Must be an image (jpg, png, etc.)"
            )
        
        # Analyze job request
        result = await analyze_job_request(message, image_bytes)
        
        # Generate response message
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
            acceptance_criteria=result["acceptance_criteria"],
            clarifying_questions=result["clarifying_questions"],
            message=message_text
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze job: {str(e)}"
        )

# Run server
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GigShield Paralegal API - Job Architect...")
    print("📝 API Docs: http://localhost:8000/docs")
    print("🔍 Test with Postman: POST http://localhost:8000/api/jobs/analyze")
    print("⚠️  Reference image is REQUIRED")
    uvicorn.run(app, host="0.0.0.0", port=8000)
