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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
