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
from app.frontend.components.sidebar import display_sidebar, get_sidebar_state
from app.frontend.utils.api_client import api_client
from app.frontend.utils.formatters import display_loading_animation
from app.shared.config import Config

# Page configuration
st.set_page_config(
    page_title="CyberPulse - Funding Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/cyberpulse',
        'Report a bug': 'https://github.com/cyberpulse/issues',
        'About': "CyberPulse - Real-time cybersecurity funding intelligence"
    }
)

# Load custom CSS
def load_custom_css():
    """Load custom CSS styling"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Global Styles */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom background */
    .stApp {
        background: radial-gradient(ellipse at top, rgba(139, 69, 255, 0.1) 0%, rgba(0, 0, 0, 1) 50%);
        color: white;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(15, 15, 15, 0.95) 0%, rgba(30, 30, 30, 0.9) 100%);
        border-right: 1px solid rgba(139, 69, 255, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #8B45FF 0%, #FF6B35 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(139, 69, 255, 0.3);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(139, 69, 255, 0.3);
        border-radius: 8px;
        color: white;
    }
    
    .stSelectbox > div > div > select {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(139, 69, 255, 0.3);
        border-radius: 8px;
        color: white;
    }
    
    /* Metric styling */
    .metric-container {
        background: linear-gradient(145deg, rgba(15, 15, 15, 0.9) 0%, rgba(30, 30, 30, 0.8) 100%);
        border: 1px solid rgba(139, 69, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(139, 69, 255, 0.3);
        border-radius: 8px;
        color: white;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #8B45FF 0%, #FF6B35 100%);
    }
    
    /* Custom animations */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Error and success message styling */
    .stAlert {
        border-radius: 8px;
        border: 1px solid rgba(139, 69, 255, 0.3);
    }
    
    /* DataFrame styling */
    .stDataFrame {
        background: rgba(0, 0, 0, 0.6);
        border-radius: 8px;
        border: 1px solid rgba(139, 69, 255, 0.2);
    }
    
    /* Plotly chart container */
    .js-plotly-plot {
        border-radius: 8px;
        border: 1px solid rgba(139, 69, 255, 0.2);
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
        'last_refresh': time.time()
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_available_rounds():
    """Load available funding rounds"""
    try:
        rounds = api_client.get_funding_rounds()
        st.session_state.available_rounds = rounds
        return rounds
    except Exception as e:
        logger.error(f"Failed to load funding rounds: {str(e)}")
        st.error("Failed to load funding rounds")
        return []

def fetch_funding_data():
    """Fetch funding data from API"""
    try:
        sidebar_state = get_sidebar_state()
        
        # Use sidebar preferences
        items_per_page = sidebar_state.get('items_per_page', st.session_state.items_per_page)
        
        response = api_client.get_funding_data(
            page=st.session_state.current_page,
            items_per_page=items_per_page,
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

def handle_search_change():
    """Handle search parameter changes"""
    st.session_state.current_page = 1  # Reset to first page when search changes

def display_main_content():
    """Display main application content"""
    
    # Header
    display_header()
    
    # Load available rounds if not loaded
    if not st.session_state.available_rounds:
        load_available_rounds()
    
    # Search and filter controls
    st.markdown("## 🔍 Search & Filter")
    
    # Get current values from session state
    current_search = st.session_state.search_term
    current_round = st.session_state.filter_round
    
    # Display search controls
    search_term, filter_round = display_search_filters(
        st.session_state.available_rounds,
        0  # Will be updated after data fetch
    )
    
    # Check if search parameters changed
    if search_term != current_search or filter_round != current_round:
        st.session_state.search_term = search_term
        st.session_state.filter_round = filter_round
        handle_search_change()
        st.rerun()
    
    # Sort controls
    st.markdown("---")
    sort_field, sort_direction = display_sort_controls()
    
    # Check if sort parameters changed
    if (sort_field != st.session_state.sort_field or 
        sort_direction != st.session_state.sort_direction):
        st.session_state.sort_field = sort_field
        st.session_state.sort_direction = sort_direction
        handle_search_change()
        st.rerun()
    
    st.markdown("---")
    
    # Fetch and display data
    with st.spinner("Loading funding data..."):
        data_response = fetch_funding_data()
    
    if data_response:
        companies = data_response.get('data', [])
        total_count = data_response.get('totalCount', 0)
        total_pages = data_response.get('totalPages', 1)
        current_page = data_response.get('currentPage', 1)
        items_per_page = data_response.get('itemsPerPage', 12)
        
        # Update search results counter
        if companies:
            st.success(f"✅ Found {total_count:,} companies")
        
        # Display pagination info
        if total_pages > 1:
            display_pagination_info(current_page, total_pages, items_per_page, total_count)
        
        # Pagination controls
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            
            with col1:
                if st.button("⏮️ First", disabled=(current_page <= 1)):
                    st.session_state.current_page = 1
                    st.rerun()
            
            with col2:
                if st.button("◀️ Previous", disabled=(current_page <= 1)):
                    st.session_state.current_page = current_page - 1
                    st.rerun()
            
            with col3:
                # Page selector
                page_options = list(range(1, min(total_pages + 1, 11)))  # Show max 10 pages
                if current_page not in page_options and current_page <= total_pages:
                    page_options.append(current_page)
                    page_options.sort()
                
                selected_page = st.selectbox(
                    f"Page {current_page} of {total_pages}",
                    page_options,
                    index=page_options.index(current_page) if current_page in page_options else 0,
                    label_visibility="collapsed"
                )
                
                if selected_page != current_page:
                    st.session_state.current_page = selected_page
                    st.rerun()
            
            with col4:
                if st.button("▶️ Next", disabled=(current_page >= total_pages)):
                    st.session_state.current_page = current_page + 1
                    st.rerun()
            
            with col5:
                if st.button("⏭️ Last", disabled=(current_page >= total_pages)):
                    st.session_state.current_page = total_pages
                    st.rerun()
        
        # Display data
        st.markdown("---")
        display_funding_data(companies, st.session_state.view_mode)
        
        # Bottom pagination for long lists
        if total_pages > 1 and len(companies) > 6:
            st.markdown("---")
            display_pagination_info(current_page, total_pages, items_per_page, total_count)
    
    else:
        display_no_data_message()

def auto_refresh_handler():
    """Handle auto-refresh functionality"""
    sidebar_state = get_sidebar_state()
    
    if sidebar_state.get('auto_refresh', False):
        # Check if 5 minutes have passed since last refresh
        current_time = time.time()
        last_refresh = st.session_state.get('last_refresh', 0)
        
        if current_time - last_refresh > 300:  # 5 minutes
            st.session_state.last_refresh = current_time
            st.rerun()

def main():
    """Main application function"""
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Auto-refresh handler
    auto_refresh_handler()
    
    # Main content
    try:
        display_main_content()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error("An unexpected error occurred. Please refresh the page.")
        
        # Debug information in expander
        with st.expander("🐛 Debug Information"):
            st.code(str(e))
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6B7280; padding: 20px 0;">
        <p>🛡️ <strong>CyberPulse</strong> - Real-time cybersecurity funding intelligence</p>
        <p style="font-size: 0.875rem;">Built with ❤️ using Streamlit & Flask</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()