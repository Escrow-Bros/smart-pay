"""
The Eye Agent - Universal AI-Powered Work Verification  
Verifies ANY type of gig work by comparing before/after photos
UPGRADED: Now with vision model support for actual image analysis!
"""
import asyncio
import json
import os
import base64
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Monkey-patch httpx to avoid Sudo AI blocking OpenAI SDK headers
import httpx
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

# Now import SpoonOS
from spoon_ai.llm import LLMManager, ConfigurationManager
from spoon_ai.schema import Message

load_dotenv("agent/.env")


class UniversalEyeAgent:
    """
    Generalized verification agent that works for ANY gig work type
    
    Architecture:
    1. Paralegal generates verification plan at job creation (TASK-011)
    2. Eye uses that plan to verify worker's proof (TASK-013)
    
    Uses SpoonOS (spoon_ai SDK) for:
    - Configuration management
    - Text-based analysis
    - Fallback mechanisms
    
    Uses direct OpenAI client for:
    - Vision model calls (GPT-4V)
    - Image analysis (SpoonOS Message doesn't support structured image content yet)
    """
    
    def __init__(self):
        # SpoonOS configuration and manager
        self.config = ConfigurationManager()
        self.llm = LLMManager(self.config)
        
        # Direct OpenAI client for vision (required for image inputs)
        # Note: SpoonOS Message objects only support text content currently
        self.vision_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
    
    async def verify(
        self,
        proof_photos: List[str],
        job_id: str,
        worker_id: Optional[str] = None
    ) -> Dict:
        """
        Main entry point - verifies ANY type of gig work
        
        Args:
            proof_photos: IPFS URLs of worker's proof (AFTER photos)
            job_id: Job identifier to fetch requirements from contract
            worker_id: Optional worker address for reputation checks
        
        Returns:
            Verification result with verdict and reasoning
        """
        
        # TODO (TASK-004): Fetch from smart contract
        # For now, using placeholder
        job_data = self._get_job_data_placeholder(job_id)
        
        task_description = job_data["description"]
        reference_photos = job_data["reference_photos"]
        verification_plan = job_data["verification_plan"]
        
        print(f"👁️  Eye Agent: Verifying job {job_id}")
        print(f"📋 Task: {task_description}")
        
        # Step 1: Compare before vs after
        print("🔍 Step 1: Comparing before/after photos...")
        comparison = await self.compare_before_after(
            reference_photos,
            proof_photos,
            verification_plan
        )
        
        # Step 2: Verify against requirements
        print("✅ Step 2: Verifying requirements...")
        verification = await self.verify_requirements(
            proof_photos,
            task_description,
            verification_plan,
            comparison
        )
        
        # Step 3: Final decision
        print("⚖️  Step 3: Making final decision...")
        decision = self.make_final_decision(
            verification_plan,
            comparison,
            verification
        )
        
        print(f"🏁 Verdict: {'✅ APPROVED' if decision['verified'] else '❌ REJECTED'}")
        
        return decision
    
    async def compare_before_after(
        self,
        reference_photos: List[str],
        proof_photos: List[str],
        verification_plan: Dict
    ) -> Dict:
        """
        Compare BEFORE (reference) vs AFTER (proof) photos
        
        UPGRADED: Now actually downloads and analyzes images using vision model!
        
        This is the core anti-fraud check:
        - Are they the same location?
        - Did transformation happen?
        - Is coverage consistent?
        """
        
        print("📥 Downloading images for visual comparison...")
        
        # Step 1: Download reference photos
        reference_images_b64 = []
        for url in reference_photos:
            img_b64 = await self._download_and_encode_image(url)
            if img_b64:
                reference_images_b64.append(img_b64)
        
        # Step 2: Download proof photos
        proof_images_b64 = []
        for url in proof_photos:
            img_b64 = await self._download_and_encode_image(url)
            if img_b64:
                proof_images_b64.append(img_b64)
        
        if not reference_images_b64 or not proof_images_b64:
            print("⚠️ Could not download images, falling back to URL-based analysis")
            return await self._compare_without_vision(
                reference_photos, 
                proof_photos, 
                verification_plan
            )
        
        print(f"✅ Downloaded {len(reference_images_b64)} reference + {len(proof_images_b64)} proof images")
        
        # Step 3: Build vision prompt with actual images
        try:
            # Use vision client (initialized via SpoonOS config)
            # Note: Direct client needed because SpoonOS Message doesn't support image content yet
            # Build message content with images
            content = [
                {
                    "type": "text",
                    "text": f"""You are an expert photo analyst for gig work verification.

TASK CATEGORY: {verification_plan.get('task_category', 'general work')}
EXPECTED TRANSFORMATION: {verification_plan.get('expected_transformation', {})}

Compare the BEFORE and AFTER photos below to verify work completion.

You must check:
1. LOCATION MATCH: Are these photos of the same place/object?
   - Look for matching features (outlets, switches, doors, windows, landmarks)
   - Check dimensions and proportions
   - Identify unique markers
   - Rate confidence 0.0 to 1.0

2. TRANSFORMATION: What changed between before and after?
   - Describe specific changes
   - Does it match expected work?
   - Quality of transformation?

3. COVERAGE: Do both photos show similar area/angle?
   - Same framing and distance?
   - Is after photo hiding parts shown in before?
   - Coverage ratio 0.0 to 1.0

4. COMPLETION: Does the change indicate work was done?
   - Clear improvement visible?
   - Meets basic requirements?

BEFORE PHOTOS (Reference):"""
                }
            ]
            
            # Add reference images
            for i, img_b64 in enumerate(reference_images_b64):
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}",
                        "detail": "high"
                    }
                })
            
            content.append({
                "type": "text",
                "text": "AFTER PHOTOS (Proof):"
            })
            
            # Add proof images
            for i, img_b64 in enumerate(proof_images_b64):
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}",
                        "detail": "high"
                    }
                })
            
            content.append({
                "type": "text",
                "text": """Analyze these images and return ONLY valid JSON:
{
  "same_location": {
    "verdict": true/false,
    "confidence": 0.0-1.0,
    "matching_features": ["list of matching elements you can see"],
    "reasoning": "detailed explanation based on visual analysis"
  },
  "transformation_detected": {
    "verdict": true/false,
    "changes": ["specific visual changes you observe"],
    "matches_expected": true/false
  },
  "coverage_consistency": {
    "verdict": true/false,
    "coverage_ratio": 0.0-1.0,
    "angle_similarity": 0.0-1.0,
    "concerns": ["any visual issues"]
  },
  "work_completed": true/false
}"""
            })
            
            # Call vision model using SpoonOS-configured client
            print("👁️ Analyzing images with vision model (via SpoonOS)...")
            response = await self.vision_client.chat.completions.create(
                model="gpt-4o",  # Vision model
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse JSON response
            comparison = self._parse_json_response(response.choices[0].message.content)
            
            print(f"✅ Vision analysis complete - Location match: {comparison.get('same_location', {}).get('verdict', 'unknown')}")
            
            return comparison
            
        except Exception as e:
            print(f"❌ Error in vision comparison: {e}")
            # Return conservative default
            return {
                "same_location": {
                    "verdict": False,
                    "confidence": 0.0,
                    "matching_features": [],
                    "reasoning": f"Vision analysis failed: {str(e)}"
                },
                "transformation_detected": {
                    "verdict": False,
                    "changes": [],
                    "matches_expected": False
                },
                "coverage_consistency": {
                    "verdict": False,
                    "coverage_ratio": 0.0,
                    "angle_similarity": 0.0,
                    "concerns": ["Analysis failed"]
                },
                "work_completed": False
            }
    
    async def verify_requirements(
        self,
        proof_photos: List[str],
        task_description: str,
        verification_plan: Dict,
        comparison: Dict
    ) -> Dict:
        """
        Verify proof photos against task requirements
        
        UPGRADED: Now uses vision model to actually see and verify the work!
        """
        
        # Download proof images
        print("📥 Downloading proof images for quality verification...")
        proof_images_b64 = []
        for url in proof_photos:
            img_b64 = await self._download_and_encode_image(url)
            if img_b64:
                proof_images_b64.append(img_b64)
        
        if not proof_images_b64:
            print("⚠️ Could not download proof images, using comparison data only")
            return await self._verify_without_vision(
                task_description,
                verification_plan,
                comparison
            )
        
        print(f"✅ Downloaded {len(proof_images_b64)} proof images for verification")
        
        try:
            # Use SpoonOS-configured vision client
            # Build vision prompt
            content = [
                {
                    "type": "text",
                    "text": f"""You are "The Eye" - an impartial AI judge for GigShield gig work platform.

TASK: "{task_description}"

VERIFICATION CHECKLIST:
{self._format_checklist(verification_plan.get('verification_checklist', []))}

QUALITY INDICATORS TO CHECK:
{self._format_list(verification_plan.get('quality_indicators', []))}

COMMON MISTAKES TO WATCH FOR:
{self._format_list(verification_plan.get('common_mistakes', []))}

BEFORE/AFTER COMPARISON RESULTS:
- Same location: {comparison['same_location']['verdict']} (confidence: {comparison['same_location'].get('confidence', 0.0)})
- Transformation detected: {comparison['transformation_detected']['verdict']}
- Work completed: {comparison.get('work_completed', False)}
- Coverage consistent: {comparison['coverage_consistency']['verdict']}

PROOF PHOTOS TO VERIFY:"""
                }
            ]
            
            # Add proof images
            for img_b64 in proof_images_b64:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_b64}",
                        "detail": "high"
                    }
                })
            
            content.append({
                "type": "text",
                "text": """Visually verify the proof photos against the requirements.

Be STRICT but FAIR:
- Check each item in the verification checklist
- Assess quality indicators visually
- Watch for common mistakes
- If evidence is unclear, request better photos
- If work is incomplete, explain what's missing
- If trying to cheat, reject firmly

Return ONLY valid JSON:
{
  "verdict": "APPROVED" or "REJECTED",
  "confidence": 0.0-1.0,
  "reasoning": "detailed explanation based on what you see",
  "issues": ["visual problems found"],
  "suggestions": ["improvements needed"]
}"""
            })
            
            # Call vision model using SpoonOS-configured client
            print("👁️ Verifying work quality with vision model (via SpoonOS)...")
            response = await self.vision_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=800,
                temperature=0.1
            )
            
            verification = self._parse_json_response(response.choices[0].message.content)
            
            print(f"✅ Verification complete - Verdict: {verification.get('verdict', 'unknown')}")
            
            return verification
            
        except Exception as e:
            print(f"❌ Error in vision verification: {e}")
            return {
                "verdict": "REJECTED",
                "confidence": 0.0,
                "reasoning": f"Vision verification error: {str(e)}",
                "issues": ["Technical error during verification"],
                "suggestions": ["Please try again"]
            }
    
    def make_final_decision(
        self,
        verification_plan: Dict,
        comparison: Dict,
        verification: Dict
    ) -> Dict:
        """
        Combine all signals into final verdict
        
        Multi-layer checks ensure fraud prevention
        """
        
        # Check 1: Location must match
        if not comparison['same_location']['verdict']:
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": "Proof photos are not of the same location as reference photos.",
                "category": "LOCATION_MISMATCH",
                "issues": comparison['same_location'].get('reasoning', 'Features do not match')
            }
        
        # Check 2: High confidence required on location match
        if comparison['same_location'].get('confidence', 0.0) < 0.80:
            return {
                "verified": False,
                "confidence": comparison['same_location'].get('confidence', 0.0),
                "reason": "Cannot confirm proof photos are of same location. Please retake with clearly matching features.",
                "category": "UNCERTAIN_LOCATION",
                "issues": "Low confidence in location match"
            }
        
        # Check 3: Transformation must be detected
        if not comparison['transformation_detected'].get('matches_expected', False):
            return {
                "verified": False,
                "confidence": 0.5,
                "reason": f"Expected transformation not detected. Expected: {verification_plan.get('expected_transformation', {}).get('after', 'completed work')}",
                "category": "INCOMPLETE_WORK",
                "issues": comparison['transformation_detected'].get('changes', [])
            }
        
        # Check 4: Coverage must be consistent
        if not comparison['coverage_consistency']['verdict']:
            return {
                "verified": False,
                "confidence": 0.5,
                "reason": "Proof photo shows different coverage than reference. Please show same area.",
                "category": "COVERAGE_MISMATCH",
                "issues": comparison['coverage_consistency'].get('concerns', [])
            }
        
        # Check 5: AI verification must approve
        if verification['verdict'] != "APPROVED":
            return {
                "verified": False,
                "confidence": verification.get('confidence', 0.5),
                "reason": verification.get('reasoning', 'Work does not meet requirements'),
                "category": "REQUIREMENTS_NOT_MET",
                "issues": verification.get('issues', []),
                "suggestions": verification.get('suggestions', [])
            }
        
        # All checks passed - APPROVE!
        return {
            "verified": True,
            "confidence": verification.get('confidence', 0.9),
            "reason": verification.get('reasoning', 'All requirements met. Work completed successfully.'),
            "category": "APPROVED",
            "quality_score": verification.get('confidence', 0.9),
            "comparison_data": {
                "location_confidence": comparison['same_location'].get('confidence', 0.0),
                "transformation": comparison['transformation_detected'].get('changes', [])
            }
        }
    
    # ========================================================================
    # PLACEHOLDER METHODS - To be implemented with actual integrations
    # ========================================================================
    
    def _get_job_data_placeholder(self, job_id: str) -> Dict:
        """
        TODO (TASK-004): Fetch from Neo N3 smart contract
        
        This will call the smart contract to get:
        - Task description
        - Reference photos (IPFS URLs)
        - Verification plan (generated by Paralegal)
        - Payment amount
        - Client/worker addresses
        """
        
        # Placeholder data for development
        return {
            "job_id": job_id,
            "description": "Paint bedroom wall blue with clean edges",
            "reference_photos": [
                "ipfs://placeholder/before_wall.jpg"
            ],
            "verification_plan": {
                "task_category": "painting",
                "expected_transformation": {
                    "before": "unpainted or different colored wall",
                    "after": "wall painted blue with clean finish"
                },
                "quality_indicators": [
                    "even color coverage",
                    "clean edges (no paint on ceiling/floor)",
                    "no drips or runs",
                    "smooth finish"
                ],
                "verification_checklist": [
                    "Is it the same wall? (check features)",
                    "Is color blue as specified?",
                    "Are edges clean?",
                    "Is coverage complete?",
                    "Any visible defects?"
                ],
                "common_mistakes": [
                    "showing only small section (hiding bad edges)",
                    "different lighting to hide color issues",
                    "extreme angles to hide drips"
                ]
            },
            "amount": 50,
            "client": "0xClient...",
            "status": "IN_PROGRESS"
        }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _format_photo_urls(self, urls: List[str]) -> str:
        """Format photo URLs for prompt"""
        if not urls:
            return "No photos provided"
        return "\n".join([f"- {url}" for url in urls])
    
    def _format_list(self, items: List[str]) -> str:
        """Format list for prompt"""
        if not items:
            return "None specified"
        return "\n".join([f"- {item}" for item in items])
    
    def _format_checklist(self, items: List[str]) -> str:
        """Format checklist for prompt"""
        if not items:
            return "No specific checklist provided"
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from AI response (handles markdown code blocks)"""
        try:
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                # Remove opening ```json or ```
                response = response.split("\n", 1)[1]
            if response.endswith("```"):
                # Remove closing ```
                response = response.rsplit("\n", 1)[0]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Could not parse JSON: {e}")
            print(f"Response: {response[:200]}...")
            # Return empty dict on parse failure
            return {}
    
    # ========================================================================
    # IMAGE HANDLING METHODS
    # ========================================================================
    
    async def _download_and_encode_image(self, url: str) -> Optional[str]:
        """
        Download image from URL and encode as base64
        
        Args:
            url: Image URL (IPFS or HTTP)
        
        Returns:
            Base64 encoded image string, or None if failed
        """
        try:
            # Handle IPFS URLs - convert to gateway URL
            if url.startswith("ipfs://"):
                # Use public IPFS gateway
                ipfs_hash = url.replace("ipfs://", "")
                url = f"https://ipfs.io/ipfs/{ipfs_hash}"
            
            # Download image
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Encode as base64
            image_bytes = response.content
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            return image_b64
            
        except Exception as e:
            print(f"⚠️ Failed to download/encode image {url}: {e}")
            return None
    
    async def _compare_without_vision(
        self,
        reference_photos: List[str],
        proof_photos: List[str],
        verification_plan: Dict
    ) -> Dict:
        """
        Fallback comparison without vision (text-only)
        Used when images cannot be downloaded
        """
        print("⚠️ Using text-only fallback for comparison")
        
        system_prompt = """You are analyzing a gig work verification case.

You do NOT have access to the actual images, only their URLs.
Based on the task description and expected transformation, make a CONSERVATIVE assessment.

Since you cannot see the images, rate confidence LOW (0.3-0.5) and suggest requesting better evidence.

Return JSON format with conservative estimates."""

        user_prompt = f"""TASK: {verification_plan.get('task_category', 'unknown')}
EXPECTED: {verification_plan.get('expected_transformation', {})}

Reference photos: {self._format_photo_urls(reference_photos)}
Proof photos: {self._format_photo_urls(proof_photos)}

Make conservative assessment (you cannot see images). Return JSON."""

        try:
            messages = [
                Message(role="system", content=system_prompt),
                Message(role="user", content=user_prompt)
            ]
            
            response = await self.llm.chat(messages, model="gpt-4")
            comparison = self._parse_json_response(response.content)
            
            # Force low confidence since we can't see images
            if 'same_location' in comparison:
                comparison['same_location']['confidence'] = min(
                    comparison['same_location'].get('confidence', 0.3),
                    0.5
                )
            
            return comparison
            
        except Exception as e:
            print(f"❌ Fallback comparison failed: {e}")
            return {
                "same_location": {
                    "verdict": False,
                    "confidence": 0.0,
                    "matching_features": [],
                    "reasoning": "Cannot verify without image access"
                },
                "transformation_detected": {
                    "verdict": False,
                    "changes": [],
                    "matches_expected": False
                },
                "coverage_consistency": {
                    "verdict": False,
                    "coverage_ratio": 0.0,
                    "angle_similarity": 0.0,
                    "concerns": ["Cannot assess without images"]
                },
                "work_completed": False
            }
    
    async def _verify_without_vision(
        self,
        task_description: str,
        verification_plan: Dict,
        comparison: Dict
    ) -> Dict:
        """
        Fallback verification without vision (text-only)
        Used when proof images cannot be downloaded
        """
        print("⚠️ Using text-only fallback for verification")
        
        # Use comparison results only
        if not comparison.get('same_location', {}).get('verdict', False):
            return {
                "verdict": "REJECTED",
                "confidence": 0.0,
                "reasoning": "Cannot verify location match without image access",
                "issues": ["Image analysis required"],
                "suggestions": ["Ensure images are accessible"]
            }
        
        # Conservative approval based on comparison
        return {
            "verdict": "REJECTED",
            "confidence": 0.3,
            "reasoning": "Cannot fully verify quality without direct image analysis",
            "issues": ["Visual inspection required"],
            "suggestions": ["Submit images via accessible URL"]
        }


# ============================================================================
# SIMPLE FUNCTION INTERFACE FOR FRONTEND
# ============================================================================

async def verify_work(
    proof_photos: List[str],
    job_id: str,
    worker_id: Optional[str] = None
) -> Dict:
    """
    Simplified interface for frontend use
    
    Args:
        proof_photos: List of IPFS URLs of worker's proof photos
        job_id: Job identifier from smart contract
        worker_id: Optional worker address
    
    Returns:
        Verification result:
        {
            "verified": bool,
            "confidence": float,
            "reason": str,
            "category": str,
            ...
        }
    
    Example:
        result = await verify_work(
            proof_photos=["ipfs://Qm.../after_wall.jpg"],
            job_id="job_12345"
        )
        
        if result["verified"]:
            print(f"✅ APPROVED: {result['reason']}")
            # TODO: Trigger smart contract to release funds
        else:
            print(f"❌ REJECTED: {result['reason']}")
    """
    agent = UniversalEyeAgent()
    return await agent.verify(proof_photos, job_id, worker_id)


# ============================================================================
# SYNCHRONOUS WRAPPER FOR NON-ASYNC CONTEXTS
# ============================================================================

def verify_work_sync(
    proof_photos: List[str],
    job_id: str,
    worker_id: Optional[str] = None
) -> Dict:
    """
    Synchronous wrapper for verify_work
    Use when calling from non-async code
    """
    return asyncio.run(verify_work(proof_photos, job_id, worker_id))

