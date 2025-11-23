# Eye Agent - Universal Work Verifier

**Task:** TASK-013  
**File:** `agent/eye.py`  
**Status:** ✅ Complete

## 🎯 Purpose

The Eye Agent is the **impartial AI judge** that verifies worker proof photos. It works for ANY type of gig work by comparing before/after photos and checking against requirements.

## 🔄 What It Does

### Input:
```python
proof_photos = ["ipfs://Qm.../after_wall.jpg"]
job_id = "job_12345"
```

### Process:
1. **Fetches job data** from smart contract (verification plan from Paralegal)
2. **Downloads images** (reference + proof) from IPFS
3. **Compares before/after** using GPT-4V vision analysis
4. **Verifies requirements** against Paralegal's verification plan
5. **Makes final decision** with multi-layer checks

### Output:
```python
{
    "verified": True,
    "confidence": 0.95,
    "reason": "All requirements met. Work completed successfully.",
    "category": "APPROVED",
    "quality_score": 0.95,
    "comparison_data": {
        "location_confidence": 0.97,
        "transformation": ["white → blue", "clean edges visible"]
    }
}
```

## 🔍 Verification Pipeline

### Step 1: Compare Before/After (Vision)
```python
comparison = await compare_before_after(
    reference_photos,  # From client (BEFORE state)
    proof_photos,      # From worker (AFTER state)
    verification_plan  # From Paralegal
)
```

**Checks with GPT-4V:**
- ✅ Same location? (matching features: outlets, doors, windows)
- ✅ Transformation detected? (white wall → blue wall)
- ✅ Coverage consistent? (same area shown in both photos)
- ✅ Quality of transformation? (clean, professional)

**Returns:**
```python
{
    "same_location": {
        "verdict": True,
        "confidence": 0.97,
        "matching_features": ["outlet bottom-right", "door frame left"],
        "reasoning": "All key landmarks match"
    },
    "transformation_detected": {
        "verdict": True,
        "changes": ["color changed white to blue", "surface cleaned"],
        "matches_expected": True
    },
    "coverage_consistency": {
        "verdict": True,
        "coverage_ratio": 0.98,
        "angle_similarity": 0.95,
        "concerns": []
    },
    "work_completed": True
}
```

### Step 2: Verify Requirements (Vision)
```python
verification = await verify_requirements(
    proof_photos,
    task_description,
    verification_plan,  # From Paralegal
    comparison
)
```

**Checks with GPT-4V:**
- ✅ Quality indicators met? (even coverage, clean edges, no drips)
- ✅ Verification checklist passed? (all yes/no questions)
- ✅ Common mistakes avoided? (not hiding defects)
- ✅ Required evidence present? (full wall, corners visible)

**Returns:**
```python
{
    "verdict": "APPROVED",
    "confidence": 0.95,
    "reasoning": "Work completed to professional standard. All criteria met.",
    "issues": [],
    "suggestions": []
}
```

### Step 3: Final Decision (Multi-Layer)
```python
decision = make_final_decision(
    verification_plan,
    comparison,
    verification
)
```

**Multi-layer checks:**
1. ✅ Location match with >80% confidence
2. ✅ Expected transformation detected
3. ✅ Coverage consistent with reference
4. ✅ AI verification approved
5. ✅ Quality standards met

**Returns final verdict:**
```python
{
    "verified": True,        # ← Approve/Reject
    "confidence": 0.95,      # ← How certain
    "reason": "...",         # ← Why
    "category": "APPROVED"   # ← Status code
}
```

## 🧩 Key Methods

### `verify(proof_photos, job_id)`
Main entry point for verification.

### `compare_before_after(reference, proof, plan)`
Vision-based before/after comparison with GPT-4V.

### `verify_requirements(proof, task, plan, comparison)`
Vision-based quality verification against checklist.

### `make_final_decision(plan, comparison, verification)`
Multi-layer approval logic with fraud prevention.

### `_download_and_encode_image(url)`
Downloads from IPFS and encodes as base64 for vision API.

## 🛡️ Fraud Prevention

### 1. Location Matching
```python
# Prevents: Using photo of different location
Check: Do landmarks match? (outlets, switches, doors)
Confidence: Must be >80%
If not: REJECT - "Not the same location"
```

### 2. Coverage Consistency
```python
# Prevents: Hiding incomplete work by zooming in
Check: Does proof show same area as reference?
Coverage ratio: Must be >0.9
If not: REJECT - "Proof shows less area than reference"
```

### 3. Transformation Verification
```python
# Prevents: No actual work done
Check: Did expected change occur? (white → blue)
Matches expected: Must be True
If not: REJECT - "Expected transformation not detected"
```

### 4. Quality Assessment
```python
# Prevents: Poor quality work
Check: Visual inspection of edges, drips, coverage
Quality indicators: All must pass
If not: REJECT - "Quality issues detected"
```

## 🎨 Example Verifications

### Example 1: Painting Job - APPROVED ✅
```
Task: "Paint wall blue"
Reference: White wall photo
Proof: Blue wall photo

Vision Analysis:
✅ Same wall (outlet and door match)
✅ Color changed white → blue
✅ Edges clean (no spillover)
✅ Coverage complete
✅ No drips detected

Decision: APPROVED (95% confidence)
```

### Example 2: Lawn Mowing - REJECTED ❌
```
Task: "Mow front lawn"
Reference: Overgrown lawn
Proof: Partially mowed lawn

Vision Analysis:
✅ Same property (house matches)
✅ Grass height reduced
❌ Northwest corner not mowed
❌ Edges not trimmed

Decision: REJECTED
Reason: "Incomplete coverage - patches visible in northwest corner"
```

### Example 3: Fraud Attempt - REJECTED ❌
```
Task: "Paint bedroom wall blue"
Reference: Client's wall (outlet on right)
Proof: Different wall (no outlet, different features)

Vision Analysis:
❌ Features don't match
❌ Location confidence: 0.23

Decision: REJECTED
Category: LOCATION_MISMATCH
Reason: "Proof photo is not of the same location"
```

## 🔌 Integration Points

### With Paralegal Agent:
```python
# Paralegal generates plan once:
verification_plan = {...}

# Eye uses plan for all verifications:
verdict = await verify_work(proof_photos, job_id)
# Fetches verification_plan from contract
```

### With Smart Contract:
```python
# Eye fetches job data:
job_data = contract.get_job(job_id)

# Eye makes decision:
if verdict["verified"]:
    contract.release_funds(job_id, worker)
else:
    worker_can_retry()
```

### With Frontend:
```python
# Simple function call:
verdict = await verify_work(proof_photos, job_id)

if verdict["verified"]:
    st.success(f"✅ {verdict['reason']}")
else:
    st.error(f"❌ {verdict['reason']}")
```

## 🎓 Key Features

### ✅ Task-Agnostic
Works for painting, cleaning, delivery, repair, landscaping, etc.

### ✅ Vision-Powered
Actually sees and analyzes images with GPT-4V.

### ✅ Fraud-Resistant
Multiple layers of verification prevent cheating.

### ✅ Consistent
Uses Paralegal's plan for same standards across all workers.

### ✅ Transparent
Clear reasoning for every decision.

## 🚀 Usage

```python
from agent.eye import verify_work

# Verify worker's submitted proof
verdict = await verify_work(
    proof_photos=["ipfs://Qm.../proof.jpg"],
    job_id="job_12345"
)

if verdict["verified"]:
    print(f"✅ APPROVED: {verdict['reason']}")
    # Trigger payment release
else:
    print(f"❌ REJECTED: {verdict['reason']}")
    # Worker can retry
```

## 🔑 Key Technologies

- **SpoonOS SDK** - Configuration & LLM management
- **GPT-4V (gpt-4o)** - Vision analysis
- **IPFS** - Image download from decentralized storage
- **Sudo AI** - LLM provider
- **httpx monkey-patch** - API compatibility

## ⚙️ Configuration

Requires in `agent/.env`:
```env
OPENAI_API_KEY=your-sudo-api-key
OPENAI_BASE_URL=https://sudoapp.dev/api/v1
```

## 📊 Performance

- **Image downloads:** 1-5 seconds
- **Vision analysis:** 3-8 seconds per comparison
- **Total time:** 5-15 seconds per verification
- **Cost:** ~$0.02-0.05 per verification

## 🎯 Decision Categories

- `APPROVED` - Work meets all requirements
- `LOCATION_MISMATCH` - Wrong location/different object
- `UNCERTAIN_LOCATION` - Can't confirm same location (<80% confidence)
- `INCOMPLETE_WORK` - Expected transformation not detected
- `COVERAGE_MISMATCH` - Proof shows different area than reference
- `REQUIREMENTS_NOT_MET` - Quality issues or checklist failures

## 💡 Why It Works

1. **Paralegal defines rules once** at job creation
2. **Eye enforces rules consistently** for all workers
3. **Vision models** provide actual image analysis
4. **Multi-layer checks** prevent fraud
5. **Clear feedback** helps workers improve

The Eye sees all, judges fairly, and protects both clients and workers! 👁️⚖️

