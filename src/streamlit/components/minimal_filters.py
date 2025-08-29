"""
Minimal filter interface that doesn't interfere with map visibility
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
try:
    from .filters import RESIDUE_TYPES, AGGREGATE_TYPES, apply_residue_filters
except ImportError:
    from components.filters import RESIDUE_TYPES, AGGREGATE_TYPES, apply_residue_filters


def render_minimal_filters(key_prefix: str = "main", show_in_sidebar: bool = False) -> Dict[str, Any]:
    """
    Renders minimal, non-intrusive filters
    """
    
    if show_in_sidebar:
        container = st.sidebar
        container.markdown("## 🎯 Quick Filters")
    else:
        # Create a collapsible expander in main content
        with st.expander("🎯 **Filters & Options**", expanded=False):
            container = st
    
    # Quick residue type selection
    container.markdown("**Select Data to Display:**")
    
    col1, col2, col3 = container.columns(3)
    
    with col1:
        view_mode = container.selectbox(
            "View:",
            ["All Sources", "Agricultural", "Livestock", "Urban", "Individual"],
            key=f"{key_prefix}_quick_view",
            help="Quick view selection"
        )
    
    with col2:
        show_zeros = container.checkbox(
            "Include zeros",
            value=False,
            key=f"{key_prefix}_zeros",
            help="Include municipalities with zero potential"
        )
    
    with col3:
        max_results = container.selectbox(
            "Limit:",
            [50, 100, 250, "All"],
            index=1,
            key=f"{key_prefix}_limit"
        )
    
    # Individual residue selection (only if Individual mode)
    selected_residues = []
    if view_mode == "Individual":
        container.markdown("**Choose Specific Residues:**")
        
        # Quick buttons for common residues
        col1, col2, col3 = container.columns(3)
        
        with col1:
            container.markdown("*Agricultural:*")
            if container.checkbox("🌾 Sugar Cane", key=f"{key_prefix}_cana"):
                selected_residues.append('biogas_cana_nm_ano')
            if container.checkbox("🌱 Soybean", key=f"{key_prefix}_soja"):
                selected_residues.append('biogas_soja_nm_ano')
            if container.checkbox("🌽 Corn", key=f"{key_prefix}_milho"):
                selected_residues.append('biogas_milho_nm_ano')
        
        with col2:
            container.markdown("*Livestock:*")
            if container.checkbox("🐄 Cattle", key=f"{key_prefix}_bovinos"):
                selected_residues.append('biogas_bovinos_nm_ano')
            if container.checkbox("🐷 Swine", key=f"{key_prefix}_suino"):
                selected_residues.append('biogas_suino_nm_ano')
            if container.checkbox("🐔 Poultry", key=f"{key_prefix}_aves"):
                selected_residues.append('biogas_aves_nm_ano')
        
        with col3:
            container.markdown("*Urban:*")
            if container.checkbox("🗑️ Municipal Waste", key=f"{key_prefix}_rsu"):
                selected_residues.append('rsu_potencial_nm_habitante_ano')
            if container.checkbox("🍃 Garden Waste", key=f"{key_prefix}_rpo"):
                selected_residues.append('rpo_potencial_nm_habitante_ano')
    
    # Convert view mode to residue list
    elif view_mode == "Agricultural":
        selected_residues = ['total_agricola_nm_ano']
    elif view_mode == "Livestock":
        selected_residues = ['total_pecuaria_nm_ano']
    elif view_mode == "Urban":
        selected_residues = ['rsu_potencial_nm_habitante_ano', 'rpo_potencial_nm_habitante_ano']
    else:  # All Sources
        selected_residues = ['total_final_nm_ano']
    
    return {
        "view_mode": view_mode,
        "selected_residues": selected_residues,
        "show_zero_values": show_zeros,
        "max_results": max_results if max_results != "All" else None,
        "min_potential": 0,
        "sort_by": "Total Potential"
    }


def render_floating_filter_controls() -> Dict[str, Any]:
    """
    Renders floating filter controls that don't take up main space
    """
    
    # Create columns for horizontal layout
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        # Quick category selector as buttons
        st.markdown("**Quick Select:**")
        
        # Create button row
        btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)
        
        selected_view = "All Sources"  # default
        
        with btn_col1:
            if st.button("🌾 Agricultural", help="Show agricultural residues"):
                selected_view = "Agricultural"
        with btn_col2:
            if st.button("🐄 Livestock", help="Show livestock residues"):
                selected_view = "Livestock"
        with btn_col3:
            if st.button("🗑️ Urban", help="Show urban waste"):
                selected_view = "Urban"
        with btn_col4:
            if st.button("⚡ All Sources", help="Show total potential"):
                selected_view = "All Sources"
        with btn_col5:
            if st.button("🔧 Custom", help="Custom selection"):
                selected_view = "Individual"
    
    with col2:
        show_zeros = st.checkbox("Include zeros", value=False, help="Include zero potential")
    
    with col3:
        max_results = st.selectbox("Results:", [50, 100, 250, "All"], index=1)
    
    with col4:
        sort_order = st.selectbox("Sort:", ["Highest first", "Lowest first", "A-Z"], index=0)
    
    with col5:
        if st.button("🔄", help="Refresh data"):
            st.cache_data.clear()
            st.rerun()
    
    # Store selection in session state
    st.session_state.quick_filter_view = selected_view
    
    # Convert to filter format
    selected_residues = []
    if selected_view == "Agricultural":
        selected_residues = ['total_agricola_nm_ano']
    elif selected_view == "Livestock":
        selected_residues = ['total_pecuaria_nm_ano']
    elif selected_view == "Urban":
        selected_residues = ['rsu_potencial_nm_habitante_ano', 'rpo_potencial_nm_habitante_ano']
    elif selected_view == "Individual":
        # Show expanded selection in sidebar or modal
        pass
    else:  # All Sources
        selected_residues = ['total_final_nm_ano']
    
    return {
        "view_mode": selected_view,
        "selected_residues": selected_residues,
        "show_zero_values": show_zeros,
        "max_results": max_results if max_results != "All" else None,
        "sort_by": "Total Potential",
        "sort_ascending": sort_order != "Highest first"
    }


def render_sidebar_filters(key_prefix: str = "sidebar") -> Dict[str, Any]:
    """
    Renders filters in sidebar without taking main content space
    """
    
    st.sidebar.markdown("## 🎯 Data Filters")
    
    # View mode
    view_mode = st.sidebar.selectbox(
        "**Data to Display:**",
        ["All Sources", "Agricultural", "Livestock", "Urban", "Individual Types"],
        key=f"{key_prefix}_view",
        help="Select which type of data to show on the map"
    )
    
    # Individual selection for Individual Types mode
    selected_residues = []
    if view_mode == "Individual Types":
        st.sidebar.markdown("**Select Residues:**")
        
        # Agricultural
        with st.sidebar.expander("🌾 Agricultural", expanded=False):
            if st.checkbox("Sugar Cane", key=f"{key_prefix}_cana"):
                selected_residues.append('biogas_cana_nm_ano')
            if st.checkbox("Soybean", key=f"{key_prefix}_soja"):
                selected_residues.append('biogas_soja_nm_ano')
            if st.checkbox("Corn", key=f"{key_prefix}_milho"):
                selected_residues.append('biogas_milho_nm_ano')
            if st.checkbox("Coffee", key=f"{key_prefix}_cafe"):
                selected_residues.append('biogas_cafe_nm_ano')
            if st.checkbox("Citrus", key=f"{key_prefix}_citros"):
                selected_residues.append('biogas_citros_nm_ano')
        
        # Livestock
        with st.sidebar.expander("🐄 Livestock", expanded=False):
            if st.checkbox("Cattle", key=f"{key_prefix}_bovinos"):
                selected_residues.append('biogas_bovinos_nm_ano')
            if st.checkbox("Swine", key=f"{key_prefix}_suino"):
                selected_residues.append('biogas_suino_nm_ano')
            if st.checkbox("Poultry", key=f"{key_prefix}_aves"):
                selected_residues.append('biogas_aves_nm_ano')
            if st.checkbox("Fish Farming", key=f"{key_prefix}_piscicultura"):
                selected_residues.append('biogas_piscicultura_nm_ano')
        
        # Urban
        with st.sidebar.expander("🗑️ Urban", expanded=False):
            if st.checkbox("Municipal Waste", key=f"{key_prefix}_rsu"):
                selected_residues.append('rsu_potencial_nm_habitante_ano')
            if st.checkbox("Garden Waste", key=f"{key_prefix}_rpo"):
                selected_residues.append('rpo_potencial_nm_habitante_ano')
        
        # Forestry
        with st.sidebar.expander("🌲 Forestry", expanded=False):
            if st.checkbox("Forestry", key=f"{key_prefix}_silvicultura"):
                selected_residues.append('silvicultura_nm_ano')
    
    else:
        # Convert view mode to residue list
        if view_mode == "Agricultural":
            selected_residues = ['total_agricola_nm_ano']
        elif view_mode == "Livestock":
            selected_residues = ['total_pecuaria_nm_ano']
        elif view_mode == "Urban":
            selected_residues = ['rsu_potencial_nm_habitante_ano', 'rpo_potencial_nm_habitante_ano']
        else:  # All Sources
            selected_residues = ['total_final_nm_ano']
    
    st.sidebar.markdown("---")
    
    # Additional options
    st.sidebar.markdown("**Display Options:**")
    
    show_zeros = st.sidebar.checkbox(
        "Include zero values",
        value=False,
        key=f"{key_prefix}_zeros",
        help="Show municipalities with zero biogas potential"
    )
    
    max_results = st.sidebar.selectbox(
        "Maximum results:",
        [25, 50, 100, 250, "All"],
        index=2,
        key=f"{key_prefix}_max",
        help="Limit number of municipalities shown"
    )
    
    min_potential = st.sidebar.number_input(
        "Minimum potential (Nm³/ano):",
        min_value=0,
        value=0,
        step=1000,
        key=f"{key_prefix}_min_pot",
        help="Filter by minimum biogas potential"
    )
    
    return {
        "view_mode": view_mode,
        "selected_residues": selected_residues,
        "show_zero_values": show_zeros,
        "max_results": max_results if max_results != "All" else None,
        "min_potential": min_potential,
        "sort_by": "Total Potential",
        "display_column": selected_residues[0] if len(selected_residues) == 1 else "total_final_nm_ano"
    }