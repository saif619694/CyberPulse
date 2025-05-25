import streamlit as st

def display_sidebar():
    """Sidebar disabled in new design"""
    pass

def display_navigation_menu():
    """Navigation disabled in new design"""
    pass

def display_api_status():
    """API status moved to main app"""
    pass

def display_quick_stats():
    """Stats moved to main app"""
    pass

def display_settings():
    """Settings moved to main app"""
    pass

def display_data_management():
    """Data management moved to main app"""
    pass

def display_footer():
    """Footer disabled in new design"""
    pass

def get_sidebar_state():
    """Get sidebar state"""
    return {
        'items_per_page': 12,
        'default_sort': 'date',
        'auto_refresh': False,
        'current_page': 'dashboard'
    }