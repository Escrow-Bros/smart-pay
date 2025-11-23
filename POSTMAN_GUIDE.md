# Testing GigShield Agents with Postman

## 🚀 Quick Start

### 1. Start the API Server

```bash
cd /Users/tusharsingh/Desktop/smart-pay
source .venv/bin/activate
python api_server.py
```

Server will start at: `http://localhost:8000`

### 2. Open Postman

Visit the interactive docs or use Postman:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📡 API Endpoints

### 1. **Create Job (Test Paralegal)**

**Endpoint:** `POST http://localhost:8000/api/jobs/create`

**Method:** POST (multipart/form-data)

**Body:**
- `description` (text): Job description
- `reference_image` (file): Photo of current state

**Postman Setup:**
1. Method: POST
2. URL: `http://localhost:8000/api/jobs/create`
3. Body tab → form-data
4. Add key: `description` (Text)
   - Value: `Paint my bedroom wall blue at 123 Main Street for 50 GAS`
5. Add key: `reference_image` (File)
   - Select a JPG/PNG image file

**Example Response:**
```json
{
  "success": true,
  "status": "complete",
  "job_id": "job_001",
  "data": {
    "task": "Paint my bedroom wall blue",
    "location": "123 Main Street",
    "price_amount": 50,
    "price_currency": "GAS"
  },
  "verification_plan": {
    "task_category": "painting",
    "quality_indicators": [...],
    "verification_checklist": [...],
    "expected_transformation": {...}
  },
  "acceptance_criteria": [...],
  "clarifying_questions": [],
  "message": "Job created successfully! Job ID: job_001"
}
```

---

### 2. **Verify Work (Test Eye)**

**Endpoint:** `POST http://localhost:8000/api/jobs/verify`

**Method:** POST (application/json)

**Body:**
```json
{
  "job_id": "job_001",
  "proof_photos": ["ipfs://test/proof.jpg"],
  "worker_id": "0xWorker123..." 
}
```

**Postman Setup:**
1. Method: POST
2. URL: `http://localhost:8000/api/jobs/verify`
3. Headers: `Content-Type: application/json`
4. Body tab → raw → JSON
5. Paste JSON above (use job_id from create response)

**Example Response:**
```json
{
  "success": true,
  "verified": true,
  "confidence": 0.95,
  "reason": "All requirements met. Work completed successfully.",
  "category": "APPROVED",
  "quality_score": 0.95,
  "issues": null,
  "suggestions": null
}
```

---

### 3. **Get Job Details**

**Endpoint:** `GET http://localhost:8000/api/jobs/{job_id}`

**Postman Setup:**
1. Method: GET
2. URL: `http://localhost:8000/api/jobs/job_001`

**Response:**
```json
{
  "success": true,
  "job": {
    "job_id": "job_001",
    "description": "Paint bedroom wall blue...",
    "verification_plan": {...},
    "status": "OPEN",
    "amount": 50
  }
}
```

---

### 4. **List All Jobs**

**Endpoint:** `GET http://localhost:8000/api/jobs`

**Postman Setup:**
1. Method: GET
2. URL: `http://localhost:8000/api/jobs`

---

## 🧪 Testing Flow in Postman

### Complete Test Scenario:

**Step 1: Create Job (Paralegal)**
```
POST /api/jobs/create
Body:
  - description: "Paint my bedroom wall blue at 123 Main for 50 GAS"
  - reference_image: [upload any JPG file]

Response: 
  - job_id: "job_001" ← Save this!
  - verification_plan: {...}
```

**Step 2: Get Job Details**
```
GET /api/jobs/job_001

Response:
  - Shows job data
  - Shows verification plan
  - Status: "OPEN"
```

**Step 3: Verify Work (Eye)**
```
POST /api/jobs/verify
Body:
{
  "job_id": "job_001",
  "proof_photos": ["ipfs://test/proof.jpg"],
  "worker_id": "0xWorker123"
}

Response:
  - verified: true/false
  - confidence: 0.95
  - reason: "..."
```

**Step 4: Check Final Status**
```
GET /api/jobs/job_001

Response:
  - Status: "COMPLETED" or "REJECTED"
```

## 📝 Postman Collection

### Sample Requests:

**1. Valid Job Creation:**
```
Description: "Clean graffiti at 555 Market Street for 10 GAS"
Image: Any photo
Expected: ✅ status: "complete", job created
```

**2. Vague Job (Missing Info):**
```
Description: "Clean my wall"
Image: Any photo
Expected: ⚠️ status: "needs_clarification", questions returned
```

**3. Work Verification:**
```
{
  "job_id": "job_001",
  "proof_photos": ["ipfs://test/proof.jpg"]
}
Expected: ✅ verified: true, confidence: 0.9+
```

## 🔧 Troubleshooting

### Server won't start:
```bash
# Install FastAPI dependencies
pip install fastapi uvicorn python-multipart

# Check port not in use
lsof -i:8000
```

### Vision errors with test images:
```
⚠️ Vision verification failed: image_parse_error
```
**Solution:** Use real JPG/PNG images, not test data

### Job not found:
```
404: Job job_001 not found
```
**Solution:** Create job first with POST /api/jobs/create

## 💡 Tips

### Using Swagger UI (Easiest):
1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in the form
4. Click "Execute"
5. See response below

### Using Postman:
1. Create new request
2. Set method and URL
3. Add body/form-data
4. Send request
5. View response

### Testing with curl:
```bash
# Create job
curl -X POST http://localhost:8000/api/jobs/create \
  -F "description=Paint wall blue at 123 Main for 50 GAS" \
  -F "reference_image=@/path/to/image.jpg"

# Verify work
curl -X POST http://localhost:8000/api/jobs/verify \
  -H "Content-Type: application/json" \
  -d '{"job_id":"job_001","proof_photos":["ipfs://test/proof.jpg"]}'
```

## 📊 Expected Results

### Paralegal (Create Job):
- ✅ Extracts task, location, price
- ✅ Generates verification_plan
- ✅ Creates job_id
- ✅ Returns status: "complete"

### Eye (Verify Work):
- ✅ Fetches job from database
- ✅ Uses verification_plan from Paralegal
- ✅ Makes APPROVED/REJECTED decision
- ✅ Returns confidence score

---

**Ready to test!** Start the server and open Postman. 🚀

