# The Eye Agent - Universal Work Verification

**Status:** ✅ Implemented (TASK-013 partial)

## Overview

The Eye Agent is a generalized AI-powered verification system that works for ANY type of gig work by:

1. Comparing BEFORE (reference) vs AFTER (proof) photos
2. Verifying against job requirements from Paralegal agent
3. Making approval/rejection decisions

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  PARALEGAL AGENT (Job Creation - TASK-011)          │
│  Generates verification plan once                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  SMART CONTRACT (TASK-004/006)                      │
│  Stores verification plan on-chain                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  EYE AGENT (Verification - TASK-013) ← YOU ARE HERE │
│  Uses stored plan to verify work                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────┐
│  SMART CONTRACT (Release Funds - TASK-005)          │
│  If approved, releases payment to worker            │
└─────────────────────────────────────────────────────┘
```

## Features

### ✅ Implemented

- Universal verification for any task type
- Before/after photo comparison
- Location matching (anti-fraud)
- Coverage consistency checks
- AI-powered quality assessment
- Multi-layer decision logic
- SpoonOS integration with Sudo AI

### 🚧 Placeholders (To Be Implemented)

- Smart contract integration (TASK-004) - currently uses mock data
- Vision model support (GPT-4V) - currently uses text model
- Paralegal agent integration (TASK-011) - expects verification plan
- Apro Oracle integration (TASK-014) - for GPS/weather verification

## Usage

### Basic Usage

```python
from agent.eye import verify_work

# Verify worker's proof
result = await verify_work(
    proof_photos=["ipfs://Qm.../after_photo.jpg"],
    job_id="job_12345"
)

if result["verified"]:
    print(f"✅ APPROVED: {result['reason']}")
    # Release payment via smart contract
else:
    print(f"❌ REJECTED: {result['reason']}")
    # Worker can retry
```

### Frontend Integration

```python
# frontend/gigshield_app.py

from agent.eye import verify_work

# When worker submits proof
with st.spinner("👁️ AI Tribunal reviewing..."):
    verdict = await verify_work(
        proof_photos=[public_url],
        job_id=selected_job_id
    )

if verdict["verified"]:
    st.success(f"🏆 APPROVED: {verdict['reason']}")
    st.balloons()
else:
    st.error(f"❌ REJECTED: {verdict['reason']}")
```

## Verification Flow

### Step 1: Compare Before/After

```python
comparison = await compare_before_after(
    reference_photos,  # From client at job creation
    proof_photos,      # From worker after completion
    verification_plan  # From Paralegal agent
)

# Checks:
# - Same location? (matching features)
# - Transformation detected?
# - Coverage consistent?
```

### Step 2: Verify Requirements

```python
verification = await verify_requirements(
    proof_photos,
    task_description,
    verification_plan,
    comparison
)

# Checks:
# - Quality standards met?
# - All checklist items passed?
# - Common mistakes avoided?
```

### Step 3: Final Decision

```python
decision = make_final_decision(
    verification_plan,
    comparison,
    verification
)

# Multi-layer checks:
# - Location match (>80% confidence)
# - Transformation matches expected
# - Coverage consistent
# - AI approves quality
```

## Response Format

```python
{
    "verified": bool,           # True = approved, False = rejected
    "confidence": float,        # 0.0 to 1.0
    "reason": str,             # Human-readable explanation
    "category": str,           # APPROVED, LOCATION_MISMATCH, etc.
    "issues": [str],           # Problems found (if rejected)
    "suggestions": [str],      # How to improve (if rejected)
    "quality_score": float,    # Overall quality rating
    "comparison_data": {...}   # Detailed comparison info
}
```

## Testing

```bash
# Run test with placeholder data
cd agent
python test_eye.py
```

## Integration Points

### With Paralegal (TASK-011)

```python
# Paralegal generates at job creation:
verification_plan = {
    "task_category": "painting",
    "expected_transformation": {...},
    "quality_indicators": [...],
    "verification_checklist": [...]
}

# Eye uses it for verification:
result = await verify_work(proof_photos, job_id)
# Fetches verification_plan from smart contract
```

### With Smart Contract (TASK-004/005)

```python
# Eye fetches job data:
job_data = get_job_from_contract(job_id)

# Eye verifies and returns verdict:
if result["verified"]:
    # Smart contract releases funds to worker
    contract.release_funds(job_id, worker_address)
```

### With Apro Oracle (TASK-014)

```python
# Future enhancement - add context verification:
context = apro_oracle.verify_context(
    gps=photo_metadata.gps,
    timestamp=photo_metadata.timestamp
)

# Combine with visual verification
final_verdict = combine_verifications(
    visual_verification,
    context_verification
)
```

## Examples

### Example 1: Painting Job

```python
# Job: "Paint bedroom wall blue"
# Reference: White wall photo
# Proof: Blue wall photo

# Eye checks:
✅ Same wall (outlet and switch match)
✅ Color changed white → blue
✅ Clean edges visible
✅ Complete coverage
✅ Quality professional

Result: APPROVED ✅
```

### Example 2: Lawn Mowing

```python
# Job: "Mow front lawn"
# Reference: Overgrown lawn
# Proof: Mowed lawn

# Eye checks:
✅ Same property (house and fence match)
✅ Grass height reduced
✅ Edges trimmed
✅ Complete coverage
❌ Some patches missed

Result: REJECTED ❌
Reason: "Incomplete coverage - patches visible in northwest corner"
```

### Example 3: Fraud Attempt

```python
# Job: "Paint bedroom wall blue"
# Reference: Client's wall (outlet on right)
# Proof: Different wall (no outlet)

# Eye checks:
❌ Features don't match
❌ Location confidence: 0.23

Result: REJECTED ❌
Category: LOCATION_MISMATCH
Reason: "Proof photos are not of the same location as reference photos"
```

## Configuration

Set up your `.env` file:

```env
# Sudo AI (for verification)
OPENAI_API_KEY=your-sudo-api-key
OPENAI_BASE_URL=https://sudoapp.dev/api/v1
```

## Future Enhancements

- [ ] Add GPT-4V vision model support
- [ ] Integrate with Apro Oracle for GPS verification
- [ ] Worker reputation scoring
- [ ] Image hash fraud detection
- [ ] Multi-photo requirement enforcement
- [ ] Quality trend analysis
- [ ] Dispute resolution system

## Notes

- Currently uses text-based AI with photo URL references
- Upgrade to GPT-4V or similar for actual image analysis
- Verification plan comes from Paralegal (TASK-011)
- Smart contract integration needed (TASK-004)
- Works with any task type - fully generalized!
