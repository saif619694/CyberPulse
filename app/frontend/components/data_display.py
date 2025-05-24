import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import sys
import os
import html

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
        'Seed': '#00ccff',          # cyan/blue
        'Series A': '#00ff88',      # green
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
    """Display a single funding card with modern layout matching the reference design"""
    
    # Prepare dynamic content
    company_name = company.get('company_name', 'Unknown Company')
    round_name = company.get('round', 'Unknown Round')
    round_color = get_round_color(round_name)
    amount_display = format_amount(company.get('amount', 0)) if company.get('amount', 0) > 0 else 'Undisclosed'
    date_display = format_date(company.get('date', ''))
    description_display = company.get('description', 'No description available.')[:200]
    if len(company.get('description', '')) > 200:
        description_display += '...'
    company_type_display = company.get('company_type', 'Unknown')
    investors_count = len(company.get('investors', []))
    investors_text = f"{investors_count} investor{'s' if investors_count != 1 else ''}"
    source_value = company.get('source', 'Unknown')
    source_display = f'<a href="{html.unescape(source_value)}" target="_blank" style="color: #ffffff; text-decoration: none;">{html.unescape(source_value)}</a>' if source_value.startswith('http') else html.unescape(source_value)

    # Construct Website button HTML
    website_button_html = ""
    if company.get('company_url'):
        website_button_html = f'''
        <a href="{html.unescape(company.get('company_url', ''))}" target="_blank" style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            color: #000000;
            padding: 12px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1);
        " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(255, 255, 255, 0.2)'"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(255, 255, 255, 0.1)'">
            <span style="font-size: 0.9rem;">🔗</span>
            Website
        </a>
        '''
    else:
        website_button_html = '''
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: #333333;
            color: #888888;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: not-allowed;
        ">
            <span style="font-size: 0.9rem;">🔗</span>
            No Website
        </div>
        '''

    # Construct Story button HTML
    story_button_html = ""
    if company.get('story_link'):
        story_button_html = f'''
        <a href="{html.unescape(company.get('story_link', ''))}" target="_blank" style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: linear-gradient(135deg, #ffffff 0%, #e0e0e0 100%);
            color: #000000;
            padding: 12px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1);
        " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(255, 255, 255, 0.2)'"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(255, 255, 255, 0.1)'">
            <span style="font-size: 0.9rem;">📰</span>
            Story
        </a>
        '''
    else:
        story_button_html = '''
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: #333333;
            color: #888888;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: not-allowed;
        ">
            <span style="font-size: 0.9rem;">📰</span>
            No Story
        </div>
        '''
    
    # Construct Key Investors HTML
    key_investors_html = ""
    if company.get('investors'):
        key_investors_html = f'''
        <div style="
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 12px;
            margin: 16px 0;
        ">
            <div style="color: #888888; font-size: 0.8rem; margin-bottom: 6px;">Key Investors:</div>
            <div style="color: #cccccc; font-size: 0.85rem; line-height: 1.4;">
                {", ".join([inv.get("name", str(inv)) if isinstance(inv, dict) else str(inv) for inv in company.get("investors", [])[:3]])}
                {" +{}more".format(len(company.get("investors", [])) - 3) if len(company.get("investors", [])) > 3 else ""}
            </div>
        </div>
        '''

    # Main card HTML template
    card_html_template = """
    <div style="
        background: linear-gradient(145deg, #1a1a1a 0%, #0f0f0f 100%);
        border: 1px solid #333333;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
            <div style="flex: 1;">
                <h2 style="
                    color: #ffffff;
                    font-size: 1.5rem;
                    font-weight: 700;
                    margin: 0 0 8px 0;
                    letter-spacing: -0.02em;
                ">
                    {company_name}
                </h2>
                <span style="
                    background: {round_color}40;
                    color: {round_color};
                    border: 1px solid {round_color}60;
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-size: 0.85rem;
                    font-weight: 600;
                    display: inline-block;
                ">
                    {round_name}
                </span>
            </div>
            <div style="text-align: right; margin-left: 20px;">
                <div style="
                    font-size: 1.75rem;
                    font-weight: 700;
                    color: #00ff88;
                    margin-bottom: 4px;
                    letter-spacing: -0.02em;
                ">
                    {amount_display}
                </div>
                <div style="
                    color: #888888;
                    font-size: 0.9rem;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    gap: 6px;
                ">
                    <span style="font-size: 0.8rem;">📅</span>
                    {date_display}
                </div>
            </div>
        </div>
        <div style="margin: 20px 0;">
            <p style="
                color: #cccccc;
                font-size: 0.95rem;
                line-height: 1.5;
                margin: 0;
                text-align: justify;
            ">
                {description_display}
            </p>
        </div>
        <div style="margin: 20px 0; display: flex; flex-direction: column; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="color: #00ccff; font-size: 1rem;">🏢</span>
                <span style="color: #888888; font-size: 0.9rem; font-weight: 500;">Type:</span>
                <span style="color: #ffffff; font-weight: 600; font-size: 0.9rem;">
                    {company_type_display}
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="color: #ab47bc; font-size: 1rem;">👥</span>
                <span style="color: #888888; font-size: 0.9rem; font-weight: 500;">Investors:</span>
                <span style="color: #ffffff; font-weight: 600; font-size: 0.9rem;">
                    {investors_text}
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="color: #ff6b35; font-size: 1rem;">🌐</span>
                <span style="color: #888888; font-size: 0.9rem; font-weight: 500;">Source:</span>
                <span style="color: #ffffff; font-weight: 600; font-size: 0.9rem;">
                    {source_display}
                </span>
            </div>
        </div>
        {key_investors_html}
        <div style="display: flex; gap: 12px; margin-top: 20px;">
            <div style="flex: 1;">
                {website_button_html}
            </div>
            <div style="flex: 1;">
                {story_button_html}
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html_template.format(
        company_name=company_name,
        round_name=round_name,
        round_color=round_color,
        amount_display=amount_display,
        date_display=date_display,
        description_display=description_display,
        company_type_display=company_type_display,
        investors_text=investors_text,
        source_display=source_display,
        key_investors_html=key_investors_html,
        website_button_html=website_button_html,
        story_button_html=story_button_html
    ), unsafe_allow_html=True)

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