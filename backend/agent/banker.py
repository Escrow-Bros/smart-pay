import json
import os
import ssl
from typing import Dict, Optional
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urlunparse
from dotenv import load_dotenv

load_dotenv()  # Loads from root .env

# Constants
GAS_SYMBOL = "GAS"
ESTIMATED_NETWORK_FEE = 0.1  # Buffer for Neo N3 transaction fees


class BankerConfig:
    """Configuration for Banker Agent"""
    NETWORK_FEE_BUFFER = float(os.getenv("NETWORK_FEE_BUFFER", 0.1))
    NEO_TESTNET_RPC = os.getenv("NEO_TESTNET_RPC", "").strip().strip("`")


def _normalize_rpc_url(rpc_url: str) -> str:
    """Normalize RPC URL to ensure proper format."""
    parsed = urlparse(rpc_url)
    path_stripped = parsed.path.strip("/")
    netloc = parsed.netloc
    scheme = parsed.scheme or "https"
    
    # Handle port 443 in path
    if path_stripped == "443" and ":443" not in netloc:
        netloc = f"{netloc}:443"
        parsed = parsed._replace(netloc=netloc, path="/")
    
    # Ensure trailing slash
    if not parsed.path:
        parsed = parsed._replace(path="/")
    
    return urlunparse(parsed)


def _rpc_call(rpc_url: str, method: str, params: list) -> dict:
    """
    Make JSON-RPC call to Neo N3 node.
    
    Args:
        rpc_url: Neo N3 RPC endpoint
        method: RPC method name
        params: Method parameters
    
    Returns:
        JSON response as dict
    """
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    }).encode()
    
    req = Request(rpc_url, data=payload, headers={"Content-Type": "application/json"})
    
    # Build SSL context
    try:
        import certifi
        context = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        context = ssl.create_default_context()
    
    with urlopen(req, context=context) as resp:
        data = resp.read()
    
    return json.loads(data)


def _get_gas_balance(rpc_url: str, address: str) -> float:
    """
    Get GAS balance for a Neo N3 address.
    
    Args:
        rpc_url: Neo N3 RPC endpoint
        address: Neo N3 address (Nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
    
    Returns:
        GAS balance as float
    
    Raises:
        RuntimeError: If RPC call fails
    """
    res = _rpc_call(rpc_url, "getnep17balances", [address])
    
    if "error" in res:
        raise RuntimeError(f"RPC error: {res['error']}")
    
    # Extract balances from response
    result = res.get("result", {})
    balances = result.get("balances") or result.get("balance") or []
    
    # Find GAS token
    for balance_entry in balances:
        symbol = balance_entry.get("symbol") or ""
        if symbol.upper() == GAS_SYMBOL:
            amount_raw = int(balance_entry.get("amount", "0"))
            decimals = int(balance_entry.get("decimals", 8))
            return amount_raw / (10 ** decimals)
    
    return 0.0


async def check_balance(client_address: str, job_amount: float) -> Dict:
    """
    Check if client has sufficient GAS balance for job payment + fees.
    
    This is the main entry point for the Banker agent. Call this before
    creating a blockchain transaction to validate the client can afford it.
    
    Args:
        client_address: Neo N3 wallet address of the client
        job_amount: Amount of GAS to be paid for the job
    
    Returns:
        Dict containing:
            - sufficient (bool): True if balance covers job_amount + fees
            - balance (float): Current GAS balance
            - required (float): Total amount needed (job + fee buffer)
            - error (Optional[str]): Error message if check failed
    
    Example:
        >>> result = await check_balance("NXXXabc123...", 5.0)
        >>> if result["sufficient"]:
        ...     print("Balance OK")
        >>> else:
        ...     print(f"Insufficient: need {result['required']}, have {result['balance']}")
    """
    try:
        # Get RPC URL from config
        rpc_url = BankerConfig.NEO_TESTNET_RPC
        if not rpc_url:
            return {
                "sufficient": False,
                "balance": 0.0,
                "required": job_amount + BankerConfig.NETWORK_FEE_BUFFER,
                "error": "NEO_TESTNET_RPC not configured in .env"
            }
        
        # Normalize RPC URL
        rpc_url = _normalize_rpc_url(rpc_url)
        
        # Get current balance
        balance = _get_gas_balance(rpc_url, client_address)
        
        # Calculate required amount (job + network fee buffer)
        required = job_amount + BankerConfig.NETWORK_FEE_BUFFER
        
        # Check sufficiency
        sufficient = balance >= required
        
        return {
            "sufficient": sufficient,
            "balance": balance,
            "required": required,
            "error": None
        }
    
    except Exception as e:
        # Return error state
        return {
            "sufficient": False,
            "balance": 0.0,
            "required": job_amount + BankerConfig.NETWORK_FEE_BUFFER,
            "error": str(e)
        }


# Sync version for non-async contexts
def check_balance_sync(client_address: str, job_amount: float) -> Dict:
    """
    Synchronous version of check_balance.
    
    See check_balance() for full documentation.
    """
    try:
        rpc_url = BankerConfig.NEO_TESTNET_RPC
        if not rpc_url:
            return {
                "sufficient": False,
                "balance": 0.0,
                "required": job_amount + BankerConfig.NETWORK_FEE_BUFFER,
                "error": "NEO_TESTNET_RPC not configured in .env"
            }
        
        rpc_url = _normalize_rpc_url(rpc_url)
        balance = _get_gas_balance(rpc_url, client_address)
        required = job_amount + BankerConfig.NETWORK_FEE_BUFFER
        sufficient = balance >= required
        
        return {
            "sufficient": sufficient,
            "balance": balance,
            "required": required,
            "error": None
        }
    
    except Exception as e:
        return {
            "sufficient": False,
            "balance": 0.0,
            "required": job_amount + BankerConfig.NETWORK_FEE_BUFFER,
            "error": str(e)
        }
