import streamlit as st
import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import components
from app.frontend.components.data_display import display_funding_cards
from app.frontend.utils.api_client import api_client
from app.shared.config import Config

# Page configuration
st.set_page_config(
    page_title="CyberPulse - Funding Intelligence",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional dark theme
def load_professional_css():
    """Load professional dark theme CSS"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    /* Reset and base styles */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main container */
    .main .block-container {
        max-width: 1400px;
        padding: 2rem 1rem;
    }
    
    /* Logo and title section */
    .header-section {
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .logo-wrapper {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .logo-icon {
        font-size: 1.5rem;
        color: #8b5cf6;
    }
    
    .logo-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: #8b5cf6;
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    .funding-text {
        background: linear-gradient(180deg, #8b5cf6 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .intelligence-text {
        color: #ffffff;
    }
    
    .subtitle {
        color: #9ca3af;
        font-size: 1rem;
        line-height: 1.5;
        max-width: 600px;
        margin: 0 auto 2rem;
    }
    
    /* Stats section */
    .stats-container {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-bottom: 2rem;
    }
    
    .stat-box {
        text-align: center;
        padding: 1.5rem 2rem;
        background: rgba(139, 92, 246, 0.1);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 12px;
        min-width: 120px;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: #9ca3af;
        text-transform: capitalize;
    }
    
    /* Search and filter section */
    .controls-section {
        background: #111111;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    /* Search input styling */
    .stTextInput > div > div > input {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        color: white;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #6b7280;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #8b5cf6;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
    }
    
    /* Select box styling */
    .stSelectbox > div > div > select {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        color: white;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: transparent;
        border: 1px solid #333;
        color: #9ca3af;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        border-color: #8b5cf6;
        color: #8b5cf6;
    }
    
    /* Main collect button */
    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
    
    /* Results count */
    .results-info {
        text-align: center;
        color: #9ca3af;
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }
    
    /* Hide default Streamlit elements */
    .css-1dp5vir {display: none;}
    .css-18ni7ap {display: none;}
    section[data-testid="stSidebar"] {display: none;}
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #8b5cf6;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: transparent;
        padding: 0;
    }
    
    [data-testid="metric-container"] > div {
        background: transparent;
    }
    
    /* Pagination button in center */
    .center-button {
        text-align: center;
        padding: 0.5rem;
        background: #8b5cf6;
        color: white;
        border-radius: 4px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ''
    if 'filter_round' not in st.session_state:
        st.session_state.filter_round = ''
    if 'sort_field' not in st.session_state:
        st.session_state.sort_field = 'date'
    if 'sort_direction' not in st.session_state:
        st.session_state.sort_direction = 'desc'
    if 'available_rounds' not in st.session_state:
        st.session_state.available_rounds = []

def display_header_section():
    """Display the header section with logo and title"""
    st.markdown("""
    <div class="header-section">
        <div class="logo-wrapper">
            <span class="logo-icon">🔮</span>
            <span class="logo-text">CyberPulse</span>
        </div>
        <div class="main-title">
            <div class="funding-text">FUNDING</div>
            <div class="intelligence-text">INTELLIGENCE</div>
        </div>
        <p class="subtitle">
            Real-time analytics on cybersecurity investments, funding rounds, and market trends. 
            Track the pulse of cyber innovation with comprehensive data insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_stats_section():
    """Display statistics section"""
    try:
        stats = api_client.get_stats()
        total_companies = stats.get('total_companies', 0)
        total_funding = stats.get('total_funding', 0)
        
        # Format funding
        if total_funding >= 1000000000:
            funding_display = f"${total_funding / 1000000000:.1f}B+"
        elif total_funding >= 1000000:
            funding_display = f"${total_funding / 1000000:.0f}M+"
        else:
            funding_display = f"${total_funding:,.0f}+"
        
        # Always show "Live" for data feed
        data_feed = "Live"
        
    except:
        total_companies = "---"
        funding_display = "---"
        data_feed = "---"
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-box">
            <div class="stat-value">{funding_display}</div>
            <div class="stat-label">Total Funding</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{total_companies}+</div>
            <div class="stat-label">Companies</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{data_feed}</div>
            <div class="stat-label">Data Feed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_collect_button():
    """Display the collect intelligence button"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Collect Latest Intelligence", use_container_width=True, key="collect_btn"):
            with st.spinner("Collecting fresh intelligence..."):
                try:
                    result = api_client.trigger_data_collection()
                    st.success("✅ Intelligence collected successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to collect data: {str(e)}")

    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="color: #6b7280; font-size: 0.75rem;">
            Triggers fresh data collection from security funding sources
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_controls():
    """Display search and filter controls"""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "",
            placeholder="🔍 Search companies, descriptions, technologies...",
            value=st.session_state.search_term,
            label_visibility="collapsed",
            key="search_input"
        )
    
    with col2:
        # Load rounds if needed
        if not st.session_state.available_rounds:
            try:
                rounds = api_client.get_funding_rounds()
                st.session_state.available_rounds = rounds
            except:
                st.session_state.available_rounds = []
        
        options = ["All Rounds"] + sorted(st.session_state.available_rounds)
        current_display = st.session_state.filter_round if st.session_state.filter_round else "All Rounds"
        
        filter_round = st.selectbox(
            "",
            options,
            index=options.index(current_display) if current_display in options else 0,
            label_visibility="collapsed",
            key="round_filter"
        )
    
    with col3:
        sort_by = st.selectbox(
            "",
            ["Sort by Date", "Sort by Company", "Sort by Amount"],
            index=0,  # Default to date
            label_visibility="collapsed",
            key="sort_select"
        )

    
    # Process changes
    new_filter_round = "" if filter_round == "All Rounds" else filter_round
    new_sort_field = {
        "Sort by Company": "company_name",
        "Sort by Amount": "amount",
        "Sort by Date": "date"
    }.get(sort_by, "date")
    
    if (search_term != st.session_state.search_term or
        new_filter_round != st.session_state.filter_round or
        new_sort_field != st.session_state.sort_field):
        st.session_state.search_term = search_term
        st.session_state.filter_round = new_filter_round
        st.session_state.sort_field = new_sort_field
        st.session_state.current_page = 1
        st.rerun()

def display_pagination(current_page: int, total_pages: int, total_count: int, location: str = "top"):
    """Display pagination controls"""
    if total_pages <= 1:
        return
    
    # Results info (only on top)
    if location == "top":
        items_per_page = 12
        start = (current_page - 1) * items_per_page + 1
        end = min(current_page * items_per_page, total_count)
        
        st.markdown(f"""
        <div class="results-info">
            Showing {start} to {end} of {total_count} results
        </div>
        """, unsafe_allow_html=True)
    
    # Pagination controls
    cols = st.columns([1, 1, 1, 1, 1, 1, 1])
    
    # First page button
    with cols[0]:
        if st.button("◀◀", disabled=(current_page <= 1), key=f"first_{location}"):
            st.session_state.current_page = 1
            st.rerun()
    
    # Previous page button
    with cols[1]:
        if st.button("◀", disabled=(current_page <= 1), key=f"prev_{location}"):
            st.session_state.current_page = current_page - 1
            st.rerun()
    
    # Previous page number
    with cols[2]:
        if current_page > 1:
            if st.button(str(current_page - 1), key=f"page_prev_{location}"):
                st.session_state.current_page = current_page - 1
                st.rerun()
        else:
            st.write("")
    
    # Current page
    with cols[3]:
        st.markdown(f"""
        <div class="center-button">
            {current_page}
        </div>
        """, unsafe_allow_html=True)
    
    # Next page number
    with cols[4]:
        if current_page < total_pages:
            if st.button(str(current_page + 1), key=f"page_next_{location}"):
                st.session_state.current_page = current_page + 1
                st.rerun()
        else:
            st.write("")
    
    # Next page button
    with cols[5]:
        if st.button("▶", disabled=(current_page >= total_pages), key=f"next_{location}"):
            st.session_state.current_page = current_page + 1
            st.rerun()
    
    # Last page button
    with cols[6]:
        if st.button("▶▶", disabled=(current_page >= total_pages), key=f"last_{location}"):
            st.session_state.current_page = total_pages
            st.rerun()

def main():
    """Main application"""
    # Load CSS
    load_professional_css()
    
    # Initialize state
    initialize_session_state()
    
    # Header section
    display_header_section()
    
    # Stats section
    display_stats_section()
    
    # Collect button
    display_collect_button()
    
    # Controls
    display_controls()
    
    # Fetch and display data
    try:
        data = api_client.get_funding_data(
            page=st.session_state.current_page,
            items_per_page=12,
            sort_field=st.session_state.sort_field,
            sort_direction=st.session_state.sort_direction,
            search=st.session_state.search_term or None,
            filter_round=st.session_state.filter_round or None
        )
        
        if data and data.get('data'):
            companies = data['data']
            total_count = data.get('totalCount', 0)
            total_pages = data.get('totalPages', 1)
            current_page = data.get('currentPage', 1)
            
            # Top pagination
            display_pagination(current_page, total_pages, total_count, location="top")
            
            # Display funding cards
            display_funding_cards(companies)
            
            # Bottom pagination
            if total_pages > 1:
                display_pagination(current_page, total_pages, total_count, location="bottom")
        else:
            st.info("No funding data available. Click 'Collect Latest Intelligence' to fetch data.")
            
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        logger.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    main()