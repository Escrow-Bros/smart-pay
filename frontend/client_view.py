"""
GigShield Client Dashboard - Job Creation View
TASK-010: Client View with Paralegal Agent Integration

This demonstrates how to call the Paralegal API from Streamlit frontend.
"""
import streamlit as st
import requests
import json
from typing import Optional

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page Configuration
st.set_page_config(
    page_title="GigShield - Create Job",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'user_wallet' not in st.session_state:
    st.session_state.user_wallet = "0x1234...5678"  # Mock wallet

# Header
st.title("🛡️ GigShield - Create a Gig")
st.markdown(f"**Wallet:** `{st.session_state.user_wallet}`")
st.divider()

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Describe Your Task")
    
    # User Input
    user_message = st.text_area(
        "What do you need done?",
        placeholder="Example: Clean graffiti at 555 Market St for 10 GAS",
        height=100,
        help="Describe the task, location, and how much you're willing to pay"
    )
    
    # Action Buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=True)
    
    with col_btn2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_btn:
        st.session_state.extracted_data = None
        st.rerun()
    
    # Call the API when user clicks Analyze
    if analyze_btn and user_message:
        with st.spinner("🤖 AI is analyzing your request..."):
            try:
                # Call the Paralegal API
                response = requests.post(
                    f"{API_BASE_URL}/api/jobs/parse",
                    json={"message": user_message},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.extracted_data = result
                else:
                    st.error(f"API Error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API server. Make sure it's running at http://localhost:8000")
                st.info("Run: `cd agent && python api_server.py`")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display Results
    if st.session_state.extracted_data:
        st.divider()
        
        data = st.session_state.extracted_data['data']
        ready = st.session_state.extracted_data['ready_for_contract']
        
        if ready:
            st.markdown('<div class="success-box">✅ All information extracted! Ready to create contract.</div>', 
                       unsafe_allow_html=True)
        else:
            missing = ", ".join(data['missing_fields'])
            st.markdown(f'<div class="warning-box">⚠️ Missing information: {missing}</div>', 
                       unsafe_allow_html=True)
        
        st.subheader("📊 Extracted Data")
        
        # Display extracted fields
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Task:**")
            if data['task']:
                st.success(data['task'])
            else:
                st.error("Not specified")
            
            st.markdown("**Location:**")
            if data['location']:
                st.success(data['location'])
            else:
                st.error("Not specified")
        
        with col_b:
            st.markdown("**Price:**")
            if data['price_amount']:
                st.success(f"{data['price_amount']} {data['price_currency']}")
            else:
                st.error("Not specified")
        
        # Manual Override Section (if data is missing)
        if not ready:
            st.divider()
            st.subheader("✏️ Complete Missing Information")
            
            with st.form("manual_override"):
                if not data['task']:
                    task_input = st.text_input("Task Description", value="")
                else:
                    task_input = data['task']
                
                if not data['location']:
                    location_input = st.text_input("Location", value="")
                else:
                    location_input = data['location']
                
                col_price1, col_price2 = st.columns(2)
                with col_price1:
                    if not data['price_amount']:
                        amount_input = st.number_input("Amount", min_value=1, value=10)
                    else:
                        amount_input = data['price_amount']
                
                with col_price2:
                    if not data['price_currency']:
                        currency_input = st.selectbox("Currency", ["GAS", "NEO", "USDC", "USD"])
                    else:
                        currency_input = data['price_currency']
                
                submit_override = st.form_submit_button("Update Information", type="primary")
                
                if submit_override:
                    # Update the data
                    st.session_state.extracted_data['data']['task'] = task_input
                    st.session_state.extracted_data['data']['location'] = location_input
                    st.session_state.extracted_data['data']['price_amount'] = amount_input
                    st.session_state.extracted_data['data']['price_currency'] = currency_input
                    st.session_state.extracted_data['data']['missing_fields'] = []
                    st.session_state.extracted_data['ready_for_contract'] = True
                    st.rerun()
        
        # Create Contract Button (only if ready)
        if ready:
            st.divider()
            if st.button("🚀 Create Smart Contract", type="primary", use_container_width=True):
                with st.spinner("Creating contract on Neo N3..."):
                    # TODO: Call TASK-004 smart contract here
                    st.success("✅ Contract created successfully!")
                    st.balloons()
                    st.info("This will integrate with TASK-004 (Smart Contract)")

with col2:
    st.subheader("💡 Tips")
    st.markdown("""
    **Include in your message:**
    - ✅ What needs to be done
    - ✅ Where it should be done
    - ✅ How much you'll pay
    
    **Examples:**
    - "Clean graffiti at 555 Market St for 10 GAS"
    - "Verify ad at Times Square for 20 NEO"
    - "Stock shelf at Building 7 for 15 USDC"
    """)
    
    st.divider()
    
    st.subheader("🔧 API Status")
    
    # Check API health
    try:
        health_response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        if health_response.status_code == 200:
            st.success("🟢 API Online")
            health_data = health_response.json()
            st.caption(f"Model: {health_data.get('model', 'N/A')}")
        else:
            st.error("🔴 API Error")
    except:
        st.error("🔴 API Offline")
        st.caption("Run: `python agent/api_server.py`")
    
    st.divider()
    
    # Debug Panel (for development)
    with st.expander("🐛 Debug Info"):
        if st.session_state.extracted_data:
            st.json(st.session_state.extracted_data)
        else:
            st.caption("No data yet")

# Footer
st.divider()
st.caption("GigShield - Trustless payments for the Physical Gig Economy")
