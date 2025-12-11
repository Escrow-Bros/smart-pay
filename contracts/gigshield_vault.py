from typing import Any
from boa3.sc.compiletime import public
from boa3.sc.types import UInt160
from boa3.sc.runtime import calling_script_hash, check_witness, executing_script_hash
from boa3.sc.storage import (
    get_uint160,
    put_uint160,
    get_int,
    put_int,
    get_str,
    put_str,
)
from boa3.sc.contracts import GasToken, StdLib
from boa3.sc.utils import CreateNewEvent

# Job Status Constants
STATUS_NONE = 0
STATUS_OPEN = 1
STATUS_LOCKED = 2
STATUS_COMPLETED = 3
STATUS_DISPUTED = 4
STATUS_REFUNDED = 5

# Events
on_job_created = CreateNewEvent(
    [
        ('job_id', int),
        ('client', UInt160),
        ('amount', int),
        ('reference_urls', str)
    ],
    'JobCreated'
)

on_worker_assigned = CreateNewEvent(
    [
        ('job_id', int),
        ('worker', UInt160)
    ],
    'WorkerAssigned'
)

on_funds_released = CreateNewEvent(
    [
        ('job_id', int),
        ('worker', UInt160),
        ('worker_amount', int),
        ('fee_amount', int),
        ('treasury', UInt160)
    ],
    'FundsReleased'
)

on_funds_refunded = CreateNewEvent(
    [
        ('job_id', int),
        ('client', UInt160),
        ('amount', int),
        ('arbiter', UInt160)
    ],
    'FundsRefunded'
)

on_dispute_resolved = CreateNewEvent(
    [
        ('job_id', int),
        ('resolution', str),
        ('arbiter', UInt160)
    ],
    'DisputeResolved'
)

def _key(field: bytes, job_id: int) -> bytes:
    """Generate storage key for job data"""
    return field + StdLib.serialize(job_id)

@public
def _deploy(data: Any, update: bool):
    """
    Initialize contract storage on deployment.
    Sets the deployer as owner and initializes default values.
    
    :param data: Can contain initialization data [agent_addr, treasury_addr, fee_bps]
    :param update: True if contract is being updated
    """
    if not update:
        # Initialize default fee: 5% (500 basis points)
        put_int(b'fee_bps', 500)
        # Owner must be set via set_owner after deployment

@public
def onNEP17Payment(from_address: UInt160, amount: int, data: Any):
    """
    NEP-17 payment callback. Required to receive GAS transfers.
    This is called automatically when someone transfers GAS to this contract.
    
    :param from_address: Address sending the GAS
    :param amount: Amount of GAS being sent
    :param data: Optional data attached to the transfer
    """
    # Accept all GAS payments (for job creation)
    pass

@public
def create_job(job_id: int, client: UInt160, amount: int, details: str, reference_urls: str, latitude: int, longitude: int) -> bool:
    """
    Atomically create a job and deposit funds.
    Client must sign transaction with appropriate witness scope.
    
    :param job_id: Unique identifier for the job
    :param client: Address of the client creating the job
    :param amount: Amount of GAS to lock (in Fixed8 format: 1 GAS = 100_000_000)
    :param details: AI-generated acceptance criteria and job requirements
    :param reference_urls: Comma-separated IPFS URLs of reference images (e.g., "ipfs://abc,ipfs://def")
    :param latitude: Job location latitude * 1000000 (e.g., 37.335708 -> 37335708)
    :param longitude: Job location longitude * 1000000 (e.g., -121.886665 -> -121886665)
    :return: True if successful, False otherwise
    """
    # Validate inputs
    if amount <= 0:
        return False
    
    # Check if job already exists
    if get_int(_key(b"job_status", job_id)) != STATUS_NONE:
        return False
    
    # Verify the client is the one calling this function
    if not check_witness(client):
        return False
    
    # Transfer GAS from client to this contract (atomic operation)
    success = GasToken.transfer(client, executing_script_hash, amount, None)
    if not success:
        return False
    
    # Store job data
    put_uint160(_key(b"job_client", job_id), client)
    put_int(_key(b"job_required", job_id), amount)
    put_str(_key(b"job_details", job_id), details)
    put_str(_key(b"job_reference_urls", job_id), reference_urls)
    put_int(_key(b"job_latitude", job_id), latitude)
    put_int(_key(b"job_longitude", job_id), longitude)
    put_int(_key(b"job_status", job_id), STATUS_OPEN)
    
    # Emit event
    on_job_created(job_id, client, amount, reference_urls)
    
    return True

@public
def get_job_client(job_id: int) -> UInt160:
    return get_uint160(_key(b"job_client", job_id))

@public
def get_job_required(job_id: int) -> int:
    return get_int(_key(b"job_required", job_id))

@public
def get_job_status(job_id: int) -> int:
    return get_int(_key(b"job_status", job_id))

@public
def get_job_details(job_id: int) -> str:
    """Get the AI-generated acceptance criteria for a job"""
    return get_str(_key(b"job_details", job_id))

@public
def get_job_reference_urls(job_id: int) -> str:
    """Get comma-separated IPFS URLs of reference images"""
    return get_str(_key(b"job_reference_urls", job_id))

@public
def get_job_worker(job_id: int) -> UInt160:
    """Get the worker assigned to a job"""
    return get_uint160(_key(b"job_worker", job_id))

@public
def get_job_latitude(job_id: int) -> int:
    """Get job location latitude (scaled by 1000000)"""
    return get_int(_key(b"job_latitude", job_id))

@public
def get_job_longitude(job_id: int) -> int:
    """Get job location longitude (scaled by 1000000)"""
    return get_int(_key(b"job_longitude", job_id))

@public
def get_agent_addr() -> UInt160:
    """Get the current agent (AI Tribunal) address"""
    return get_uint160(b'agent_addr')

@public
def get_treasury_addr() -> UInt160:
    """Get the current treasury address"""
    return get_uint160(b'treasury_addr')

@public
def get_fee_bps() -> int:
    """Get the current fee in basis points (e.g., 500 = 5%)"""
    return get_int(b'fee_bps')

@public
def get_owner() -> UInt160:
    """Get the contract owner address"""
    return get_uint160(b'owner')

@public
def set_owner(new_owner: UInt160) -> bool:
    """
    Set the contract owner. Can only be called by current owner.
    Used for initial setup since we can't easily get deployer address in _deploy.
    
    :param new_owner: Address of the new owner
    :return: True if successful
    """
    current_owner = get_uint160(b'owner')
    
    # Check if owner is the zero address (not set yet)
    zero_address = UInt160()
    
    # If no owner set yet (first time), allow anyone to claim
    # Otherwise, require current owner's witness
    if current_owner != zero_address:
        if not check_witness(current_owner):
            return False
    
    put_uint160(b'owner', new_owner)
    return True

@public
def set_agent(agent: UInt160) -> bool:
    """
    Set the agent (AI Tribunal Banker) address.
    Only callable by contract owner.
    
    :param agent: Address of the agent wallet
    :return: True if successful
    """
    owner = get_uint160(b'owner')
    if not check_witness(owner):
        return False
    
    put_uint160(b'agent_addr', agent)
    return True

@public
def set_treasury(treasury: UInt160) -> bool:
    """
    Set the treasury address for fee collection.
    Only callable by contract owner.
    
    :param treasury: Address of the treasury wallet
    :return: True if successful
    """
    owner = get_uint160(b'owner')
    if not check_witness(owner):
        return False
    
    put_uint160(b'treasury_addr', treasury)
    return True

@public
def set_fee_bps(bps: int) -> bool:
    """
    Set the fee in basis points (100 bps = 1%).
    Only callable by contract owner.
    
    :param bps: Fee in basis points (e.g., 500 = 5%)
    :return: True if successful
    """
    owner = get_uint160(b'owner')
    if not check_witness(owner):
        return False
    
    # Validate reasonable fee range (0-20%)
    if bps < 0 or bps > 2000:
        return False
    
    put_int(b'fee_bps', bps)
    return True

@public
def assign_worker(job_id: int, worker: UInt160) -> bool:
    """
    Assign a worker to a job (first-come-first-served).
    Worker must sign the transaction to claim the job.
    
    :param job_id: The job to assign
    :param worker: Address of the worker claiming the job
    :return: True if successful
    """
    # Check job status - must be OPEN
    status = get_int(_key(b"job_status", job_id))
    if status != STATUS_OPEN:
        return False
    
    # Verify the worker is signing this transaction
    if not check_witness(worker):
        return False
    
    # Assign worker and lock job
    put_uint160(_key(b"job_worker", job_id), worker)
    put_int(_key(b"job_status", job_id), STATUS_LOCKED)
    
    # Emit event
    on_worker_assigned(job_id, worker)
    
    return True

@public
def release_funds(job_id: int) -> bool:
    """
    Release funds to worker and treasury after AI Tribunal verification.
    Only callable by the agent (AI Tribunal Banker).
    
    :param job_id: The job to settle
    :return: True if successful
    """
    # Verify agent signature
    agent = get_uint160(b'agent_addr')
    if not check_witness(agent):
        return False
    
    # Check job status - must be LOCKED
    status = get_int(_key(b"job_status", job_id))
    if status != STATUS_LOCKED:
        return False
    
    # Get job details
    worker = get_uint160(_key(b"job_worker", job_id))
    amount = get_int(_key(b"job_required", job_id))
    treasury = get_uint160(b'treasury_addr')
    fee_bps = get_int(b'fee_bps')
    
    # Calculate fee and worker payment
    fee_amount = amount * fee_bps // 10000
    worker_amount = amount - fee_amount
    
    # Transfer to worker
    success_worker = GasToken.transfer(executing_script_hash, worker, worker_amount, None)
    if not success_worker:
        return False
    
    # Transfer fee to treasury
    success_treasury = GasToken.transfer(executing_script_hash, treasury, fee_amount, None)
    if not success_treasury:
        return False
    
    # Mark job as completed
    put_int(_key(b"job_status", job_id), STATUS_COMPLETED)
    
    # Emit event
    on_funds_released(job_id, worker, worker_amount, fee_amount, treasury)
    
    return True

@public
def set_arbiter(arbiter: UInt160) -> bool:
    """
    Set arbiter address for dispute resolution.
    Only callable by contract owner.
    Arbiter can resolve disputed jobs by approving payment or refunding client.
    
    :param arbiter: Address of the arbiter wallet
    :return: True if successful
    """
    owner = get_uint160(b'owner')
    if not check_witness(owner):
        return False
    
    put_uint160(b'arbiter_addr', arbiter)
    return True

@public
def get_arbiter() -> UInt160:
    """Get current arbiter address"""
    return get_uint160(b'arbiter_addr')

@public
def refund_client(job_id: int) -> bool:
    """
    Refund locked funds to client after dispute resolution.
    Only callable by arbiter.
    Full refund - no platform fee on failed jobs.
    
    :param job_id: The job to refund
    :return: True if successful
    """
    # Verify arbiter signature
    arbiter = get_uint160(b'arbiter_addr')
    if not check_witness(arbiter):
        return False
    
    # Check job status - must be LOCKED or DISPUTED
    status = get_int(_key(b"job_status", job_id))
    if status != STATUS_LOCKED and status != STATUS_DISPUTED:
        return False
    
    # Get job details
    client = get_uint160(_key(b"job_client", job_id))
    amount = get_int(_key(b"job_required", job_id))
    
    # Transfer full amount back to client (no fee on refunds)
    success = GasToken.transfer(executing_script_hash, client, amount, None)
    if not success:
        return False
    
    # Mark job as refunded
    put_int(_key(b"job_status", job_id), STATUS_REFUNDED)
    
    # Emit events
    on_funds_refunded(job_id, client, amount, arbiter)
    on_dispute_resolved(job_id, 'REFUNDED', arbiter)
    
    return True

@public
def arbiter_resolve(job_id: int, approve_worker: bool) -> bool:
    """
    Arbiter manually resolves a disputed job.
    This is the human override for AI decisions.
    
    :param job_id: The job to resolve
    :param approve_worker: True to pay worker, False to refund client
    :return: True if successful
    """
    # Verify arbiter signature
    arbiter = get_uint160(b'arbiter_addr')
    if not check_witness(arbiter):
        return False
    
    # Check job status - must be LOCKED or DISPUTED
    status = get_int(_key(b"job_status", job_id))
    if status != STATUS_LOCKED and status != STATUS_DISPUTED:
        return False
    
    if approve_worker:
        # Arbiter rules in favor of WORKER
        # Get job details
        worker = get_uint160(_key(b"job_worker", job_id))
        amount = get_int(_key(b"job_required", job_id))
        treasury = get_uint160(b'treasury_addr')
        fee_bps = get_int(b'fee_bps')
        
        # Calculate fee and worker payment
        fee_amount = amount * fee_bps // 10000
        worker_amount = amount - fee_amount
        
        # Transfer to worker
        success_worker = GasToken.transfer(executing_script_hash, worker, worker_amount, None)
        if not success_worker:
            return False
        
        # Transfer fee to treasury
        success_treasury = GasToken.transfer(executing_script_hash, treasury, fee_amount, None)
        if not success_treasury:
            return False
        
        # Mark job as completed
        put_int(_key(b"job_status", job_id), STATUS_COMPLETED)
        
        # Emit events
        on_funds_released(job_id, worker, worker_amount, fee_amount, treasury)
        on_dispute_resolved(job_id, 'APPROVED', arbiter)
        
        return True
    
    # Arbiter rules in favor of CLIENT (Refund)
    return refund_client(job_id)
