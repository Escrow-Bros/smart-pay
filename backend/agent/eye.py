"""
The Eye Agent - Universal AI-Powered Work Verification  
Verifies ANY type of gig work by comparing before/after photos
Uses modular AI client with GPT-4.1 (reasoning) and GPT-4o (vision)
"""
import asyncio
import json
import base64
import httpx
from typing import List, Dict, Optional
from dotenv import load_dotenv
from backend.agent.gps_verifier import verify_gps_location
from backend.agent.paralegal import get_ai_client
from backend.config import AgentConfig

load_dotenv()


class UniversalEyeAgent:
    """
    Generalized verification agent that works for ANY gig work type
    
    Architecture:
    1. Paralegal generates verification plan at job creation (TASK-011)
    2. Eye uses that plan to verify worker's proof (TASK-013)
    
    Uses modular AI client for:
    - Text reasoning: GPT-4.1 (decision making, scoring logic)
    - Vision analysis: GPT-4o (image comparison, quality assessment)
    - All via Sudo AI unified proxy
    """
    
    def __init__(self):
        # Get shared AI client (supports both text and vision)
        self.ai_client = get_ai_client()
    
    async def verify(
        self,
        proof_photos: List[str],
        job_id: str,
        worker_location: Optional[Dict] = None
    ) -> Dict:
        """
        Main entry point - verifies ANY type of gig work
        
        Args:
            proof_photos: IPFS URLs of worker's proof (AFTER photos)
            job_id: Job identifier to fetch requirements from contract
            worker_id: Optional worker address for reputation checks
            worker_location: Optional worker GPS location from browser/app permissions
                            {"latitude": float, "longitude": float, "accuracy": float}
        
        Returns:
            Verification result with verdict and reasoning
        """
        print("Proof photos: ")
        print(proof_photos)
        # Fetch from smart contract (Source of Truth)
        job_data = await self._get_job_data_from_chain(int(job_id))

        print("Job data: ")
        print(job_data)
        task_description = job_data["description"]
        reference_photos = job_data["reference_photos"]
        verification_plan = job_data["verification_plan"]
        
        # Fix: Sanitize URLs to remove double slashes (caused by old upload code)
        def sanitize_url(url: str) -> str:
            """Remove double slashes from URL path"""
            if not url:
                return url
            # Replace double slashes with single, but preserve https://
            return url.replace('https://', 'HTTPS_PLACEHOLDER').replace('//', '/').replace('HTTPS_PLACEHOLDER', 'https://')
        
        print(f"🔧 Sanitizing URLs...")
        print(f"   Before: reference={reference_photos}")
        print(f"   Before: proof={proof_photos}")
        
        reference_photos = [sanitize_url(url) for url in reference_photos]
        proof_photos = [sanitize_url(url) for url in proof_photos]
        
        print(f"   After: reference={reference_photos}")
        print(f"   After: proof={proof_photos}")
        
        print(f"👁️  Eye Agent: Verifying job {job_id}")
        print(f"📋 Task: {task_description}")
        
        # Step 1: Compare before vs after
        print("🔍 Step 1: Comparing before/after photos...")
        job_location = job_data.get("location")  # Get job location from job_data
        comparison = await self.compare_before_after(
            reference_photos,
            proof_photos,
            verification_plan,
            job_location,  # Job location for comparison
            worker_location  # Worker location from browser/app permissions
        )
        
        
        # Step 2: Verify against requirements
        print("✅ Step 2: Verifying requirements...")
        verification = await self.verify_requirements(
            proof_photos,
            task_description,
            verification_plan,
            comparison
        )
        
        # Safety check: ensure verification returned valid data
        if verification is None:
            verification = {
                "verdict": "REJECTED",
                "confidence": 0.0,
                "reasoning": "Verification returned no result",
                "issues": ["Internal error during verification"],
                "suggestions": ["Please try again"]
            }
        
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
        verification_plan: Dict,
        job_location: Optional[Dict] = None,
        worker_location: Optional[Dict] = None
    ) -> Dict:
        """
        Compare BEFORE (reference) vs AFTER (proof) photos
        
        UPGRADED: Now actually downloads and analyzes images using vision model!
        
        This is the core anti-fraud check:
        - Are they the same location?
        - Did transformation happen?
        - Is coverage consistent?
        - GPS location verification (if locations provided)
        
        Args:
            reference_photos: List of reference photo URLs
            proof_photos: List of proof photo URLs
            verification_plan: Verification plan from job_data
            job_location: Optional job GPS location from job_data {"latitude": float, "longitude": float, "accuracy": float}
            worker_location: Optional worker GPS location from browser/app permissions {"latitude": float, "longitude": float, "accuracy": float}
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
        
        # GPS Location Verification (REQUIRED)
        if not job_location:
            raise ValueError("Job location is required for work verification")
        
        if not worker_location:
            raise ValueError("Worker location is required for work verification. Please enable location services.")
        
        print("📍 Verifying GPS location (REQUIRED - 300m radius)...")
        print("job_location", job_location)
        print("worker_location", worker_location)
        try:
            gps_verification = verify_gps_location(
                reference_gps=job_location,
                proof_gps=worker_location,
                max_distance_meters=300.0
            )
            print(f"📍 GPS Result: {gps_verification['reasoning']}")
            
            # FAIL IMMEDIATELY if location doesn't match
            if not gps_verification["location_match"]:
                print(f"❌ LOCATION VERIFICATION FAILED - Worker not at job site!")
                return {
                    "same_location": False,
                    "same_object": False,
                    "transformation_occurred": False,
                    "location_confidence": 0.0,
                    "fraud_detected": True,
                    "visual_changes": [],
                    "gps_verification": gps_verification,
                    "rejection_reason": f"Location check failed: {gps_verification['reasoning']}. Worker must be within 300m of job location.",
                    "distance_meters": gps_verification.get("distance_meters")
                }
            
            print(f"✅ Location verified - Worker within {gps_verification['distance_meters']:.1f}m of job site")
            
        except Exception as e:
            print(f"❌ GPS verification error: {e}")
            return {
                "same_location": False,
                "same_object": False,
                "transformation_occurred": False,
                "location_confidence": 0.0,
                "fraud_detected": True,
                "visual_changes": [],
                "gps_verification": {
                    "location_match": False,
                    "distance_meters": None,
                    "confidence": 0.0,
                    "reasoning": f"GPS verification failed: {str(e)}"
                },
                "rejection_reason": f"GPS verification error: {str(e)}"
            }
        
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
            
            # Call vision model for image comparison
            print("👁️ Analyzing images with GPT-4o vision model...")
            response_text = await self.ai_client.analyze_multi_image(
                content=content,
                model=AgentConfig.VISION_MODEL,
                max_tokens=1000
            )
            
            # Parse JSON response
            comparison = self._parse_json_response(response_text)
            
            # Add GPS verification result to comparison
            if gps_verification:
                comparison['gps_verification'] = gps_verification
            
            print(f"✅ Vision analysis complete - Location match: {comparison.get('same_location', {}).get('verdict', 'unknown')}")
            if gps_verification:
                print(f"📍 GPS match: {gps_verification.get('location_match', 'N/A')} (distance: {gps_verification.get('distance_meters', 'N/A')}m)")
            
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
        print(proof_photos)
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
                    "text": f"""You are "The Eye" - an impartial AI judge for GigSmartPay gig work platform.

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
            
            # Call vision model for work quality verification
            print("👁️ Verifying work quality with GPT-4o vision model...")
            response_text = await self.ai_client.analyze_multi_image(
                content=content,
                model=AgentConfig.VISION_MODEL,
                max_tokens=800
            )
            
            verification = self._parse_json_response(response_text)
            
            print(f"✅ Verification complete - Verdict: {verification.get('verdict', 'unknown')}")
            
            return verification
            
        except Exception as e:
            print(f"❌ Fallback verification failed: {e}")
            return {
                "verdict": "REJECTED",
                "confidence": 0.3,
                "reasoning": "Cannot verify work without image access - assuming work attempted",
                "issues": ["Image verification unavailable"],
                "suggestions": ["Please ensure reference photos are accessible"]
            }
    
    def make_final_decision(
        self,
        verification_plan: Dict,
        comparison: Dict,
        verification: Dict
    ) -> Dict:
        """
        Two-Stage Verification System (Production-Grade)
        
        STAGE 1: Critical Checks (Must Pass)
        - GPS within 300m (HARD FAIL if exceeded - checked in compare_before_after)
        - Visible transformation (HARD FAIL if no work detected)
        
        STAGE 2: Quality Scoring (0-100 points)
        - GPS Quality: 25 points
        - Visual Location Match: 20 points
        - Transformation Quality: 25 points
        - Coverage Consistency: 15 points
        - Requirements Met: 15 points
        
        STAGE 3: Decision Thresholds
        - ≥70 points: APPROVED ✅
        - 50-69 points: NEEDS_IMPROVEMENT ⚠️ (can resubmit)
        - <50 points: REJECTED ❌
        
        Benefits:
        - Ensures work is done (critical checks)
        - Forgives photo quality issues (scoring)
        - Transparent feedback (see exact score)
        - Professional presentation (for demos)
        """
        
        # ===================================================================
        # STAGE 1: CRITICAL CHECKS (Must Pass)
        # ===================================================================
        
        # Critical Check 1: GPS - Must be within 300m (fraud detection)
        gps_check = comparison.get('gps_verification', {})
        distance = gps_check.get('distance_meters', 9999)
        
        if not gps_check.get('location_match', False):
            # GPS failed - worker not at job site
            distance_text = f"{distance:.1f}m" if isinstance(distance, (int, float)) else "unknown"
            
            return {
                "verified": False,
                "confidence": 0.0,
                "verdict": "REJECTED",
                "reason": f"Worker not at job location ({distance_text} away - max 300m)",
                "category": "GPS_LOCATION_FAILED",
                "score": 0,
                "breakdown": {
                    "gps_quality": 0,
                    "visual_location": 0,
                    "transformation": 0,
                    "coverage": 0,
                    "requirements": 0
                },
                "issues": [
                    f"Worker location: {distance_text} from job site",
                    "Maximum allowed: 500m",
                    "Please ensure you are physically at the job location"
                ],
                "gps_data": {
                    "distance_meters": distance,
                    "max_allowed_meters": 500.0,
                    "tier": gps_check.get('tier', 'failed'),
                    "reasoning": gps_check.get('reasoning')
                },
                "payment_recommended": False,
                "can_resubmit": True,
                "suggestions": [
                    "Go to the actual job location",
                    "Enable high-accuracy GPS on your device",
                    "Wait for GPS to stabilize (10-30 seconds)"
                ]
            }
        
        # Critical Check 2: Transformation - Must show visible work
        transformation_detected = comparison['transformation_detected'].get('verdict', False)
        
        if not transformation_detected:
            return {
                "verified": False,
                "confidence": 0.0,
                "verdict": "REJECTED",
                "reason": "No visible work completed",
                "category": "NO_WORK_DETECTED",
                "score": 0,
                "breakdown": {
                    "gps_quality": 0,
                    "visual_location": 0,
                    "transformation": 0,
                    "coverage": 0,
                    "requirements": 0
                },
                "issues": [
                    "Expected transformation not visible in photos",
                    f"Expected: {verification_plan.get('expected_transformation', {}).get('after', 'completed work')}",
                    "Actual: No significant changes detected"
                ],
                "payment_recommended": False,
                "can_resubmit": True,
                "suggestions": [
                    "Complete the work as described",
                    "Take clear before/after photos showing the change",
                    "Ensure lighting is good enough to see the work"
                ]
            }
        
        # ===================================================================
        # STAGE 2: QUALITY SCORING (0-100 points)
        # ===================================================================
        
        score = 0
        max_score = 100
        breakdown = {}
        
        # Component 1: GPS Quality (25 points)
        gps_confidence = gps_check.get('confidence', 0.5)
        gps_tier = gps_check.get('tier', 'acceptable')
        
        if gps_tier == 'excellent':
            gps_score = 25
        elif gps_tier == 'good':
            gps_score = 20
        elif gps_tier == 'acceptable':
            gps_score = 15
        else:
            gps_score = 25 * gps_confidence  # Fallback to confidence-based
        
        score += gps_score
        breakdown['gps_quality'] = round(gps_score, 1)
        
        # Component 2: Visual Location Match (20 points)
        location_verdict = comparison['same_location'].get('verdict', False)
        location_confidence = comparison['same_location'].get('confidence', 0.0)
        
        # Dynamic threshold based on GPS
        # If GPS is strong, lower vision requirement (they're complementary)
        if gps_confidence >= 0.8:
            required_vision_confidence = 0.50  # GPS verified, vision just confirms
        else:
            required_vision_confidence = 0.60  # Need stronger vision if GPS weak
        
        if location_verdict and location_confidence >= required_vision_confidence:
            visual_score = 20 * min(location_confidence / required_vision_confidence, 1.0)
        elif location_verdict:
            visual_score = 20 * (location_confidence / required_vision_confidence) * 0.7
        else:
            visual_score = 20 * location_confidence * 0.5
        
        score += visual_score
        breakdown['visual_location'] = round(visual_score, 1)
        
        # Component 3: Transformation Quality (25 points)
        matches_expected = comparison['transformation_detected'].get('matches_expected', False)
        
        if matches_expected:
            transform_score = 25
        else:
            # Partial credit if transformation visible but unclear
            transform_score = 15
        
        score += transform_score
        breakdown['transformation'] = round(transform_score, 1)
        
        # Component 4: Coverage Consistency (15 points)
        coverage_verdict = comparison['coverage_consistency'].get('verdict', False)
        coverage_ratio = comparison['coverage_consistency'].get('coverage_ratio', 0.5)
        
        if coverage_verdict:
            coverage_score = 15
        else:
            coverage_score = 15 * coverage_ratio
        
        score += coverage_score
        breakdown['coverage'] = round(coverage_score, 1)
        
        # Component 5: Requirements Met (15 points)
        requirements_verdict = verification.get('verdict', 'REJECTED')
        requirements_confidence = verification.get('confidence', 0.5)
        
        if requirements_verdict == 'APPROVED':
            req_score = 15 * requirements_confidence
        else:
            req_score = 15 * requirements_confidence * 0.5
        
        score += req_score
        breakdown['requirements'] = round(req_score, 1)
        
        # ===================================================================
        # STAGE 3: FINAL DECISION BASED ON SCORE
        # ===================================================================
        
        percentage = (score / max_score) * 100
        
        if percentage >= 70:
            # APPROVED: High quality work
            return {
                "verified": True,
                "confidence": score / max_score,
                "verdict": "APPROVED",
                "reason": f"Work verified with {percentage:.0f}% quality score",
                "category": "APPROVED",
                "score": round(percentage, 1),
                "breakdown": breakdown,
                "gps_data": {
                    "distance_meters": distance,
                    "tier": gps_tier,
                    "confidence": gps_confidence
                },
                "quality_indicators": {
                    "location_verified": location_verdict,
                    "transformation_clear": matches_expected,
                    "coverage_adequate": coverage_verdict,
                    "requirements_met": requirements_verdict == 'APPROVED'
                },
                "payment_recommended": True
            }
        
        elif percentage >= 50:
            # NEEDS IMPROVEMENT: Work done but quality issues
            return {
                "verified": False,
                "confidence": score / max_score,
                "verdict": "NEEDS_IMPROVEMENT",
                "reason": f"Work quality insufficient ({percentage:.0f}% score - need 70%)",
                "category": "NEEDS_IMPROVEMENT",
                "score": round(percentage, 1),
                "breakdown": breakdown,
                "gps_data": {
                    "distance_meters": distance,
                    "tier": gps_tier,
                    "confidence": gps_confidence
                },
                "issues": self._generate_improvement_suggestions(breakdown, verification),
                "payment_recommended": False,
                "can_resubmit": True,
                "suggestions": [
                    "Retake photos with better lighting",
                    "Show complete work area (not just partial)",
                    "Ensure before/after photos match clearly"
                ]
            }
        
        else:
            # REJECTED: Significant quality issues
            return {
                "verified": False,
                "confidence": score / max_score,
                "verdict": "REJECTED",
                "reason": f"Work does not meet requirements ({percentage:.0f}% score)",
                "category": "REJECTED",
                "score": round(percentage, 1),
                "breakdown": breakdown,
                "gps_data": {
                    "distance_meters": distance,
                    "tier": gps_tier,
                    "confidence": gps_confidence
                },
                "issues": verification.get('issues', []),
                "payment_recommended": False,
                "can_resubmit": True,
                "suggestions": verification.get('suggestions', [])
            }
    
    def _generate_improvement_suggestions(self, breakdown: Dict, verification: Dict) -> List[str]:
        """Generate specific improvement suggestions based on low scores"""
        suggestions = []
        
        if breakdown.get('gps_quality', 0) < 15:
            suggestions.append("Move closer to the job location (currently too far)")
        
        if breakdown.get('visual_location', 0) < 12:
            suggestions.append("Retake photo showing clearly matching features (outlets, windows, landmarks)")
        
        if breakdown.get('transformation', 0) < 15:
            suggestions.append("Show clearer evidence of work completed (before/after difference)")
        
        if breakdown.get('coverage', 0) < 10:
            suggestions.append("Show full work area (not just small section)")
        
        if breakdown.get('requirements', 0) < 10:
            suggestions.append("Address specific requirements: " + ", ".join(verification.get('issues', [])[:2]))
        
        return suggestions if suggestions else ["Improve overall photo quality and ensure work is clearly visible"]
    
    # ========================================================================
    # PLACEHOLDER METHODS - To be implemented with actual integrations
    # ========================================================================
    

    
    async def _get_job_data_from_chain(self, job_id: int) -> Dict:
        """
        Fetch job data from Neo N3 smart contract via NeoMCP
        STRICT: Must fetch from chain to ensure Source of Truth.
        """
        from src.neo_mcp import NeoMCP
        from backend.database import get_db
        
        print(f"\n📡 Fetching job #{job_id} from blockchain...")
        mcp = NeoMCP()
        
        # Get details from blockchain
        job_details = await mcp.get_job_details(int(job_id))
        
        if not job_details:
            raise ValueError(f"Job {job_id} not found on blockchain")
        
        print(f"✅ Raw blockchain data received:")
        print(f"   Status: {job_details.get('status_name')}")
        print(f"   Client: {job_details.get('client_address')}")
        print(f"   Worker: {job_details.get('worker_address')}")
        print(f"   Amount: {job_details.get('amount_gas')} GAS")
        print(f"   Details length: {len(job_details.get('details', ''))} chars")
        print(f"   Reference URLs: {len(job_details.get('reference_urls', []))} photos")

        # Fetch location from database (blockchain doesn't store it)
        db = get_db()
        db_job = db.get_job(job_id)
        location_data = None
        
        if db_job:
            location_data = {
                "latitude": db_job.get("latitude"),
                "longitude": db_job.get("longitude"),
                "location_name": db_job.get("location")
            }
            print(f"   📍 Location from DB: {location_data.get('location_name')} ({location_data.get('latitude')}, {location_data.get('longitude')})")
        else:
            print(f"   ⚠️  No location data found in database")

        # Parse description and verification plan from details string
        full_details = job_details.get("details", "")
        description = full_details
        
        print(f"\n📝 Parsing job details...")
        print(f"   Full details preview: {full_details[:200]}...")
        
        # Default empty plan
        plan = {
            "task_category": "general",
            "expected_transformation": {},
            "quality_indicators": [],
            "verification_checklist": [],
            "common_mistakes": []
        }
        
        # Parse VERIFICATION PLAN section if present
        if "VERIFICATION PLAN:" in full_details:
            print(f"   ✓ Found VERIFICATION PLAN section")
            parts = full_details.split("VERIFICATION PLAN:")
            description = parts[0].strip()
            plan_text = parts[1].strip()
            
            # Parse Category
            import re
            cat_match = re.search(r"Category: (.*)", plan_text)
            if cat_match:
                plan["task_category"] = cat_match.group(1).strip()
                print(f"   ✓ Category: {plan['task_category']}")
            
            # Parse Transformation
            before_match = re.search(r"Before: (.*)", plan_text)
            after_match = re.search(r"After: (.*)", plan_text)
            if before_match:
                plan["expected_transformation"]["before"] = before_match.group(1).strip()
            if after_match:
                plan["expected_transformation"]["after"] = after_match.group(1).strip()
                print(f"   ✓ Transformation: {before_match.group(1).strip()[:50]}... -> {after_match.group(1).strip()[:50]}...")
            
            # Parse Lists (Checklist, Quality Indicators)
            current_section = None
            for line in plan_text.split("\n"):
                line = line.strip()
                if "Checklist:" in line:
                    current_section = "checklist"
                elif "Quality Indicators:" in line:
                    current_section = "quality"
                elif line.startswith("- ") and current_section:
                    item = line[2:].strip()
                    if current_section == "checklist":
                        plan["verification_checklist"].append(item)
                    elif current_section == "quality":
                        plan["quality_indicators"].append(item)
            
            print(f"   ✓ Checklist: {len(plan['verification_checklist'])} items")
            print(f"   ✓ Quality indicators: {len(plan['quality_indicators'])} items")
        
        # Fallback for legacy format (ACCEPTANCE CRITERIA:)
        elif "ACCEPTANCE CRITERIA:" in full_details:
            print(f"   ⚠️  Using legacy ACCEPTANCE CRITERIA format")
            parts = full_details.split("ACCEPTANCE CRITERIA:")
            description = parts[0].strip()
            criteria_text = parts[1].strip()
            plan["verification_checklist"] = [line.strip("- ").strip() for line in criteria_text.split("\n") if line.strip().startswith("-")]
            print(f"   ✓ Parsed {len(plan['verification_checklist'])} criteria items")
        else:
            print(f"   ⚠️  No verification plan found, using defaults")
        
        result = {
            "job_id": job_id,
            "description": description,
            "reference_photos": job_details.get("reference_urls", []),
            "location": location_data,  # From database
            "verification_plan": plan,
            "amount": job_details.get("amount_gas", 0),
            "client": job_details.get("client_address"),
            "status": job_details.get("status_name")
        }
        
        print(f"\n✅ Parsed job data ready for verification:")
        print(f"   Description: {description[:100]}...")
        print(f"   Reference photos: {len(result['reference_photos'])}")
        print(f"   Verification plan items: {len(plan['verification_checklist'])}")
        if location_data:
            print(f"   Location: {location_data.get('location_name')}")
        
        return result
    
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
            
            # Download image asynchronously to avoid blocking event loop
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30)
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
        print("⚠️ Using text-only fallback - cannot verify actual images")
        
        # Return optimistic but low-confidence result with ALL required keys
        return {
            "same_location": {
                "verdict": True,
                "confidence": 0.5,
                "reasoning": "Image verification unavailable - assuming same location"
            },
            "transformation_detected": {
                "matches_expected": True,
                "confidence": 0.5,
                "changes": ["Unable to verify actual changes - images not accessible"]
            },
            "coverage_consistency": {
                "verdict": True,
                "confidence": 0.5,
                "concerns": []
            },
            "gps_verification": None
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
    worker_location: Optional[Dict] = None
) -> Dict:
    """
    Simplified interface for frontend use
    
    Args:
        proof_photos: List of IPFS URLs of worker's proof photos
        job_id: Job identifier from smart contract
        worker_id: Optional worker address
        worker_location: Optional worker GPS location from browser/app permissions
                        {"latitude": float, "longitude": float, "accuracy": float}
    
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
            job_id="job_12345",
            worker_location={"latitude": 37.7749, "longitude": -122.4194, "accuracy": 10.0}
        )
        
        if result["verified"]:
            print(f"✅ APPROVED: {result['reason']}")
            # TODO: Trigger smart contract to release funds
        else:
            print(f"❌ REJECTED: {result['reason']}")
    """
    agent = UniversalEyeAgent()
    return await agent.verify(proof_photos, job_id, worker_location)


# ============================================================================
# SYNCHRONOUS WRAPPER FOR NON-ASYNC CONTEXTS
# ============================================================================

def verify_work_sync(
    proof_photos: List[str],
    job_id: str,
    worker_location: Optional[Dict] = None
) -> Dict:
    """
    Synchronous wrapper for verify_work
    Use when calling from non-async code
    
    Args:
        proof_photos: List of IPFS URLs of worker's proof photos
        job_id: Job identifier from smart contract
        worker_location: Optional worker GPS location from browser/app permissions
    """
    return asyncio.run(verify_work(proof_photos, job_id, worker_location))
