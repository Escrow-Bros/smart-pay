# Storage Module - IPFS Upload Handler

**Task:** TASK-012  
**File:** `services/storage.py`  
**Status:** ✅ Complete

## 🎯 Purpose

The Storage Module handles **permanent, decentralized storage** of images via 4Everland IPFS. It uploads photos and returns permanent public URLs.

## 🔄 What It Does

### Input:
```python
image_bytes = camera_photo.getvalue()
filename = "proof.jpg"
```

### Process:
1. Uploads image to 4Everland bucket
2. Image is automatically pinned to IPFS
3. Returns permanent public URL

### Output:
```python
"https://endpoint.4everland.co/bucket-name/proof.jpg"
# or
"https://gateway.4everland.co/ipfs/Qm..."
```

## 🧩 Main Function

### `upload_to_ipfs(image_bytes, filename)`

**S3-Compatible API Method (Default):**
```python
from services.storage import upload_to_ipfs

url = upload_to_ipfs(
    image_bytes=photo_bytes,
    filename="worker_proof_123.jpg"
)

# Returns: Public IPFS URL
```

**Features:**
- Uses boto3 S3-compatible API
- Uploads to 4Everland bucket
- Returns permanent URL
- Handles errors gracefully

## 📁 Upload Methods

### Method 1: S3-Compatible API (Recommended)
```python
def upload_to_ipfs(image_bytes, filename):
    """Uses boto3 with S3-compatible API"""
    
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv("EVERLAND_ENDPOINT"),
        aws_access_key_id=os.getenv("EVERLAND_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("EVERLAND_SECRET_KEY")
    )
    
    s3_client.put_object(
        Bucket=os.getenv("EVERLAND_BUCKET_NAME"),
        Key=filename,
        Body=image_bytes,
        ContentType='image/jpeg'
    )
    
    return f"{endpoint}/{bucket}/{filename}"
```

### Method 2: Direct IPFS API (Alternative)
```python
def upload_to_ipfs_api(image_bytes, filename):
    """Direct API upload"""
    
    files = {'file': (filename, image_bytes, 'image/jpeg')}
    headers = {'Authorization': f'Bearer {api_key}'}
    
    response = requests.post(
        "https://api.4everland.dev/ipfs/upload",
        files=files,
        headers=headers
    )
    
    ipfs_hash = response.json()['cid']
    return f"https://gateway.4everland.co/ipfs/{ipfs_hash}"
```

## ⚙️ Configuration

### Required in `agent/.env`:

**Method 1 (S3-Compatible):**
```env
EVERLAND_BUCKET_NAME=your-bucket-name
EVERLAND_ACCESS_KEY=your-access-key-id
EVERLAND_SECRET_KEY=your-secret-access-key
EVERLAND_ENDPOINT=https://endpoint.4everland.co
```

**Method 2 (Direct API):**
```env
EVERLAND_API_KEY=your-api-key
```

### Get Credentials:
1. Sign up at https://dashboard.4everland.org/
2. Create a bucket
3. Generate access keys
4. Add to `.env` file

## 🎨 Usage Examples

### Example 1: Upload Camera Photo
```python
from services.storage import upload_to_ipfs

# From Streamlit camera
photo = st.camera_input("Take photo")
if photo:
    image_bytes = photo.getvalue()
    url = upload_to_ipfs(image_bytes, "proof_123.jpg")
    
    if url:
        st.success(f"Uploaded: {url}")
```

### Example 2: Upload File
```python
# From file upload
with open("proof.jpg", "rb") as f:
    image_bytes = f.read()

url = upload_to_ipfs(image_bytes, "my_proof.jpg")
print(f"IPFS URL: {url}")
```

### Example 3: Reference Photo
```python
# Client uploads reference photo
reference_bytes = get_camera_input()
ref_url = upload_to_ipfs(reference_bytes, "ref_job_123.jpg")

# Store ref_url in smart contract
contract.create_job(..., reference_photos=[ref_url])
```

## 🔧 Error Handling

### Missing Credentials:
```python
❌ Error: Missing 4Everland credentials in .env
Required: EVERLAND_BUCKET_NAME, EVERLAND_ACCESS_KEY, EVERLAND_SECRET_KEY
```

### Upload Failure:
```python
❌ Error uploading to 4Everland: Access Denied
# Check bucket permissions
```

### boto3 Not Installed:
```python
❌ Error: boto3 not installed. Run: pip install boto3
```

## 📊 Why IPFS?

### Permanent Storage
- Files cannot be deleted
- Content-addressed (hash-based)
- Immutable proof

### Decentralized
- No single point of failure
- Globally distributed
- Censorship-resistant

### Perfect for Blockchain
- On-chain proof references
- Tamper-proof evidence
- Permanent audit trail

## 🎯 Use Cases in GigShield

### 1. Reference Photos (Client)
```python
# Client uploads BEFORE photo
ref_url = upload_to_ipfs(before_photo)
# Stored in smart contract
# Used by Eye agent for comparison
```

### 2. Proof Photos (Worker)
```python
# Worker uploads AFTER photo
proof_url = upload_to_ipfs(after_photo)
# Submitted for verification
# Analyzed by Eye agent
```

### 3. Evidence Trail
```python
# Permanent record:
Job created → ref_url stored
Work done → proof_url submitted
Verified → both URLs in contract
# Immutable audit trail!
```

## 🚀 Integration

### With Paralegal:
```python
# Client submits job with reference
ref_bytes = camera_input()
ref_url = upload_to_ipfs(ref_bytes)

result = await paralegal.analyze_job_request(
    text="Paint wall...",
    reference_image=ref_bytes  # Bytes for analysis
)

# Store ref_url in contract
contract.create_job(..., reference_photos=[ref_url])
```

### With Eye Agent:
```python
# Worker uploads proof
proof_bytes = camera_input()
proof_url = upload_to_ipfs(proof_bytes)

# Eye downloads and verifies
verdict = await eye.verify_work(
    proof_photos=[proof_url],  # Eye downloads from IPFS
    job_id=job_id
)
```

## 📊 Performance

- **Upload speed:** 2-10 seconds (depends on image size)
- **File size limit:** Typically 10-20 MB
- **Reliability:** High (distributed infrastructure)
- **Cost:** Low (pay-as-you-go)

## 🔑 Key Technologies

- **4Everland** - IPFS infrastructure provider
- **boto3** - S3-compatible API client
- **requests** - Direct API calls
- **IPFS** - Decentralized storage protocol

## 💡 Best Practices

### Filename Convention:
```python
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"proof_{job_id}_{timestamp}.jpg"
```

### Error Handling:
```python
url = upload_to_ipfs(image_bytes)

if url:
    # Success - use URL
    store_in_contract(url)
else:
    # Failed - retry or alert user
    show_error("Upload failed")
```

### Content Type:
```python
# Explicitly set for different file types
ContentType='image/jpeg'  # For photos
ContentType='image/png'   # For screenshots
ContentType='video/mp4'   # For videos
```

## 🎯 Future Enhancements

- [ ] Video upload support
- [ ] Multiple file batch upload
- [ ] Progress tracking
- [ ] Compression before upload
- [ ] Automatic retry on failure
- [ ] Upload resumption
- [ ] Metadata attachment

## ✅ Summary

**Purpose:** Permanent, decentralized storage for proof photos  
**Provider:** 4Everland IPFS  
**API:** S3-compatible (boto3)  
**Returns:** Permanent public URLs  
**Status:** Production-ready ✅

Simple, reliable, and essential for the GigShield proof-of-work system! ☁️

