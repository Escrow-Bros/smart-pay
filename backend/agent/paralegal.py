import json
import os
import base64
from typing import List
import httpx
from dotenv import load_dotenv
from spoon_ai.llm import LLMManager, ConfigurationManager
from spoon_ai.schema import Message

# Monkey patch for Sudo AI compatibility
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

load_dotenv()  # Loads from root .env


class ParalegalConfig:
    """Configuration for Paralegal Agent"""
    MODEL = "gpt-4"
    VISION_MODEL = "gpt-4o"
    TEMPERATURE = 0.1
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
    
    config = ConfigurationManager()
    manager = LLMManager(config)
    
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

Return ONLY valid JSON:
{{
  "is_clear": boolean,
  "issues": ["only list MISSING critical info"],
  "questions": ["only ask for MISSING info"]
}}
"""
    
    try:
        messages = [Message(role="user", content=clarity_prompt)]
        response = await manager.chat(messages, model=ParalegalConfig.MODEL)
        content = response.content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
        
        return {
            "is_clear": result.get("is_clear", False),
            "issues": result.get("issues", []),
            "questions": result.get("questions", [])
        }
    except Exception:
        if has_task and has_description and has_location and has_price:
            return {"is_clear": True, "issues": [], "questions": []}
        return {
            "is_clear": False,
            "issues": ["Could not validate clarity"],
            "questions": ["Please provide more details about the task and location"]
        }


async def verify_image_match(text: str, task: str, task_description: str, image_bytes: bytes) -> dict:
    """
    Compare text description to reference image using Vision AI.
    
    Returns:
        dict: {match: bool, confidence: float, image_shows: str, mismatch_reason: str|None}
    """
    try:
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        
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

Return ONLY valid JSON:
{{
  "match": true/false,
  "confidence": 0.0-1.0,
  "image_shows": "detailed description of what you actually see in the image",
  "mismatch_reason": "explanation if match is false, null if match is true"
}}"""
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": vision_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }],
            max_tokens=500,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content)
        
        return {
            "match": result.get("match", False),
            "confidence": result.get("confidence", 0.0),
            "image_shows": result.get("image_shows", "Unknown"),
            "mismatch_reason": result.get("mismatch_reason")
        }
        
    except Exception as e:
        return {
            "match": True,
            "confidence": 0.5,
            "image_shows": f"Vision analysis failed: {str(e)}",
            "mismatch_reason": None
        }


async def generate_verification_plan(task: str, task_description: str) -> dict:
    """
    Generate verification plan for Eye agent.
    
    Returns:
        dict: Verification plan with task category, transformation, checklist, etc.
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
    """
    Generate strict, measurable acceptance criteria.
    
    Returns:
        List[str]: List of specific criteria strings
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
"""
    
    try:
        messages = [Message(role="user", content=criteria_prompt)]
        response = await manager.chat(messages, model=ParalegalConfig.MODEL)
        content = response.content.replace("```json", "").replace("```", "").strip()
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


async def analyze_job_request(text: str, reference_image: bytes, location: str = None) -> dict:
    """
    Intelligent job analysis with validation and criteria generation.
    
    Args:
        text: Job description from user
        reference_image: Photo of current state (REQUIRED)
        location: Job location (optional, if provided separately)
    
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
        reference_image
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
    config = ConfigurationManager()
    manager = LLMManager(config)
    
    extraction_prompt = f"""
Extract structured data from this job description:

Text: "{text}"

Return ONLY valid JSON:
{{
  "task": "short summary of task (e.g. 'Fix Window') or null if missing",
  "task_description": "rephrased, clear, and professional description of what exactly needs to be done based on the text or null if missing",
  "location": "address or location description or null if missing",
  "price_amount": number or null if missing,
  "price_currency": "string or null if missing",
  "missing_fields": ["list", "of", "missing", "fields"]
}}

Rules:
- If currency is '$', use 'USD'
- If currency missing but amount exists, use 'GAS'
- Do not invent data
- If a field is missing, set it to null AND add it to missing_fields list
"""
    
    try:
        messages = [Message(role="user", content=extraction_prompt)]
        response = await manager.chat(messages, model=ParalegalConfig.MODEL)
        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception:
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
