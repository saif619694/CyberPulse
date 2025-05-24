import streamlit as st
from app.frontend.utils.api_client import api_client
import time

def display_header():
    """Display the main header with logo and data collection functionality"""
    
    # Custom CSS for the header
    st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(145deg, rgba(15, 15, 15, 0.95) 0%, rgba(30, 30, 30, 0.9) 100%);
        padding: 40px 20px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
        border: 1px solid rgba(139, 69, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .logo-icon {
        font-size: 3rem;
        background: linear-gradient(135deg, #8B45FF 0%, #FF6B35 50%, #F093FB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .logo-text {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #8B45FF 0%, #FF6B35 50%, #F093FB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(139, 69, 255, 0.5);
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 900;
        margin-bottom: 16px;
        background: linear-gradient(135deg, #8B45FF 0%, #FF6B35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 50px rgba(139, 69, 255, 0.3);
        line-height: 1.1;
    }
    
    .subtitle {
        font-size: 1.5rem;
        color: #D1D5DB;
        margin-bottom: 32px;
        line-height: 1.6;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 24px;
        margin-bottom: 32px;
        flex-wrap: wrap;
    }
    
    .stat-box {
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(139, 69, 255, 0.3);
        border-radius: 12px;
        padding: 20px;
        min-width: 150px;
        backdrop-filter: blur(10px);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #10B981;
        margin-bottom: 4px;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #9CA3AF;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header HTML
    header_html = """
    <div class="header-container">
        <div class="logo-container">
            <div class="logo-icon">🛡️⚡🔒</div>
            <div class="logo-text">CyberPulse</div>
        </div>
        
        <h1 class="main-title">FUNDING<br>INTELLIGENCE</h1>
        
        <p class="subtitle">
            Real-time analytics on cybersecurity investments, funding rounds, and market trends. 
            Track the pulse of cyber innovation with comprehensive data insights.
        </p>
        
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-value">$2.1B+</div>
                <div class="stat-label">Total Funding</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">500+</div>
                <div class="stat-label">Companies</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">Live</div>
                <div class="stat-label">Data Feed</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Data collection section
    st.markdown("### 🔄 Data Management")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔍 Collect Latest Intelligence", 
                    type="primary", 
                    use_container_width=True,
                    help="Trigger fresh data collection from security funding sources"):
            
            with st.spinner("🔄 Collecting fresh data from security funding sources..."):
                try:
                    result = api_client.trigger_data_collection()
                    
                    st.success("✅ Data collection completed successfully!")
                    
                    # Display collection details
                    if 'details' in result:
                        details = result['details']
                        st.info(f"📊 Processed: {details.get('processed', 0)} | "
                               f"Skipped: {details.get('skipped', 0)} | "
                               f"Errors: {details.get('errors', 0)}")
                    
                    # Auto-refresh after successful collection
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Data collection failed: {str(e)}")

def display_api_status():
    """Display API connection status"""
    with st.sidebar:
        st.markdown("### 🔌 API Status")
        
        if api_client.health_check():
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Disconnected")
            st.warning("Please ensure the backend service is running.")