import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
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
    TEXT_MODEL = "gpt-4"           # For text extraction and analysis
    VISION_MODEL = "gpt-4o"        # For image verification
    
    # Agent Behavior
    TEMPERATURE = 0.1              # Low for consistency
    MAX_RETRIES = 3                # For API failures
    
    # Currency Configuration
    DEFAULT_CURRENCY = "GAS"
    SUPPORTED_CURRENCIES = ["GAS", "NEO", "USDC", "USD", "USDT"]
    
    # Required Fields for Job Analysis
    REQUIRED_FIELDS = ["task", "task_description", "location", "price_amount", "price_currency"]
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.SUDO_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        return True


# Validate on import
AgentConfig.validate()
