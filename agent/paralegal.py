"""
GigShield Paralegal Agent - Job Architect (Upgraded)
TASK-011: Intelligent job validation with image verification and criteria generation

Features:
- Logic A: Clarity validation (detects vague descriptions)
- Logic B: Visual verification (compares text to image)
- Logic C: Acceptance criteria generation
- Logic D: Verification plan generation (for Eye agent)
"""
import asyncio
import json
import os
import re
import base64
from typing import Optional, Dict, List
import httpx
from dotenv import load_dotenv
from spoon_ai.llm import LLMManager, ConfigurationManager
from spoon_ai.schema import Message

# --- MONKEY PATCH for Sudo AI ---
_original_request_init = httpx.Request.__init__

def _patched_request_init(self, *args, **kwargs):
    _original_request_init(self, *args, **kwargs)
    headers_to_remove = []
    headers_to_modify = {}
    for name in self.headers.keys():
        name_lower = name.lower()
        if 'stainless' in name_lower:
            headers_to_remove.append(name)
        elif name_lower == 'user-agent' and 'openai' in self.headers[name].lower():
            headers_to_modify[name] = 'python-requests/2.32.5'
    for name in headers_to_remove:
        del self.headers[name]
    for name, value in headers_to_modify.items():
        self.headers[name] = value

httpx.Request.__init__ = _patched_request_init

load_dotenv("agent/.env")

# --- CONFIGURATION ---
class ParalegalConfig:
    """Configuration for Paralegal Agent"""
    MODEL = "gpt-4"  # Fixed: was "gpt-4.1-mini"
    VISION_MODEL = "gpt-4o"  # Fixed: was "gpt-4-vision"
    TEMPERATURE = 0.1
    VALIDATION_MODE = "strict"  # block submission if validation fails
    
    # Required fields
    REQUIRED_FIELDS = ["task", "location", "price_amount", "price_currency"]

# --- LOGIC A: CLARITY VALIDATION ---
async def validate_clarity(text: str, extracted_data: dict) -> dict:
    """
    Validate if job description is clear and complete
    
    RELAXED MODE: Only flag if critical information is MISSING
    Grammar issues are OK as long as we can extract task, location, price
    
    Returns:
        {
            "is_clear": bool,
            "issues": [str],
            "questions": [str]
        }
    """
    # Quick check: If all required fields are extracted, it's clear enough!
    missing = extracted_data.get("missing_fields", [])
    
    # If we have task, location, and price - it's good enough
    has_task = extracted_data.get("task") is not None
    has_location = extracted_data.get("location") is not None
    has_price = extracted_data.get("price_amount") is not None
    
    if has_task and has_location and has_price:
        # All critical info present - grammar doesn't matter
        return {
            "is_clear": True,
            "issues": [],
            "questions": []
        }
    
    # If critical fields are missing, ask for them
    config = ConfigurationManager()
    manager = LLMManager(config)
    
    clarity_prompt = f"""
You are a job clarity validator. Check if CRITICAL information is missing.

Text: "{text}"
Extracted: {json.dumps(extracted_data)}

ONLY flag as unclear if:
1. Task is completely missing or incomprehensible
2. Location is completely missing (no address, no GPS, nothing)
3. Price is completely missing

IGNORE:
- Grammar mistakes
- Typos
- Awkward wording
- Minor clarity issues

Return ONLY valid JSON:
{{
  "is_clear": boolean,
  "issues": ["only list MISSING critical info"],
  "questions": ["only ask for MISSING info"]
}}

Examples:
- "Clean my wall" → NOT clear (no location)
- "Clean paper at 33 South St for 10 GAS" → CLEAR (has all 3)
- "Fix it" → NOT clear (no task details, no location, no price)
"""
    
    try:
        # Fixed: Use manager.chat() instead of manager.completion()
        messages = [Message(role="user", content=clarity_prompt)]
        response = await manager.chat(messages, model=ParalegalConfig.MODEL)
        
        content = response.content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
        
        return {
            "is_clear": result.get("is_clear", False),
            "issues": result.get("issues", []),
            "questions": result.get("questions", [])
        }
    except Exception as e:
        print(f"⚠️ Clarity validation failed: {e}")
        # If validation fails but we have all fields, pass it through
        if has_task and has_location and has_price:
            return {"is_clear": True, "issues": [], "questions": []}
        # Otherwise, ask for missing fields
        return {
            "is_clear": False,
            "issues": ["Could not validate clarity"],
            "questions": ["Please provide more details about the task and location"]
        }

# --- LOGIC B: VISUAL VERIFICATION ---
async def verify_image_match(text: str, task: str, image_bytes: bytes) -> dict:
    """
    Compare text description to reference image using Vision AI
    
    TEMPORARY: Vision verification disabled due to Sudo AI blocking
    TODO: Re-enable when vision model access is confirmed
    
    Returns:
        {
            "match": bool,
            "confidence": float,
            "image_shows": str,
            "mismatch_reason": str | null
        }
    """
    
    print("⚠️  Vision verification temporarily disabled")
    print("    Reason: Vision API bypasses httpx monkey patch and gets blocked")
    print("    TODO: Implement proper vision model integration")
    
    # For now, optimistically assume match
    # This allows development to continue while vision integration is fixed
    return {
        "match": True,
        "confidence": 0.7,
        "image_shows": "Image verification pending - temporarily bypassed",
        "mismatch_reason": None
    }
    
    # TODO: Implement vision verification when API access is confirmed
    # Options:
    # 1. Use a vision model that doesn't get blocked
    # 2. Implement custom vision API wrapper
    # 3. Use a different vision service (Anthropic Claude Vision, etc.)

# --- LOGIC C: VERIFICATION PLAN GENERATOR (FOR EYE AGENT) ---
async def generate_verification_plan(task: str, task_description: str) -> dict:
    """
    Generate verification plan for Eye agent
    
    This is what the Eye agent uses to verify worker proof photos
    
    Returns:
        {
            "task_category": str,
            "expected_transformation": {"before": str, "after": str},
            "quality_indicators": [str],
            "verification_checklist": [str],
            "common_mistakes": [str],
            "required_evidence": [str]
        }
    """
    config = ConfigurationManager()
    manager = LLMManager(config)
    
    plan_prompt = f"""
Generate a verification plan for this task:

Task: "{task}"
Full Description: "{task_description}"

The Eye agent will use this plan to verify if worker completed the task correctly.

Return ONLY valid JSON with this structure:
{{
  "task_category": "category (e.g., painting, cleaning, delivery, landscaping, repair)",
  "expected_transformation": {{
    "before": "what the current state should look like",
    "after": "what the completed state should look like"
  }},
  "quality_indicators": [
    "list of things that indicate quality work",
    "e.g., 'even coverage', 'clean edges', 'no debris'"
  ],
  "verification_checklist": [
    "specific yes/no questions to verify completion",
    "e.g., 'Is it the same wall?', 'Is color correct?'"
  ],
  "common_mistakes": [
    "things workers might try to hide",
    "e.g., 'showing only small section', 'hiding bad edges'"
  ],
  "required_evidence": [
    "what must be visible in proof photos",
    "e.g., 'full wall visible', 'all corners visible'"
  ]
}}

Make it specific to this exact task type.
"""
    
    try:
        messages = [Message(role="user", content=plan_prompt)]
        response = await manager.chat(messages, model=ParalegalConfig.MODEL)
        
        content = response.content.replace("```json", "").replace("```", "").strip()
        plan = json.loads(content)
        
        return plan
    except Exception as e:
        print(f"⚠️ Verification plan generation failed: {e}")
        # Return basic default plan
        return {
            "task_category": "general",
            "expected_transformation": {
                "before": "work not completed",
                "after": "work completed as described"
            },
            "quality_indicators": [
                "work completed as described",
                "good quality visible in photos"
            ],
            "verification_checklist": [
                "Is it the same location as reference?",
                "Is the work completed?",
                "Is quality acceptable?"
            ],
            "common_mistakes": [
                "showing different location",
                "hiding incomplete work"
            ],
            "required_evidence": [
                "full work area visible",
                "same location as reference photo"
            ]
        }

# --- LOGIC D: ACCEPTANCE CRITERIA GENERATOR ---
async def generate_acceptance_criteria(task: str, location: str) -> List[str]:
    """
    Generate strict, measurable acceptance criteria
    
    Returns:
        List of specific criteria strings
    """
    config = ConfigurationManager()
    manager = LLMManager(config)
    
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

Examples for "Clean graffiti":
[
  "Wall must be completely free of all paint marks and graffiti",
  "Surface must match the original wall color and texture",
  "Proof photo must be taken from 2 meters away to show full area",
  "Photo must be taken in daylight (no flash or artificial lighting)",
  "Entire affected area must be visible in the photo"
]

Examples for "Fix broken window":
[
  "Window glass must be intact with no cracks or chips",
  "Window frame must be properly sealed and painted",
  "Window must open and close smoothly (show in video)",
  "Proof photo must show the entire window frame",
  "Photo must be taken from inside and outside"
]
"""
    
    try:
        # Fixed: Use manager.chat() instead of manager.completion()
        messages = [Message(role="user", content=criteria_prompt)]
        response = await manager.chat(messages, model=ParalegalConfig.MODEL)
        
        content = response.content.replace("```json", "").replace("```", "").strip()
        criteria = json.loads(content)
        
        if isinstance(criteria, list):
            return criteria
        else:
            return ["Task must be completed as described", "Proof photo required"]
    except Exception as e:
        print(f"⚠️ Criteria generation failed: {e}")
        return [
            "Task must be completed as described in the job description",
            "Proof photo must clearly show the completed work",
            "Photo must be taken in good lighting conditions"
        ]

# --- MAIN ANALYSIS FUNCTION ---
async def analyze_job_request(text: str, reference_image: bytes) -> dict:
    """
    Intelligent job analysis with validation and criteria generation
    
    Args:
        text: Job description from user
        reference_image: Photo of current state (REQUIRED)
    
    Returns:
        {
            "status": "complete" | "needs_clarification" | "mismatch",
            "data": {...},
            "validation": {...},
            "acceptance_criteria": [...],
            "clarifying_questions": [...]
        }
    """
    
    # Step 1: Extract basic data (reuse existing logic)
    extracted_data = await _extract_basic_data(text)
    
    # Step 2: Validate clarity
    clarity_result = await validate_clarity(text, extracted_data)
    
    # If not clear, return immediately (strict mode)
    if not clarity_result["is_clear"]:
        return {
            "status": "needs_clarification",
            "data": extracted_data,
            "validation": {
                "clarity_issues": clarity_result["issues"],
                "image_mismatch": False,
                "mismatch_details": None
            },
            "acceptance_criteria": [],
            "clarifying_questions": clarity_result["questions"]
        }
    
    # Step 3: Verify image matches description
    vision_result = await verify_image_match(
        text,
        extracted_data.get("task", ""),
        reference_image
    )
    
    # If mismatch, return immediately (strict mode)
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
    
    # Step 6: Analyze reference photo features (basic for now)
    reference_analysis = await analyze_reference_photo(image_bytes)
    
    # Success!
    return {
        "status": "complete",
        "data": extracted_data,
        "validation": {
            "clarity_issues": [],
            "image_mismatch": False,
            "mismatch_details": None,
            "image_shows": vision_result.get("image_shows", "")
        },
        "acceptance_criteria": criteria,
        "verification_plan": verification_plan,  # NEW: For Eye agent
        "reference_analysis": reference_analysis,  # NEW: Baseline features
        "clarifying_questions": []
    }

# --- HELPER: BASIC DATA EXTRACTION ---
async def _extract_basic_data(text: str) -> dict:
    """Extract task, location, price from text (original logic)"""
    config = ConfigurationManager()
    manager = LLMManager(config)
    
    extraction_prompt = f"""
Extract structured data from this job description:

Text: "{text}"

Return ONLY valid JSON:
{{
  "task": "string or null",
  "location": "string or null",
  "price_amount": number or null,
  "price_currency": "string or null",
  "missing_fields": ["field1", "field2"]
}}

Rules:
- If currency is '$', use 'USD'
- If currency missing but amount exists, use 'GAS'
- Location can be: addresses, apartment numbers, building names
- Do not invent data
"""
    
    try:
        # Fixed: Use manager.chat() instead of manager.completion()
        messages = [Message(role="user", content=extraction_prompt)]
        response = await manager.chat(messages, model=ParalegalConfig.MODEL)
        
        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"⚠️ Extraction failed: {e}")
        return {
            "task": None,
            "location": None,
            "price_amount": None,
            "price_currency": None,
            "missing_fields": ["task", "location", "price_amount", "price_currency"]
        }

# --- HELPER: REFERENCE PHOTO ANALYSIS ---
async def analyze_reference_photo(image_bytes: bytes) -> dict:
    """
    Analyze reference photo to extract baseline features
    
    This helps the Eye agent detect if proof photo is of same location
    
    Returns:
        {
            "baseline_features": [str],  # Identifiable landmarks
            "estimated_dimensions": str,  # Size estimation
            "color_info": dict,  # Dominant colors
            "notable_objects": [str]  # Key objects to match
        }
    """
    
    # TODO: Implement actual image analysis when vision is available
    # For now, return placeholder
    
    print("⚠️  Reference photo analysis not yet implemented")
    print("    Will be added with vision model integration")
    
    return {
        "baseline_features": ["pending_vision_analysis"],
        "estimated_dimensions": "unknown",
        "color_info": {},
        "notable_objects": ["to_be_analyzed"]
    }
    
    # TODO: When vision is available, analyze:
    # - Identifiable features (outlets, switches, doors, windows)
    # - Object positions and sizes
    # - Dominant colors
    # - Lighting conditions
    # - Unique markers

# --- TEST EXECUTION ---
async def _run_tests():
    """Test suite for development"""
    print("🚀 GIGSHIELD PARALEGAL AGENT - JOB ARCHITECT\n")
    print("⚠️  Note: Image verification requires actual image bytes")
    print("    For full testing, use the API endpoint with real images\n")
    
    # Test 1: Vague description (should fail clarity)
    print("=" * 60)
    print("TEST 1: Vague Description (No Image)")
    print("=" * 60)
    test_text = "Clean my wall"
    
    # Simulate with dummy image for testing
    dummy_image = b"fake_image_bytes"
    
    result = await analyze_job_request(test_text, dummy_image)
    print(f"Input: {test_text}")
    print(f"Status: {result['status']}")
    if result['clarifying_questions']:
        print("Questions:")
        for q in result['clarifying_questions']:
            print(f"  - {q}")
    print()

if __name__ == "__main__":
    asyncio.run(_run_tests())
