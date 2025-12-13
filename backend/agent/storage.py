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
    
    # Try boto3 S3-compatible upload (most reliable for 4Everland)
    try:
        import boto3
        from botocore.exceptions import ClientError
        from botocore.client import Config
        
        print(f"[IPFS] Initializing S3 client for 4Everland...")
        
        # Use client interface (not resource) for better control over headers
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='us-west-1',
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'path'},
                request_checksum_calculation='when_required',
                response_checksum_validation='when_required'
            )
        )
        
        file_size = len(image_bytes)
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(max_retries):
            try:
                print(f"[IPFS] Upload attempt {attempt + 1}/{max_retries} - Uploading {file_size} bytes to {bucket_name}/{filename}")
                
                # Use BytesIO to ensure proper streaming
                file_obj = BytesIO(image_bytes)
                
                # Use client.put_object with explicit Content-Length
                response = s3_client.put_object(
                    Bucket=bucket_name,
                    Key=filename,
                    Body=file_obj,
                    ContentLength=file_size,
                    ContentType='image/jpeg',
                    ACL='public-read'
                )
                
                print(f"[IPFS] Upload response: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
                
                # Generate public IPFS URL
                endpoint_clean = endpoint.rstrip('/')
                public_url = f"{endpoint_clean}/{bucket_name}/{filename}"
                
                print(f"✅ Successfully uploaded to IPFS ({file_size} bytes): {public_url}" + (f" (attempt {attempt + 1}/{max_retries})" if attempt > 0 else ""))
                return public_url
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                error_msg = e.response.get('Error', {}).get('Message', str(e))
                last_error = f"{error_code}: {error_msg}"
                
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    print(f"⚠️ Upload attempt {attempt + 1} failed ({error_code}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Error uploading to 4Everland after {max_retries} attempts: {last_error}")
                    return None
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt)
                    print(f"⚠️ Upload attempt {attempt + 1} failed ({e}), retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Unexpected error after {max_retries} attempts: {last_error}")
                    return None
        
        return None
        
    except ImportError:
        print("❌ Error: boto3 not installed. Run: pip install boto3")
        return None
    except Exception as e:
        print(f"❌ Unexpected boto3 error: {e}")
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
            
    except httpx.RequestError as e:
        print(f"❌ Error uploading to 4Everland API: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

