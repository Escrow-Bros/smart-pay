"""
FastAPI Server for GigShield Paralegal Agent
Provides REST API endpoints for testing with Postman

Run with: uvicorn api_server:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
from paralegal import extract_contract

# Initialize FastAPI app
app = FastAPI(
    title="GigShield Paralegal API",
    description="AI-powered contract extraction for the gig economy",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class JobRequest(BaseModel):
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Clean graffiti at 555 Market St for 10 GAS"
            }
        }

class ContractData(BaseModel):
    task: Optional[str]
    location: Optional[str]
    price_amount: Optional[int]
    price_currency: Optional[str]
    missing_fields: List[str]

class JobResponse(BaseModel):
    success: bool
    data: ContractData
    ready_for_contract: bool
    message: str

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "GigShield Paralegal API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/jobs/parse": "Extract contract data from natural language",
            "GET /api/health": "Health check"
        }
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ai_service": "Sudo AI",
        "model": "gpt-4.1-mini"
    }

@app.post("/api/jobs/parse", response_model=JobResponse)
async def parse_job(request: JobRequest):
    """
    Extract structured contract data from natural language
    
    **Example Request:**
    ```json
    {
        "message": "Clean graffiti at 555 Market St for 10 GAS"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "success": true,
        "data": {
            "task": "Clean graffiti",
            "location": "555 Market St",
            "price_amount": 10,
            "price_currency": "GAS",
            "missing_fields": []
        },
        "ready_for_contract": true,
        "message": "Contract data extracted successfully"
    }
    ```
    """
    try:
        # Extract contract using the Paralegal agent
        result = await extract_contract(request.message)
        
        # Check if ready for contract creation
        ready = len(result["missing_fields"]) == 0
        
        # Generate appropriate message
        if ready:
            message = "Contract data extracted successfully. Ready to create smart contract."
        else:
            missing = ", ".join(result["missing_fields"])
            message = f"Partial data extracted. Missing: {missing}"
        
        return JobResponse(
            success=True,
            data=ContractData(**result),
            ready_for_contract=ready,
            message=message
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process request: {str(e)}"
        )

@app.post("/api/jobs/validate")
async def validate_job(request: JobRequest):
    """
    Validate a job description and return detailed feedback
    """
    try:
        result = await extract_contract(request.message)
        
        feedback = []
        if result["task"]:
            feedback.append(f"✅ Task identified: {result['task']}")
        else:
            feedback.append("❌ Task not clear. Please describe what needs to be done.")
        
        if result["location"]:
            feedback.append(f"✅ Location identified: {result['location']}")
        else:
            feedback.append("❌ Location missing. Please specify where the work should be done.")
        
        if result["price_amount"]:
            feedback.append(f"✅ Price identified: {result['price_amount']} {result['price_currency']}")
        else:
            feedback.append("❌ Price missing. Please specify how much you're willing to pay.")
        
        return {
            "success": True,
            "valid": len(result["missing_fields"]) == 0,
            "data": result,
            "feedback": feedback
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )

# Run with: uvicorn api_server:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GigShield Paralegal API Server...")
    print("📝 API Docs: http://localhost:8000/docs")
    print("🔍 Test with Postman: POST http://localhost:8000/api/jobs/parse")
    uvicorn.run(app, host="0.0.0.0", port=8000)
