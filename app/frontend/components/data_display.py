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
        'Pre-Seed': '#ff6b35',      # orange
        'Seed': '#00ff88',          # green
        'Series A': '#00ccff',      # cyan
        'Series B': '#ff4081',      # pink
        'Series C': '#ffa726',      # amber
        'Series D': '#ab47bc',      # purple
        'Series E': '#26a69a',      # teal
        'Growth': '#66bb6a',        # light green
        'Late Stage': '#ef5350',    # red
        'IPO': '#ffee58',           # yellow
        'Acquisition': '#42a5f5',   # blue
        'Post-IPO Debt': '#ec407a', # pink
        'Venture': '#26c6da',       # cyan
    }
    return colors.get(round_name, '#888888')  # default gray

def display_funding_card(company: Dict[str, Any]):
    """Display a single funding card using proper Streamlit components"""
    
    # Use streamlit container instead of raw HTML
    with st.container():
        # Card styling with CSS class
        st.markdown(f"""
        <div class="funding-card" style="
            background: linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%);
            border: 1px solid #333333;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        ">
        """, unsafe_allow_html=True)
        
        # Company name and round - using columns for better control
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <h3 style="color: #ffffff; font-size: 1.4rem; font-weight: bold; margin: 0 0 12px 0;">
                {company.get('company_name', 'Unknown Company')}
            </h3>
            """, unsafe_allow_html=True)
            
            round_color = get_round_color(company.get('round', ''))
            st.markdown(f"""
            <span style="
                background: {round_color}20;
                color: {round_color};
                border: 1px solid {round_color}40;
                padding: 6px 12px;
                border-radius: 16px;
                font-size: 0.85rem;
                font-weight: 600;
                display: inline-block;
            ">
                {company.get('round', 'Unknown Round')}
            </span>
            """, unsafe_allow_html=True)
        
        with col2:
            amount = company.get('amount', 0)
            amount_display = format_amount(amount) if amount > 0 else 'Undisclosed'
            
            st.markdown(f"""
            <div style="text-align: right;">
                <div style="
                    font-size: 1.6rem;
                    font-weight: bold;
                    color: #00ff88;
                    margin-bottom: 4px;
                ">
                    {amount_display}
                </div>
                <div style="color: #888888; font-size: 0.9rem;">
                    📅 {format_date(company.get('date', ''))}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Description
        description = company.get('description', 'No description available.')
        if len(description) > 200:
            description = description[:200] + '...'
        
        st.markdown(f"""
        <p style="
            color: #cccccc; 
            font-size: 0.95rem; 
            line-height: 1.6; 
            margin: 16px 0; 
            min-height: 60px;
            background: #111111;
            padding: 12px;
            border-radius: 8px;
            border-left: 3px solid #00ff88;
        ">
            {description}
        </p>
        """, unsafe_allow_html=True)
        
        # Company details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <span style="color: #00ccff;">🏢 Type:</span>
                <span style="color: #ffffff; font-weight: 500; margin-left: 8px;">
                    {company.get('company_type', 'Unknown')}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <span style="color: #ff6b35;">🌐 Source:</span>
                <span style="color: #ffffff; font-weight: 500; margin-left: 8px;">
                    {company.get('source', 'Unknown')}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Investors
            investors = company.get('investors', [])
            investor_count = len(investors)
            
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <span style="color: #ab47bc;">👥 Investors:</span>
                <span style="color: #ffffff; font-weight: 500; margin-left: 8px;">
                    {investor_count} investor{'s' if investor_count != 1 else ''}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Show top investors
            if investors:
                top_investors = investors[:3]
                investor_names = []
                for inv in top_investors:
                    if isinstance(inv, dict):
                        investor_names.append(inv.get('name', 'Unknown'))
                    else:
                        investor_names.append(str(inv))
                
                investor_text = ', '.join(investor_names)
                if len(investors) > 3:
                    investor_text += f' +{len(investors) - 3} more'
                
                st.markdown(f"""
                <div style="
                    font-size: 0.85rem; 
                    color: #888888; 
                    background: #0a0a0a; 
                    padding: 8px; 
                    border-radius: 6px;
                    border: 1px solid #333333;
                ">
                    {investor_text}
                </div>
                """, unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            company_url = company.get('company_url', '')
            if company_url:
                st.markdown(f"""
                <a href="{company_url}" target="_blank" style="
                    display: block;
                    text-align: center;
                    background: linear-gradient(135deg, #00ff88 0%, #00ccff 100%);
                    color: #000000;
                    padding: 10px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: 600;
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='translateY(-2px)'" 
                   onmouseout="this.style.transform='translateY(0)'">
                    🔗 Visit Website
                </a>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    text-align: center;
                    background: #333333;
                    color: #888888;
                    padding: 10px;
                    border-radius: 6px;
                    font-weight: 500;
                ">
                    No Website
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            story_link = company.get('story_link', '')
            if story_link:
                st.markdown(f"""
                <a href="{story_link}" target="_blank" style="
                    display: block;
                    text-align: center;
                    background: linear-gradient(135deg, #ff6b35 0%, #ffa726 100%);
                    color: #000000;
                    padding: 10px;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: 600;
                    transition: all 0.3s ease;
                " onmouseover="this.style.transform='translateY(-2px)'" 
                   onmouseout="this.style.transform='translateY(0)'">
                    📰 Read Story
                </a>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    text-align: center;
                    background: #333333;
                    color: #888888;
                    padding: 10px;
                    border-radius: 6px;
                    font-weight: 500;
                ">
                    No Story
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_funding_data(companies: List[Dict[str, Any]], view_mode: str = "cards"):
    """
    Display funding data in different view modes with professional styling
    """
    
    if not companies:
        display_no_data_message()
        return
    
    if view_mode == "cards":
        display_card_view(companies)
    elif view_mode == "table":
        display_table_view(companies)
    elif view_mode == "chart":
        display_chart_view(companies)

def display_card_view(companies: List[Dict[str, Any]]):
    """Display companies in card format with improved layout"""
    
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h3 style="color: #00ff88; font-size: 1.5rem; margin-bottom: 16px;">
            🏢 Funding Intelligence ({len(companies)} companies)
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display cards in a responsive grid
    for i in range(0, len(companies), 2):
        cols = st.columns(2, gap="medium")
        
        # First card
        with cols[0]:
            display_funding_card(companies[i])
        
        # Second card (if exists)
        if i + 1 < len(companies):
            with cols[1]:
                display_funding_card(companies[i + 1])

def display_table_view(companies: List[Dict[str, Any]]):
    """Display companies in table format with enhanced styling"""
    
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h3 style="color: #00ff88; font-size: 1.5rem; margin-bottom: 16px;">
            📊 Funding Table ({len(companies)} companies)
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare data for table
    table_data = []
    for company in companies:
        table_data.append({
            "Company": company.get('company_name', 'Unknown'),
            "Round": company.get('round', 'Unknown'),
            "Amount": format_amount(company.get('amount', 0)) if company.get('amount', 0) > 0 else 'Undisclosed',
            "Type": company.get('company_type', 'Unknown'),
            "Date": format_date(company.get('date', '')),
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
            "Company": st.column_config.TextColumn("🏢 Company", width="large"),
            "Round": st.column_config.TextColumn("💼 Round", width="medium"),
            "Amount": st.column_config.TextColumn("💰 Amount", width="medium"),
            "Type": st.column_config.TextColumn("🏷️ Type", width="small"),
            "Date": st.column_config.TextColumn("📅 Date", width="medium"),
            "Investors": st.column_config.NumberColumn("👥 Investors", width="small"),
            "Source": st.column_config.TextColumn("🌐 Source", width="medium")
        }
    )
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="cybersecurity_funding_data.csv",
        mime="text/csv",
        use_container_width=True
    )

def display_chart_view(companies: List[Dict[str, Any]]):
    """Display companies in chart format with dark theme"""
    
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h3 style="color: #00ff88; font-size: 1.5rem; margin-bottom: 16px;">
            📈 Funding Analytics ({len(companies)} companies)
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Prepare data for charts
    df = pd.DataFrame(companies)
    
    # Chart tabs
    tab1, tab2, tab3, tab4 = st.tabs(["💰 By Round", "📊 Distribution", "📅 Timeline", "🏢 By Type"])
    
    with tab1:
        display_funding_by_round_chart(df)
    
    with tab2:
        display_amount_distribution_chart(df)
    
    with tab3:
        display_funding_timeline_chart(df)
    
    with tab4:
        display_funding_by_type_chart(df)

def display_funding_by_round_chart(df: pd.DataFrame):
    """Display funding distribution by round with dark theme"""
    
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
    
    # Create bar chart with dark theme
    fig = px.bar(
        round_data,
        x='Round',
        y='Total_Amount',
        title='Total Funding by Round',
        labels={'Total_Amount': 'Total Funding ($)', 'Round': 'Funding Round'},
        color='Total_Amount',
        color_continuous_scale=['#ff6b35', '#00ff88', '#00ccff']
    )
    
    # Dark theme styling
    fig.update_layout(
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#111111',
        font_color='#ffffff',
        title_font_size=20,
        title_font_color='#00ff88',
        xaxis=dict(gridcolor='#333333'),
        yaxis=dict(gridcolor='#333333'),
        coloraxis_colorbar=dict(
            title_font_color='#ffffff',
            tickfont_color='#ffffff'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rounds", len(round_data), help="Number of different funding rounds")
    with col2:
        st.metric("Total Funding", format_amount(round_data['Total_Amount'].sum()), help="Sum of all disclosed funding")
    with col3:
        st.metric("Total Companies", round_data['Company_Count'].sum(), help="Number of companies with disclosed funding")

def display_amount_distribution_chart(df: pd.DataFrame):
    """Display funding amount distribution with dark theme"""
    
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
        color_discrete_sequence=['#00ff88']
    )
    
    # Dark theme styling
    fig.update_layout(
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#111111',
        font_color='#ffffff',
        title_font_size=20,
        title_font_color='#00ff88',
        xaxis=dict(gridcolor='#333333'),
        yaxis=dict(gridcolor='#333333')
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
    """Display funding timeline with dark theme"""
    
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
        line=dict(color='#00ff88', width=3),
        marker=dict(size=8, color='#00ccff')
    ))
    
    # Dark theme styling
    fig.update_layout(
        title='Funding Timeline',
        title_font_color='#00ff88',
        title_font_size=20,
        xaxis_title='Month',
        yaxis_title='Total Funding ($)',
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#111111',
        font_color='#ffffff',
        xaxis=dict(gridcolor='#333333'),
        yaxis=dict(gridcolor='#333333')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_funding_by_type_chart(df: pd.DataFrame):
    """Display funding by company type with dark theme"""
    
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
        color_discrete_sequence=['#00ff88', '#00ccff', '#ff6b35', '#ab47bc']
    )
    
    # Dark theme styling
    fig.update_layout(
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#111111',
        font_color='#ffffff',
        title_font_size=20,
        title_font_color='#00ff88'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_no_data_message():
    """Display message when no data is found"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(145deg, #111111 0%, #1a1a1a 100%);
        border: 1px solid #333333;
        border-radius: 16px;
        padding: 48px;
        text-align: center;
        margin: 32px 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 16px;">🔍</div>
        <h3 style="color: #ffffff; font-size: 1.5rem; margin-bottom: 16px;">No funding data found</h3>
        <p style="color: #888888; font-size: 1rem;">Try adjusting your search criteria or filters</p>
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