# Frontend Integration Guide

## How Your Frontend Calls the API

I've created a complete Streamlit example that shows exactly how to integrate the Paralegal API into your frontend.

## 📁 File Created

**[frontend/client_view.py](file:///Users/vineet/Documents/smart-pay/frontend/client_view.py)** - Complete working example

## 🔑 Key Integration Code

### 1. Basic API Call (Python/Streamlit)

```python
import requests

# Call the Paralegal API
response = requests.post(
    "http://localhost:8000/api/jobs/parse",
    json={"message": user_input},
    timeout=10
)

if response.status_code == 200:
    result = response.json()
    # result contains: success, data, ready_for_contract, message
```

### 2. With Error Handling

```python
try:
    response = requests.post(
        "http://localhost:8000/api/jobs/parse",
        json={"message": user_message},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Check if ready for contract
        if result['ready_for_contract']:
            # All fields present - create contract
            create_smart_contract(result['data'])
        else:
            # Show missing fields to user
            missing = result['data']['missing_fields']
            show_error(f"Missing: {', '.join(missing)}")
    else:
        show_error(f"API Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    show_error("API server is not running")
except Exception as e:
    show_error(f"Error: {str(e)}")
```

### 3. Response Structure

```python
{
    "success": true,
    "data": {
        "task": "Clean graffiti",
        "location": "555 Market St",
        "price_amount": 10,
        "price_currency": "GAS",
        "missing_fields": []
    },
    "ready_for_contract": true,
    "message": "Contract data extracted successfully"
}
```

## 🚀 Run the Frontend

### 1. Install Dependencies
```bash
cd /Users/vineet/Documents/smart-pay
source .venv/bin/activate
pip install streamlit requests
```

### 2. Start the API Server (Terminal 1)
```bash
cd agent
python api_server.py
```

### 3. Start the Frontend (Terminal 2)
```bash
streamlit run frontend/client_view.py
```

### 4. Open in Browser
The frontend will open at: `http://localhost:8501`

## 🎨 Frontend Features

The example includes:

✅ **Natural language input** - User types their request  
✅ **AI analysis** - Calls the Paralegal API  
✅ **Visual feedback** - Shows extracted data with color coding  
✅ **Missing field handling** - Allows manual input for missing data  
✅ **API health check** - Shows if backend is online  
✅ **Smart contract integration** - Placeholder for TASK-004  

## 📱 Other Frontend Options

### JavaScript/React

```javascript
// Fetch API
const response = await fetch('http://localhost:8000/api/jobs/parse', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: userInput
    })
});

const result = await response.json();

if (result.ready_for_contract) {
    // Create smart contract
    createContract(result.data);
} else {
    // Show missing fields
    showMissingFields(result.data.missing_fields);
}
```

### Axios (React/Vue)

```javascript
import axios from 'axios';

const analyzeJob = async (message) => {
    try {
        const response = await axios.post(
            'http://localhost:8000/api/jobs/parse',
            { message }
        );
        
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
    }
};

// Usage
const result = await analyzeJob("Clean graffiti at 555 Market St for 10 GAS");
```

### jQuery

```javascript
$.ajax({
    url: 'http://localhost:8000/api/jobs/parse',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        message: userInput
    }),
    success: function(result) {
        if (result.ready_for_contract) {
            createContract(result.data);
        }
    }
});
```

## 🔄 Integration Flow

```
User Input (Frontend)
    ↓
POST /api/jobs/parse
    ↓
Paralegal Agent (AI)
    ↓
Response with extracted data
    ↓
Frontend displays results
    ↓
If ready → Create Smart Contract (TASK-004)
```

## 🐛 Troubleshooting

### "Connection refused"
- Make sure API server is running: `python agent/api_server.py`
- Check it's on port 8000: `http://localhost:8000`

### CORS errors (if using JavaScript)
The API already has CORS enabled:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Already configured
)
```

### "API Offline" in frontend
Check API health endpoint:
```bash
curl http://localhost:8000/api/health
```

## 📋 Next Steps

1. **Test the frontend:**
   ```bash
   streamlit run frontend/client_view.py
   ```

2. **Customize the UI** - Edit `client_view.py` to match your design

3. **Connect to Smart Contract** - Replace the TODO in the "Create Contract" button with TASK-004 integration

4. **Add Worker View** - Create `frontend/worker_view.py` for the gig worker interface

## 🎯 Summary

Your frontend calls the API like this:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/jobs/parse",
    json={"message": "Clean graffiti at 555 Market St for 10 GAS"}
)

result = response.json()
# Use result['data'] to get task, location, price
```

**That's it!** The complete working example is in `frontend/client_view.py` 🚀
