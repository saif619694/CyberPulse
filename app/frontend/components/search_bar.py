import streamlit as st
from typing import List, Tuple, Optional

def display_search_filters(available_rounds: List[str], total_results: int) -> Tuple[str, str]:
    """
    Display search and filter controls
    
    Returns:
        Tuple of (search_term, selected_round)
    """
    
    # Custom CSS for search components
    st.markdown("""
    <style>
    .search-container {
        background: linear-gradient(145deg, rgba(15, 15, 15, 0.9) 0%, rgba(30, 30, 30, 0.8) 100%);
        border: 1px solid rgba(139, 69, 255, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    
    .results-counter {
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 16px;
    }
    
    .results-number {
        font-size: 2rem;
        font-weight: bold;
        color: #10B981;
        margin-bottom: 4px;
    }
    
    .results-label {
        font-size: 0.875rem;
        color: #9CA3AF;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Results counter
    results_html = f"""
    <div class="results-counter">
        <div class="results-number">{total_results:,}</div>
        <div class="results-label">Companies Found</div>
    </div>
    """
    st.markdown(results_html, unsafe_allow_html=True)
    
    # Search and filter container
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("#### 🔍 Search Companies")
            search_term = st.text_input(
                "",
                placeholder="Search companies, descriptions, technologies...",
                help="Search across company names, descriptions, and company types",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("#### 🎯 Filter by Round")
            round_options = ["All Rounds"] + sorted(available_rounds)
            selected_round = st.selectbox(
                "",
                round_options,
                help="Filter by funding round type",
                label_visibility="collapsed"
            )
            
            # Convert back to API format
            if selected_round == "All Rounds":
                selected_round = ""
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return search_term, selected_round

def display_sort_controls() -> Tuple[str, str]:
    """
    Display sorting controls
    
    Returns:
        Tuple of (sort_field, sort_direction)
    """
    
    st.markdown("#### 📊 Sort Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sort_field = st.selectbox(
            "Sort by",
            ["date", "company_name", "amount"],
            format_func=lambda x: {
                "date": "📅 Date",
                "company_name": "🏢 Company Name", 
                "amount": "💰 Funding Amount"
            }[x],
            help="Choose sorting criteria"
        )
    
    with col2:
        sort_direction = st.selectbox(
            "Order",
            ["desc", "asc"],
            format_func=lambda x: "📉 Descending" if x == "desc" else "📈 Ascending",
            help="Choose sort order"
        )
    
    return sort_field, sort_direction

def display_quick_filters(available_rounds: List[str]) -> Optional[str]:
    """
    Display quick filter buttons for popular funding rounds
    
    Returns:
        Selected round or None
    """
    
    # Popular rounds to display as quick filters
    popular_rounds = ["Seed", "Series A", "Series B", "Series C", "Growth"]
    
    # Filter to only show rounds that exist in the data
    existing_popular_rounds = [r for r in popular_rounds if r in available_rounds]
    
    if not existing_popular_rounds:
        return None
    
    st.markdown("#### ⚡ Quick Filters")
    
    # Create columns for buttons
    cols = st.columns(len(existing_popular_rounds) + 1)
    
    # All button
    with cols[0]:
        if st.button("All", use_container_width=True):
            return ""
    
    # Round buttons
    for i, round_name in enumerate(existing_popular_rounds):
        with cols[i + 1]:
            if st.button(round_name, use_container_width=True):
                return round_name
    
    return None

def display_advanced_search():
    """Display advanced search options in an expander"""
    
    with st.expander("🔧 Advanced Search Options"):
        st.markdown("#### Additional Filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_amount = st.number_input(
                "Minimum Funding Amount ($)",
                min_value=0,
                value=0,
                step=1000000,
                help="Filter by minimum funding amount"
            )
        
        with col2:
            max_amount = st.number_input(
                "Maximum Funding Amount ($)",
                min_value=0,
                value=0,
                step=1000000,
                help="Filter by maximum funding amount (0 = no limit)"
            )
        
        company_type = st.selectbox(
            "Company Type",
            ["All Types", "Product", "Service"],
            help="Filter by company type"
        )
        
        date_range = st.date_input(
            "Date Range",
            value=None,
            help="Filter by funding date range"
        )
        
        return {
            "min_amount": min_amount if min_amount > 0 else None,
            "max_amount": max_amount if max_amount > 0 else None,
            "company_type": company_type if company_type != "All Types" else None,
            "date_range": date_range
        }