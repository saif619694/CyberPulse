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

def display_loading_animation():
    """Display a professional loading animation"""
    st.markdown("""
    <div style="
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        height: 200px; 
        gap: 20px;
        background: linear-gradient(145deg, #0a0a0a 0%, #1a1a1a 100%);
        border: 1px solid #333333;
        border-radius: 16px;
        margin: 32px 0;
    ">
        <div style="
            width: 64px;
            height: 64px;
            border: 4px solid #333333;
            border-top: 4px solid #00ff88;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
        <div style="
            color: #00ff88; 
            font-size: 1.2rem; 
            font-weight: 600;
            text-align: center;
        ">
            ⚡ Loading Intelligence Data...
        </div>
        <div style="
            color: #888888; 
            font-size: 0.9rem; 
            text-align: center;
        ">
            Processing cybersecurity funding information
        </div>
    </div>
    
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    </style>
    """, unsafe_allow_html=True)

def display_success_message(message: str, details: str = ""):
    """Display a professional success message"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, #0a2e0a 0%, #1a4d1a 100%);
        border: 1px solid #00ff88;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        color: #00ff88;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="font-size: 1.5rem;">✅</div>
        <div>
            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 4px;">
                {message}
            </div>
            {f'<div style="font-size: 0.9rem; color: #88cc88;">{details}</div>' if details else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_error_message(message: str, details: str = ""):
    """Display a professional error message"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, #2e0a0a 0%, #4d1a1a 100%);
        border: 1px solid #ff4444;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        color: #ff8888;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="font-size: 1.5rem;">❌</div>
        <div>
            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 4px;">
                {message}
            </div>
            {f'<div style="font-size: 0.9rem; color: #cc8888;">{details}</div>' if details else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_info_message(message: str, details: str = ""):
    """Display a professional info message"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(145deg, #0a1a2e 0%, #1a2e4d 100%);
        border: 1px solid #00ccff;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        color: #88ccff;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="font-size: 1.5rem;">ℹ️</div>
        <div>
            <div style="font-weight: 600; font-size: 1rem; margin-bottom: 4px;">
                {message}
            </div>
            {f'<div style="font-size: 0.9rem; color: #aaccdd;">{details}</div>' if details else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)