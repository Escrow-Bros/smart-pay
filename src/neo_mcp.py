import asyncio
from typing import Optional, Dict, Any, List
from neo3.wallet.account import Account
from neo3.api.wrappers import ChainFacade, GenericContract
from neo3.api.helpers.signing import sign_with_account
from neo3.network.payloads.verification import Signer, WitnessScope
from neo3.core import types
from neo3.wallet import utils as wallet_utils

try:
    from .neo_config import NeoConfig
    from .exceptions import (
        TransactionFailedException,
        ContractValidationException,
        ConfigurationException
    )
except ImportError:
    from neo_config import NeoConfig
    from exceptions import (
        TransactionFailedException,
        ContractValidationException,
        ConfigurationException
    )


# Job status constants (must match contract)
STATUS_NONE = 0
STATUS_OPEN = 1
STATUS_LOCKED = 2
STATUS_COMPLETED = 3
STATUS_DISPUTED = 4
STATUS_REFUNDED = 5

STATUS_NAMES = {
    0: "NONE",
    1: "OPEN",
    2: "LOCKED",
    3: "COMPLETED",
    4: "DISPUTED",
    5: "REFUNDED"
}


class NeoMCP:
    def __init__(self, config: Optional[NeoConfig] = None):
        """
        Initialize Neo MCP wrapper
        
        Args:
            config: Optional NeoConfig instance. If None, uses singleton.
        """
        self.config = config or NeoConfig.get_instance()
        self.contract_hash = types.UInt160.from_string(
            self.config.contract_hash.replace("0x", "")
        )
        self.contract = GenericContract(self.contract_hash)
        self._facade_cache: Dict[str, ChainFacade] = {}
    
    def _get_facade(self, role: str) -> ChainFacade:
        """
        Get or create a ChainFacade for a specific role with signing configured.
        Cached to avoid recreating connections.
        
        Args:
            role: One of 'agent', 'client', 'worker', 'deployer', 'treasury'
        
        Returns:
            Configured ChainFacade instance
        """
        if role in self._facade_cache:
            return self._facade_cache[role]
        
        # Load account for role
        wif = self.config.get_account_wif(role)
        account = Account.from_wif(wif)
        
        # Create facade
        facade = ChainFacade(self.config.rpc_url, receipt_timeout=30.0)
        facade.add_signer(
            sign_with_account(account),
            Signer(account.script_hash, scope=WitnessScope.GLOBAL)
        )
        
        self._facade_cache[role] = facade
        return facade
    
    def _get_read_facade(self) -> ChainFacade:
        """Get facade for read-only operations (no signing needed)"""
        if 'readonly' not in self._facade_cache:
            self._facade_cache['readonly'] = ChainFacade(self.config.rpc_url)
        return self._facade_cache['readonly']
    
    # ==================== READ OPERATIONS ====================
    
    async def get_job_status(self, job_id: int) -> Dict[str, Any]:
        """
        Get job status from blockchain.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Dict with status code and name
        """
        facade = self._get_read_facade()
        receipt = await facade.test_invoke(
            self.contract.call_function("get_job_status", [job_id])
        )
        
        status_code = receipt.result.stack[0].value
        return {
            "job_id": job_id,
            "status_code": status_code,
            "status_name": STATUS_NAMES.get(status_code, "UNKNOWN")
        }
    
    async def get_job_details(self, job_id: int) -> Dict[str, Any]:
        """
        Get full job details from blockchain for AI verification.
        Agent uses this to verify task completion.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Dict with all job information
        """
        facade = self._get_read_facade()
        
        # Parallel reads for efficiency
        status_result, client_result, worker_result, amount_result, \
        details_result, urls_result = await asyncio.gather(
            facade.test_invoke(self.contract.call_function("get_job_status", [job_id])),
            facade.test_invoke(self.contract.call_function("get_job_client", [job_id])),
            facade.test_invoke(self.contract.call_function("get_job_worker", [job_id])),
            facade.test_invoke(self.contract.call_function("get_job_required", [job_id])),
            facade.test_invoke(self.contract.call_function("get_job_details", [job_id])),
            facade.test_invoke(self.contract.call_function("get_job_reference_urls", [job_id]))
        )
        
        # Parse results
        status_code = status_result.result.stack[0].value
        # Fix: Convert bytes to UInt160 properly
        client_bytes = client_result.result.stack[0].value
        worker_bytes = worker_result.result.stack[0].value
        client_hash = types.UInt160(data=bytes(client_bytes)) if client_bytes else types.UInt160.zero()
        worker_hash = types.UInt160(data=bytes(worker_bytes)) if worker_bytes else types.UInt160.zero()
        amount = amount_result.result.stack[0].value
        details = details_result.result.stack[0].value.decode('utf-8') if details_result.result.stack[0].value else ""
        urls = urls_result.result.stack[0].value.decode('utf-8') if urls_result.result.stack[0].value else ""
        
        # Convert addresses
        client_addr = wallet_utils.script_hash_to_address(client_hash)
        worker_addr = wallet_utils.script_hash_to_address(worker_hash)
        
        return {
            "job_id": job_id,
            "status_code": status_code,
            "status_name": STATUS_NAMES.get(status_code, "UNKNOWN"),
            "client_address": client_addr,
            "worker_address": worker_addr,
            "amount_locked": amount,
            "amount_gas": amount / 100_000_000,  # Convert to GAS
            "details": details,
            "reference_urls": urls.split(",") if urls else []
        }
    
    async def get_contract_config(self) -> Dict[str, Any]:
        """
        Get contract configuration (owner, agent, treasury, fee).
        
        Returns:
            Dict with contract settings
        """
        facade = self._get_read_facade()
        
        owner_result, agent_result, treasury_result, fee_result = await asyncio.gather(
            facade.test_invoke(self.contract.call_function("get_owner", [])),
            facade.test_invoke(self.contract.call_function("get_agent_addr", [])),
            facade.test_invoke(self.contract.call_function("get_treasury_addr", [])),
            facade.test_invoke(self.contract.call_function("get_fee_bps", []))
        )
        
        owner_hash = types.UInt160(owner_result.result.stack[0].value)
        agent_hash = types.UInt160(agent_result.result.stack[0].value)
        treasury_hash = types.UInt160(treasury_result.result.stack[0].value)
        fee_bps = fee_result.result.stack[0].value
        
        return {
            "owner": wallet_utils.script_hash_to_address(owner_hash),
            "agent": wallet_utils.script_hash_to_address(agent_hash),
            "treasury": wallet_utils.script_hash_to_address(treasury_hash),
            "fee_bps": fee_bps,
            "fee_percentage": fee_bps / 100
        }
    
    # ==================== WRITE OPERATIONS ====================
    
    async def create_job_on_chain(
        self,
        client_address: str,
        description: str,
        reference_photos: List[str],
        amount: float
    ) -> Dict[str, Any]:
        """
        Create a new job and lock funds atomically (API-friendly).
        
        Args:
            client_address: Client Neo N3 address
            description: Job description (used as details)
            reference_photos: List of IPFS URLs for reference images
            amount: Amount in GAS to lock (e.g., 10.0 for 10 GAS)
        
        Returns:
            Dict with transaction result and job_id
        """
        import time
        
        # Generate job_id from timestamp
        job_id = int(time.time())
        
        # Pre-validation: Check if job already exists
        existing = await self.get_job_status(job_id)
        if existing['status_code'] != STATUS_NONE:
            # Retry with incremented ID
            job_id += 1
        
        # Find which role has this address
        client_role = None
        for role in ['client', 'worker', 'agent', 'deployer', 'treasury']:
            if self.config.get_account_addr(role) == client_address:
                client_role = role
                break
        
        if not client_role:
            return {
                "success": False,
                "error": f"Address {client_address} not found in wallet configuration",
                "job_id": job_id
            }
        
        client_script_hash = wallet_utils.address_to_script_hash(client_address)
        
        # Convert GAS to Fixed8 format (1 GAS = 100_000_000)
        amount_int = int(amount * 100_000_000)
        
        # Format reference URLs
        urls_str = ",".join(reference_photos)
        
        # Get facade with client signing
        facade = self._get_facade(client_role)
        
        try:
            # Invoke transaction (fast - doesn't wait for receipt)
            tx_hash = await facade.invoke_fast(
                self.contract.call_function(
                    "create_job",
                    [job_id, client_script_hash, amount_int, description, urls_str]
                )
            )
            
            return {
                "success": True,
                "tx_hash": str(tx_hash),
                "job_id": job_id,
                "client": client_address,
                "amount": amount,
                "note": "Transaction sent. Wait ~15s then check status."
            }
        
        except TransactionFailedException:
            raise
        except Exception as e:
            raise TransactionFailedException(f"Failed to create job: {str(e)}")
    
    async def assign_worker_on_chain(
        self,
        job_id: int,
        worker_address: str
    ) -> Dict[str, Any]:
        """
        Assign worker to a job (first-come-first-served, API-friendly).
        
        Args:
            job_id: Job to claim
            worker_address: Worker Neo N3 address
        
        Returns:
            Dict with transaction result
        """
        # Pre-validation: Check job is OPEN
        status = await self.get_job_status(job_id)
        if status['status_code'] != STATUS_OPEN:
            return {
                "success": False,
                "error": f"Job must be OPEN to assign worker. Current: {status['status_name']}",
                "job_id": job_id,
                "current_status": status['status_name']
            }
        
        # Find which role has this address
        worker_role = None
        for role in ['worker', 'client', 'agent', 'deployer', 'treasury']:
            if self.config.get_account_addr(role) == worker_address:
                worker_role = role
                break
        
        if not worker_role:
            return {
                "success": False,
                "error": f"Address {worker_address} not found in wallet configuration",
                "job_id": job_id
            }
        
        worker_script_hash = wallet_utils.address_to_script_hash(worker_address)
        
        # Get facade with worker signing
        facade = self._get_facade(worker_role)
        
        try:
            tx_hash = await facade.invoke_fast(
                self.contract.call_function("assign_worker", [job_id, worker_script_hash])
            )
            
            return {
                "success": True,
                "tx_hash": str(tx_hash),
                "job_id": job_id,
                "worker": worker_address,
                "note": "Transaction sent. Wait ~15s then check status."
            }
        
        except TransactionFailedException:
            raise
        except Exception as e:
            raise TransactionFailedException(f"Failed to assign worker: {str(e)}")
    
    async def release_funds_on_chain(self, job_id: int) -> Dict[str, Any]:
        """
        Release funds to worker after AI Tribunal verification.
        Only callable by AGENT role.
        
        This is the core method for TASK-015: Agent verifies task completion
        from blockchain data and releases payment.
        
        Args:
            job_id: Job to settle
        
        Returns:
            Dict with transaction result including payment breakdown
        """
        # Pre-validation: Get job details for verification
        job_details = await self.get_job_details(job_id)
        
        # Check job is LOCKED (worker assigned, work in progress)
        if job_details['status_code'] != STATUS_LOCKED:
            return {
                "success": False,
                "error": f"Job must be LOCKED to release funds. Current: {job_details['status_name']}",
                "job_id": job_id,
                "current_status": job_details['status_name'],
                "job_details": job_details
            }
        
        # Get contract config for fee calculation
        config = await self.get_contract_config()
        
        # Calculate payment breakdown
        total_amount = job_details['amount_locked']
        fee_amount = total_amount * config['fee_bps'] // 10000
        worker_amount = total_amount - fee_amount
        
        # Get agent facade (requires agent signature)
        facade = self._get_facade('agent')
        
        try:
            tx_hash = await facade.invoke_fast(
                self.contract.call_function("release_funds", [job_id])
            )
            
            return {
                "success": True,
                "tx_hash": str(tx_hash),
                "job_id": job_id,
                "worker": job_details['worker_address'],
                "worker_paid_gas": worker_amount / 100_000_000,
                "fee_collected_gas": fee_amount / 100_000_000,
                "treasury": config['treasury'],
                "note": "Transaction sent. Funds will be transferred once confirmed.",
                "job_details": job_details
            }
        
        except TransactionFailedException:
            raise
        except Exception as e:
            raise TransactionFailedException(f"Failed to release funds: {str(e)}")
    
    async def refund_client_on_chain(self, job_id: int, arbiter_role: str = 'agent') -> Dict[str, Any]:
        """
        Refund locked funds to client after dispute resolution.
        Only callable by arbiter role.
        
        Args:
            job_id: Job to refund
            arbiter_role: Role with arbiter permissions (default: 'agent')
        
        Returns:
            Dict with transaction result
        """
        # Pre-validation: Get job details
        job_details = await self.get_job_details(job_id)
        
        # Check job is LOCKED or DISPUTED
        if job_details['status_code'] not in [STATUS_LOCKED, STATUS_DISPUTED]:
            return {
                "success": False,
                "error": f"Job must be LOCKED or DISPUTED to refund. Current: {job_details['status_name']}",
                "job_id": job_id,
                "current_status": job_details['status_name']
            }
        
        # Get arbiter facade
        facade = self._get_facade(arbiter_role)
        
        try:
            tx_hash = await facade.invoke_fast(
                self.contract.call_function("refund_client", [job_id])
            )
            
            return {
                "success": True,
                "tx_hash": str(tx_hash),
                "job_id": job_id,
                "client": job_details['client_address'],
                "refunded_amount_gas": job_details['amount_locked'] / 100_000_000,
                "note": "Transaction sent. Full refund (no fee) will be processed.",
                "job_details": job_details
            }
        
        except TransactionFailedException:
            raise
        except Exception as e:
            raise TransactionFailedException(f"Failed to refund client: {str(e)}")
    
    async def arbiter_resolve_on_chain(
        self,
        job_id: int,
        approve_worker: bool,
        arbiter_role: str = 'agent'
    ) -> Dict[str, Any]:
        """
        Arbiter manually resolves a disputed job.
        This is the human override for AI decisions.
        
        Args:
            job_id: Job to resolve
            approve_worker: True to pay worker, False to refund client
            arbiter_role: Role with arbiter permissions (default: 'agent')
        
        Returns:
            Dict with transaction result and payment breakdown
        """
        # Pre-validation: Get job details
        job_details = await self.get_job_details(job_id)
        
        # Check job is LOCKED or DISPUTED
        if job_details['status_code'] not in [STATUS_LOCKED, STATUS_DISPUTED]:
            return {
                "success": False,
                "error": f"Job must be LOCKED or DISPUTED to resolve. Current: {job_details['status_name']}",
                "job_id": job_id,
                "current_status": job_details['status_name']
            }
        
        # Get contract config for fee calculation
        config = await self.get_contract_config()
        
        # Calculate payment breakdown
        total_amount = job_details['amount_locked']
        fee_amount = total_amount * config['fee_bps'] // 10000
        worker_amount = total_amount - fee_amount
        
        # Get arbiter facade
        facade = self._get_facade(arbiter_role)
        
        try:
            tx_hash = await facade.invoke_fast(
                self.contract.call_function("arbiter_resolve", [job_id, approve_worker])
            )
            
            if approve_worker:
                return {
                    "success": True,
                    "tx_hash": str(tx_hash),
                    "job_id": job_id,
                    "resolution": "APPROVED",
                    "worker": job_details['worker_address'],
                    "worker_paid_gas": worker_amount / 100_000_000,
                    "fee_collected_gas": fee_amount / 100_000_000,
                    "treasury": config['treasury'],
                    "note": "Arbiter approved work. Funds released to worker.",
                    "job_details": job_details
                }
            else:
                return {
                    "success": True,
                    "tx_hash": str(tx_hash),
                    "job_id": job_id,
                    "resolution": "REFUNDED",
                    "client": job_details['client_address'],
                    "refunded_amount_gas": total_amount / 100_000_000,
                    "note": "Arbiter refunded client. Full refund (no fee).",
                    "job_details": job_details
                }
        
        except TransactionFailedException:
            raise
        except Exception as e:
            raise TransactionFailedException(f"Failed to resolve dispute: {str(e)}")
