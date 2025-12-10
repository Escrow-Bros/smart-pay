"""SSL context helpers for Neo N3 testnet deployment scripts.

Provides secure, environment-aware SSL configuration that:
- Enforces SSL verification by default
- Only allows insecure mode for explicit testnet environments
- Fails fast in production to prevent MITM vulnerabilities
"""

import ssl
import os
import sys


def create_testnet_ssl_context():
    """Create SSL context for testnet with optional verification bypass.
    
    Returns:
        ssl.SSLContext: Configured context for RPC client usage
        
    Raises:
        SystemExit: If attempting to disable SSL in production environment
    """
    # Check if we're explicitly in testnet environment
    env_mode = os.getenv('NETWORK_MODE', 'testnet').lower()
    allow_insecure = os.getenv('TESTNET_ALLOW_INSECURE', 'false').lower() == 'true'
    
    # Fail-safe: refuse to disable SSL in production
    if env_mode == 'production':
        print("ERROR: Cannot disable SSL verification in production mode")
        print("   Set NETWORK_MODE=testnet if you need insecure SSL for testing")
        sys.exit(1)
    
    if allow_insecure and env_mode == 'testnet':
        print("WARNING: SSL verification disabled for testnet (TESTNET_ALLOW_INSECURE=true)")
        print("   This should NEVER be used in production environments")
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    else:
        # Use default SSL verification
        return ssl.create_default_context()
