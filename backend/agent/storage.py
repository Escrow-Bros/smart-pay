import os
import time
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Loads from root .env

def upload_to_ipfs(image_bytes: bytes, filename: str = "proof.jpg", max_retries: int = 3) -> Optional[str]:
    """
    Upload image bytes to IPFS via Pinata API
    
    Args:
        image_bytes: Raw image bytes to upload
        filename: Name to give the file
        max_retries: Maximum number of retry attempts
    
    Returns:
        Public IPFS URL if successful, None otherwise
    """
    pinata_jwt = os.getenv("PINATA_JWT")
    pinata_api_key = os.getenv("PINATA_API_KEY")
    pinata_secret_key = os.getenv("PINATA_SECRET_KEY")
    
    if not pinata_jwt and not (pinata_api_key and pinata_secret_key):
        print("❌ Error: Missing Pinata credentials in .env")
        return None

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    # Headers
    headers = {}
    if pinata_jwt:
        headers["Authorization"] = f"Bearer {pinata_jwt}"
    else:
        # Fallback to key/secret headers if JWT missing (though JWT preferred)
        headers["pinata_api_key"] = pinata_api_key
        headers["pinata_secret_api_key"] = pinata_secret_key

    # File payload
    files = {
        'file': (filename, image_bytes, 'image/jpeg')
    }
    
    # Metadata & Options
    pinata_options = {
        "cidVersion": 1
    }
    
    group_id = os.getenv("PINATA_GROUP_ID")
    if group_id:
        pinata_options["groupId"] = group_id
        
    data = {
        "pinataOptions": str(pinata_options).replace("'", '"')  # JSON string required for options, simplified hack
    }
    # Better approach for JSON field in multipart:
    import json
    data = {"pinataOptions": json.dumps(pinata_options)}

    last_error = None
    file_size = len(image_bytes)

    for attempt in range(max_retries):
        try:
            print(f"[IPFS] Upload attempt {attempt + 1}/{max_retries} - Uploading {file_size} bytes to Pinata...")
            
            # Need to re-create files dict per attempt if reading from stream, but bytes is safe to reuse? 
            # Requests 'files' param handles bytes directly.
            response = requests.post(url, files=files, data=data, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                ipfs_hash = result.get('IpfsHash')
                if ipfs_hash:
                    # Use Pinata Gateway
                    public_url = f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}"
                    print(f"✅ Successfully uploaded to Pinata: {public_url}")
                    return public_url
                else:
                    print(f"❌ Error: No IpfsHash in Pinata response: {result}")
            else:
                last_error = f"HTTP {response.status_code}: {response.text}"
                print(f"⚠️ Pinata upload failed: {last_error}")

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"⚠️ Network error uploading to Pinata: {e}")
        except Exception as e:
            last_error = str(e)
            print(f"⚠️ Unexpected error uploading to Pinata: {e}")
            
        if attempt < max_retries - 1:
            wait_time = (2 ** attempt)
            print(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
            # Re-initialize files tuple just in case requests closed it? (Unlikely for bytes, but safe)
            files = {'file': (filename, image_bytes, 'image/jpeg')}

    print(f"❌ Failed to upload to Pinata after {max_retries} attempts. Last error: {last_error}")
    return None

# Deprecated/Unused legacy function (kept signature just in case, or remove if unused)
def upload_to_ipfs_api(image_bytes: bytes, filename: str = "proof.jpg") -> Optional[str]:
    return upload_to_ipfs(image_bytes, filename)

