#!/bin/bash
# Test job creation with location data

curl -X POST 'http://localhost:8000/api/jobs/create' \
  -H 'Content-Type: application/json' \
  -d '{
    "client_address": "NYKdk2LUEngRZNc5hnFvuFJV6n2hpppSVg",
    "description": "Build a tar road 5 meters wide and 15 meters long in front of the user'\''s house, leading up to the entrance. Permissions are already obtained.",
    "reference_photos": ["https://endpoint.4everland.co/gig-pay/upload_8cba21d1.jpg"],
    "location": "101 E San Fernando St, San Jose, CA 95112, USA",
    "latitude": 37.3357088,
    "longitude": -121.8866652,
    "amount": 2,
    "verification_plan": {
      "task_category": "Construct a road",
      "verification_checklist": [],
      "quality_indicators": []
    }
  }'
