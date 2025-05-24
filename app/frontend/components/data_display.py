import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

def format_amount(amount: int) -> str:
    """Format a numeric amount into a readable string with K/M/B suffix"""
    if amount >= 1000000000:
        return f"${amount / 1000000000:.1f}B"
    elif amount >= 1000000:
        return f"${amount / 1000000:.1f}M"
    elif amount >= 1000:
        return f"${amount / 1000:.0f}K"
    else:
        return f"${amount:,}"

def format_date(date_str: str) -> str:
    """Format date string for display"""
    try:
        from datetime import datetime
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%b %d, %Y")
    except:
        return date_str or "Unknown Date"

def get_round_color(round_name: str) -> str:
    """Get color for funding round badge"""
    colors = {
        'Pre-Seed': '#8B5CF6',      # violet
        'Seed': '#3B82F6',          # blue
        'Series A': '#10B981',      # emerald
        'Series B': '#F59E0B',      # amber
        'Series C': '#EF4444',      # red
        'Series D': '#06B6D4',      # cyan
        'Series E': '#8B5CF6',      # purple
        'Growth': '#F97316',        # orange
        'Late Stage': '#DC2626',    # red
        'IPO': '#EAB308',           # yellow
        'Acquisition': '#6366F1',   # indigo
        'Post-IPO Debt': '#EC4899', # pink
        'Venture': '#14B8A6',       # teal
    }
    return colors.get(round_name, '#6B7280')  # default gray

def display_funding_card(company: Dict[str, Any]):
    """Display a single funding card using Streamlit components"""
    
    with st.container():
        # Create card with custom styling
        card_html = f"""
        <div style="
            background: linear-gradient(145deg, rgba(15, 15, 15, 0.9) 0%, rgba(30, 30, 30, 0.8) 100%);
            border: 1px solid rgba(139, 69, 255, 0.2);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        ">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
                <div style="flex: 1;">
                    <h3 style="color: white; font-size: 1.25rem; font-weight: bold; margin-bottom: 8px;">
                        {company.get('company_name', 'Unknown Company')}
                    </h3>
                    <span style="
                        background-color: {get_round_color(company.get('round', ''))}20;
                        color: {get_round_color(company.get('round', ''))};
                        border: 1px solid {get_round_color(company.get('round', ''))}40;
                        padding: 4px 12px;
                        border-radius: 16px;
                        font-size: 0.875rem;
                        font-weight: 500;
                    ">
                        {company.get('round', 'Unknown Round')}
                    </span>
                </div>
                <div style="text-align: right;">
                    <div style="
                        font-size: 1.5rem;
                        font-weight: bold;
                        background: linear-gradient(to right, #10B981, #059669);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                    ">
                        {format_amount(company.get('amount', 0)) if company.get('amount', 0) > 0 else 'Undisclosed'}
                    </div>
                    <div style="color: #9CA3AF; font-size: 0.875rem; margin-top: 4px;">
                        📅 {format_date(company.get('date', ''))}
                    </div>
                </div>
            </div>
            
            <p style="color: #D1D5DB; font-size: 0.875rem; line-height: 1.5; margin-bottom: 16px; min-height: 60px;">
                {company.get('description', 'No description available.')[:200]}{'...' if len(company.get('description', '')) > 200 else ''}
            </p>
            
            <div style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="color: #60A5FA;">🏢</span>
                    <span style="color: #9CA3AF; font-size: 0.875rem;">Type:</span>
                    <span style="color: #60A5FA; font-weight: 500; font-size: 0.875rem;">
                        {company.get('company_type', 'Unknown')}
                    </span>
                </div>
                
                <div style="display: flex; align-items: flex-start; gap: 8px; margin-bottom: 12px;">
                    <span style="color: #06B6D4;">👥</span>
                    <span style="color: #9CA3AF; font-size: 0.875rem;">Investors:</span>
                    <div style="flex: 1;">
                        {_format_investors_html(company.get('investors', []))}
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #8B5CF6;">🌐</span>
                    <span style="color: #9CA3AF; font-size: 0.875rem;">Source:</span>
                    <span style="color: #8B5CF6; font-weight: 500; font-size: 0.875rem;">
                        {company.get('source', 'Unknown')}
                    </span>
                </div>
            </div>
            
            <div style="display: flex; gap: 8px; padding-top: 16px; border-top: 1px solid #374151;">
                {_format_action_buttons_html(company)}
            </div>
        </div>
        """
        
        st.markdown(card_html, unsafe_allow_html=True)

def _format_investors_html(investors: list) -> str:
    """Format investors list as HTML"""
    if not investors:
        return '<span style="color: #6B7280; font-size: 0.75rem;">No investors listed</span>'
    
    investor_html = []
    for i, investor in enumerate(investors[:5]):  # Limit to 5 investors
        name = investor.get('name', 'Unknown') if isinstance(investor, dict) else str(investor)
        url = investor.get('url', '') if isinstance(investor, dict) else ''
        
        if url:
            investor_html.append(f'''
                <a href="{url}" target="_blank" style="
                    background-color: rgba(6, 182, 212, 0.2);
                    color: #06B6D4;
                    border: 1px solid rgba(6, 182, 212, 0.4);
                    padding: 2px 8px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    text-decoration: none;
                    display: inline-block;
                    margin: 2px;
                    transition: all 0.2s;
                " onmouseover="this.style.backgroundColor='rgba(6, 182, 212, 0.3)'" 
                   onmouseout="this.style.backgroundColor='rgba(6, 182, 212, 0.2)'">
                    {name}
                </a>
            ''')
        else:
            investor_html.append(f'''
                <span style="
                    background-color: rgba(107, 114, 128, 0.3);
                    color: #9CA3AF;
                    border: 1px solid rgba(107, 114, 128, 0.4);
                    padding: 2px 8px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    display: inline-block;
                    margin: 2px;
                ">
                    {name}
                </span>
            ''')
    
    if len(investors) > 5:
        investor_html.append(f'''
            <span style="
                background-color: rgba(107, 114, 128, 0.3);
                color: #9CA3AF;
                border: 1px solid rgba(107, 114, 128, 0.4);
                padding: 2px 8px;
                border-radius: 6px;
                font-size: 0.75rem;
                display: inline-block;
                margin: 2px;
            ">
                +{len(investors) - 5} more
            </span>
        ''')
    
    return ''.join(investor_html)

def _format_action_buttons_html(company: Dict[str, Any]) -> str:
    """Format action buttons as HTML"""
    buttons_html = []
    
    # Website button
    if company.get('company_url'):
        buttons_html.append(f'''
            <a href="{company['company_url']}" target="_blank" style="
                flex: 1;
                background-color: rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(139, 69, 255, 0.3);
                color: #A855F7;
                padding: 8px 16px;
                border-radius: 6px;
                text-decoration: none;
                text-align: center;
                font-size: 0.875rem;
                transition: all 0.2s;
            " onmouseover="this.style.backgroundColor='rgba(139, 69, 255, 0.2)'; this.style.borderColor='rgba(139, 69, 255, 0.4)'; this.style.color='white';"
               onmouseout="this.style.backgroundColor='rgba(0, 0, 0, 0.4)'; this.style.borderColor='rgba(139, 69, 255, 0.3)'; this.style.color='#A855F7';">
                🔗 Website
            </a>
        ''')
    else:
        buttons_html.append('''
            <div style="
                flex: 1;
                background-color: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(107, 114, 128, 0.3);
                color: #6B7280;
                padding: 8px 16px;
                border-radius: 6px;
                text-align: center;
                font-size: 0.875rem;
            ">
                No Website
            </div>
        ''')
    
    # Story button
    if company.get('story_link'):
        buttons_html.append(f'''
            <a href="{company['story_link']}" target="_blank" style="
                flex: 1;
                background-color: rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(249, 115, 22, 0.3);
                color: #F97316;
                padding: 8px 16px;
                border-radius: 6px;
                text-decoration: none;
                text-align: center;
                font-size: 0.875rem;
                transition: all 0.2s;
            " onmouseover="this.style.backgroundColor='rgba(249, 115, 22, 0.2)'; this.style.borderColor='rgba(249, 115, 22, 0.4)'; this.style.color='white';"
               onmouseout="this.style.backgroundColor='rgba(0, 0, 0, 0.4)'; this.style.borderColor='rgba(249, 115, 22, 0.3)'; this.style.color='#F97316';">
                📈 Story
            </a>
        ''')
    else:
        buttons_html.append('''
            <div style="
                flex: 1;
                background-color: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(107, 114, 128, 0.3);
                color: #6B7280;
                padding: 8px 16px;
                border-radius: 6px;
                text-align: center;
                font-size: 0.875rem;
            ">
                No Story
            </div>
        ''')
    
    return ''.join(buttons_html)

def display_loading_animation():
    """Display a loading animation"""
    st.markdown("""
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 200px; gap: 16px;">
        <div style="
            width: 64px;
            height: 64px;
            border: 4px solid rgba(139, 69, 255, 0.3);
            border-top: 4px solid #8B45FF;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
        <div style="color: #A855F7; font-size: 1.125rem; font-weight: 500;">
            ✨ Loading funding intelligence...
        </div>
    </div>
    
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def display_funding_data(companies: List[Dict[str, Any]], view_mode: str = "cards"):
    """
    Display funding data in different view modes
    
    Args:
        companies: List of company funding data
        view_mode: "cards", "table", or "chart"
    """
    
    if not companies:
        display_no_data_message()
        return
    
    # View mode selector
    st.markdown("#### 👀 Display Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Card View", use_container_width=True, 
                    type="primary" if view_mode == "cards" else "secondary"):
            st.session_state.view_mode = "cards"
    
    with col2:
        if st.button("📊 Table View", use_container_width=True,
                    type="primary" if view_mode == "table" else "secondary"):
            st.session_state.view_mode = "table"
    
    with col3:
        if st.button("📈 Chart View", use_container_width=True,
                    type="primary" if view_mode == "chart" else "secondary"):
            st.session_state.view_mode = "chart"
    
    # Update view mode from session state
    if 'view_mode' in st.session_state:
        view_mode = st.session_state.view_mode
    
    st.markdown("---")
    
    # Display based on view mode
    if view_mode == "cards":
        display_card_view(companies)
    elif view_mode == "table":
        display_table_view(companies)
    elif view_mode == "chart":
        display_chart_view(companies)

def display_card_view(companies: List[Dict[str, Any]]):
    """Display companies in card format"""
    
    st.markdown(f"### 🏢 Funding Data ({len(companies)} companies)")
    
    # Display cards in a grid
    for i in range(0, len(companies), 2):
        cols = st.columns(2)
        
        # First card
        with cols[0]:
            display_funding_card(companies[i])
        
        # Second card (if exists)
        if i + 1 < len(companies):
            with cols[1]:
                display_funding_card(companies[i + 1])

def display_table_view(companies: List[Dict[str, Any]]):
    """Display companies in table format"""
    
    st.markdown(f"### 📊 Funding Table ({len(companies)} companies)")
    
    # Prepare data for table
    table_data = []
    for company in companies:
        table_data.append({
            "Company": company.get('company_name', 'Unknown'),
            "Round": company.get('round', 'Unknown'),
            "Amount": format_amount(company.get('amount', 0)) if company.get('amount', 0) > 0 else 'Undisclosed',
            "Type": company.get('company_type', 'Unknown'),
            "Date": company.get('date', 'Unknown'),
            "Investors": len(company.get('investors', [])),
            "Source": company.get('source', 'Unknown')
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Display with custom styling
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Company": st.column_config.TextColumn("🏢 Company", width="medium"),
            "Round": st.column_config.TextColumn("💼 Round", width="small"),
            "Amount": st.column_config.TextColumn("💰 Amount", width="small"),
            "Type": st.column_config.TextColumn("🏷️ Type", width="small"),
            "Date": st.column_config.DateColumn("📅 Date", width="small"),
            "Investors": st.column_config.NumberColumn("👥 Investors", width="small"),
            "Source": st.column_config.TextColumn("🌐 Source", width="small")
        }
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="cybersecurity_funding_data.csv",
        mime="text/csv"
    )

def display_chart_view(companies: List[Dict[str, Any]]):
    """Display companies in chart format"""
    
    st.markdown(f"### 📈 Funding Analytics ({len(companies)} companies)")
    
    # Prepare data for charts
    df = pd.DataFrame(companies)
    
    # Chart tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Funding by Round", "📊 Amount Distribution", "📅 Timeline", "🏢 By Type"])
    
    with tab1:
        display_funding_by_round_chart(df)
    
    with tab2:
        display_amount_distribution_chart(df)
    
    with tab3:
        display_funding_timeline_chart(df)
    
    with tab4:
        display_funding_by_type_chart(df)

def display_funding_by_round_chart(df: pd.DataFrame):
    """Display funding distribution by round"""
    
    if df.empty:
        st.warning("No data available for chart")
        return
    
    # Group by round and sum amounts
    round_data = df.groupby('round').agg({
        'amount': 'sum',
        'company_name': 'count'
    }).reset_index()
    round_data.columns = ['Round', 'Total_Amount', 'Company_Count']
    
    # Filter out zero amounts for better visualization
    round_data = round_data[round_data['Total_Amount'] > 0]
    
    if round_data.empty:
        st.warning("No disclosed funding amounts available for chart")
        return
    
    # Create bar chart
    fig = px.bar(
        round_data,
        x='Round',
        y='Total_Amount',
        title='Total Funding by Round',
        labels={'Total_Amount': 'Total Funding ($)', 'Round': 'Funding Round'},
        color='Total_Amount',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rounds", len(round_data))
    with col2:
        st.metric("Total Funding", format_amount(round_data['Total_Amount'].sum()))
    with col3:
        st.metric("Total Companies", round_data['Company_Count'].sum())

def display_amount_distribution_chart(df: pd.DataFrame):
    """Display funding amount distribution"""
    
    if df.empty:
        st.warning("No data available for chart")
        return
    
    # Filter out zero amounts
    funded_companies = df[df['amount'] > 0]
    
    if funded_companies.empty:
        st.warning("No disclosed funding amounts available for chart")
        return
    
    # Create histogram
    fig = px.histogram(
        funded_companies,
        x='amount',
        nbins=20,
        title='Funding Amount Distribution',
        labels={'amount': 'Funding Amount ($)', 'count': 'Number of Companies'},
        color_discrete_sequence=['#8B45FF']
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Median", format_amount(funded_companies['amount'].median()))
    with col2:
        st.metric("Mean", format_amount(funded_companies['amount'].mean()))
    with col3:
        st.metric("Min", format_amount(funded_companies['amount'].min()))
    with col4:
        st.metric("Max", format_amount(funded_companies['amount'].max()))

def display_funding_timeline_chart(df: pd.DataFrame):
    """Display funding timeline"""
    
    if df.empty:
        st.warning("No data available for chart")
        return
    
    # Convert date column and group by month
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    
    if df.empty:
        st.warning("No valid dates available for timeline")
        return
    
    # Group by month
    df['month'] = df['date'].dt.to_period('M')
    timeline_data = df.groupby('month').agg({
        'amount': 'sum',
        'company_name': 'count'
    }).reset_index()
    timeline_data['month'] = timeline_data['month'].astype(str)
    
    # Create line chart
    fig = go.Figure()
    
    # Add funding amount line
    fig.add_trace(go.Scatter(
        x=timeline_data['month'],
        y=timeline_data['amount'],
        mode='lines+markers',
        name='Total Funding',
        line=dict(color='#8B45FF', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Funding Timeline',
        xaxis_title='Month',
        yaxis_title='Total Funding ($)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_funding_by_type_chart(df: pd.DataFrame):
    """Display funding by company type"""
    
    if df.empty:
        st.warning("No data available for chart")
        return
    
    # Group by company type
    type_data = df.groupby('company_type').agg({
        'amount': 'sum',
        'company_name': 'count'
    }).reset_index()
    type_data.columns = ['Type', 'Total_Amount', 'Company_Count']
    
    # Create pie chart
    fig = px.pie(
        type_data,
        values='Company_Count',
        names='Type',
        title='Companies by Type',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_no_data_message():
    """Display message when no data is found"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(145deg, rgba(15, 15, 15, 0.9) 0%, rgba(30, 30, 30, 0.8) 100%);
        border: 1px solid rgba(139, 69, 255, 0.2);
        border-radius: 16px;
        padding: 48px;
        text-align: center;
        margin: 32px 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 16px;">🔍</div>
        <h3 style="color: white; font-size: 1.5rem; margin-bottom: 16px;">No funding data found</h3>
        <p style="color: #9CA3AF; font-size: 1rem;">Try adjusting your search criteria or filters</p>
    </div>
    """, unsafe_allow_html=True)

def display_pagination_info(current_page: int, total_pages: int, items_per_page: int, total_items: int):
    """Display pagination information"""
    
    start_item = (current_page - 1) * items_per_page + 1
    end_item = min(current_page * items_per_page, total_items)
    
    st.markdown(f"""
    <div style="
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(139, 69, 255, 0.2);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin: 16px 0;
        color: #9CA3AF;
    ">
        Showing <span style="color: #8B45FF; font-weight: bold;">{start_item}</span> to 
        <span style="color: #8B45FF; font-weight: bold;">{end_item}</span> of 
        <span style="color: #8B45FF; font-weight: bold;">{total_items:,}</span> results
    </div>
    """, unsafe_allow_html=True)