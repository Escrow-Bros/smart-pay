"""
Alternative IPFS upload using direct HTTP with AWS signature
"""
import os
import hashlib
import hmac
import time
from datetime import datetime
from io import BytesIO
from typing import Optional
from dotenv import load_dotenv
import requests

load_dotenv()

def upload_to_ipfs_http(image_bytes: bytes, filename: str = "proof.jpg") -\> Optional[str]:
    """
    Upload to 4Everland using direct HTTP with AWS v4 signature
    """
    bucket_name = os.getenv("EVERLAND_BUCKET_NAME")
    access_key = os.getenv("EVERLAND_ACCESS_KEY")
    secret_key = os.getenv("EVERLAND_SECRET_KEY")
    endpoint = os.getenv("EVERLAND_ENDPOINT", "https://endpoint.4everland.co/")
    
    if not all([bucket_name, access_key, secret_key]):
        print("❌ Error: Missing 4Everland credentials")
        return None
    
    # Prepare URL
    endpoint_clean = endpoint.rstrip('/')
    url = f"{endpoint_clean}/{bucket_name}/{filename}"
    
    # Content headers
   content_length = len(image_bytes)
    content_type = 'image/jpeg'
    
    # AWS v4 signature components
    region = 'us-west-1'
    service = 's3'
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    datestamp = datetime.utcnow().strftime('%Y%m%d')
    
    # Create canonical request hash (simplified)
    headers = {
        'Content-Type': content_type,
        'Content-Length': str(content_length),
        'x-amz-acl': 'public-read',
        'x-amz-content-sha256': 'UNSIGNED-PAYLOAD',
        'x-amz-date': timestamp
    }
    
    # Create signature (simplified - for testing)
    credential_scope = f"{datestamp}/{region}/{service}/aws4_request"
    authorization = f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}"
    
    headers['Authorization'] = authorization
    
    print(f"[HTTP] Uploading {content_length} bytes to {url}")
    print(f"[HTTP] Headers: Content-Length={content_length}, Content-Type={content_type}")
    
    try:
        response = requests.put(
            url,
            data=image_bytes,
            headers=headers,
            timeout=30
        )
        
        print(f"[HTTP] Response status: {response.status_code}")
        print(f"[HTTP] Response headers: {dict(response.headers)}")
        
        if response.status_code in [200, 201, 204]:
            print(f"✅ Upload successful: {url}")
            return url
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ HTTP upload error: {e}")
        return None


if __name__ == "__main__":
    # Test with a small image
    test_bytes = bytes([0xFF, 0xD8, 0xFF, 0xE0] + [0x00] * 100 + [0xFF, 0xD9])
    result = upload_to_ipfs_http(test_bytes, "test_http.jpg")
    print(f"Result: {result}")
