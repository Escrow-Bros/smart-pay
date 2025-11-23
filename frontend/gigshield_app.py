"""
GigShield Worker Portal - Streamlit Frontend
Secure, AI-verified proof-of-work for the gig economy
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import from agent module
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from agent.storage import upload_to_ipfs
from agent.eye import verify_work

st.set_page_config(
    page_title="GigShield Worker Portal",
    page_icon="🛡️",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    .success-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #d4edda;
        border: 2px solid #28a745;
    }
    .error-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 2px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ GigShield Worker Portal")
st.markdown("**Decentralized Work Verification** | Powered by AI & Blockchain")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("How It Works")
    st.markdown("""
    1. 📋 **Task Assignment**
       - Review your task
    
    2. 📸 **Capture Proof**
       - Take a photo when done
    
    3. ☁️ **IPFS Upload**
       - Secure, permanent storage
    
    4. 👁️ **AI Verification**
       - The Eye judges your work
    
    5. 💰 **Get Paid**
       - Smart contract releases funds
    """)
    
    st.divider()
    st.caption("**Status:** Beta v0.1")
    st.caption("**Network:** Testnet")

# Main Content

# 1. Task Description (In production, this comes from smart contract)
st.subheader("📋 Your Task")
task_desc = st.text_input(
    "Task Description",
    value="Mow the lawn and give a thumbs up",
    help="In production, this is loaded from the blockchain"
)

if not task_desc:
    st.warning("⚠️ No task assigned")
    st.stop()

st.info(f"**Assigned Task:** {task_desc}")

st.markdown("---")

# 2. Capture Photo
st.subheader("📸 Step 1: Capture Proof")
st.caption("Take a clear photo showing the completed work")

photo = st.camera_input("Take a photo of the finished job")

if photo:
    st.success("✅ Photo captured!")
    
    # Show preview
    with st.expander("🖼️ Preview Your Proof", expanded=False):
        st.image(photo, caption="Your proof photo", use_container_width=True)
    
    st.markdown("---")
    
    # 3. Upload to IPFS
    st.subheader("☁️ Step 2: Upload to Blockchain Storage")
    
    if 'public_url' not in st.session_state:
        st.session_state.public_url = None
    
    if st.button("🚀 Upload to IPFS", type="primary", use_container_width=True):
        with st.spinner("📤 Uploading Evidence to Decentralized Storage (IPFS)..."):
            image_bytes = photo.getvalue()
            public_url = upload_to_ipfs(image_bytes, filename="gigshield_proof.jpg")
            
            if public_url:
                st.session_state.public_url = public_url
                st.rerun()
    
    # If we have a URL, show it and proceed to verification
    if st.session_state.public_url:
        st.success("✅ Proof Uploaded to Blockchain Storage!")
        st.caption(f"**Verified URL:** {st.session_state.public_url}")
        
        st.markdown("---")
        
        # 4. AI Verification
        st.subheader("👁️ Step 3: AI Tribunal Review")
        
        if 'verdict' not in st.session_state:
            st.session_state.verdict = None
        
        if st.button("⚖️ Submit for Verification", type="primary", use_container_width=True):
            with st.spinner("👁️ The AI Tribunal is reviewing your work..."):
                verdict = verify_work(st.session_state.public_url, task_desc)
                st.session_state.verdict = verdict
                st.rerun()
        
        # 5. Display Verdict
        if st.session_state.verdict:
            verdict = st.session_state.verdict
            
            st.markdown("---")
            st.subheader("⚖️ Verdict")
            
            if verdict.get("verified"):
                st.balloons()
                
                st.markdown("""
                <div class="success-box">
                    <h2>🏆 WORK APPROVED</h2>
                    <p style="font-size: 18px;">{}</p>
                    <p><strong>Confidence:</strong> {:.0%}</p>
                </div>
                """.format(
                    verdict.get('reason', 'Task completed successfully'),
                    verdict.get('confidence', 0.95)
                ), unsafe_allow_html=True)
                
                st.markdown("---")
                st.success("💰 **Next Step:** Smart contract will release payment to your wallet")
                st.info("🔗 **Transaction Hash:** Coming soon...")
                
                # Show raw AI response in expander
                if 'raw_response' in verdict:
                    with st.expander("🤖 View AI Analysis"):
                        st.text(verdict['raw_response'])
            
            else:
                st.markdown("""
                <div class="error-box">
                    <h2>❌ WORK REJECTED</h2>
                    <p style="font-size: 18px;">{}</p>
                    <p><strong>Confidence:</strong> {:.0%}</p>
                </div>
                """.format(
                    verdict.get('reason', 'Task requirements not met'),
                    verdict.get('confidence', 0.95)
                ), unsafe_allow_html=True)
                
                st.markdown("---")
                st.warning("⚠️ **Please retake the photo ensuring all requirements are met:**")
                st.markdown(f"- {task_desc}")
                st.markdown("- Clear, well-lit photo")
                st.markdown("- All required elements visible")
                
                # Show raw AI response in expander
                if 'raw_response' in verdict:
                    with st.expander("🤖 View AI Analysis"):
                        st.text(verdict['raw_response'])
                
                # Reset button
                if st.button("🔄 Try Again", use_container_width=True):
                    st.session_state.public_url = None
                    st.session_state.verdict = None
                    st.rerun()

else:
    st.info("👆 Click 'Take a photo' above to get started")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>GigShield</strong> | Protecting Workers & Employers with AI + Blockchain</p>
    <p style="font-size: 12px;">
        Proof stored on IPFS | Verified by AI | Secured by Smart Contracts
    </p>
</div>
""", unsafe_allow_html=True)

