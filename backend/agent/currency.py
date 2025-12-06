"""
Currency conversion utilities for GAS/USD
Shared configuration and logic for price fetching and conversions
This module mirrors the frontend currency.ts implementation
"""
import requests
from typing import Optional
import time

# ==================== CONFIGURATION ====================

COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=gas&vs_currencies=usd'
CACHE_DURATION = 300  # 5 minutes in seconds
DEFAULT_GAS_PRICE = 4.50  # Fallback price in USD
API_TIMEOUT = 5  # 5 seconds

# ==================== CACHE ====================

_cached_gas_price: Optional[float] = None
_last_fetch_time: float = 0

# ==================== PRICE FETCHING ====================


def fetch_gas_usd_price() -> float:
    """
    Fetch real-time GAS/USD price from CoinGecko API.
    Falls back to a reasonable default if API fails.
    
    Returns:
        Current GAS price in USD
    """
    try:
        response = requests.get(
            COINGECKO_API_URL,
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            price = data.get('gas', {}).get('usd')
            
            if isinstance(price, (int, float)) and price > 0:
                return float(price)
        
        # If API call didn't work, raise exception to trigger fallback
        raise ValueError("Invalid price data from API")
        
    except Exception as e:
        print(f"⚠️  Failed to fetch GAS price from API: {e}")
        return DEFAULT_GAS_PRICE


def get_gas_usd_price() -> float:
    """
    Get current GAS/USD price with caching.
    Uses 5-minute cache to avoid excessive API calls.
    
    Returns:
        Current GAS price in USD
    """
    global _cached_gas_price, _last_fetch_time
    
    current_time = time.time()
    
    # Return cached price if still valid
    if _cached_gas_price is not None and (current_time - _last_fetch_time) < CACHE_DURATION:
        return _cached_gas_price
    
    # Fetch new price
    price = fetch_gas_usd_price()
    _cached_gas_price = price
    _last_fetch_time = current_time
    
    return price


def get_cached_gas_price() -> float:
    """
    Get cached price synchronously (may be stale).
    Returns default if no cached price available.
    
    Returns:
        Cached GAS price or default
    """
    return _cached_gas_price if _cached_gas_price is not None else DEFAULT_GAS_PRICE


# ==================== CONVERSIONS ====================


def gas_to_usd(gas_amount: float) -> float:
    """
    Convert GAS amount to USD using cached price.
    
    Args:
        gas_amount: Amount in GAS
        
    Returns:
        Equivalent amount in USD
    """
    return gas_amount * get_cached_gas_price()


def usd_to_gas(usd_amount: float) -> float:
    """
    Convert USD amount to GAS using current price.
    Will fetch fresh price if cache expired.
    
    Args:
        usd_amount: Amount in USD
        
    Returns:
        Equivalent amount in GAS
    """
    gas_price = get_gas_usd_price()
    return usd_amount / gas_price


# ==================== FORMATTING ====================


def format_usd(amount: float) -> str:
    """
    Format amount as USD currency.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted string like "$22.50"
    """
    return f"${amount:.2f}"


def format_gas_with_usd(gas_amount: float) -> dict:
    """
    Format GAS amount with USD equivalent.
    
    Args:
        gas_amount: Amount in GAS
        
    Returns:
        Dict with 'gas' and 'usd' formatted strings
    """
    return {
        'gas': f"{gas_amount:.2f}",
        'usd': format_usd(gas_to_usd(gas_amount))
    }


def format_usd_with_gas(usd_amount: float) -> dict:
    """
    Format USD amount with GAS equivalent.
    
    Args:
        usd_amount: Amount in USD
        
    Returns:
        Dict with 'usd' and 'gas' formatted strings
    """
    return {
        'usd': format_usd(usd_amount),
        'gas': f"{usd_to_gas(usd_amount):.2f}"
    }


def format_price_with_conversion(amount: float, currency: str) -> str:
    """
    Format price with currency conversion for display.
    
    Args:
        amount: The amount
        currency: Either "GAS" or "USD"
        
    Returns:
        Formatted string like "5.00 GAS (~$22.50)" or "$20.00 (~4.44 GAS)"
    """
    if currency.upper() == "GAS":
        usd_value = gas_to_usd(amount)
        return f"{amount:.2f} GAS (~${usd_value:.2f})"
    elif currency.upper() == "USD":
        gas_value = usd_to_gas(amount)
        return f"${amount:.2f} (~{gas_value:.2f} GAS)"
    else:
        return f"{amount:.2f} {currency}"


# ==================== INITIALIZATION ====================


def initialize_price_cache():
    """
    Initialize price cache.
    Call this when the application starts.
    """
    try:
        get_gas_usd_price()
        print(f"✓ GAS price cache initialized: ${get_cached_gas_price():.2f}/GAS")
    except Exception as e:
        print(f"⚠️  Failed to initialize price cache: {e}")


# Auto-initialize cache on module import
try:
    _cached_gas_price = fetch_gas_usd_price()
    _last_fetch_time = time.time()
    print(f"✓ Currency module loaded. GAS price: ${_cached_gas_price:.2f}/GAS")
except Exception:
    print("⚠️  Using default GAS price until API becomes available")

