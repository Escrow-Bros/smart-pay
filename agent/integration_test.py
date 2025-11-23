"""
GigShield Agent Integration Test
Demonstrates complete flow: Paralegal → Smart Contract → Eye

Flow:
1. Client creates job with description + reference photo
2. Paralegal validates and generates verification plan
3. Smart contract stores job data (simulated)
4. Worker completes task and submits proof
5. Eye agent verifies using Paralegal's plan
6. Decision: Approve or Reject
"""
import asyncio
import json
from paralegal import analyze_job_request
from eye import verify_work

# Simulated smart contract storage
SMART_CONTRACT_DB = {}

async def simulate_job_creation(job_description: str, reference_image_bytes: bytes) -> dict:
    """
    PHASE 1: CLIENT CREATES JOB
    
    This simulates the job creation flow where:
    - Client submits description + reference photo
    - Paralegal validates and processes
    - Data is stored in smart contract
    """
    print("=" * 70)
    print("PHASE 1: JOB CREATION (CLIENT SIDE)")
    print("=" * 70)
    print(f"\n📝 Client submits job:")
    print(f"   Description: \"{job_description}\"")
    print(f"   Reference photo: {len(reference_image_bytes)} bytes")
    print()
    
    # Call Paralegal agent
    print("🤖 Calling Paralegal Agent...")
    paralegal_result = await analyze_job_request(job_description, reference_image_bytes)
    
    print(f"   Status: {paralegal_result['status']}")
    
    if paralegal_result['status'] == 'needs_clarification':
        print("\n❌ Job creation FAILED - needs clarification")
        print("   Questions:")
        for q in paralegal_result['clarifying_questions']:
            print(f"   - {q}")
        return None
    
    if paralegal_result['status'] == 'mismatch':
        print("\n❌ Job creation FAILED - image mismatch")
        print(f"   Reason: {paralegal_result['validation']['mismatch_details']}")
        return None
    
    # Success! Extract job data
    job_data = paralegal_result['data']
    verification_plan = paralegal_result['verification_plan']
    acceptance_criteria = paralegal_result['acceptance_criteria']
    reference_analysis = paralegal_result['reference_analysis']
    
    print("\n✅ Paralegal validation PASSED")
    print(f"   Task: {job_data.get('task')}")
    print(f"   Location: {job_data.get('location')}")
    print(f"   Price: {job_data.get('price_amount')} {job_data.get('price_currency')}")
    print(f"   Category: {verification_plan.get('task_category')}")
    
    # Generate job ID
    job_id = f"job_{len(SMART_CONTRACT_DB) + 1}"
    
    # Store in "smart contract"
    SMART_CONTRACT_DB[job_id] = {
        "job_id": job_id,
        "client": "0xClient123...",
        "description": job_description,
        "task": job_data.get('task'),
        "location": job_data.get('location'),
        "price_amount": job_data.get('price_amount'),
        "price_currency": job_data.get('price_currency'),
        "reference_photos": ["ipfs://Qm.../reference.jpg"],  # Simulated IPFS URL
        "verification_plan": verification_plan,  # ← FROM PARALEGAL
        "acceptance_criteria": acceptance_criteria,  # ← FROM PARALEGAL
        "reference_analysis": reference_analysis,  # ← FROM PARALEGAL
        "status": "OPEN",
        "worker": None
    }
    
    print(f"\n💾 Job stored in smart contract:")
    print(f"   Job ID: {job_id}")
    print(f"   Status: OPEN")
    
    print(f"\n📋 Verification Plan Generated:")
    print(f"   Quality Indicators: {len(verification_plan.get('quality_indicators', []))} items")
    print(f"   Verification Checklist: {len(verification_plan.get('verification_checklist', []))} checks")
    print(f"   Required Evidence: {len(verification_plan.get('required_evidence', []))} requirements")
    
    return {
        "job_id": job_id,
        "job_data": SMART_CONTRACT_DB[job_id]
    }

async def simulate_work_verification(job_id: str, proof_photos: list, worker_address: str) -> dict:
    """
    PHASE 2: WORK VERIFICATION (WORKER SUBMITS PROOF)
    
    This simulates:
    - Worker submits proof photos
    - Eye agent fetches job data from contract
    - Eye uses Paralegal's verification plan
    - Decision is made
    """
    print("\n" + "=" * 70)
    print("PHASE 2: WORK VERIFICATION (WORKER SIDE)")
    print("=" * 70)
    print(f"\n👷 Worker submits proof:")
    print(f"   Job ID: {job_id}")
    print(f"   Worker: {worker_address}")
    print(f"   Proof photos: {len(proof_photos)} photo(s)")
    for i, photo in enumerate(proof_photos):
        print(f"   - Photo {i+1}: {photo}")
    print()
    
    # Update job status in contract
    if job_id in SMART_CONTRACT_DB:
        SMART_CONTRACT_DB[job_id]['worker'] = worker_address
        SMART_CONTRACT_DB[job_id]['status'] = 'VERIFYING'
    
    # Call Eye agent
    print("👁️  Calling Eye Agent...")
    print("   Fetching job data from smart contract...")
    
    # Eye agent verifies
    verification_result = await verify_work(
        proof_photos=proof_photos,
        job_id=job_id
    )
    
    print(f"\n⚖️  VERIFICATION RESULT:")
    print(f"   Verified: {verification_result['verified']}")
    print(f"   Confidence: {verification_result['confidence']:.2%}")
    print(f"   Reason: {verification_result['reason']}")
    print(f"   Category: {verification_result['category']}")
    
    # Update contract based on result
    if verification_result['verified']:
        SMART_CONTRACT_DB[job_id]['status'] = 'COMPLETED'
        print("\n💰 Smart Contract: RELEASING FUNDS TO WORKER")
        print(f"   Amount: {SMART_CONTRACT_DB[job_id]['price_amount']} {SMART_CONTRACT_DB[job_id]['price_currency']}")
        print(f"   To: {worker_address}")
    else:
        SMART_CONTRACT_DB[job_id]['status'] = 'REJECTED'
        print("\n❌ Smart Contract: PAYMENT HELD")
        print("   Worker can retry with better proof")
        if 'suggestions' in verification_result:
            print("\n💡 Suggestions:")
            for suggestion in verification_result.get('suggestions', []):
                print(f"   - {suggestion}")
    
    return verification_result

async def run_integration_test():
    """
    Complete integration test showing full flow
    """
    print("\n" + "=" * 70)
    print("🛡️  GIGSHIELD INTEGRATION TEST")
    print("=" * 70)
    print("\nTesting: Paralegal Agent ↔ Eye Agent Integration")
    print("Simulating: Job Creation → Verification → Payment")
    print()
    
    # ========================================================================
    # TEST CASE 1: Valid Job with Good Work
    # ========================================================================
    print("\n" + "🧪 " + "=" * 66)
    print("TEST CASE 1: Valid Job → Good Work → APPROVED")
    print("=" * 70)
    
    # Client creates job
    job_description = "Paint my bedroom wall blue at 123 Main St for 50 GAS"
    reference_image = b"fake_reference_image_bytes"  # Simulated
    
    job_result = await simulate_job_creation(job_description, reference_image)
    
    if job_result:
        job_id = job_result['job_id']
        
        # Worker completes and submits proof
        await asyncio.sleep(0.5)  # Simulate time passing
        
        proof_photos = ["ipfs://Qm.../painted_wall_blue.jpg"]  # Simulated
        worker_address = "0xWorker456..."
        
        verification = await simulate_work_verification(
            job_id,
            proof_photos,
            worker_address
        )
        
        print("\n" + "=" * 70)
        print("TEST CASE 1 RESULT:", "✅ PASSED" if verification['verified'] else "❌ FAILED")
        print("=" * 70)
    
    # ========================================================================
    # TEST CASE 2: Vague Job Description
    # ========================================================================
    print("\n\n" + "🧪 " + "=" * 66)
    print("TEST CASE 2: Vague Description → REJECTED")
    print("=" * 70)
    
    vague_description = "Clean my wall"  # Missing location and price
    reference_image = b"fake_image"
    
    job_result = await simulate_job_creation(vague_description, reference_image)
    
    if not job_result:
        print("\n" + "=" * 70)
        print("TEST CASE 2 RESULT: ✅ PASSED (Correctly rejected vague description)")
        print("=" * 70)
    
    # ========================================================================
    # Summary
    # ========================================================================
    print("\n\n" + "=" * 70)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"\nTotal jobs in contract: {len(SMART_CONTRACT_DB)}")
    print("\nJob statuses:")
    for job_id, job_data in SMART_CONTRACT_DB.items():
        print(f"  {job_id}: {job_data['status']}")
    
    print("\n✅ Integration test completed!")
    print("\nKey takeaways:")
    print("  1. Paralegal validates and generates verification plan")
    print("  2. Smart contract stores the plan")
    print("  3. Eye uses the stored plan to verify work")
    print("  4. System enforces quality standards automatically")
    print()

async def show_integration_flow():
    """
    Display detailed integration flow diagram
    """
    print("\n" + "=" * 70)
    print("🔄 GIGSHIELD INTEGRATION FLOW")
    print("=" * 70)
    
    flow = """
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: JOB CREATION                        │
└─────────────────────────────────────────────────────────────────┘

CLIENT
  │
  │ 1. Submits job description + reference photo
  ↓
PARALEGAL AGENT (TASK-011)
  │
  ├─→ Validates clarity (has task, location, price?)
  ├─→ Verifies image matches description (vision)
  ├─→ Generates verification plan for Eye agent
  ├─→ Analyzes reference photo baseline
  │
  │ Returns: {
  │   status: "complete",
  │   data: {task, location, price},
  │   verification_plan: {...},        ← Eye will use this!
  │   acceptance_criteria: [...],
  │   reference_analysis: {...}
  │ }
  ↓
SMART CONTRACT (TASK-004)
  │
  │ Stores:
  │ - Job data (task, location, price)
  │ - Verification plan (from Paralegal)
  │ - Reference photos (IPFS)
  │ - Status: OPEN
  │
  │ Locks payment in escrow
  ↓
JOB IS NOW AVAILABLE FOR WORKERS


┌─────────────────────────────────────────────────────────────────┐
│                  PHASE 2: WORK VERIFICATION                     │
└─────────────────────────────────────────────────────────────────┘

WORKER
  │
  │ 2. Completes work
  │ 3. Captures proof photos
  │ 4. Uploads to IPFS (4Everland)
  │ 5. Submits proof to contract
  ↓
EYE AGENT (TASK-013)
  │
  │ Fetches from contract:
  │ - Job description
  │ - Reference photos
  │ - Verification plan (← generated by Paralegal!)
  │
  ├─→ Compares before/after photos
  │   • Same location? (feature matching)
  │   • Transformation detected?
  │   • Coverage consistent?
  │
  ├─→ Verifies against plan
  │   • Quality indicators met?
  │   • Checklist items passed?
  │   • Required evidence present?
  │
  ├─→ Makes decision
  │   • Multi-layer checks
  │   • Confidence scoring
  │   • Fraud prevention
  │
  │ Returns: {
  │   verified: true/false,
  │   confidence: 0.0-1.0,
  │   reason: "explanation",
  │   category: "APPROVED/REJECTED"
  │ }
  ↓
SMART CONTRACT (TASK-005)
  │
  ├─→ If APPROVED:
  │   • Releases payment to worker
  │   • Updates status: COMPLETED
  │
  └─→ If REJECTED:
      • Payment stays in escrow
      • Worker can retry
      • Updates status: REJECTED


┌─────────────────────────────────────────────────────────────────┐
│                    KEY INTEGRATION POINTS                        │
└─────────────────────────────────────────────────────────────────┘

1. PARALEGAL → SMART CONTRACT
   • Paralegal generates verification_plan once
   • Contract stores it permanently
   • No need to regenerate for each verification

2. SMART CONTRACT → EYE
   • Eye fetches stored verification_plan
   • Uses Paralegal's criteria consistently
   • All workers verified by same standards

3. DATA CONSISTENCY
   • verification_plan structure matches exactly
   • Eye expects what Paralegal provides
   • No data loss or transformation needed

4. COST EFFICIENCY
   • Paralegal runs once (job creation)
   • Eye runs per verification attempt
   • Plan generation not repeated = saves AI costs
"""
    
    print(flow)

if __name__ == "__main__":
    # Show flow diagram first
    asyncio.run(show_integration_flow())
    
    # Run integration test
    asyncio.run(run_integration_test())

