import streamlit as st
import requests
import os
from typing import List, Dict, Optional
import pandas as pd

# Configuration
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Learner Engagement Platform",
    page_icon="📚",
    layout="wide"
)

def fetch_learners(risk_filter: Optional[str] = None) -> List[Dict]:
    """Fetch learners from the backend API with optional risk filtering."""
    try:
        url = f"{API_BASE}/api/learners"
        params = {}
        if risk_filter and risk_filter != "all":
            params["risk"] = risk_filter
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot connect to backend API at {API_BASE}")
        st.info("Make sure the backend server is running on the correct port.")
        return []
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Backend may be overloaded.")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return []

def generate_nudge(learner_id: str, channel: str) -> Optional[Dict]:
    """Generate a nudge for a specific learner."""
    try:
        url = f"{API_BASE}/api/learners/{learner_id}/nudge"
        payload = {"channel": channel}
        
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to generate nudge: {str(e)}")
        return None

def display_learner_table(learners: List[Dict]):
    """Display learners in a table with action buttons."""
    if not learners:
        st.warning("No learners found. Make sure the backend is running and has data.")
        return
    
    # Convert to DataFrame for better display
    df_data = []
    for learner in learners:
        df_data.append({
            "Name": learner["name"],
            "Email": learner["email"],
            "Program": learner["program"],
            "Completion %": f"{learner['completed_percent']:.1f}%",
            "Risk Score": f"{learner['risk_score']:.3f}",
            "Risk Level": learner["risk_label"].upper(),
            "Last Login": learner["last_login"]
        })
    
    df = pd.DataFrame(df_data)
    
    # Color code risk levels
    def color_risk_level(val):
        if val == "HIGH":
            return "background-color: #ffebee; color: #c62828"
        elif val == "MEDIUM":
            return "background-color: #fff3e0; color: #ef6c00"
        else:
            return "background-color: #e8f5e8; color: #2e7d32"
    
    styled_df = df.style.applymap(color_risk_level, subset=["Risk Level"])
    st.dataframe(styled_df, use_container_width=True)
    
    # Action buttons for each learner
    st.subheader("📤 Generate Nudges")
    
    cols = st.columns(min(len(learners), 3))
    for idx, learner in enumerate(learners):
        with cols[idx % 3]:
            with st.expander(f"🎯 {learner['name']} ({learner['risk_label'].upper()})"):
                st.write(f"**Email:** {learner['email']}")
                st.write(f"**Risk Score:** {learner['risk_score']:.3f}")
                st.write(f"**Completion:** {learner['completed_percent']:.1f}%")
                
                # Channel selection
                channel = st.selectbox(
                    "Select Channel:",
                    ["in-app", "whatsapp", "email"],
                    key=f"channel_{learner['id']}"
                )
                
                # Generate nudge button
                if st.button(f"Generate Nudge", key=f"nudge_{learner['id']}"):
                    with st.spinner("Generating nudge..."):
                        nudge_result = generate_nudge(learner["id"], channel)
                        
                        if nudge_result:
                            # Display the generated nudge
                            st.success("✅ Nudge generated successfully!")
                            
                            # Show fallback indicator
                            if nudge_result.get("gptFallback", False):
                                st.warning("⚠️ **Fallback Mode**: Using pre-defined template (OpenAI API unavailable)")
                            else:
                                st.info("🤖 **AI Generated**: Content created using OpenAI")
                            
                            # Display nudge content
                            st.text_area(
                                "Generated Nudge:",
                                value=nudge_result.get("content", "No content available"),
                                height=100,
                                key=f"content_{learner['id']}_{channel}"
                            )
                            
                            # Show metadata
                            with st.expander("📊 Nudge Details"):
                                st.json({
                                    "channel": nudge_result.get("channel", channel),
                                    "prompt_version": nudge_result.get("prompt_version", "unknown"),
                                    "gpt_fallback": nudge_result.get("gptFallback", False),
                                    "learner_id": learner["id"]
                                })

def main():
    """Main dashboard application."""
    st.title("📚 Learner Engagement Platform")
    st.markdown("Monitor learner risk levels and generate personalized interventions")
    
    # Sidebar for configuration and filters
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Base URL display
        st.info(f"**Backend API:** {API_BASE}")
        
        # Risk filter
        st.header("🔍 Filters")
        risk_filter = st.selectbox(
            "Filter by Risk Level:",
            ["all", "low", "medium", "high"],
            index=0
        )
        
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # Setup instructions
        st.header("🚀 Setup Instructions")
        st.markdown("""
        **Backend Setup:**
        1. Navigate to backend directory
        2. Install dependencies: `pip install -r requirements.txt`
        3. Run server: `uvicorn app:app --reload`
        4. Seed data: `python scripts/seed.py`
        
        **Dashboard Setup:**
        1. Install Streamlit: `pip install streamlit`
        2. Run dashboard: `streamlit run dashboard/app.py`
        
        **Environment Variables:**
        - `API_BASE`: Backend URL (default: http://localhost:8000)
        """)
    
    # Main content area
    st.header("👥 Learner Overview")
    
    # Fetch and display learners
    learners = fetch_learners(risk_filter)
    
    if learners:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_learners = len(learners)
        high_risk = len([l for l in learners if l["risk_label"] == "high"])
        medium_risk = len([l for l in learners if l["risk_label"] == "medium"])
        low_risk = len([l for l in learners if l["risk_label"] == "low"])
        
        col1.metric("Total Learners", total_learners)
        col2.metric("High Risk", high_risk, delta=f"{high_risk/total_learners*100:.1f}%")
        col3.metric("Medium Risk", medium_risk, delta=f"{medium_risk/total_learners*100:.1f}%")
        col4.metric("Low Risk", low_risk, delta=f"{low_risk/total_learners*100:.1f}%")
        
        # Display learner table and actions
        display_learner_table(learners)
    
    else:
        st.warning("No learner data available. Check backend connectivity.")

if __name__ == "__main__":
    main()


# In your_project.py
import clone_ui

def process_multiple_sites():
    sites = ["https://site1.com", "https://site2.com"]
    for i, site_url in enumerate(sites):
        print(f"Cloning site: {site_url}")
        # Give each clone a unique directory
        output_directory = f"clone_output_{i}"
        clone_ui.run_clone(site_url, output_directory)
        # You can now add logic to process the files in output_directory

process_multiple_sites()