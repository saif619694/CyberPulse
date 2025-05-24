import streamlit as st
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import components
from app.frontend.components.header import display_header
from app.frontend.components.search_bar import display_search_filters, display_sort_controls
from app.frontend.components.data_display import (
    display_funding_data, 
    display_pagination_info,
    display_no_data_message
)
from app.frontend.utils.api_client import api_client
from app.frontend.utils.formatters import display_loading_animation
from app.shared.config import Config

# Page configuration with better icon
st.set_page_config(
    page_title="CyberPulse - Funding Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/cyberpulse',
        'Report a bug': 'https://github.com/cyberpulse/issues',
        'About': "CyberPulse - Real-time cybersecurity funding intelligence"
    }
)

# Load custom CSS with deep black professional theme
def load_custom_css():
    """Load custom CSS styling with deep black professional theme"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global Styles */
    .main .block-container {
        max-width: 1400px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Deep Black Professional Background */
    .stApp {
        background: #000000;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Main content area */
    .main {
        background: #000000;
    }
    
    /* Professional Header Styling */
    .professional-header {
        background: linear-gradient(135deg, #111111 0%, #1a1a1a 100%);
        border: 1px solid #333333;
        border-radius: 16px;
        padding: 40px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }
    
    .logo-container {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
        border-radius: 50%;
        margin-bottom: 20px;
        position: relative;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.4);
    }
    
    .logo-icon {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #000000 0%, #333333 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    }
    
    .header-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 16px;
        text-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: #cccccc;
        margin-bottom: 24px;
        font-weight: 400;
    }
    
    /* Control Panel Styling */
    .control-panel {
        background: linear-gradient(145deg, #111111 0%, #1a1a1a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    /* Stats Cards */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 24px 0;
    }
    
    .stat-card {
        background: linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: #00ff88;
        box-shadow: 0 4px 20px rgba(0, 255, 136, 0.2);
        transform: translateY(-2px);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #00ff88;
        margin-bottom: 8px;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #888888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
        color: #000000;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 255, 136, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 255, 136, 0.4);
        background: linear-gradient(135deg, #00ccff 0%, #00ff88 100%);
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        background: #0a0a0a;
        border: 2px solid #333333;
        border-radius: 8px;
        color: #ffffff;
        font-size: 16px;
        padding: 12px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ff88;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
    }
    
    .stSelectbox > div > div > select {
        background: #0a0a0a;
        border: 2px solid #333333;
        border-radius: 8px;
        color: #ffffff;
        font-size: 16px;
        padding: 12px;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #00ff88;
        box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
    }
    
    /* Card Container */
    .funding-card {
        background: linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%);
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    .funding-card:hover {
        border-color: #00ff88;
        box-shadow: 0 8px 32px rgba(0, 255, 136, 0.1);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #111111;
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 6px;
        color: #cccccc;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #333333;
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
        color: #000000;
        border-color: #00ff88;
    }
    
    /* DataFrame styling */
    .stDataFrame {
        background: #0a0a0a;
        border-radius: 8px;
        border: 1px solid #333333;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(145deg, #003d1f 0%, #004d28 100%);
        border: 1px solid #00ff88;
        color: #00ff88;
    }
    
    .stError {
        background: linear-gradient(145deg, #4d0000 0%, #660000 100%);
        border: 1px solid #ff4444;
        color: #ff8888;
    }
    
    .stWarning {
        background: linear-gradient(145deg, #4d3300 0%, #664400 100%);
        border: 1px solid #ffaa00;
        color: #ffcc88;
    }
    
    /* Pagination */
    .pagination-info {
        background: #111111;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        margin: 16px 0;
        color: #cccccc;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #111111;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555555;
    }
    
    /* Animation keyframes */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(0, 255, 136, 0.3); }
        50% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.5); }
        100% { box-shadow: 0 0 5px rgba(0, 255, 136, 0.3); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    .glow {
        animation: glow 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'current_page': 1,
        'search_term': '',
        'filter_round': '',
        'sort_field': 'date',
        'sort_direction': 'desc',
        'view_mode': 'cards',
        'items_per_page': 12,
        'available_rounds': [],
        'last_refresh': time.time(),
        'api_stats': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def display_professional_header():
    """Display professional header with enhanced logo"""
    
    # Header section with improved logo
    st.markdown("""
    <div class="professional-header">
        <div class="logo-container">
            <div class="logo-icon">🛡️</div>
        </div>
        <h1 class="header-title">CYBERPULSE</h1>
        <p class="header-subtitle">Real-time cybersecurity funding intelligence and market analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats and controls
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("🔄 Refresh Data", key="header_refresh", use_container_width=True, help="Collect latest funding data"):
            with st.spinner("🔄 Collecting fresh intelligence..."):
                try:
                    result = api_client.trigger_data_collection()
                    st.success("✅ Data refresh completed!")
                    if 'details' in result:
                        details = result['details']
                        st.info(f"📊 Processed: {details.get('processed', 0)} | "
                               f"Skipped: {details.get('skipped', 0)}")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Refresh failed: {str(e)}")

def display_stats_dashboard():
    """Display stats dashboard integrated into main page"""
    try:
        stats = api_client.get_stats()
        st.session_state.api_stats = stats
        
        total_companies = stats.get('total_companies', 0)
        total_funding = stats.get('total_funding', 0)
        
        # Format funding amount
        if total_funding >= 1000000000:
            funding_display = f"${total_funding / 1000000000:.1f}B"
        elif total_funding >= 1000000:
            funding_display = f"${total_funding / 1000000:.1f}M"
        else:
            funding_display = f"${total_funding:,.0f}"
        
        # Stats grid
        stats_html = f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_companies:,}</div>
                <div class="stat-label">Total Companies</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{funding_display}</div>
                <div class="stat-label">Total Funding</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">Live</div>
                <div class="stat-label">Data Feed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{'🟢' if api_client.health_check() else '🔴'}</div>
                <div class="stat-label">API Status</div>
            </div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Failed to load stats: {str(e)}")
        st.markdown("""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">---</div>
                <div class="stat-label">Loading Stats...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_control_panel():
    """Display integrated control panel"""
    
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    
    # Row 1: Search and Filter
    st.markdown("#### 🔍 Search & Filter")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input(
            "",
            value=st.session_state.search_term,
            placeholder="Search companies, descriptions, technologies...",
            help="Search across company names, descriptions, and company types",
            label_visibility="collapsed",
            key="main_search"
        )
    
    with col2:
        # Load available rounds if not loaded
        if not st.session_state.available_rounds:
            try:
                rounds = api_client.get_funding_rounds()
                st.session_state.available_rounds = rounds
            except:
                st.session_state.available_rounds = []
        
        round_options = ["All Rounds"] + sorted(st.session_state.available_rounds)
        current_round_display = st.session_state.filter_round if st.session_state.filter_round else "All Rounds"
        
        selected_round = st.selectbox(
            "",
            round_options,
            index=round_options.index(current_round_display) if current_round_display in round_options else 0,
            help="Filter by funding round type",
            label_visibility="collapsed",
            key="main_filter"
        )
        
        # Convert back to API format
        filter_round = "" if selected_round == "All Rounds" else selected_round
    
    # Row 2: Sort and View Controls
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sort_field = st.selectbox(
            "Sort by",
            ["date", "company_name", "amount"],
            index=["date", "company_name", "amount"].index(st.session_state.sort_field),
            format_func=lambda x: {
                "date": "📅 Date",
                "company_name": "🏢 Company Name", 
                "amount": "💰 Funding Amount"
            }[x],
            key="main_sort_field"
        )
    
    with col2:
        sort_direction = st.selectbox(
            "Order",
            ["desc", "asc"],
            index=0 if st.session_state.sort_direction == "desc" else 1,
            format_func=lambda x: "📉 Newest First" if x == "desc" else "📈 Oldest First",
            key="main_sort_direction"
        )
    
    with col3:
        items_per_page = st.selectbox(
            "Items per page",
            [6, 12, 24, 48],
            index=[6, 12, 24, 48].index(st.session_state.items_per_page),
            help="Number of companies to display per page",
            key="main_items_per_page"
        )
        st.session_state.items_per_page = items_per_page
    
    with col4:
        view_mode = st.selectbox(
            "View mode",
            ["cards", "table", "chart"],
            index=["cards", "table", "chart"].index(st.session_state.view_mode),
            format_func=lambda x: {
                "cards": "📋 Cards",
                "table": "📊 Table",
                "chart": "📈 Charts"
            }[x],
            key="main_view_mode"
        )
        st.session_state.view_mode = view_mode
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check if parameters changed
    params_changed = (
        search_term != st.session_state.search_term or
        filter_round != st.session_state.filter_round or
        sort_field != st.session_state.sort_field or
        sort_direction != st.session_state.sort_direction
    )
    
    if params_changed:
        st.session_state.search_term = search_term
        st.session_state.filter_round = filter_round
        st.session_state.sort_field = sort_field
        st.session_state.sort_direction = sort_direction
        st.session_state.current_page = 1  # Reset to first page
        st.rerun()

def fetch_funding_data():
    """Fetch funding data from API"""
    try:
        response = api_client.get_funding_data(
            page=st.session_state.current_page,
            items_per_page=st.session_state.items_per_page,
            sort_field=st.session_state.sort_field,
            sort_direction=st.session_state.sort_direction,
            search=st.session_state.search_term or None,
            filter_round=st.session_state.filter_round or None
        )
        return response
    except Exception as e:
        logger.error(f"Failed to fetch funding data: {str(e)}")
        st.error(f"Failed to fetch data: {str(e)}")
        return None

def display_pagination_controls(current_page, total_pages, location="top"):
    """Display pagination controls with unique keys based on location"""
    if total_pages <= 1:
        return
    
    # Use location to make keys unique
    key_prefix = f"pagination_{location}"
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️ First", disabled=(current_page <= 1), key=f"{key_prefix}_first"):
            st.session_state.current_page = 1
            st.rerun()
    
    with col2:
        if st.button("◀️ Previous", disabled=(current_page <= 1), key=f"{key_prefix}_prev"):
            st.session_state.current_page = current_page - 1
            st.rerun()
    
    with col3:
        # Page info
        st.markdown(f"""
        <div class="pagination-info">
            Page <strong>{current_page}</strong> of <strong>{total_pages}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.button("▶️ Next", disabled=(current_page >= total_pages), key=f"{key_prefix}_next"):
            st.session_state.current_page = current_page + 1
            st.rerun()
    
    with col5:
        if st.button("⏭️ Last", disabled=(current_page >= total_pages), key=f"{key_prefix}_last"):
            st.session_state.current_page = total_pages
            st.rerun()

def main():
    """Main application function"""
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Professional header with integrated features
    display_professional_header()
    
    # Stats dashboard
    display_stats_dashboard()
    
    # Control panel
    display_control_panel()
    
    # Main content
    st.markdown("---")
    
    # Fetch and display data
    with st.spinner("Loading funding intelligence..."):
        data_response = fetch_funding_data()
    
    if data_response:
        companies = data_response.get('data', [])
        total_count = data_response.get('totalCount', 0)
        total_pages = data_response.get('totalPages', 1)
        current_page = data_response.get('currentPage', 1)
        items_per_page = data_response.get('itemsPerPage', 12)
        
        # Results info
        if companies:
            start_item = (current_page - 1) * items_per_page + 1
            end_item = min(current_page * items_per_page, total_count)
            
            st.markdown(f"""
            <div class="pagination-info">
                Showing <strong>{start_item}</strong> to <strong>{end_item}</strong> of <strong>{total_count:,}</strong> results
            </div>
            """, unsafe_allow_html=True)
        
        # Top pagination controls
        display_pagination_controls(current_page, total_pages, location="top")
        
        # Display data
        st.markdown("---")
        display_funding_data(companies, st.session_state.view_mode)
        
        # Bottom pagination for long lists
        if total_pages > 1 and len(companies) > 6:
            st.markdown("---")
            display_pagination_controls(current_page, total_pages, location="bottom")
    else:
        display_no_data_message()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666666; padding: 20px 0; border-top: 1px solid #333333;">
        <p style="margin: 0;"><strong>CyberPulse</strong> - Real-time cybersecurity funding intelligence</p>
        <p style="margin: 8px 0 0 0; font-size: 0.9rem;">Built with modern technology for security professionals</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()