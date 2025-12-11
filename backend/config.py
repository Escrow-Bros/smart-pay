import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables - searches upward from current directory
load_dotenv()


class AgentConfig:
    """Configuration for GigSmartPay AI Agents"""
    
    # Sudo AI Configuration
    SUDO_API_KEY = os.getenv("SUDO_API_KEY")
    SUDO_SERVER_URL = os.getenv("SUDO_SERVER_URL")
    
    # Model Selection
    TEXT_MODEL = "gpt-4.1"         # For text extraction and analysis (Paralegal)
    REASONING_MODEL = "gpt-4.1"    # For verification reasoning (Eye)
    VISION_MODEL = "gpt-4o"        # For image verification (Vision)
    
    # Agent Behavior
    TEMPERATURE = 0.1              # Low for consistency
    MAX_RETRIES = 3                # For API failures
    
    # Currency Configuration
    DEFAULT_CURRENCY = "GAS"
    SUPPORTED_CURRENCIES = ["GAS", "NEO", "USDC", "USD", "USDT"]
    
    # Required Fields for Job Analysis
    REQUIRED_FIELDS = ["task", "task_description", "location", "price_amount", "price_currency"]


class DatabaseConfig:
    """Configuration for Database Connection"""
    
    # Database URL (Supabase PostgreSQL - REQUIRED)
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL environment variable is required.\n"
            "Please set it in your .env file:\n"
            "DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
        )
