import os
from dotenv import load_dotenv

# Try loading from multiple locations
locations = [
    '.env',
    'backend/.env',
]

for loc in locations:
    if os.path.exists(loc):
        print(f"✓ Found: {loc}")
        load_dotenv(loc)
    else:
        print(f"✗ NOT FOUND: {loc}")

print("\n=== IPFS Configuration ===")
bucket = os.getenv('EVERLAND_BUCKET_NAME')
access_key = os.getenv('EVERLAND_ACCESS_KEY')
secret_key = os.getenv('EVERLAND_SECRET_KEY')
endpoint = os.getenv('EVERLAND_ENDPOINT', 'https://endpoint.4everland.co')

print(f"EVERLAND_BUCKET_NAME: {bucket if bucket else '❌ NOT SET'}")
print(f"EVERLAND_ACCESS_KEY: {'✓ SET' if access_key else '❌ NOT SET'}")
print(f"EVERLAND_SECRET_KEY: {'✓ SET' if secret_key else '❌ NOT SET'}")
print(f"EVERLAND_ENDPOINT: {endpoint}")

if not all([bucket, access_key, secret_key]):
    print("\n⚠️  IPFS uploads will FAIL - missing required credentials!")
    print("Please set these in your .env file:")
    print("  - EVERLAND_BUCKET_NAME")
    print("  - EVERLAND_ACCESS_KEY")
    print("  - EVERLAND_SECRET_KEY")
else:
    print("\n✅ All IPFS credentials are configured!")
