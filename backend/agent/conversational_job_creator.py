"""Conversational Job Creator Agent

Multi-turn dialogue system for natural job creation through chat.
Uses Sudo AI SDK with structured output for reliable conversation flow.
"""
import json
import threading
from typing import Dict, List, Optional, Any
from backend.agent.paralegal import get_ai_client
from backend.config import AgentConfig


# ==================== CONVERSATION SCHEMAS ====================

CONVERSATION_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "ai_message": {
            "type": "string",
            "description": "Natural language response to user"
        },
        "extracted_data": {
            "type": "object",
            "properties": {
                "task": {"type": ["string", "null"]},
                "task_description": {"type": ["string", "null"]},
                "location": {"type": ["string", "null"]},
                "price_amount": {"type": ["number", "null"]},
                "price_currency": {"type": ["string", "null"]},
                "has_image": {"type": "boolean"}
            },
            "required": ["task", "task_description", "location", "price_amount", "price_currency", "has_image"],
            "additionalProperties": False
        },
        "verification_requirements": {
            "type": "object",
            "properties": {
                "requires_before_photo": {"type": "boolean"},
                "requires_after_photo": {"type": "boolean"},
                "requires_gps_verification": {"type": "boolean"},
                "requires_time_tracking": {"type": "boolean"},
                "visual_evidence_critical": {"type": "boolean"},
                "reason": {"type": "string"}
            },
            "required": ["requires_before_photo", "requires_after_photo", "requires_gps_verification", "requires_time_tracking", "visual_evidence_critical", "reason"],
            "additionalProperties": False
        },
        "missing_fields": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of fields still needed"
        },
        "current_step": {
            "type": "string",
            "enum": ["greeting", "ask_task", "ask_location", "ask_details", "ask_price", "ask_image", "confirm", "complete"],
            "description": "Current conversation stage"
        },
        "is_complete": {
            "type": "boolean",
            "description": "Whether all required info is collected"
        },
        "clarifying_questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Questions to improve job clarity"
        }
    },
    "required": ["ai_message", "extracted_data", "verification_requirements", "missing_fields", "current_step", "is_complete", "clarifying_questions"],
    "additionalProperties": False
}


# ==================== CONVERSATION STATE ====================

class ConversationState:
    """Manages state for a job creation conversation"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.extracted_data = {
            "task": None,
            "task_description": None,
            "location": None,
            "price_amount": None,
            "price_currency": None,
            "has_image": False
        }
        self.verification_requirements = {
            "requires_before_photo": False,
            "requires_after_photo": False,
            "requires_gps_verification": False,
            "requires_time_tracking": False,
            "visual_evidence_critical": False,
            "reason": ""
        }
        self.current_step = "greeting"
        self.is_complete = False
        self.history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.history.append({"role": role, "content": content})
    
    def update_extracted_data(self, new_data: Dict[str, Any]):
        """Update extracted fields"""
        for key, value in new_data.items():
            if value is not None and key in self.extracted_data:
                self.extracted_data[key] = value
    
    def update_verification_requirements(self, requirements: Dict[str, Any]):
        """Update verification requirements"""
        self.verification_requirements.update(requirements)
    
    def get_missing_fields(self) -> List[str]:
        """Get list of fields that are still None, considering verification requirements"""
        missing = []
        
        # Always need these
        for key in ["task", "task_description", "price_amount", "price_currency"]:
            if self.extracted_data.get(key) is None:
                missing.append(key)
        
        # Location only if GPS verification required
        if self.verification_requirements.get("requires_gps_verification", False):
            location = self.extracted_data.get("location")
            # Validate location has proper format (not just any string)
            if not location or not self._is_valid_location(location):
                missing.append("location")
        
        # Image only if before photo required
        if self.verification_requirements.get("requires_before_photo", False):
            if not self.extracted_data.get("has_image"):
                missing.append("reference_image")
        
        return missing
    
    def _is_valid_location(self, location: str) -> bool:
        """Check if location looks like a proper address"""
        if not location or len(location) < 10:
            return False
        # Basic validation: should contain comma (street, city) or common address keywords
        address_indicators = [',', 'street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln', 'boulevard', 'blvd']
        location_lower = location.lower()
        return any(indicator in location_lower for indicator in address_indicators)
    
    def to_dict(self) -> Dict:
        """Serialize state"""
        return {
            "session_id": self.session_id,
            "extracted_data": self.extracted_data,
            "verification_requirements": self.verification_requirements,
            "current_step": self.current_step,
            "is_complete": self.is_complete,
            "history": self.history
        }


# ==================== CONVERSATION ENGINE ====================

class ConversationalJobCreator:
    """AI-powered conversational interface for job creation"""
    
    def __init__(self):
        self.ai_client = get_ai_client()
        self.sessions: Dict[str, ConversationState] = {}
    
    def get_or_create_session(self, session_id: str) -> ConversationState:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationState(session_id)
        return self.sessions[session_id]
    
    async def process_message(
        self,
        session_id: str,
        user_message: str,
        image_uploaded: bool = False
    ) -> Dict[str, Any]:
        """
        Process user message and return AI response with updated state.
        
        Args:
            session_id: Unique conversation identifier
            user_message: User's text input
            image_uploaded: Whether user just uploaded an image
        
        Returns:
            Dict with ai_message, extracted_data, missing_fields, etc.
        """
        state = self.get_or_create_session(session_id)
        
        # Update image status if uploaded
        if image_uploaded:
            state.extracted_data["has_image"] = True
        
        # Add user message to history
        state.add_message("user", user_message)
        
        # Build context for AI
        context = self._build_conversation_context(state, user_message)
        
        # Get AI response with structured output
        try:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "conversation_response",
                    "schema": CONVERSATION_RESPONSE_SCHEMA,
                    "strict": True
                }
            }
            
            response_text = await self.ai_client.generate_text(
                context,
                model=AgentConfig.TEXT_MODEL,
                temperature=0.7,  # Slightly higher for natural conversation
                max_tokens=500,
                response_format=response_format
            )
            
            response_data = json.loads(response_text)
            
            # Update state with extracted data
            state.update_extracted_data(response_data["extracted_data"])
            state.update_verification_requirements(response_data["verification_requirements"])
            state.current_step = response_data["current_step"]
            state.is_complete = response_data["is_complete"]
            
            # Add AI response to history
            state.add_message("assistant", response_data["ai_message"])
            
            # Add current state info to response
            response_data["session_state"] = {
                "extracted_data": state.extracted_data,
                "verification_requirements": state.verification_requirements,
                "missing_fields": state.get_missing_fields(),
                "is_complete": state.is_complete
            }
            
            return response_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            # Fallback response for malformed AI response
            fallback = {
                "ai_message": "I'm having trouble processing that. Could you rephrase?",
                "extracted_data": state.extracted_data,
                "verification_requirements": state.verification_requirements,
                "missing_fields": state.get_missing_fields(),
                "current_step": state.current_step,
                "is_complete": False,
                "clarifying_questions": [],
                "session_state": {
                    "extracted_data": state.extracted_data,
                    "verification_requirements": state.verification_requirements,
                    "missing_fields": state.get_missing_fields(),
                    "is_complete": False
                }
            }
            state.add_message("assistant", fallback["ai_message"])
            return fallback
        except Exception as e:
            print(f"❌ Conversation error: {e!r}")
            # Fallback response for general errors
            fallback = {
                "ai_message": "I'm having trouble processing that. Could you rephrase?",
                "extracted_data": state.extracted_data,
                "verification_requirements": state.verification_requirements,
                "missing_fields": state.get_missing_fields(),
                "current_step": state.current_step,
                "is_complete": False,
                "clarifying_questions": [],
                "session_state": {
                    "extracted_data": state.extracted_data,
                    "verification_requirements": state.verification_requirements,
                    "missing_fields": state.get_missing_fields(),
                    "is_complete": False
                }
            }
            state.add_message("assistant", fallback["ai_message"])
            return fallback
    
    def _build_conversation_context(self, state: ConversationState, user_message: str) -> str:
        """Build prompt context for AI"""
        
        # Recent conversation history (last 6 messages)
        recent_history = state.history[-6:] if len(state.history) > 6 else state.history
        history_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in recent_history
        ])
        
        missing_fields = state.get_missing_fields()
        
        prompt = f"""You are a helpful AI assistant guiding users to create job postings on GigSmartPay, a blockchain-secured gig platform with AI-powered verification.

CONVERSATION HISTORY:
{history_text}

CURRENT USER MESSAGE:
USER: {user_message}

EXTRACTED DATA SO FAR:
{json.dumps(state.extracted_data, indent=2)}

MISSING FIELDS: {', '.join(missing_fields) if missing_fields else 'None - all info collected!'}

YOUR TASK:
1. Analyze the user's message and extract any job-related information
2. Update extracted_data with any NEW information found
3. **CRITICALLY**: Determine what verification requirements are needed for this SPECIFIC task type
4. Determine what's still missing based on verification needs
5. Respond naturally to guide the user to the next step

VERIFICATION REQUIREMENTS - THINK LIKE A TRIBUNAL JUDGE:

You MUST analyze the task and determine verification requirements:

**PHYSICAL TRANSFORMATION TASKS** (REQUIRES BEFORE/AFTER PHOTOS):
- Repairs: "fix fence", "repair window", "patch wall" → MUST have before photo showing damage
- Construction: "build deck", "install shelf", "make road" → MUST have before photo showing area
- Cleaning: "clean garage", "remove graffiti", "wash car" → MUST have before photo showing mess
- Painting: "paint wall", "repaint door" → MUST have before photo showing old state
- Landscaping: "mow lawn", "trim hedges", "plant flowers" → MUST have before photo showing before state

**DELIVERY/TRANSPORT TASKS** (GPS + TIME CRITICAL):
- "deliver package", "pick up groceries", "transport items" → GPS verification critical, before photo optional
- Location verification is PRIMARY evidence
- Time tracking important for proof of delivery

**SERVICE TASKS** (FLEXIBLE VERIFICATION):
- "babysit for 2 hours", "tutor math", "walk dog" → Time tracking + GPS, photos optional
- Trust-based with location verification

**DIGITAL TASKS** (NO PHOTOS NEEDED):
- "write blog post", "design logo", "code website" → NO photos, submit deliverable file instead
- Verification based on submitted work product

**YOUR DECISION LOGIC**:
1. Does the task create a VISIBLE CHANGE? → requires_before_photo=true, visual_evidence_critical=true
2. Does the task happen at a SPECIFIC LOCATION? → requires_gps_verification=true
3. Does the task involve TIME-BASED SERVICE? → requires_time_tracking=true
4. Will the worker COMPLETE it and submit proof? → requires_after_photo=true

**EXAMPLES**:
- "Fix fence": requires_before_photo=true (show damage), requires_after_photo=true (show repair), visual_evidence_critical=true, requires_gps_verification=true
- "Deliver package": requires_before_photo=false, requires_after_photo=true (proof of delivery), visual_evidence_critical=false, requires_gps_verification=true
- "Write article": requires_before_photo=false, requires_after_photo=false, visual_evidence_critical=false, requires_gps_verification=false
- "Clean garage": requires_before_photo=true (show mess), requires_after_photo=true (show clean), visual_evidence_critical=true, requires_gps_verification=true

**IMPORTANT**: 
- If task requires before photo, EXPLAIN to user why: "For verification, I'll need a photo showing the current state so the tribunal can verify the work was done"
- Be FLEXIBLE: Not every task needs photos. Digital work doesn't need photos. Simple errands might only need GPS.
- Make it CLEAR: Tell user what evidence will be needed for verification

CONVERSATION FLOW:
- greeting: Welcome user, ask what job they need help with
- ask_task: Get clear task name (e.g., "Fix Window", "Clean Garage")
- ask_details: Get detailed description of work needed
- ask_location: Get specific address or location (if task requires GPS verification)
- ask_price: Get payment amount (in GAS or USD)
- ask_image: Request reference photo upload ONLY if requires_before_photo=true
- confirm: Show summary and verification requirements
- complete: All done!

PRICING AND CURRENCY RULES:
- **ALWAYS CLARIFY CURRENCY**: When user gives just a number (e.g., "5", "10"), ALWAYS ask: "Is that 5 GAS or 5 USD?"
- **ACCEPT BOTH CURRENCIES**: 
  - If user says "5 GAS" or "5 gas" → set price_amount=5, price_currency="GAS"
  - If user says "5 USD" or "$5" or "5 dollars" → set price_amount=5, price_currency="USD" 
  - If user says just "5" → ASK which currency before proceeding
- **PROVIDE CONTEXT**: Tell user current GAS/USD rate if helpful (e.g., "That's about X USD" or "That's about Y GAS")
- **SUGGEST REASONABLE RANGES**: 
  - Simple tasks (1-2hr): 2-5 GAS (~$8-20 USD)
  - Medium tasks (3-5hr): 5-15 GAS (~$20-60 USD)
  - Large tasks (full day): 15-50 GAS (~$60-200 USD)
- **NEVER ASSUME**: If currency is unclear, ALWAYS ask for clarification

RULES:
- Be conversational and friendly
- Extract info from user messages even if they provide multiple fields at once
- If user says "actually" or "wait", they're correcting previous info - update it
- **LOCATION VALIDATION**: If task requires GPS verification:
  - Location MUST be a FULL street address (e.g., "123 Main St, San Francisco, CA")
  - REJECT vague locations: "my house", "downtown", "Location: 1", "123", partial addresses
  - Tell user to use the location picker or provide complete address with street, city, state
  - DO NOT accept location until it contains street name AND city/area
- **PRICE CLARIFICATION**: If price seems unreasonable, suggest typical range
- **CURRENCY HANDLING**: ALWAYS ask which currency (GAS or USD) if user provides just a number
- ONLY ask for image if verification_requirements.requires_before_photo=true
- Explain WHY you need certain info (e.g., "For tribunal verification, we need a photo showing the current damage")

RESPONSE FORMAT:
Your response MUST be valid JSON matching the schema. Fill verification_requirements based on task analysis:
{{
  "ai_message": "...",
  "extracted_data": {{...}},
  "verification_requirements": {{
    "requires_before_photo": true/false,
    "requires_after_photo": true/false,
    "requires_gps_verification": true/false,
    "requires_time_tracking": true/false,
    "visual_evidence_critical": true/false,
    "reason": "Explain why these requirements are needed for this specific task"
  }},
  "missing_fields": [...],
  "current_step": "...",
  "is_complete": false,
  "clarifying_questions": [...]
}}

Be natural, helpful, and SMART about what evidence is actually needed!"""
        
        return prompt
    
    def get_session_state(self, session_id: str) -> Optional[Dict]:
        """Get current state of a session"""
        if session_id in self.sessions:
            return self.sessions[session_id].to_dict()
        return None
    
    def clear_session(self, session_id: str):
        """Clear a conversation session"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# Global instance with thread-safety
_conversation_engine = None
_engine_lock = threading.Lock()

def get_conversation_engine() -> ConversationalJobCreator:
    """Get or create global conversation engine (thread-safe)"""
    global _conversation_engine
    if _conversation_engine is None:
        with _engine_lock:
            if _conversation_engine is None:
                _conversation_engine = ConversationalJobCreator()
    return _conversation_engine
