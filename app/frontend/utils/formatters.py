import streamlit as st
from datetime import datetime
from typing import Dict, Any
import random

def format_amount(amount: Any) -> str:
    try:
        num_amount = float(amount) if amount is not None else 0
        num_amount = int(num_amount)
        if num_amount >= 1000000000: return f"${num_amount / 1000000000:.1f}B"
        if num_amount >= 1000000: return f"${num_amount / 1000000:.1f}M"
        if num_amount >= 1000: return f"${num_amount / 1000:.0f}K"
        if num_amount > 0: return f"${num_amount:,}"
        return "Undisclosed"
    except (ValueError, TypeError): return "Undisclosed"

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
        'Pre-seed': '#f59e0b',      # amber
        'Seed': '#10b981',          # green
        'Series A': '#3b82f6',      # blue
        'Series B': '#8b5cf6',      # purple
        'Series C': '#f97316',      # orange
        'Series D': '#ec4899',      # pink
        'Series E': '#14b8a6',      # teal
        'Growth': '#84cc16',        # lime
        'Late Stage': '#ef4444',    # red
        'IPO': '#f59e0b',           # yellow
        'Acquisition': '#06b6d4',   # cyan
        'Venture': "#ff0990",       # indigo
        'Equity Crowdfunding': "#00FFF2",

    }
    # Return random color if round name not found
    return colors.get(round_name, f'#{random.randint(0, 0xFFFFFF):06x}')

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
    ">
        <div style="
            width: 48px;
            height: 48px;
            border: 3px solid #1f2937;
            border-top: 3px solid #8b5cf6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
        <div style="
            color: #8b5cf6; 
            font-size: 1rem; 
            font-weight: 500;
        ">
            Loading intelligence data...
        </div>
    </div>
    
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def display_success_message(message: str, details: str = ""):
    """Display a professional success message"""
    st.markdown(f"""
    <div style="
        background: #065f46;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        color: #10b981;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="font-size: 1.25rem;">✅</div>
        <div>
            <div style="font-weight: 500;">
                {message}
            </div>
            {f'<div style="font-size: 0.875rem; color: #6ee7b7; margin-top: 4px;">{details}</div>' if details else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_error_message(message: str, details: str = ""):
    """Display a professional error message"""
    st.markdown(f"""
    <div style="
        background: #7f1d1d;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        color: #ef4444;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="font-size: 1.25rem;">❌</div>
        <div>
            <div style="font-weight: 500;">
                {message}
            </div>
            {f'<div style="font-size: 0.875rem; color: #fca5a5; margin-top: 4px;">{details}</div>' if details else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_info_message(message: str, details: str = ""):
    """Display a professional info message"""
    st.markdown(f"""
    <div style="
        background: #1e3a8a;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        color: #3b82f6;
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="font-size: 1.25rem;">ℹ️</div>
        <div>
            <div style="font-weight: 500;">
                {message}
            </div>
            {f'<div style="font-size: 0.875rem; color: #93bbfe; margin-top: 4px;">{details}</div>' if details else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)