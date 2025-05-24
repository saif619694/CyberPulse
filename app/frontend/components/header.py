import streamlit as st
from app.frontend.utils.api_client import api_client
import time

def display_header():
    """Display the main header optimized for the new design"""
    
    # Simplified header for integration into main page
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%);
        border: 1px solid #333333;
        border-radius: 16px;
        padding: 40px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    ">
        <div style="display: flex; align-items: center; justify-content: center; gap: 16px; margin-bottom: 24px;">
            <div style="font-size: 3rem;">🛡️</div>
            <h1 style="
                font-size: 3.5rem;
                font-weight: 900;
                background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 0;
                text-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
            ">CYBERPULSE</h1>
        </div>
        <p style="
            font-size: 1.2rem;
            color: #cccccc;
            margin: 0;
            font-weight: 400;
        ">Real-time cybersecurity funding intelligence and market analytics</p>
    </div>
    """, unsafe_allow_html=True)

def display_stats_and_controls():
    """Display stats dashboard and data refresh controls"""
    
    # Get stats for display
    try:
        stats = api_client.get_stats()
        total_companies = stats.get('total_companies', 0)
        total_funding = stats.get('total_funding', 0)
        
        # Format funding amount
        if total_funding >= 1000000000:
            funding_display = f"${total_funding / 1000000000:.1f}B"
        elif total_funding >= 1000000:
            funding_display = f"${total_funding / 1000000:.1f}M"
        else:
            funding_display = f"${total_funding:,.0f}"
        
        # Check API status
        api_status = "🟢 Online" if api_client.health_check() else "🔴 Offline"
        
    except Exception:
        total_companies = "---"
        funding_display = "---"
        api_status = "🔴 Error"
    
    # Stats and controls layout
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%);
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        ">
            <div style="
                font-size: 2rem;
                font-weight: bold;
                color: #00ff88;
                margin-bottom: 8px;
            ">{total_companies:,}</div>
            <div style="
                font-size: 0.9rem;
                color: #888888;
                text-transform: uppercase;
                letter-spacing: 1px;
            ">Companies</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%);
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        ">
            <div style="
                font-size: 2rem;
                font-weight: bold;
                color: #00ff88;
                margin-bottom: 8px;
            ">{funding_display}</div>
            <div style="
                font-size: 0.9rem;
                color: #888888;
                text-transform: uppercase;
                letter-spacing: 1px;
            ">Total Funding</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%);
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        ">
            <div style="
                font-size: 2rem;
                font-weight: bold;
                color: #00ff88;
                margin-bottom: 8px;
            ">Live</div>
            <div style="
                font-size: 0.9rem;
                color: #888888;
                text-transform: uppercase;
                letter-spacing: 1px;
            ">Data Feed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%);
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        ">
            <div style="
                font-size: 1.2rem;
                font-weight: bold;
                color: #00ff88;
                margin-bottom: 8px;
            ">{api_status}</div>
            <div style="
                font-size: 0.9rem;
                color: #888888;
                text-transform: uppercase;
                letter-spacing: 1px;
            ">API Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        if st.button("🔄 Refresh Data", 
                    use_container_width=True, 
                    help="Collect latest funding data",
                    type="primary"):
            
            with st.spinner("🔄 Collecting fresh intelligence..."):
                try:
                    result = api_client.trigger_data_collection()
                    st.success("✅ Data refresh completed!")
                    
                    if 'details' in result:
                        details = result['details']
                        st.info(f"📊 Processed: {details.get('processed', 0)} | "
                               f"Skipped: {details.get('skipped', 0)} | "
                               f"Errors: {details.get('errors', 0)}")
                    
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Refresh failed: {str(e)}")

def display_professional_header_with_stats():
    """Combined header and stats display for the main page"""
    
    # Main header
    display_header()
    
    # Stats and controls
    display_stats_and_controls()

def display_api_status():
    """Display minimal API status for debugging"""
    try:
        is_healthy = api_client.health_check()
        status_text = "🟢 Connected" if is_healthy else "🔴 Disconnected"
        status_color = "#00ff88" if is_healthy else "#ff4444"
        
        st.markdown(f"""
        <div style="
            background: #111111;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            margin: 8px 0;
        ">
            <div style="color: {status_color}; font-weight: 600;">
                API Status: {status_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown(f"""
        <div style="
            background: #111111;
            border: 1px solid #ff4444;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            margin: 8px 0;
        ">
            <div style="color: #ff4444; font-weight: 600;">
                API Error: Connection Failed
            </div>
            <div style="color: #888888; font-size: 0.8rem; margin-top: 4px;">
                {str(e)[:50]}...
            </div>
        </div>
        """, unsafe_allow_html=True)