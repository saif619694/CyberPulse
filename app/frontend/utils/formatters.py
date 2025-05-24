import streamlit as st
from datetime import datetime
from typing import Dict, Any

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
        name = investor.get('name', 'Unknown')
        url = investor.get('url', '')
        
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