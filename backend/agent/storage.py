"""
4Everland IPFS Storage Module
Handles uploading images and files to IPFS via 4Everland with retry logic
"""
import os
import time
import httpx
from io import BytesIO
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Loads from root .env

def upload_to_ipfs(image_bytes: bytes, filename: str = "proof.jpg", max_retries: int = 3) -> Optional[str]:
    """
    Upload image bytes to IPFS via 4Everland with exponential backoff retry
    
    Args:
        image_bytes: Raw image bytes to upload
        filename: Name to give the file (default: proof.jpg)
        max_retries: Maximum number of retry attempts (default: 3)
    
    Returns:
        Public IPFS URL if successful, None otherwise
    """
    # Get 4Everland credentials from environment
    bucket_name = os.getenv("EVERLAND_BUCKET_NAME")
    access_key = os.getenv("EVERLAND_ACCESS_KEY")
    secret_key = os.getenv("EVERLAND_SECRET_KEY")
    endpoint = os.getenv("EVERLAND_ENDPOINT", "https://endpoint.4everland.co")
    
    if not all([bucket_name, access_key, secret_key]):
        print("❌ Error: Missing 4Everland credentials in .env")
        print("Required: EVERLAND_BUCKET_NAME, EVERLAND_ACCESS_KEY, EVERLAND_SECRET_KEY")
        return None
    
    # Try HTTP-based upload first (more reliable than boto3 for 4Everland)
    try:
        import requests
        from datetime import datetime
        import hmac
        import hashlib
        from urllib.parse import quote
        
        # Prepare the upload
        file_size = len(image_bytes)
        content_type = 'image/jpeg'
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Build the URL
        endpoint_clean = endpoint.rstrip('/')
        url = f"{endpoint_clean}/{bucket_name}/{filename}"
        
        # Create AWS Signature Version 4 (simplified for PUT)
        string_to_sign = f"PUT\n\n{content_type}\n{date}\n/{bucket_name}/{filename}"
        signature = hmac.new(
            secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
        import base64
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(file_size),
            'Date': date,
            'Authorization': f'AWS {access_key}:{signature_b64}',
            'x-amz-acl': 'public-read'
        }
        
        print(f"[IPFS] Uploading via HTTP PUT to {url} ({file_size} bytes)")
        
        # Retry logic
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.put(url, data=image_bytes, headers=headers, timeout=30)
                
                if response.status_code in [200, 201, 204]:
                    print(f"✅ Successfully uploaded to IPFS ({file_size} bytes): {url}")
                    return url
                else:
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt)
                        print(f"⚠️ Upload attempt {attempt + 1} failed ({response.status_code}), retrying in {wait_time}s...")
                        time.sleep(wait_time)
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    print(f"⚠️ Upload attempt {attempt + 1} failed ({e}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        print(f"❌ HTTP upload failed after {max_retries} attempts: {last_error}")
        
    except ImportError:
        print("❌ Error: requests not installed. Run: pip install requests")
        return None
    except Exception as e:
        print(f"❌ HTTP upload error: {e}")
    
    # Fallback to boto3 if HTTP fails
    print("[IPFS] Trying boto3 fallback...")
    try:
        # 4Everland uses S3-compatible API
        import boto3
        from botocore.exceptions import ClientError
        
        # Initialize S3 client for 4Everland
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-west-1'  # 4Everland default region
        )
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(max_retries):
            try:
                # Convert bytes to BytesIO for proper Content-Length handling
                file_obj = BytesIO(image_bytes)
                file_size = len(image_bytes)
                
                # Reset file pointer to beginning
                file_obj.seek(0)
                
                # Upload to 4Everland bucket - boto3 should auto-calculate Content-Length from BytesIO
                response = s3_client.put_object(
                    Bucket=bucket_name,
                    Key=filename,
                    Body=file_obj,
                    ContentType='image/jpeg',
                    ContentEncoding='identity'  # Explicitly disable compression
                )
                
                print(f"[IPFS] Upload response: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
                
                # Generate public IPFS URL
                endpoint_clean = endpoint.rstrip('/')
                public_url = f"{endpoint_clean}/{bucket_name}/{filename}"
                
                print(f"✅ Successfully uploaded to IPFS ({file_size} bytes): {public_url}" + (f" (attempt {attempt + 1}/{max_retries})" if attempt > 0 else ""))
                return public_url
                
            except ClientError as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    print(f"⚠️ Upload attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Error uploading to 4Everland after {max_retries} attempts: {e}")
                    return None
        
        return None
        
    except ImportError:
        print("❌ Error: boto3 not installed. Run: pip install boto3")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def upload_to_ipfs_api(image_bytes: bytes, filename: str = "proof.jpg") -> Optional[str]:
    """
    Alternative method: Upload directly via 4Everland IPFS API
    (Use this if you prefer direct API over S3-compatible interface)
    
    Args:
        image_bytes: Raw image bytes to upload
        filename: Name to give the file
    
    Returns:
        Public IPFS URL if successful, None otherwise
    """
    api_key = os.getenv("EVERLAND_API_KEY")
    
    if not api_key:
        print("❌ Error: Missing EVERLAND_API_KEY in .env")
        return None
    
    try:
        # 4Everland IPFS Upload API
        url = "https://api.4everland.dev/ipfs/upload"
        
        files = {
            'file': (filename, image_bytes, 'image/jpeg')
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        response = httpx.post(url, files=files, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Get IPFS hash from response
        ipfs_hash = result.get('cid') or result.get('Hash')
        
        if ipfs_hash:
            # Return public gateway URL
            public_url = f"https://gateway.4everland.co/ipfs/{ipfs_hash}"
            print(f"✅ Successfully uploaded to IPFS: {public_url}")
            return public_url
        else:
            print(f"❌ Error: No IPFS hash in response: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error uploading to 4Everland API: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

