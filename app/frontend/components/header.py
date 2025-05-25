import streamlit as st
from app.frontend.utils.api_client import api_client

def display_header():
    """Legacy header function - functionality moved to main app"""
    pass

def display_stats_and_controls():
    """Legacy stats function - functionality moved to main app"""
    pass

def display_professional_header_with_stats():
    """Legacy combined header - functionality moved to main app"""
    pass

def display_api_status():
    """Display minimal API status for debugging"""
    try:
        is_healthy = api_client.health_check()
        if not is_healthy:
            st.warning("⚠️ API connection issue detected")
    except Exception:
        st.error("❌ Cannot connect to backend API")