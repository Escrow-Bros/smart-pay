"""
Test Script for Eye Agent GPS Location Verification
Run this to verify eye.py is working correctly with 50m radius checks
"""
import asyncio
import json
from eye import UniversalEyeAgent

async def test_eye_agent():
    """Test Eye Agent with different GPS scenarios"""
    
    print("=" * 60)
    print("EYE AGENT GPS VERIFICATION TEST")
    print("=" * 60)
    
    eye_agent = UniversalEyeAgent()
    
    # Test data
    reference_url = "https://example.com/ref.jpg"  # Replace with real IPFS URL
    proof_url = "https://example.com/proof.jpg"    # Replace with real IPFS URL
    
    verification_plan = {
        "task_category": "cleaning",
        "expected_transformation": {
            "before": "wall with graffiti",
            "after": "clean wall"
        },
        "verification_checklist": [
            "Is it the same wall?",
            "Is graffiti removed?"
        ]
    }
    
    # TEST 1: Valid location (within 50m)
    print("\n" + "=" * 60)
    print("TEST 1: Valid Location (Within 50m)")
    print("=" * 60)
    
    job_location_1 = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy": 5
    }
    
    worker_location_1 = {
        "latitude": 37.7750,  # ~11m away
        "longitude": -122.4195,
        "accuracy": 5
    }
    
    try:
        print(f"Job Location: {job_location_1}")
        print(f"Worker Location: {worker_location_1}")
        
        comparison_1 = await eye_agent.compare_before_after(
            reference_photos=[reference_url],
            proof_photos=[proof_url],
            verification_plan=verification_plan,
            job_location=job_location_1,
            worker_location=worker_location_1
        )
        
        if "gps_verification" in comparison_1:
            gps = comparison_1["gps_verification"]
            print(f"\n✅ GPS Check Result:")
            print(f"   Location Match: {gps.get('location_match')}")
            print(f"   Distance: {gps.get('distance_meters')}m")
            print(f"   Reasoning: {gps.get('reasoning')}")
        else:
            print(f"\n⚠️  Comparison result: {comparison_1.get('rejection_reason', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Test 1 Failed: {e}")
    
    # TEST 2: Invalid location (beyond 50m)
    print("\n" + "=" * 60)
    print("TEST 2: Invalid Location (Beyond 50m)")
    print("=" * 60)
    
    job_location_2 = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy": 5
    }
    
    worker_location_2 = {
        "latitude": 37.7760,  # ~150m away
        "longitude": -122.4210,
        "accuracy": 5
    }
    
    try:
        print(f"Job Location: {job_location_2}")
        print(f"Worker Location: {worker_location_2}")
        
        comparison_2 = await eye_agent.compare_before_after(
            reference_photos=[reference_url],
            proof_photos=[proof_url],
            verification_plan=verification_plan,
            job_location=job_location_2,
            worker_location=worker_location_2
        )
        
        if "rejection_reason" in comparison_2:
            print(f"\n❌ EXPECTED REJECTION:")
            print(f"   Reason: {comparison_2['rejection_reason']}")
            print(f"   Distance: {comparison_2.get('distance_meters')}m")
            print(f"   Fraud Detected: {comparison_2.get('fraud_detected')}")
        else:
            print(f"\n⚠️  Unexpected result: {comparison_2}")
            
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")
    
    # TEST 3: Missing worker location
    print("\n" + "=" * 60)
    print("TEST 3: Missing Worker Location")
    print("=" * 60)
    
    try:
        print(f"Job Location: {job_location_1}")
        print(f"Worker Location: None")
        
        comparison_3 = await eye_agent.compare_before_after(
            reference_photos=[reference_url],
            proof_photos=[proof_url],
            verification_plan=verification_plan,
            job_location=job_location_1,
            worker_location=None
        )
        
        print("❌ Test should have raised ValueError!")
        
    except ValueError as e:
        print(f"\n✅ EXPECTED ERROR:")
        print(f"   Error: {str(e)}")
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✅ Test 1: Should pass with distance ~11m")
    print("❌ Test 2: Should fail with distance >50m")
    print("❌ Test 3: Should raise ValueError for missing location")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_eye_agent())
