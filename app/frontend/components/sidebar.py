import streamlit as st
from app.frontend.utils.api_client import api_client
from app.shared.config import Config

def display_sidebar():
    """Display sidebar with navigation and controls"""
    
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(139, 69, 255, 0.2); margin-bottom: 20px;">
            <div style="font-size: 2rem; margin-bottom: 8px;">🛡️⚡</div>
            <h2 style="color: #8B45FF; margin: 0; font-size: 1.5rem;">CyberPulse</h2>
            <p style="color: #9CA3AF; margin: 4px 0 0 0; font-size: 0.875rem;">Funding Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        display_navigation_menu()
        
        # API status
        display_api_status()
        
        # Quick stats
        display_quick_stats()
        
        # Settings
        display_settings()
        
        # Footer
        display_footer()

def display_navigation_menu():
    """Display navigation menu"""
    
    st.markdown("### 📋 Navigation")
    
    # Main sections
    if st.button("🏠 Dashboard", use_container_width=True):
        st.session_state.current_page = "dashboard"
    
    if st.button("📊 Analytics", use_container_width=True):
        st.session_state.current_page = "analytics"
    
    if st.button("🔍 Search", use_container_width=True):
        st.session_state.current_page = "search"
    
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.current_page = "settings"
    
    st.markdown("---")

def display_api_status():
    """Display API connection status"""
    
    st.markdown("### 🔌 System Status")
    
    # Check API health
    try:
        is_healthy = api_client.health_check()
        if is_healthy:
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Disconnected")
            
    except Exception as e:
        st.error("🔴 Connection Error")
        st.caption(f"Error: {str(e)[:50]}...")
    
    # Display API endpoint
    st.caption(f"Endpoint: {Config.API_BASE_URL}")
    
    st.markdown("---")

def display_quick_stats():
    """Display quick statistics"""
    
    st.markdown("### 📈 Quick Stats")
    
    try:
        stats = api_client.get_stats()
        
        # Total companies
        st.metric(
            "Total Companies",
            f"{stats.get('total_companies', 0):,}",
            help="Total number of companies in database"
        )
        
        # Total funding
        total_funding = stats.get('total_funding', 0)
        if total_funding >= 1000000000:
            funding_display = f"${total_funding / 1000000000:.1f}B"
        elif total_funding >= 1000000:
            funding_display = f"${total_funding / 1000000:.1f}M"
        else:
            funding_display = f"${total_funding:,.0f}"
        
        st.metric(
            "Total Funding",
            funding_display,
            help="Total funding amount (disclosed only)"
        )
        
        # Funding by type
        funding_by_type = stats.get('funding_by_type', [])
        if funding_by_type:
            st.markdown("**By Company Type:**")
            for type_stat in funding_by_type[:3]:  # Show top 3
                type_name = type_stat.get('_id', 'Unknown')
                count = type_stat.get('count', 0)
                st.caption(f"• {type_name}: {count}")
        
    except Exception as e:
        st.error("Failed to load stats")
        st.caption(f"Error: {str(e)[:50]}...")
    
    st.markdown("---")

def display_settings():
    """Display settings and preferences"""
    
    st.markdown("### ⚙️ Preferences")
    
    # Items per page
    items_per_page = st.selectbox(
        "Items per page",
        [6, 12, 24, 48],
        index=1,  # Default to 12
        help="Number of companies to display per page"
    )
    st.session_state.items_per_page = items_per_page
    
    # Default sort
    default_sort = st.selectbox(
        "Default sort",
        ["date", "company_name", "amount"],
        format_func=lambda x: {
            "date": "📅 Date",
            "company_name": "🏢 Company Name",
            "amount": "💰 Funding Amount"
        }[x],
        help="Default sorting option"
    )
    st.session_state.default_sort = default_sort
    
    # Auto-refresh
    auto_refresh = st.checkbox(
        "Auto-refresh",
        value=False,
        help="Automatically refresh data every 5 minutes"
    )
    st.session_state.auto_refresh = auto_refresh
    
    # Dark mode toggle (placeholder - Streamlit handles this)
    st.markdown("**🌙 Theme**")
    st.caption("Use Streamlit's theme settings")
    
    st.markdown("---")

def display_data_management():
    """Display data management options"""
    
    st.markdown("### 🔄 Data Management")
    
    # Manual refresh
    if st.button("🔄 Refresh Data", use_container_width=True):
        try:
            result = api_client.trigger_data_collection()
            st.success("✅ Data refresh initiated")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Refresh failed: {str(e)}")
    
    # Last update info
    st.caption("💡 Data is automatically updated every 4 hours")
    
    # Export options
    st.markdown("**📥 Export Options**")
    if st.button("Download CSV", use_container_width=True):
        st.info("🔄 Export feature coming soon...")
    
    st.markdown("---")

def display_footer():
    """Display footer information"""
    
    st.markdown("### ℹ️ About")
    
    st.markdown("""
    **CyberPulse** tracks cybersecurity funding data from various sources to provide real-time market intelligence.
    
    **Data Sources:**
    • Return on Security
    • Public funding announcements
    • Venture capital databases
    
    **Features:**
    • Real-time data collection
    • Advanced search & filtering
    • Multiple view modes
    • Export capabilities
    """)
    
    st.markdown("---")
    
    # Version and links
    st.markdown("""
    <div style="text-align: center; color: #6B7280; font-size: 0.75rem;">
        <p>Version 1.0.0</p>
        <p>Built with Streamlit & Flask</p>
        <p>© 2024 CyberPulse</p>
    </div>
    """, unsafe_allow_html=True)

def get_sidebar_state():
    """Get current sidebar state and preferences"""
    
    return {
        'items_per_page': st.session_state.get('items_per_page', 12),
        'default_sort': st.session_state.get('default_sort', 'date'),
        'auto_refresh': st.session_state.get('auto_refresh', False),
        'current_page': st.session_state.get('current_page', 'dashboard')
    }