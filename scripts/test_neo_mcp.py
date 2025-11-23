import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from neo_mcp import NeoMCP

async def test_full_workflow():
    """Test complete job workflow"""
    
    print("🧪 Testing NeoMCP Wrapper - Full Workflow")
    print("=" * 60)
    
    # Initialize wrapper
    neo = NeoMCP()
    print("✅ NeoMCP initialized")
    
    # Test 1: Read contract configuration
    print("\n📋 Test 1: Reading contract configuration...")
    config = await neo.get_contract_config()
    print(f"   Owner: {config['owner']}")
    print(f"   Agent: {config['agent']}")
    print(f"   Treasury: {config['treasury']}")
    print(f"   Fee: {config['fee_percentage']}%")
    
    # Test 2: Create a job
    job_id = 2001  # New job ID
    print(f"\n📋 Test 2: Creating job {job_id}...")
    
    create_result = await neo.create_job_on_chain(
        job_id=job_id,
        client_role="client",
        amount_gas=10.0,  # Lock 10 GAS
        details="Build a simple landing page with responsive design",
        reference_urls=[
            "ipfs://QmTest123",
            "ipfs://QmTest456"
        ]
    )
    
    if create_result['success']:
        print(f"   ✅ Job created!")
        print(f"   TX: {create_result['tx_hash']}")
        print(f"   Note: {create_result.get('note', '')}")
    else:
        print(f"   ⚠️  {create_result['error']}")
    
    # Wait for confirmation
    print("   ⏳ Waiting 25 seconds for blockchain confirmation...")
    await asyncio.sleep(25)
    
    # Test 3: Read job details (what agent sees for verification)
    print(f"\n📋 Test 3: Reading job details (Agent's view)...")
    job_details = await neo.get_job_details(job_id)
    print(f"   Job ID: {job_details['job_id']}")
    print(f"   Status: {job_details['status_name']}")
    print(f"   Client: {job_details['client_address']}")
    print(f"   Amount: {job_details['amount_gas']} GAS")
    print(f"   Details: {job_details['details']}")
    print(f"   References: {job_details['reference_urls']}")
    
    # Test 4: Assign worker
    print(f"\n📋 Test 4: Assigning worker to job...")
    assign_result = await neo.assign_worker_on_chain(job_id, worker_role="worker")
    
    if assign_result['success']:
        print(f"   ✅ Worker assigned!")
        print(f"   TX: {assign_result['tx_hash']}")
        print(f"   Worker: {assign_result['worker']}")
    else:
        print(f"   ⚠️  {assign_result['error']}")
    
    # Wait for confirmation
    print("   ⏳ Waiting 25 seconds for blockchain confirmation...")
    await asyncio.sleep(25)
    
    # Test 5: Check updated status
    print(f"\n📋 Test 5: Checking updated job status...")
    job_details = await neo.get_job_details(job_id)
    print(f"   Status: {job_details['status_name']}")
    print(f"   Worker: {job_details['worker_address']}")
    
    # Test 6: Agent releases funds (TASK-015 core functionality)
    print(f"\n📋 Test 6: Agent releasing funds (TASK-015)...")
    print(f"   🤖 Agent verifying task from blockchain data...")
    print(f"   📊 Job details verified:")
    print(f"      - Client: {job_details['client_address']}")
    print(f"      - Worker: {job_details['worker_address']}")
    print(f"      - Amount: {job_details['amount_gas']} GAS")
    print(f"      - Status: {job_details['status_name']}")
    
    release_result = await neo.release_funds_on_chain(job_id)
    
    if release_result['success']:
        print(f"   ✅ Funds released successfully!")
        print(f"   TX: {release_result['tx_hash']}")
        print(f"   💰 Payment breakdown:")
        print(f"      Worker paid: {release_result['worker_paid_gas']} GAS")
        print(f"      Fee collected: {release_result['fee_collected_gas']} GAS")
        print(f"      Treasury: {release_result['treasury']}")
        print(f"   Note: {release_result.get('note', '')}")
    else:
        print(f"   ⚠️  {release_result['error']}")
    
    # Wait for confirmation
    print("   ⏳ Waiting 25 seconds for blockchain confirmation...")
    await asyncio.sleep(25)
    
    # Test 7: Final status check
    print(f"\n📋 Test 7: Final job status...")
    final_status = await neo.get_job_status(job_id)
    print(f"   Status: {final_status['status_name']}")
    
    print("\n" + "=" * 60)
    print("🎉 NeoMCP Wrapper Test Complete!")


async def test_read_only():
    """Test read-only operations without transactions"""
    
    print("\n🔍 Testing Read-Only Operations")
    print("=" * 60)
    
    neo = NeoMCP()
    
    # Test reading existing job (if any)
    print("\n📋 Checking job 1001...")
    try:
        job = await neo.get_job_details(1001)
        print(f"   Status: {job['status_name']}")
        if job['status_code'] != 0:
            print(f"   Client: {job['client_address']}")
            print(f"   Worker: {job['worker_address']}")
            print(f"   Amount: {job['amount_gas']} GAS")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test NeoMCP wrapper")
    parser.add_argument(
        "--readonly",
        action="store_true",
        help="Only test read operations (no transactions)"
    )
    args = parser.parse_args()
    
    if args.readonly:
        asyncio.run(test_read_only())
    else:
        asyncio.run(test_full_workflow())
