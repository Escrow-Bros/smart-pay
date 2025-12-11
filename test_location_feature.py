#!/usr/bin/env python3
"""
Test the new GPS location feature on the deployed contract
"""
import asyncio
from src.neo_mcp import NeoMCP

async def test_location_feature():
    print("🧪 Testing GPS Location Feature on Blockchain")
    print("=" * 60)
    
    mcp = NeoMCP()
    
    # Get contract config to verify it's the new contract
    config = await mcp.get_contract_config()
    print(f"\n📋 Contract Configuration:")
    print(f"   Agent: {config.get('agent', 'Not set')}")
    print(f"   Fee: {config.get('fee_percentage', 0)}%")
    
    # Try to get an existing job (if any)
    print(f"\n🔍 Testing get_job_details with location...")
    
    try:
        # Get a recent job ID (timestamp-based)
        import time
        recent_job_id = int(time.time()) - 86400  # Try last 24 hours
        
        print(f"   Attempting to fetch job {recent_job_id}...")
        job = await mcp.get_job_details(recent_job_id)
        
        if job and job.get('status_code') != 0:  # STATUS_NONE = 0
            print(f"\n✅ Found job #{recent_job_id}")
            print(f"   Status: {job.get('status_name')}")
            print(f"   Client: {job.get('client_address')}")
            print(f"   📍 Location:")
            print(f"      Latitude: {job.get('latitude')}")
            print(f"      Longitude: {job.get('longitude')}")
            
            if job.get('latitude') != 0.0 or job.get('longitude') != 0.0:
                print(f"\n🎉 SUCCESS! Location data retrieved from blockchain!")
            else:
                print(f"\n⚠️  Job exists but no location data (might be old job)")
        else:
            print(f"\n⚠️  No recent jobs found. Create a new job to test location feature.")
            
    except Exception as e:
        print(f"\n⚠️  Could not fetch job: {e}")
        print(f"   This is normal if no jobs have been created yet.")
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Create a job with location via frontend or API")
    print(f"   2. Run this script again to verify location was stored")
    print(f"   3. Submit proof with worker location to test GPS verification")
    
    print(f"\n🔗 View contract on NeoTube:")
    print(f"   https://testnet.neotube.io/contract/f880b4ede4e8b0fd75175f21b30d7b839306e2d7")

if __name__ == "__main__":
    asyncio.run(test_location_feature())
