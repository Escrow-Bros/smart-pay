import asyncio
import json
import os
import re
import httpx
from dotenv import load_dotenv
from spoon_ai.llm import LLMManager, ConfigurationManager

# --- 1. THE MONKEY PATCH (Crucial for Sudo AI) ---
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
# ------------------------------------------------

load_dotenv("agent/.env")

# --- 2. FALLBACK LOGIC (Updated to match new schema) ---
def _regex_extract(text: str) -> dict:
    """
    Fallback if AI fails. Attempts to extract data using patterns.
    Returns the same structure as the AI: {task, location, price_amount, price_currency, missing_fields}
    """
    t = text.strip()
    result = {
        "task": None,
        "location": None,
        "price_amount": None,
        "price_currency": "GAS", # Default for fallback
        "missing_fields": []
    }

    # Extract Location ("at ...")
    m_loc = re.search(r"\bat\s+(.+?)(?:\s+for\b|$)", t, flags=re.IGNORECASE)
    if m_loc:
        result["location"] = m_loc.group(1).strip()
    else:
        result["missing_fields"].append("location")

    # Extract Price ("for 10" or "for 10 GAS")
    m_price = re.search(r"\bfor\s+(\d+)\s*([A-Za-z]+)?\b", t, flags=re.IGNORECASE)
    if m_price:
        try:
            result["price_amount"] = int(m_price.group(1))
            # If regex found a currency (e.g., "USDC"), use it. Otherwise keep default.
            if m_price.group(2):
                result["price_currency"] = m_price.group(2).upper()
        except:
            result["missing_fields"].append("price")
    else:
        result["missing_fields"].append("price")

    # Extract Task (Everything before "at" or "for")
    m_task = re.search(r"^(.+?)\s+(?:at|for)\b", t, flags=re.IGNORECASE)
    if m_task:
        result["task"] = m_task.group(1).strip()
    else:
        result["missing_fields"].append("task")

    return result

# --- 3. THE SMART PARALEGAL ---
async def extract_contract(text: str) -> dict:
    """
    Extract structured contract data from natural language input.
    
    Args:
        text: User's natural language job description
        
    Returns:
        dict: {
            "task": str | None,
            "location": str | None,
            "price_amount": int | None,
            "price_currency": str | None,
            "missing_fields": list[str]
        }
    
    Example:
        >>> result = await extract_contract("Clean graffiti at 555 Market St for 10 GAS")
        >>> print(result)
        {
            "task": "Clean graffiti",
            "location": "555 Market St",
            "price_amount": 10,
            "price_currency": "GAS",
            "missing_fields": []
        }
    """
    from config import AgentConfig
    
    config = ConfigurationManager()
    manager = LLMManager(config)

    # ENHANCED PROMPT: Separates currency and handles missing data gracefully
    system_instructions = """
    You are the GigShield Paralegal. Extract structured data for a smart contract.
    
    OUTPUT FORMAT (Raw JSON only):
    {
      "task": "string or null",
      "location": "string or null",
      "price_amount": number or null,
      "price_currency": "string (e.g. GAS, NEO, USDC) or null",
      "missing_fields": ["list", "of", "missing", "keys"]
    }
    
    RULES:
    1. If currency is '$', assume 'USD'.
    2. If currency is missing but amount exists, assume 'GAS'.
    3. Do not invent data. If a field is not in the text, put it in 'missing_fields'.
    4. LOCATION can be: street addresses (555 Market St), apartment numbers (Apt 4B), 
       building names (Empire State Building), or any physical place identifier.
    
    EXAMPLES:
    - "Fix my sink at Apt 4B" → location: "Apt 4B"
    - "Clean graffiti at 555 Market St" → location: "555 Market St"
    - "Verify ad at Times Square" → location: "Times Square"
    """

    full_prompt = f"{system_instructions}\n\nInput Text: \"{text}\""

    try:
        # Use configuration for model and temperature
        resp = await manager.completion(
            full_prompt, 
            model=AgentConfig.PARALEGAL_MODEL,
            temperature=AgentConfig.PARALEGAL_TEMPERATURE
        )
        
        # Clean the response (Sudo AI sometimes adds markdown)
        content = resp.content.replace("```json", "").replace("```", "").strip()
        
        parsed = json.loads(content)
        
        # Final sanity check on the AI's work
        if not isinstance(parsed, dict):
            raise ValueError("AI did not return a dictionary")
            
        return parsed

    except Exception as e:
        print(f"⚠️ AI Failed ({e}), switching to Regex Fallback...")
        return _regex_extract(text)

# --- 4. TEST EXECUTION (Only runs when file is executed directly) ---
async def _run_tests():
    """
    Test suite for development/validation.
    This only runs when you execute: python agent/paralegal.py
    """
    test_inputs = [
        "I need someone to clean graffiti at 555 Market St for 10 GAS", # Perfect - all fields
        "Fix my sink at Apt 4B", # Apartment number location, missing price
        "Paint the wall for 50 USDC", # Missing location
        "Clean the lobby at Building 7", # Building name location
        "Verify ad at Times Square for 20 GAS" # Famous landmark location
    ]

    print("🚀 GIGSHIELD PARALEGAL AGENT - TEST MODE\n")

    for text in test_inputs:
        print(f"📝 Input: {text}")
        result = await extract_contract(text)
        print(f"📊 Result: {json.dumps(result, indent=2)}")
        print("-" * 30)

if __name__ == "__main__":
    # Only run tests when executed directly
    asyncio.run(_run_tests())