"""
Simple page navigation sidebar for CP2B Dashboard
"""

import streamlit as st
from typing import Dict, Any

def render_navigation_sidebar() -> str:
    """
    Renders expanded navigation sidebar with page selection and filters
    Returns the selected page
    """
    
    st.sidebar.markdown("# 🌱 CP2B Dashboard")
    st.sidebar.markdown("*Sistema de Análise Geoespacial para Biogás*")
    
    st.sidebar.markdown("---")
    
    # Page navigation with clickable buttons
    st.sidebar.markdown("## 📍 Navigation")
    
    pages = [
        {"label": "🏠 Dashboard", "key": "dashboard"},
        {"label": "🎯 Simulations", "key": "simulations"}, 
        {"label": "📈 Analysis", "key": "analysis"},
        {"label": "📋 Data Explorer", "key": "data"},
        {"label": "🔧 Debug", "key": "debug"}
    ]
    
    # Get current page from session state, default to dashboard
    current_page = st.session_state.get('current_page', 'dashboard')
    
    # Create navigation buttons
    selected_page = current_page  # Default to current
    
    for page in pages:
        # Highlight current page button
        is_current = (page["key"] == current_page)
        button_type = "primary" if is_current else "secondary"
        
        if st.sidebar.button(
            page["label"], 
            key=f"nav_{page['key']}", 
            use_container_width=True,
            type=button_type
        ):
            selected_page = page["key"]
            st.session_state.current_page = selected_page
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Quick stats with better formatting
    if st.session_state.get('data_loaded', False):
        st.sidebar.markdown("## 📊 Data Overview")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if hasattr(st.session_state, 'total_municipalities'):
                st.sidebar.metric(
                    "🏛️ Total Municipalities", 
                    st.session_state.total_municipalities,
                    help="All municipalities in São Paulo state"
                )
        
        if hasattr(st.session_state, 'total_potential'):
            potential_millions = st.session_state.total_potential / 1_000_000
            st.sidebar.metric(
                "⚡ Total Biogas Potential", 
                f"{potential_millions:.1f}M Nm³/ano",
                help="Combined potential from all residue types"
            )
        
        # Show filtered data stats if available
        if hasattr(st.session_state, 'filtered_count'):
            st.sidebar.metric(
                "🔍 Filtered Results",
                st.session_state.filtered_count,
                help="Municipalities matching current filters"
            )
    
    st.sidebar.markdown("---")
    
    # System controls with better organization  
    st.sidebar.markdown("## ⚙️ System Controls")
    
    # Note: Data filters moved to map interface for better UX
    
    # Theme toggle
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    dark_mode = st.sidebar.toggle(
        "🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode",
        value=st.session_state.dark_mode,
        help="Toggle between dark and light themes"
    )
    
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    # Debug mode
    debug_mode = st.sidebar.checkbox(
        "🔧 Debug Mode", 
        key="global_debug", 
        help="Show technical information and detailed error messages"
    )
    st.session_state.show_debug = debug_mode
    
    # System actions
    st.sidebar.markdown("### System Actions")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button("🔄 Refresh Data", help="Reload data from database", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.sidebar.button("🗂️ Clear Cache", help="Clear all cached data", use_container_width=True):
            try:
                from utils.database import clear_cache
                st.cache_data.clear()
                clear_cache()
                st.sidebar.success("Cache cleared!")
            except:
                st.sidebar.error("Error clearing cache")
    
    # Show cache stats in debug mode
    if debug_mode:
        st.sidebar.markdown("### 🔧 Debug Info")
        try:
            from utils.database import get_cache_stats
            stats = get_cache_stats()
            st.sidebar.json(stats)
        except:
            st.sidebar.warning("Cache stats unavailable")
    
    st.sidebar.markdown("---")
    
    # Footer info
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em; margin-top: 2rem;'>
        <p>CP2B Dashboard v2.0<br>
        São Paulo Biogas Analysis Platform</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    return selected_page


def get_page_config(page: str) -> Dict[str, Any]:
    """
    Returns configuration for each page
    """
    configs = {
        "dashboard": {
            "title": "🏠 Executive Dashboard",
            "subtitle": "Overview of biogas potential across São Paulo municipalities",
            "show_filters": True,
            "default_view": "overview"
        },
        "simulations": {
            "title": "🎯 Scenario Simulations", 
            "subtitle": "Model different scenarios and their impact on biogas potential",
            "show_filters": True,
            "default_view": "simulation"
        },
        "analysis": {
            "title": "📈 Detailed Analysis",
            "subtitle": "Deep dive into individual residue types and comparative analysis", 
            "show_filters": True,
            "default_view": "analysis"
        },
        "data": {
            "title": "📋 Data Explorer",
            "subtitle": "Explore and export raw data with advanced filtering",
            "show_filters": True,
            "default_view": "table"
        },
        "debug": {
            "title": "🔧 Debug & System Info",
            "subtitle": "Technical information and troubleshooting",
            "show_filters": False,
            "default_view": "debug"
        }
    }
    
    return configs.get(page, configs["dashboard"])