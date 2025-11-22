"""
GigShield Agent Configuration
Centralized configuration for all AI agents.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from multiple possible locations
env_paths = [
    "agent/.env",           # From project root
    ".env",                 # From agent directory
    "../agent/.env"         # From parent directory
]

for env_path in env_paths:
    if Path(env_path).exists():
        load_dotenv(env_path)
        break

class AgentConfig:
    """Configuration for GigShield AI Agents"""
    
    # Sudo AI Configuration
    SUDO_API_KEY = os.getenv("OPENAI_API_KEY")
    SUDO_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.sudoai.com/v1")
    
    # Model Selection
    PARALEGAL_MODEL = "gpt-4.1-mini"  # For contract extraction
    EYE_MODEL = "gpt-4-vision"        # For image verification (TASK-013)
    
    # Agent Behavior
    PARALEGAL_TEMPERATURE = 0.1       # Low for consistency
    MAX_RETRIES = 3                   # For API failures
    
    # Default Currency
    DEFAULT_CURRENCY = "GAS"
    
    # Supported Currencies
    SUPPORTED_CURRENCIES = ["GAS", "NEO", "USDC", "USD", "USDT"]
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.SUDO_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return True

# Validate on import
AgentConfig.validate()
