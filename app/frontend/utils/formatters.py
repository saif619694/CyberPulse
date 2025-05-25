import streamlit as st
from datetime import datetime
from typing import Dict, Any
import hashlib

def format_amount(amount: Any) -> str:
    """Format funding amount for display"""
    try:
        num_amount = int(float(amount)) if amount is not None else 0
        if num_amount >= 1000000000: 
            return f"${num_amount / 1000000000:.1f}B"
        if num_amount >= 1000000: 
            return f"${num_amount / 1000000:.1f}M"
        if num_amount >= 1000: 
            return f"${num_amount / 1000:.0f}K"
        if num_amount > 0: 
            return f"${num_amount:,}"
        return "Undisclosed"
    except (ValueError, TypeError): 
        return "Undisclosed"

def format_date(date_str: str) -> str:
    """Format date string for display"""
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%b %d, %Y")
    except:
        return date_str or "Unknown Date"

def get_round_color(round_name: str) -> str:
    """Get color for funding round badge with consistent mapping"""
    
    # Predefined colors for common rounds
    round_colors = {
        'pre-seed': '#f59e0b',
        'seed': '#10b981',
        'series a': '#3b82f6',
        'series b': '#8b5cf6',
        'series c': '#f97316',
        'series d': '#ec4899',
        'series e': '#14b8a6',
        'growth': '#84cc16',
        'late stage': '#ef4444',
        'ipo': '#f59e0b',
        'acquisition': '#06b6d4',
        'venture': '#ff0990',
        'equity crowdfunding': '#00fff2',
        'unknown': '#6b7280'
    }
    
    # Normalize the round name for lookup
    normalized_round = round_name.lower().strip()
    
    # Check for exact match first
    if normalized_round in round_colors:
        return round_colors[normalized_round]
    
    # Generate consistent color based on hash for unknown rounds
    hash_object = hashlib.md5(normalized_round.encode())
    hash_hex = hash_object.hexdigest()
    
    # Convert first 6 characters of hash to a color
    color = f"#{hash_hex[:6]}"
    
    # Ensure color is not too dark by adjusting brightness
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    
    # If color is too dark, lighten it
    if r + g + b < 200:
        r = min(255, r + 100)
        g = min(255, g + 100)
        b = min(255, b + 100)
        color = f"#{r:02x}{g:02x}{b:02x}"
    
    return color

def display_loading_animation():
    """Display professional loading animation"""
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

def display_message(message: str, message_type: str = "info", details: str = ""):
    """Display styled message with type"""
    
    message_configs = {
        "success": {
            "bg_color": "#065f46",
            "border_color": "#10b981",
            "text_color": "#10b981",
            "detail_color": "#6ee7b7",
            "icon": "✅"
        },
        "error": {
            "bg_color": "#7f1d1d",
            "border_color": "#ef4444",
            "text_color": "#ef4444",
            "detail_color": "#fca5a5",
            "icon": "❌"
        },
        "info": {
            "bg_color": "#1e3a8a",
            "border_color": "#3b82f6",
            "text_color": "#3b82f6",
            "detail_color": "#93bbfe",
            "icon": "ℹ️"
        },
        "warning": {
            "bg_color": "#92400e",
            "border_color": "#f59e0b",
            "text_color": "#f59e0b",
            "detail_color": "#fbbf24",
            "icon": "⚠️"
        }
    }
    
    config = message_configs.get(message_type, message_configs["info"])
    
    st.markdown(f"""
    <div style="
        background: {config['bg_color']};
        border: 1px solid {config['border_color']};
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        color: {config['text_color']};
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="font-size: 1.25rem;">{config['icon']}</div>
        <div>
            <div style="font-weight: 500;">
                {message}
            </div>
            {f'<div style="font-size: 0.875rem; color: {config["detail_color"]}; margin-top: 4px;">{details}</div>' if details else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Convenience functions for backward compatibility
def display_success_message(message: str, details: str = ""):
    display_message(message, "success", details)

def display_error_message(message: str, details: str = ""):
    display_message(message, "error", details)

def display_info_message(message: str, details: str = ""):
    display_message(message, "info", details)