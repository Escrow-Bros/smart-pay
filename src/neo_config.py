from pathlib import Path
from typing import Optional


class NeoConfig:
    _instance: Optional['NeoConfig'] = None
    
    def __init__(self, env_path: Optional[Path] = None):
        if NeoConfig._instance is not None:
            raise RuntimeError("NeoConfig is a singleton. Use get_instance() instead.")
        
        self.env_path = env_path or Path(__file__).resolve().parents[1] / ".env"
        self._load_env()
    
    @classmethod
    def get_instance(cls, env_path: Optional[Path] = None) -> 'NeoConfig':
        """Get or create singleton instance"""
        if cls._instance is None:
            instance = cls.__new__(cls)
            instance.env_path = env_path or Path(__file__).resolve().parents[1] / ".env"
            instance._load_env()
            cls._instance = instance
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset singleton (useful for testing)"""
        cls._instance = None
    
    def _load_env(self):
        """Load environment variables from .env file"""
        if not self.env_path.exists():
            raise FileNotFoundError(f"Environment file not found: {self.env_path}")
        
        env = {}
        for line in self.env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
        
        # Required settings
        self.rpc_url = self._get_required(env, "NEO_TESTNET_RPC")
        self.contract_hash = self._get_required(env, "VAULT_CONTRACT_HASH")
        
        # Account credentials
        self.deployer_wif = env.get("DEPLOYER_WIF")
        self.deployer_addr = env.get("DEPLOYER_ADDR")
        self.agent_wif = env.get("AGENT_WIF")
        self.agent_addr = env.get("AGENT_ADDR")
        self.client_wif = env.get("CLIENT_WIF")
        self.client_addr = env.get("CLIENT_ADDR")
        self.worker_wif = env.get("WORKER_WIF")
        self.worker_addr = env.get("WORKER_ADDR")
        self.treasury_wif = env.get("TREASURY_WIF")
        self.treasury_addr = env.get("TREASURY_ADDR")
    
    def _get_required(self, env: dict, key: str) -> str:
        """Get required environment variable or raise error"""
        value = env.get(key)
        if not value:
            raise ValueError(f"Required environment variable not found: {key}")
        return value
    
    def get_account_wif(self, role: str) -> str:
        """Get WIF for a specific role (deployer, agent, client, worker, treasury)"""
        wif = getattr(self, f"{role.lower()}_wif", None)
        if not wif:
            raise ValueError(f"WIF not found for role: {role}")
        return wif
    
    def get_account_addr(self, role: str) -> str:
        """Get address for a specific role"""
        addr = getattr(self, f"{role.lower()}_addr", None)
        if not addr:
            raise ValueError(f"Address not found for role: {role}")
        return addr
