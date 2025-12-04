"""Paralegal Agent - Job Analysis & Validation using AI

Uses native Sudo AI SDK for production-ready, type-safe AI integration.
Supports structured JSON output with schema validation.
"""
import json
import os
import base64
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from sudo_ai import Sudo
from backend.agent.config import AgentConfig

load_dotenv()


# ==================== AI CLIENT (MODULAR - SUDO SDK) ====================
class AIClient:
    """Modular AI client using native Sudo SDK for production use"""
    
    def __init__(self):
        self.client = Sudo(
            api_key=AgentConfig.SUDO_API_KEY,
            server_url=AgentConfig.SUDO_SERVER_URL
        )
    
    async def generate_text(
        self,
        prompt: str,
        model: str = None,
        temperature: float = None,
        max_tokens: int = 2000,
        response_format: Optional[Dict] = None
    ) -> str:
        """Generate text completion with optional structured output"""
        params = {
            "model": model or AgentConfig.TEXT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature or AgentConfig.TEMPERATURE,
            "max_completion_tokens": max_tokens  # Sudo SDK uses max_completion_tokens
        }
        
        # Add response format for structured JSON output
        if response_format:
            params["response_format"] = response_format
        
        response = await self.client.router.create_async(**params)
        return response.choices[0].message.content
    
    async def analyze_image(
        self,
        prompt: str,
        image_base64: str,
        mime_type: str = "image/jpeg",
        model: str = None,
        temperature: float = None,
        max_tokens: int = 500,
        response_format: Optional[Dict] = None
    ) -> str:
        """Analyze single image with vision model"""
        params = {
            "model": model or AgentConfig.VISION_MODEL,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        }
                    }
                ]
            }],
            "temperature": temperature or AgentConfig.TEMPERATURE,
            "max_completion_tokens": max_tokens  # Sudo SDK uses max_completion_tokens
        }
        
        if response_format:
            params["response_format"] = response_format
        
        response = await self.client.router.create_async(**params)
        return response.choices[0].message.content
    
    async def analyze_multi_image(
        self,
        content: List[Dict[str, Any]],
        model: str = None,
        temperature: float = None,
        max_tokens: int = 1000,
        response_format: Optional[Dict] = None
    ) -> str:
        """Analyze multiple images with vision model (advanced)"""
        params = {
            "model": model or AgentConfig.VISION_MODEL,
            "messages": [{"role": "user", "content": content}],
            "temperature": temperature or AgentConfig.TEMPERATURE,
            "max_completion_tokens": max_tokens  # Sudo SDK uses max_completion_tokens
        }
        
        if response_format:
            params["response_format"] = response_format
        
        response = await self.client.router.create_async(**params)
        return response.choices[0].message.content


# Global AI client instance (singleton pattern)
_ai_client = None

def get_ai_client() -> AIClient:
    """Get or create global AI client instance"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client


# ==================== JSON SCHEMAS FOR STRUCTURED OUTPUT ====================
# Sudo SDK supports json_schema response format for guaranteed valid JSON

CLARITY_SCHEMA = {
    "type": "object",
    "properties": {
        "is_clear": {"type": "boolean"},
        "issues": {"type": "array", "items": {"type": "string"}},
        "questions": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["is_clear", "issues", "questions"],
    "additionalProperties": False
}

VISION_MATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "match": {"type": "boolean"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "image_shows": {"type": "string"},
        "mismatch_reason": {"type": ["string", "null"]}
    },
    "required": ["match", "confidence", "image_shows"],
    "additionalProperties": False
}

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "task": {"type": ["string", "null"]},
        "task_description": {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "price_amount": {"type": ["number", "null"]},
        "price_currency": {"type": ["string", "null"]},
        "missing_fields": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["task", "task_description", "location", "price_amount", "price_currency", "missing_fields"],
    "additionalProperties": False
}

VERIFICATION_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "task_category": {"type": "string"},
        "expected_transformation": {
            "type": "object",
            "properties": {
                "before": {"type": "string"},
                "after": {"type": "string"}
            },
            "required": ["before", "after"]
        },
        "quality_indicators": {"type": "array", "items": {"type": "string"}},
        "verification_checklist": {"type": "array", "items": {"type": "string"}},
        "common_mistakes": {"type": "array", "items": {"type": "string"}},
        "required_evidence": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["task_category", "expected_transformation", "quality_indicators", "verification_checklist", "common_mistakes", "required_evidence"],
    "additionalProperties": False
}


class ParalegalConfig:
    """Configuration for Paralegal Agent"""
    MODEL = AgentConfig.TEXT_MODEL  # gpt-4.1
    VISION_MODEL = AgentConfig.VISION_MODEL  # gpt-4o
    TEMPERATURE = AgentConfig.TEMPERATURE  # 0.1
    VALIDATION_MODE = "strict"
    REQUIRED_FIELDS = ["task", "task_description", "location", "price_amount", "price_currency"]


async def validate_clarity(text: str, extracted_data: dict) -> dict:
    """
    Validate if job description is clear and complete.
    
    Returns:
        dict: {is_clear: bool, issues: List[str], questions: List[str]}
    """
    has_task = extracted_data.get("task") is not None
    has_description = extracted_data.get("task_description") is not None
    has_location = extracted_data.get("location") is not None
    has_price = extracted_data.get("price_amount") is not None
    
    if has_task and has_description and has_location and has_price:
        return {"is_clear": True, "issues": [], "questions": []}
    
    ai_client = get_ai_client()
    
    clarity_prompt = f"""
You are a job clarity validator. Check if CRITICAL information is missing.

Text: "{text}"
Extracted: {json.dumps(extracted_data)}

ONLY flag as unclear if:
1. Task is completely missing or incomprehensible
2. Description of what needs to be done is missing
3. Location is completely missing
4. Price is completely missing

IGNORE: Grammar mistakes, typos, awkward wording

Your response will be automatically parsed as JSON matching the schema provided.
"""
    
    try:
        # Use structured output with JSON schema validation
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "clarity_validation",
                "schema": CLARITY_SCHEMA,
                "strict": True
            }
        }
        
        content = await ai_client.generate_text(
            clarity_prompt, 
            model=ParalegalConfig.MODEL,
            response_format=response_format
        )
        
        # Schema validation guarantees valid JSON - no try/except needed
        result = json.loads(content)
        return result
        
    except Exception:
        if has_task and has_description and has_location and has_price:
            return {"is_clear": True, "issues": [], "questions": []}
        return {
            "is_clear": False,
            "issues": ["Could not validate clarity"],
            "questions": ["Please provide more details about the task and location"]
        }


async def verify_image_match(text: str, task: str, task_description: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Compare text description to reference image using Vision AI.
    
    Returns:
        dict: {match: bool, confidence: float, image_shows: str, mismatch_reason: str|None}
    """
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        print(f"🔍 Analyzing image: Type={mime_type}, Size={len(image_bytes)} bytes")
        
        ai_client = get_ai_client()
        
        vision_prompt = f"""Analyze this reference image and compare it to the job description.

JOB DESCRIPTION (Raw): "{text}"
TASK SUMMARY: "{task}"
TASK DETAILS: "{task_description}"

Your job:
1. Describe what you see in the image (be specific about objects, condition, location details)
2. Determine if the image matches the CONTEXT of the job description.
   - If the user wants to "fix" or "make" something, the image should show the BEFORE state (e.g. broken window, gravel road).
   - If the user wants to "clean" something, the image should show the DIRTY state.
   - If the user describes a location, the image should show that location.

Be LENIENT:
- "Make a tar road" + image shows gravel road → MATCH (shows the before state)
- "Fix broken window" + image shows broken window → MATCH (shows the problem)
- "Paint wall" + image shows unpainted wall → MATCH (shows the canvas)
- "Clean graffiti" + image shows graffiti → MATCH (shows the problem)

ONLY flag as MISMATCH if:
- The image shows something completely unrelated (e.g. "Fix window" but image shows a car).
- The image shows the work is ALREADY DONE (e.g. "Fix window" but image shows a perfect window).

Your response will be automatically parsed as JSON matching the schema provided."""
        
        # Use structured output with JSON schema validation
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "vision_match",
                "schema": VISION_MATCH_SCHEMA,
                "strict": True
            }
        }
        
        content = await ai_client.analyze_image(
            vision_prompt,
            image_base64,
            mime_type=mime_type,
            model=ParalegalConfig.VISION_MODEL,
            max_tokens=500,
            response_format=response_format
        )
        
        # Schema validation guarantees valid JSON
        result = json.loads(content)
        return result
        
    except Exception as e:
        return {
            "match": True,
            "confidence": 0.5,
            "image_shows": f"Vision analysis failed: {str(e)}",
            "mismatch_reason": None
        }


async def generate_verification_plan(task: str, task_description: str) -> dict:
    """Generate verification plan for Eye agent.
    
    Returns:
        dict: Verification plan with category, transformation, checklist, indicators.
    """
    ai_client = get_ai_client()
    
    plan_prompt = f"""Generate verification plan for this task:

Task: "{task}"
Full Description: "{task_description}"

The Eye agent will use this plan to verify if worker completed the task correctly.

Provide:
1. task_category: Type of work (painting, cleaning, delivery, landscaping, repair, etc.)
2. expected_transformation: What should change from before to after
3. quality_indicators: Signs of quality work
4. verification_checklist: Yes/no questions to verify completion
5. common_mistakes: Things workers might try to hide
6. required_evidence: What must be visible in proof photos

Make it specific to this exact task type.
Your response will be automatically parsed as JSON matching the schema provided.
"""
    
    try:
        # Use structured output with JSON schema validation
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "verification_plan",
                "schema": VERIFICATION_PLAN_SCHEMA,
                "strict": True
            }
        }
        
        content = await ai_client.generate_text(
            plan_prompt, 
            model=ParalegalConfig.MODEL,
            response_format=response_format
        )
        
        # Schema validation guarantees valid JSON
        return json.loads(content)
        
    except Exception:
        return {
            "task_category": "general",
            "expected_transformation": {
                "before": "work not completed",
                "after": "work completed as described"
            },
            "quality_indicators": ["work completed as described", "good quality visible in photos"],
            "verification_checklist": [
                "Is it the same location as reference?",
                "Is the work completed?",
                "Is quality acceptable?"
            ],
            "common_mistakes": ["showing different location", "hiding incomplete work"],
            "required_evidence": ["full work area visible", "same location as reference photo"]
        }


async def generate_acceptance_criteria(task: str, location: str) -> List[str]:
    """Generate strict, measurable acceptance criteria.
    
    Returns:
        List[str]: List of specific criteria strings
    """
    ai_client = get_ai_client()
    
    criteria_prompt = f"""
Generate strict acceptance criteria for this task:

Task: "{task}"
Location: "{location}"

Create 4-6 specific criteria that:
1. Define what the final result must look like
2. Specify what must be removed/fixed/cleaned/completed
3. Include photo requirements (distance, lighting, angle)
4. Are measurable and verifiable from a photo

Return ONLY a JSON array of criteria strings:
["criterion 1", "criterion 2", ...]
"""
    
    try:
        content = await ai_client.generate_text(criteria_prompt, model=ParalegalConfig.MODEL)
        content = content.replace("```json", "").replace("```", "").strip()
        criteria = json.loads(content)
        
        if isinstance(criteria, list):
            return criteria
        return ["Task must be completed as described", "Proof photo required"]
    except Exception:
        return [
            "Task must be completed as described in the job description",
            "Proof photo must clearly show the completed work",
            "Photo must be taken in good lighting conditions"
        ]


async def analyze_job_request(text: str, reference_image: bytes, location: str = None, mime_type: str = "image/jpeg") -> dict:
    """
    Intelligent job analysis with validation and criteria generation.
    
    Args:
        text: Job description from user
        reference_image: Photo of current state (REQUIRED)
        location: Job location (optional, if provided separately)
        mime_type: MIME type of the image (default: image/jpeg)
    
    Returns:
        dict: Analysis result with status, data, validation, criteria, etc.
    """
    # Step 1: Extract basic data (with location override if provided)
    extracted_data = await _extract_basic_data(text)
    if location:
        extracted_data["location"] = location
    
    # Step 2: Validate clarity
    clarity_result = await validate_clarity(text, extracted_data)
    
    if not clarity_result["is_clear"]:
        return {
            "status": "needs_clarification",
            "data": extracted_data,
            "validation": {
                "clarity_issues": clarity_result["issues"],
                "image_mismatch": False,
                "mismatch_details": None
            },
            "task_description": [extracted_data.get("task_description") or ""],
            "acceptance_criteria": [],
            "clarifying_questions": clarity_result["questions"]
        }
    
    # Step 3: Verify image matches description
    vision_result = await verify_image_match(
        text,
        extracted_data.get("task", ""),
        extracted_data.get("task_description", ""),
        reference_image,
        mime_type
    )
    
    if not vision_result["match"]:
        return {
            "status": "mismatch",
            "data": extracted_data,
            "validation": {
                "clarity_issues": [],
                "image_mismatch": True,
                "mismatch_details": vision_result["mismatch_reason"],
                "image_shows": vision_result["image_shows"]
            },
            "task_description": [extracted_data.get("task_description") or ""],
            "acceptance_criteria": [],
            "clarifying_questions": []
        }
    
    # Step 4: Generate acceptance criteria
    criteria = await generate_acceptance_criteria(
        extracted_data.get("task", ""),
        extracted_data.get("location", "")
    )
    
    # Step 5: Generate verification plan for Eye agent
    verification_plan = await generate_verification_plan(
        extracted_data.get("task", ""),
        text
    )
    
    # Step 6: Analyze reference photo features
    reference_analysis = await analyze_reference_photo(reference_image)
    
    return {
        "status": "complete",
        "data": extracted_data,
        "validation": {
            "clarity_issues": [],
            "image_mismatch": False,
            "mismatch_details": None,
            "image_shows": vision_result.get("image_shows", "")
        },
        "task_description": [extracted_data.get("task_description") or ""],
        "acceptance_criteria": criteria,
        "verification_plan": verification_plan,
        "reference_analysis": reference_analysis,
        "clarifying_questions": []
    }


async def _extract_basic_data(text: str) -> dict:
    """Extract task, description, location, price from text."""
    ai_client = get_ai_client()
    
    extraction_prompt = f"""
Extract structured data from this job description:

Text: "{text}"

Extract:
- task: Short summary (e.g. 'Fix Window')
- task_description: Clear, professional description of work needed
- location: Address or location description
- price_amount: Numeric amount
- price_currency: Currency code or null
- missing_fields: Array of fields that couldn't be extracted

Rules:
- If currency is '$', use 'USD'
- If currency missing but amount exists, use 'GAS'
- Do not invent data
- If a field is missing, set it to null AND add it to missing_fields list

Your response will be automatically parsed as JSON matching the schema provided.
"""
    
    try:
        # Use structured output with JSON schema validation
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "extraction",
                "schema": EXTRACTION_SCHEMA,
                "strict": True
            }
        }
        
        content = await ai_client.generate_text(
            extraction_prompt, 
            model=ParalegalConfig.MODEL,
            response_format=response_format
        )
        
        # Schema validation guarantees valid JSON
        return json.loads(content)
        
    except Exception as e:
        print(f"❌ Extraction error: {str(e)}")
        return {
            "task": None,
            "task_description": None,
            "location": None,
            "price_amount": None,
            "price_currency": None,
            "missing_fields": ["task", "task_description", "location", "price_amount", "price_currency"]
        }


async def analyze_reference_photo(image_bytes: bytes) -> dict:
    """
    Analyze reference photo to extract baseline features.
    
    Returns:
        dict: Placeholder for future vision analysis
    """
    return {
        "baseline_features": ["pending_vision_analysis"],
        "estimated_dimensions": "unknown",
        "color_info": {},
        "notable_objects": ["to_be_analyzed"]
    }
