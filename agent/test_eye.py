"""
Test script for Eye Agent
Demonstrates verification with placeholder data
"""
import asyncio
from eye import verify_work

async def test_eye_agent():
    """Test the Eye agent with sample data"""
    
    print("=" * 60)
    print("🧪 Testing Eye Agent - Universal Work Verification")
    print("=" * 60)
    print()
    
    # Simulate worker submitting proof
    proof_photos = [
        "ipfs://Qm.../painted_wall_blue.jpg",  # After photo
    ]
    
    job_id = "job_12345"  # Placeholder job
    worker_id = "0xWorker123..."
    
    print(f"📸 Worker submitted proof for job: {job_id}")
    print(f"🔗 Proof photos: {len(proof_photos)} photo(s)")
    print()
    
    # Verify the work
    result = await verify_work(
        proof_photos=proof_photos,
        job_id=job_id,
        worker_id=worker_id
    )
    
    print()
    print("=" * 60)
    print("📊 VERIFICATION RESULT")
    print("=" * 60)
    print()
    print(f"✅ Verified: {result['verified']}")
    print(f"🎯 Confidence: {result['confidence']:.2%}")
    print(f"📝 Reason: {result['reason']}")
    print(f"🏷️  Category: {result['category']}")
    print()
    
    if result['verified']:
        print("🎉 WORK APPROVED - Ready to release payment!")
        # TODO (TASK-005): Call smart contract release_funds()
    else:
        print("❌ WORK REJECTED - Worker must resubmit")
        if 'suggestions' in result:
            print("\n💡 Suggestions for improvement:")
            for suggestion in result.get('suggestions', []):
                print(f"   - {suggestion}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_eye_agent())

