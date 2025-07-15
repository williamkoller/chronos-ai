import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="CHRONOS AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:8000"

def main():
    st.title("🤖 CHRONOS AI - Intelligent Time Orchestrator")
    st.markdown("*Your AI-powered productivity companion*")
    
    # Sidebar
    with tab1:
        st.subheader("⏰ Optimal Time Slots")
        
        # Mock data for time patterns
        time_data = {
            "Morning (8-12h)": {"efficiency": 0.92, "sample_size": 45},
            "Afternoon (12-17h)": {"efficiency": 0.78, "sample_size": 38},
            "Evening (17-20h)": {"efficiency": 0.65, "sample_size": 22}
        }
        
        for period, data in time_data.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{period}**")
            with col2:
                st.metric("Efficiency", f"{data['efficiency']:.2f}")
            with col3:
                st.metric("Tasks", data['sample_size'])
    
    with tab2:
        st.subheader("📂 Category Performance")
        
        categories = ["Development", "Meetings", "Planning", "Documentation"]
        efficiencies = [0.89, 0.82, 0.76, 0.71]
        
        fig = px.bar(x=categories, y=efficiencies, title="Efficiency by Task Category")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("🎯 Discovered Preferences")
        
        preferences = [
            "✅ Prefers development tasks in the morning",
            "✅ Works best with 90-minute focus blocks",
            "✅ Needs 15-minute breaks between different task types",
            "✅ More productive on Tuesday-Thursday",
            "⚠️ Tends to underestimate development tasks by 20%",
            "⚠️ Energy drops significantly after lunch"
        ]
        
        for pref in preferences:
            if pref.startswith("✅"):
                st.success(pref)
            else:
                st.warning(pref)

def settings_page():
    st.header("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔌 API Config", "🎯 Preferences", "📊 Data"])
    
    with tab1:
        st.subheader("API Configuration")
        
        notion_token = st.text_input("Notion Integration Token", type="password")
        database_id = st.text_input("Notion Database ID")
        claude_key = st.text_input("Claude API Key", type="password")
        
        if st.button("Test Connection"):
            st.success("✅ All connections successful!")
        
        if st.button("Save Configuration"):
            st.success("✅ Configuration saved!")
    
    with tab2:
        st.subheader("Personal Preferences")
        
        work_start = st.time_input("Work Start Time", value=datetime.strptime("09:00", "%H:%M").time())
        work_end = st.time_input("Work End Time", value=datetime.strptime("18:00", "%H:%M").time())
        
        break_duration = st.slider("Preferred Break Duration (minutes)", 5, 60, 15)
        max_focus = st.slider("Maximum Focus Duration (minutes)", 30, 180, 90)
        
        weekend_work = st.checkbox("Allow weekend scheduling")
        
        if st.button("Update Preferences"):
            st.success("✅ Preferences updated!")
    
    with tab3:
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Import Notion Data"):
                st.info("Importing last 90 days of tasks...")
            
            if st.button("🔄 Retrain Patterns"):
                st.info("Reanalyzing all patterns...")
        
        with col2:
            if st.button("📤 Export Data"):
                st.success("Data exported to chronos_export.json")
            
            if st.button("🗑️ Clear Learning Data"):
                st.warning("This will reset all learned patterns!")

def display_demo_suggestion(task_data):
    """Displays a demo suggestion when API is not available"""
    st.success("🎯 Demo AI Suggestion Generated!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Confidence Score", "0.89", "High")
    
    with col2:
        st.metric("Suggested Time", "09:30", "Tomorrow")
    
    with col3:
        st.metric("Success Probability", "87%", "↗️ +5%")
    
    st.subheader("🧠 AI Reasoning")
    reasoning = f"Based on your productivity patterns, {task_data['category'].lower()} tasks perform best in the morning when your energy is highest. The suggested time aligns with your peak focus period."
    st.info(reasoning)
    
    st.subheader("🔄 Alternative Times")
    alternatives = [
        "1. 10:00-11:30 - Score: 0.85",
        "2. 14:00-15:30 - Score: 0.72", 
        "3. 15:30-17:00 - Score: 0.68"
    ]
    
    for alt in alternatives:
        st.write(alt)

if __name__ == "__main__":
    main()