# GPS Location Verification

**Feature:** GPS-based fraud prevention  
**File:** `agent/gps_verifier.py`  
**Related:** TASK-014 (Apro Oracle Integration)

## 🎯 Purpose

Verify that worker's proof photos were actually taken at the job location by comparing GPS coordinates from photo metadata.

## 🔄 How It Works

### Phase 1: Client Creates Job
```
Client takes reference photo
   ↓
Browser/App requests location permission
   ↓
GPS coordinates embedded in photo EXIF
   ↓
Photo uploaded to IPFS
   ↓
GPS stored in smart contract:
{
  "job_location": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "accuracy": 10  // meters
  }
}
```

### Phase 2: Worker Submits Proof
```
Worker takes proof photo at job site
   ↓
Browser/App requests location permission
   ↓
GPS coordinates embedded in photo EXIF
   ↓
Photo uploaded to IPFS
   ↓
GPS extracted from EXIF:
{
  "proof_location": {
    "latitude": 37.7750,
    "longitude": -122.4195,
    "accuracy": 8  // meters
  }
}
```

### Phase 3: Eye Agent Verification
```
Eye extracts GPS from both photos
   ↓
Calculates distance between coordinates
   ↓
Compares to acceptable threshold (default: 50 meters)
   ↓
If distance > threshold: REJECT (wrong location)
If distance ≤ threshold: Continue verification
```

## 📊 GPS Verification Flow

```python
# 1. Extract GPS from reference photo
reference_gps = extract_gps_from_exif(reference_image_bytes)
# Result: {"latitude": 37.7749, "longitude": -122.4194, "accuracy": 10}

# 2. Extract GPS from proof photo
proof_gps = extract_gps_from_exif(proof_image_bytes)
# Result: {"latitude": 37.7750, "longitude": -122.4195, "accuracy": 8}

# 3. Verify location match
gps_result = verify_gps_location(
    reference_gps,
    proof_gps,
    max_distance_meters=50  # Threshold
)

# Returns:
{
    "location_match": True,
    "distance_meters": 15.3,  # Photos taken 15.3m apart
    "confidence": 0.92,
    "reasoning": "Photos taken 15.3m apart (within 50m tolerance)"
}
```

## 🛡️ Integration with Eye Agent

### Enhanced Verification Pipeline:

```
Eye Agent Verification:
  │
  ├─→ Step 1: Visual Comparison (GPT-4V)
  │   • Same location? (features match)
  │   • Transformation detected?
  │   • Coverage consistent?
  │
  ├─→ Step 2: GPS Verification (NEW!)
  │   • Extract GPS from both photos
  │   • Calculate distance
  │   • Verify within threshold
  │
  ├─→ Step 3: Quality Verification (GPT-4V)
  │   • Requirements met?
  │   • Quality acceptable?
  │
  └─→ Step 4: Final Decision
      • All checks must pass
      • Multi-layer fraud prevention
```

### Updated Eye Agent Flow:

```python
async def verify(self, proof_photos, job_id):
    # Existing steps...
    comparison = await self.compare_before_after(...)
    
    # NEW: GPS Verification
    gps_check = await self.verify_gps_location(
        reference_photos,
        proof_photos,
        job_data
    )
    
    verification = await self.verify_requirements(...)
    
    # Updated decision with GPS check
    decision = self.make_final_decision(
        verification_plan,
        comparison,
        verification,
        gps_check  # ← NEW parameter
    )
```

## 🔍 GPS Verification Methods

### Method 1: EXIF Data (Automatic)
```python
# Extract from photo metadata
reference_gps = extract_gps_from_exif(reference_image_bytes)
proof_gps = extract_gps_from_exif(proof_image_bytes)

# Pros:
✅ Automatic (no user action needed if photo has EXIF)
✅ Can't be easily faked
✅ Works with most camera apps

# Cons:
❌ Not all cameras include GPS in EXIF
❌ Can be stripped from image
❌ Privacy concerns
```

### Method 2: Browser Geolocation API (Explicit Permission)
```javascript
// Frontend (Streamlit or React)
navigator.geolocation.getCurrentPosition(function(position) {
    const gps = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy
    };
    
    // Send with photo upload
    uploadWithGPS(photo, gps);
});
```

### Method 3: Manual Input (Fallback)
```python
# If no GPS available, client provides address
# Geocode to coordinates
# Less reliable but better than nothing
```

## 📏 Distance Thresholds

### Recommended Thresholds by Job Type:

```python
GPS_THRESHOLDS = {
    "default": 50,          # 50 meters (general)
    "indoor": 20,           # 20 meters (apartment, room)
    "outdoor": 100,         # 100 meters (lawn, exterior)
    "large_property": 200,  # 200 meters (estate, farm)
    "delivery": 30,         # 30 meters (delivery address)
    "inspection": 10        # 10 meters (specific location)
}

# Adjust based on GPS accuracy
if ref_accuracy > 20 or proof_accuracy > 20:
    # Poor GPS signal, increase tolerance
    threshold += 30
```

## 🎨 Usage Example

### Complete Verification with GPS:

```python
# In Eye agent verify() method:

async def verify(self, proof_photos, job_id):
    # Get job data
    job_data = get_job_from_contract(job_id)
    
    # Download images
    ref_image_bytes = download_image(job_data["reference_photos"][0])
    proof_image_bytes = download_image(proof_photos[0])
    
    # Extract GPS from both
    ref_gps = extract_gps_from_exif(ref_image_bytes)
    proof_gps = extract_gps_from_exif(proof_image_bytes)
    
    # Verify GPS match
    if ref_gps and proof_gps:
        gps_result = verify_gps_location(
            ref_gps,
            proof_gps,
            max_distance_meters=50
        )
        
        if not gps_result["location_match"]:
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": f"Location mismatch: {gps_result['reasoning']}",
                "category": "GPS_MISMATCH",
                "distance": gps_result["distance_meters"]
            }
    else:
        # GPS not available - proceed with visual verification only
        print("⚠️ GPS not available in photos, using visual verification only")
    
    # Continue with visual verification...
    comparison = await self.compare_before_after(...)
    # ... rest of verification
```

## 🚨 Fraud Prevention Examples

### Scenario 1: Worker at Wrong Location
```
Job: Paint wall at 123 Main St
Reference GPS: (37.7749, -122.4194)  // San Francisco
Proof GPS: (34.0522, -118.2437)      // Los Angeles

Distance: 559 km
Result: ❌ REJECTED - "Photos taken 559km apart"
```

### Scenario 2: Worker at Correct Location
```
Job: Paint wall at 123 Main St
Reference GPS: (37.7749, -122.4194)
Proof GPS: (37.7750, -122.4195)

Distance: 15 meters
Result: ✅ PASS GPS check, continue verification
```

### Scenario 3: No GPS Data
```
Job: Paint wall at 123 Main St
Reference GPS: None (photo has no EXIF)
Proof GPS: None

Result: ⚠️ WARNING - Rely on visual verification only
```

## 🔌 Frontend Integration

### Streamlit Example:

```python
import streamlit as st

# Request location permission
st.warning("📍 Location access required for fraud prevention")

# JavaScript to get GPS
js_code = """
<script>
navigator.geolocation.getCurrentPosition(
    function(position) {
        // Send coordinates to Streamlit
        window.parent.postMessage({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
        }, '*');
    },
    function(error) {
        alert('Location access denied. Job creation may be limited.');
    }
);
</script>
"""

# Store GPS in session
if 'gps_location' not in st.session_state:
    st.session_state.gps_location = None

# Attach GPS to photo upload
if photo and st.session_state.gps_location:
    # Include GPS with upload
    upload_with_gps(photo, st.session_state.gps_location)
```

## ⚙️ Configuration

### Smart Contract Storage:

```python
# When job is created:
{
    "job_id": "job_123",
    "reference_photos": ["ipfs://..."],
    "reference_gps": {                    # ← NEW
        "latitude": 37.7749,
        "longitude": -122.4194,
        "accuracy": 10,
        "timestamp": "2025-11-23T10:00:00Z"
    },
    "gps_required": True,                 # ← NEW
    "max_distance_meters": 50,            # ← NEW
    "verification_plan": {...}
}
```

## 📊 Benefits

### 1. Location Fraud Prevention
```
❌ Can't use photos from different location
❌ Can't hire someone else to do work elsewhere
✅ Must physically be at job site
```

### 2. Combined with Visual Verification
```
GPS Check: "Are they at the right place?"
Visual Check: "Is it the right object/work?"

Both must pass for approval!
```

### 3. Apro Oracle Enhancement (Future)
```
GPS + Weather verification:
- Check weather at GPS location
- Compare to expected conditions
- Verify timestamp matches work window
```

## 🎯 Implementation Steps

### Step 1: Add GPS to Paralegal (Job Creation)
```python
# In analyze_job_request():
reference_gps = extract_gps_from_exif(reference_image)
if reference_gps:
    result["reference_gps"] = reference_gps
```

### Step 2: Add GPS to Eye (Verification)
```python
# In verify() method:
gps_check = verify_gps_location(
    job_data["reference_gps"],
    proof_gps,
    job_data.get("max_distance_meters", 50)
)

if not gps_check["location_match"]:
    return REJECT
```

### Step 3: Update make_final_decision()
```python
def make_final_decision(plan, comparison, verification, gps_check=None):
    # NEW: GPS check
    if gps_check and not gps_check["location_match"]:
        return {
            "verified": False,
            "category": "GPS_MISMATCH",
            "reason": gps_check["reasoning"]
        }
    
    # Existing checks...
```

## 🔑 Privacy Considerations

### User Control:
- ✅ Explicit permission required
- ✅ Show what GPS data is collected
- ✅ GPS only for fraud prevention
- ✅ Not shared publicly (only verified on-chain)

### Data Minimization:
- Only store: lat, lon, accuracy
- Don't store: full location history
- Don't share: with third parties
- Delete: after job completed (optional)

## 📝 Summary

GPS verification adds a powerful anti-fraud layer:

| Without GPS | With GPS |
|-------------|----------|
| Visual check only | Visual + Location check |
| Can fake with old photos | Must be at actual location |
| Feature matching only | GPS + Feature matching |
| Medium security | High security |

**Recommended:** Enable GPS verification for high-value jobs or outdoor work where location matters.

---

**Status:** GPS verification framework ready!  
**Next:** Integrate into Eye agent's verification pipeline  
**Future:** Add Apro Oracle for weather/timestamp verification

