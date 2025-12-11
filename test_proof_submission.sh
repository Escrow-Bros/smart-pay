#!/bin/bash
# Test the proof submission with the fixed Eye Agent

echo "🧪 Testing Proof Submission (Fixed Eye Agent)"
echo "=============================================="
echo ""

curl -X POST 'http://localhost:8000/api/jobs/submit' \
  -H 'Content-Type: application/json' \
  -d '{
    "job_id": 1765062601,
    "proof_photos": ["https://endpoint.4everland.co/gig-pay/upload_8db9d105.jpg"],
    "worker_location": {
      "lat": 37.335814763559554,
      "lng": -121.88746922892958,
      "accuracy": 37
    }
  }'

echo ""
echo ""
echo "📝 Expected behavior:"
echo "  - Should download and analyze images (with httpx)"
echo "  - Should verify GPS location (50m radius)"
echo "  - Should return verification result"
echo ""
