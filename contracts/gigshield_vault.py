from boa3.sc.compiletime import public
from boa3.sc.types import UInt160
from boa3.sc.runtime import calling_script_hash, check_witness, executing_script_hash
from boa3.sc.storage import (
    get_uint160,
    put_uint160,
    get_int,
    put_int,
)
from boa3.sc.contracts import GasToken, StdLib
from boa3.sc.utils import CreateNewEvent

# Job Status Constants
STATUS_NONE = 0
STATUS_OPEN = 1
STATUS_LOCKED = 2
STATUS_COMPLETED = 3
STATUS_DISPUTED = 4

# Events
on_job_created = CreateNewEvent(
    [
        ('job_id', int),
        ('client', UInt160),
        ('amount', int)
    ],
    'JobCreated'
)

on_deposit = CreateNewEvent(
    [
        ('job_id', int),
        ('from_address', UInt160),
        ('amount', int)
    ],
    'Deposit'
)

def _key(field: bytes, job_id: int) -> bytes:
    """Generate storage key for job data"""
    return field + StdLib.serialize(job_id)

@public
def create_job(job_id: int, client: UInt160, amount: int) -> bool:
    """
    Atomically create a job and deposit funds.
    Client must sign transaction with appropriate witness scope.
    
    :param job_id: Unique identifier for the job
    :param client: Address of the client creating the job
    :param amount: Amount of GAS to lock (in Fixed8 format: 1 GAS = 100_000_000)
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
    put_int(_key(b"job_deposited", job_id), amount)
    put_int(_key(b"job_status", job_id), STATUS_OPEN)
    
    # Emit event
    on_job_created(job_id, client, amount)
    
    return True

def onNEP17Payment(from_addr: UInt160, amount: int, data: int):
    """
    Fallback to handle direct GAS transfers (for topping up existing jobs).
    This allows clients to add more funds to a job if needed.
    """
    # Only accept GAS token
    if calling_script_hash != GasToken.hash:
        return
    
    job_id = data
    
    # Check if job exists and is still open
    status = get_int(_key(b"job_status", job_id))
    if status == STATUS_NONE:
        return
    
    # Update deposited amount
    deposited = get_int(_key(b"job_deposited", job_id))
    put_int(_key(b"job_deposited", job_id), deposited + amount)
    
    # Emit event
    on_deposit(job_id, from_addr, amount)

@public
def get_job_client(job_id: int) -> UInt160:
    return get_uint160(_key(b"job_client", job_id))

@public
def get_job_required(job_id: int) -> int:
    return get_int(_key(b"job_required", job_id))

@public
def get_job_deposited(job_id: int) -> int:
    return get_int(_key(b"job_deposited", job_id))

@public
def get_job_status(job_id: int) -> int:
    return get_int(_key(b"job_status", job_id))
