# Paralegal Agent - Job Architect

**Task:** TASK-011  
**File:** `agent/paralegal.py`  
**Status:** ✅ Complete

## 🎯 Purpose

The Paralegal Agent is the **job validator and requirements architect**. It processes client job descriptions, validates them, and generates verification plans for the Eye agent.

## 🔄 What It Does

### Input:
```python
text = "Paint my bedroom wall blue at 123 Main St for 50 GAS"
reference_image = image_bytes  # Photo of current wall state
```

### Process:
1. **Extracts structured data** from natural language
2. **Validates clarity** (ensures task, location, price are clear)
3. **Verifies image match** (uses GPT-4V to check photo matches description)
4. **Generates verification plan** (rules for Eye agent to use)
5. **Creates acceptance criteria** (specific measurable requirements)
6. **Analyzes reference photo** (baseline features for comparison)

### Output:
```python
{
    "status": "complete",
    "data": {
        "task": "Paint bedroom wall blue",
        "location": "123 Main St",
        "price_amount": 50,
        "price_currency": "GAS"
    },
    "verification_plan": {
        "task_category": "painting",
        "expected_transformation": {
            "before": "unpainted wall",
            "after": "wall painted blue"
        },
        "quality_indicators": [
            "even color coverage",
            "clean edges",
            "no drips"
        ],
        "verification_checklist": [
            "Is it the same wall?",
            "Is color blue?",
            "Are edges clean?"
        ],
        "common_mistakes": [
            "showing only small section",
            "hiding bad edges"
        ],
        "required_evidence": [
            "full wall visible",
            "all corners visible"
        ]
    },
    "acceptance_criteria": [
        "Wall must be completely painted blue",
        "Edges must be clean with no paint on ceiling/floor",
        "No drips or runs visible",
        "Photo must show entire wall with all corners"
    ],
    "reference_analysis": {
        "baseline_features": [...],
        "estimated_dimensions": "...",
        "color_info": {...}
    }
}
```

## 🧩 Key Functions

### `analyze_job_request(text, reference_image)`
Main entry point that orchestrates all validation steps.

### `validate_clarity(text, extracted_data)`
Checks if job description has all critical information (task, location, price).

### `verify_image_match(text, task, image_bytes)`
Uses GPT-4V to verify reference photo matches the described task.

### `generate_verification_plan(task, task_description)`
Creates the verification rules that Eye agent will use.

### `generate_acceptance_criteria(task, location)`
Generates specific, measurable criteria for task completion.

### `analyze_reference_photo(image_bytes)`
Analyzes reference photo to extract baseline features (placeholder for now).

## 🔍 Validation Modes

### Status: "complete"
All validations passed, ready to create job.

### Status: "needs_clarification"
Missing critical information (task/location/price).
Returns questions for client to answer.

### Status: "mismatch"
Reference photo doesn't match description.
Example: Says "paint wall" but photo shows a door.

## 🎨 Example Scenarios

### Scenario 1: Valid Job
```python
Input: "Paint bedroom wall blue at 123 Main St for 50 GAS"
Photo: Shows unpainted bedroom wall

Result: ✅ COMPLETE
- Extracts all data
- Image matches
- Generates plan
```

### Scenario 2: Vague Description
```python
Input: "Clean my wall"
Photo: Shows a wall

Result: ❌ NEEDS_CLARIFICATION
Questions:
- Where is the location?
- How much will this cost?
```

### Scenario 3: Image Mismatch
```python
Input: "Fix broken window"
Photo: Shows intact window (not broken)

Result: ❌ MISMATCH
Reason: "Image shows intact window, but task says 'broken'"
```

## 🔧 Integration with Eye Agent

**What Paralegal Generates → What Eye Uses:**

| Paralegal Output | Eye Agent Uses It For |
|------------------|----------------------|
| `verification_plan.quality_indicators` | Checks each indicator visually |
| `verification_plan.verification_checklist` | Goes through each check |
| `verification_plan.expected_transformation` | Verifies before→after change |
| `verification_plan.common_mistakes` | Watches for these issues |
| `verification_plan.required_evidence` | Ensures proof shows required elements |
| `reference_analysis.baseline_features` | Matches features in proof photo |

## 💡 Why This Architecture?

**Generate Once, Use Many Times:**
- Paralegal runs once at job creation (client pays)
- Verification plan stored in smart contract
- Eye uses same plan for all verification attempts
- Cost efficient: No plan regeneration per worker

**Consistency:**
- Same verification rules for all workers
- No "moving goalposts"
- Fair for everyone

**Transparency:**
- Workers see requirements before accepting job
- No surprise rejections
- Clear expectations upfront

## 🚀 Usage

```python
from agent.paralegal import analyze_job_request

# Validate job submission
result = await analyze_job_request(
    text="Paint my wall blue at 123 Main for 50 GAS",
    reference_image=image_bytes_from_camera
)

if result["status"] == "complete":
    # Store in smart contract
    contract.create_job(
        client_address,
        result["data"],
        result["verification_plan"],
        reference_ipfs_url
    )
else:
    # Ask client for clarification
    show_questions(result["clarifying_questions"])
```

## 🔑 Key Technologies

- **SpoonOS SDK** - LLM orchestration
- **GPT-4V (gpt-4o)** - Vision analysis
- **Sudo AI** - LLM provider
- **httpx monkey-patch** - API compatibility fix

## 📊 Performance

- **Execution time:** 3-8 seconds
- **AI calls:** 3-5 (extraction, validation, plan generation, vision)
- **Cost per job:** ~$0.03-0.08
- **Success rate:** High (with proper inputs)

## 🎯 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced image analysis (dimensions, colors)
- [ ] Learning from past verifications
- [ ] Confidence calibration
- [ ] Batch processing

