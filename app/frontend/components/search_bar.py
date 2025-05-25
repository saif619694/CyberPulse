import streamlit as st
from typing import List, Tuple, Optional

def display_search_filters(available_rounds: List[str], total_results: int) -> Tuple[str, str]:
    """Legacy search filters - functionality moved to main app"""
    return "", ""

def display_sort_controls() -> Tuple[str, str]:
    """Legacy sort controls - functionality moved to main app"""
    return "date", "desc"

def display_quick_filters(available_rounds: List[str]) -> Optional[str]:
    """Legacy quick filters - functionality moved to main app"""
    return None

def display_advanced_search():
    """Legacy advanced search - functionality moved to main app"""
    pass