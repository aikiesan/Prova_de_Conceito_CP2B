"""
Navigation components for CP2B Dashboard
Includes both sidebar navigation and WebGIS top navigation bar
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
        {"label": "📚 References", "key": "references"},
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
        },
        "references": {
            "title": "📚 Scientific References",
            "subtitle": "Comprehensive scientific bibliography and citations for biogas conversion factors",
            "show_filters": False,
            "default_view": "references"
        },
    }
    
    return configs.get(page, configs["dashboard"])


def render_webgis_navigation() -> Dict[str, Any]:
    """
    Renders a professional WebGIS-style top navigation bar
    Perfect for map-focused applications
    """
    
    # Inject WebGIS navigation CSS
    st.markdown("""
    <style>
    .webgis-nav-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 70px;
        background: linear-gradient(135deg, #2c5530 0%, #4a7c59 50%, #6b9b76 100%);
        box-shadow: 0 3px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        padding: 0 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 2px solid rgba(255,255,255,0.1);
    }
    
    .webgis-logo {
        display: flex;
        align-items: center;
        gap: 15px;
        color: white;
    }
    
    .webgis-logo-icon {
        font-size: 2rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }
    
    .webgis-logo-text {
        display: flex;
        flex-direction: column;
    }
    
    .webgis-logo-title {
        font-size: 1.4rem;
        font-weight: 700;
        line-height: 1;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .webgis-logo-subtitle {
        font-size: 0.75rem;
        opacity: 0.9;
        font-weight: 400;
        line-height: 1;
        margin-top: 2px;
    }
    
    .webgis-center-title {
        color: white;
        text-align: center;
        flex: 1;
        margin: 0 40px;
    }
    
    .webgis-center-title h1 {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        line-height: 1.2;
    }
    
    .webgis-center-title p {
        font-size: 0.8rem;
        opacity: 0.85;
        margin: 2px 0 0 0;
    }
    
    .webgis-controls {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .webgis-control-button {
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.25);
        color: white;
        padding: 10px 18px;
        border-radius: 25px;
        cursor: pointer;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.3s ease;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 8px;
        backdrop-filter: blur(10px);
    }
    
    .webgis-control-button:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .webgis-control-button.active {
        background: rgba(255,255,255,0.9);
        color: #2c5530;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    .webgis-info-badge {
        background: rgba(255,255,255,0.2);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    
    .webgis-separator {
        width: 1px;
        height: 35px;
        background: rgba(255,255,255,0.2);
        margin: 0 8px;
    }
    
    /* Adjust main content area */
    .stApp > div:first-child {
        padding-top: 70px;
    }
    
    .main .block-container {
        padding-top: 85px;
        padding-left: 0;
        padding-right: 0;
        max-width: 100%;
    }
    
    /* Hide default Streamlit header */
    .stApp > header[data-testid="stHeader"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get municipality count from session state
    muni_count = len(st.session_state.get('data', []))
    
    # Navigation HTML - simplified version to avoid rendering issues
    panel_active = "active" if st.session_state.get('show_panel', True) else ""
    zen_active = "active" if st.session_state.get('zen_mode', False) else ""
    
    nav_html = f"""
    <div class="webgis-nav-container">
        <div class="webgis-logo">
            <div class="webgis-logo-icon">🌱</div>
            <div class="webgis-logo-text">
                <div class="webgis-logo-title">CP2B WebGIS</div>
                <div class="webgis-logo-subtitle">Biogas Analysis Platform</div>
            </div>
        </div>
        
        <div class="webgis-center-title">
            <h1>Dashboard Potencial de Biogás - São Paulo</h1>
            <p>Sistema de Análise Geoespacial para Resíduos Orgânicos</p>
        </div>
        
        <div class="webgis-controls">
            <div class="webgis-info-badge">📊 {muni_count} Municípios</div>
            <div class="webgis-separator"></div>
            <div class="webgis-control-button {panel_active}" id="toggle-panel-btn">🎛️ Painel</div>
            <div class="webgis-control-button {zen_active}" id="toggle-zen-btn">🗺️ Zen Mode</div>
        </div>
    </div>
    """
    
    # Use standard markdown for reliable rendering
    st.markdown(nav_html, unsafe_allow_html=True)
    
    return {'webgis_nav_rendered': True}


def inject_webgis_styles():
    """
    Injects additional styles for full WebGIS experience
    """
    st.markdown("""
    <style>
    /* Full viewport WebGIS experience */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Map takes full available space */
    .streamlit-folium {
        width: 100% !important;
        height: calc(100vh - 70px) !important;
        border-radius: 0 !important;
    }
    
    /* Enhanced floating panels */
    .floating-panel {
        top: 90px;
        right: 25px;
        width: 400px;
        max-height: calc(100vh - 120px);
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        border-radius: 12px;
    }
    
    .floating-panel.hidden {
        transform: translateX(450px);
        opacity: 0;
    }
    
    /* Professional panel styling */
    .floating-panel-header {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        margin: -15px -15px 20px -15px;
        padding: 20px;
        border-radius: 12px 12px 0 0;
        border-bottom: 1px solid #e2e8f0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
    }
    
    /* Enhanced panel tabs */
    .panel-tabs {
        display: flex;
        margin-bottom: 20px;
        border-bottom: 2px solid #e2e8f0;
        gap: 5px;
    }
    
    .panel-tabs .tab {
        background: rgba(44, 85, 48, 0.08);
        color: #2c5530;
        border: 1px solid rgba(44, 85, 48, 0.15);
        padding: 12px 20px;
        border-radius: 8px 8px 0 0;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s;
        font-size: 0.9rem;
    }
    
    .panel-tabs .tab:hover {
        background: rgba(44, 85, 48, 0.15);
        transform: translateY(-1px);
    }
    
    .panel-tabs .tab.active {
        background: #2c5530;
        color: white;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(44, 85, 48, 0.3);
    }
    
    /* Remove the old toggle button */
    .panel-toggle-button {
        display: none;
    }
    
    /* Enhance metrics in panels */
    .stMetric {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    </style>
    """, unsafe_allow_html=True)