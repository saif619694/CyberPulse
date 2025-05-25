# Sidebar functionality removed in new design
# All controls are now integrated into main app layout

def get_sidebar_state():
    """Get sidebar state for backwards compatibility"""
    return {
        'items_per_page': 12,
        'default_sort': 'date',
        'auto_refresh': False,
        'current_page': 'dashboard'
    }