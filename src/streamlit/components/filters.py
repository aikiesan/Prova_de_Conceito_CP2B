"""
Main content filter system for individual residue types and data filtering
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional

# Define all individual residue types with metadata
RESIDUE_TYPES = {
    # Agricultural residues
    'biogas_cana_nm_ano': {
        'label': 'Sugar Cane',
        'category': 'Agricultural', 
        'icon': '🌾',
        'description': 'Bagasse and straw from sugar cane',
        'unit': 'Nm³/ano'
    },
    'biogas_soja_nm_ano': {
        'label': 'Soybean',
        'category': 'Agricultural',
        'icon': '🌱', 
        'description': 'Residues from soybean cultivation',
        'unit': 'Nm³/ano'
    },
    'biogas_milho_nm_ano': {
        'label': 'Corn',
        'category': 'Agricultural',
        'icon': '🌽',
        'description': 'Residues from corn cultivation', 
        'unit': 'Nm³/ano'
    },
    'biogas_cafe_nm_ano': {
        'label': 'Coffee',
        'category': 'Agricultural',
        'icon': '☕',
        'description': 'Coffee pulp and husks',
        'unit': 'Nm³/ano'
    },
    'biogas_citros_nm_ano': {
        'label': 'Citrus',
        'category': 'Agricultural', 
        'icon': '🍊',
        'description': 'Residues from citrus fruits',
        'unit': 'Nm³/ano'
    },
    
    # Livestock residues
    'biogas_bovinos_nm_ano': {
        'label': 'Cattle',
        'category': 'Livestock',
        'icon': '🐄',
        'description': 'Cattle manure',
        'unit': 'Nm³/ano'
    },
    'biogas_suino_nm_ano': {
        'label': 'Swine',
        'category': 'Livestock',
        'icon': '🐷',
        'description': 'Swine manure',
        'unit': 'Nm³/ano'
    },
    'biogas_aves_nm_ano': {
        'label': 'Poultry',
        'category': 'Livestock',
        'icon': '🐔',
        'description': 'Poultry manure',
        'unit': 'Nm³/ano'
    },
    'biogas_piscicultura_nm_ano': {
        'label': 'Fish Farming',
        'category': 'Livestock',
        'icon': '🐟',
        'description': 'Fish farming residues',
        'unit': 'Nm³/ano'
    },
    
    # Urban residues
    'rsu_potencial_nm_habitante_ano': {
        'label': 'Municipal Solid Waste',
        'category': 'Urban',
        'icon': '🗑️',
        'description': 'Municipal solid waste',
        'unit': 'Nm³/habitant/ano'
    },
    'rpo_potencial_nm_habitante_ano': {
        'label': 'Organic Garden Waste',
        'category': 'Urban',
        'icon': '🍃',
        'description': 'Organic garden and pruning waste',
        'unit': 'Nm³/habitant/ano'
    },
    
    # Forestry
    'silvicultura_nm_ano': {
        'label': 'Forestry',
        'category': 'Forestry',
        'icon': '🌲',
        'description': 'Forestry residues',
        'unit': 'Nm³/ano'
    }
}

# Aggregate categories
AGGREGATE_TYPES = {
    'total_agricola_nm_ano': {
        'label': 'Total Agricultural',
        'category': 'Aggregate',
        'icon': '🌾',
        'description': 'All agricultural residues combined',
        'unit': 'Nm³/ano'
    },
    'total_pecuaria_nm_ano': {
        'label': 'Total Livestock', 
        'category': 'Aggregate',
        'icon': '🐄',
        'description': 'All livestock residues combined',
        'unit': 'Nm³/ano'
    },
    'total_final_nm_ano': {
        'label': 'Total All Sources',
        'category': 'Aggregate',
        'icon': '⚡',
        'description': 'Total potential from all sources',
        'unit': 'Nm³/ano'
    }
}

def render_residue_selector(key_prefix: str = "main") -> Dict[str, Any]:
    """
    Renders horizontal residue type selector
    Returns selected residue types and view mode
    """
    
    st.markdown("### 🎯 Select Residue Types")
    
    # View mode selection
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        view_mode = st.selectbox(
            "View Mode:",
            ["Individual Types", "By Category", "Aggregated", "Comparison"],
            key=f"{key_prefix}_view_mode",
            help="Choose how to display the data"
        )
    
    with col2:
        if view_mode == "By Category":
            selected_category = st.selectbox(
                "Category:",
                ["Agricultural", "Livestock", "Urban", "Forestry", "All"],
                key=f"{key_prefix}_category"
            )
        else:
            selected_category = "All"
    
    with col3:
        show_zero_values = st.checkbox(
            "Include zero values",
            value=False,
            key=f"{key_prefix}_show_zeros",
            help="Include municipalities with zero potential"
        )
    
    # Residue selection based on view mode
    selected_residues = []
    
    if view_mode == "Individual Types":
        selected_residues = render_individual_selector(key_prefix, selected_category)
    elif view_mode == "By Category":
        selected_residues = get_residues_by_category(selected_category)
    elif view_mode == "Aggregated":
        selected_residues = render_aggregate_selector(key_prefix)
    elif view_mode == "Comparison":
        selected_residues = render_comparison_selector(key_prefix)
    
    # Additional filters
    st.markdown("### 🔍 Additional Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_potential = st.number_input(
            "Min Potential (Nm³/ano):",
            min_value=0,
            value=0,
            step=1000,
            key=f"{key_prefix}_min_potential",
            help="Minimum total potential threshold"
        )
    
    with col2:
        max_results = st.selectbox(
            "Max Results:",
            [10, 25, 50, 100, 250, "All"],
            index=3,
            key=f"{key_prefix}_max_results",
            help="Limit number of results"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by:",
            ["Total Potential", "Municipality Name", "Selected Residue"],
            key=f"{key_prefix}_sort_by"
        )
    
    return {
        "view_mode": view_mode,
        "selected_category": selected_category, 
        "selected_residues": selected_residues,
        "show_zero_values": show_zero_values,
        "min_potential": min_potential,
        "max_results": max_results if max_results != "All" else None,
        "sort_by": sort_by
    }


def render_individual_selector(key_prefix: str, category: str = "All") -> List[str]:
    """Renders individual residue type selection"""
    
    # Filter residues by category if specified
    if category == "All":
        available_residues = RESIDUE_TYPES
    else:
        available_residues = {
            k: v for k, v in RESIDUE_TYPES.items() 
            if v['category'] == category
        }
    
    # Group by category for better organization
    categories = {}
    for residue, info in available_residues.items():
        cat = info['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((residue, info))
    
    selected_residues = []
    
    # Create expandable sections for each category
    for cat_name, residues in categories.items():
        with st.expander(f"{cat_name} Residues", expanded=True):
            cols = st.columns(min(3, len(residues)))
            
            for i, (residue_key, residue_info) in enumerate(residues):
                with cols[i % len(cols)]:
                    selected = st.checkbox(
                        f"{residue_info['icon']} {residue_info['label']}",
                        key=f"{key_prefix}_{residue_key}",
                        help=residue_info['description']
                    )
                    if selected:
                        selected_residues.append(residue_key)
    
    return selected_residues


def render_aggregate_selector(key_prefix: str) -> List[str]:
    """Renders aggregate type selection"""
    
    selected_residues = []
    
    st.markdown("**Select aggregate views:**")
    cols = st.columns(len(AGGREGATE_TYPES))
    
    for i, (agg_key, agg_info) in enumerate(AGGREGATE_TYPES.items()):
        with cols[i]:
            selected = st.checkbox(
                f"{agg_info['icon']} {agg_info['label']}",
                key=f"{key_prefix}_{agg_key}",
                help=agg_info['description']
            )
            if selected:
                selected_residues.append(agg_key)
    
    return selected_residues


def render_comparison_selector(key_prefix: str) -> List[str]:
    """Renders comparison mode selection"""
    
    st.markdown("**Select up to 4 residue types to compare:**")
    
    # Create a list of all available residues
    all_residues = {**RESIDUE_TYPES, **AGGREGATE_TYPES}
    
    selected_residues = []
    
    for i in range(4):
        residue_options = ["None"] + [f"{info['icon']} {info['label']}" for info in all_residues.values()]
        
        selected = st.selectbox(
            f"Comparison {i+1}:",
            residue_options,
            key=f"{key_prefix}_compare_{i}",
            index=0
        )
        
        if selected != "None":
            # Find the residue key from the label
            for res_key, res_info in all_residues.items():
                if f"{res_info['icon']} {res_info['label']}" == selected:
                    selected_residues.append(res_key)
                    break
    
    return selected_residues


def get_residues_by_category(category: str) -> List[str]:
    """Returns list of residue keys for a specific category"""
    if category == "All":
        return list(RESIDUE_TYPES.keys()) + list(AGGREGATE_TYPES.keys())
    elif category == "Aggregate":
        return list(AGGREGATE_TYPES.keys())
    else:
        return [k for k, v in RESIDUE_TYPES.items() if v['category'] == category]


def apply_residue_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies residue-based filters to the dataframe
    """
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    # Filter by minimum potential
    if filters.get("min_potential", 0) > 0:
        # Use total_final_nm_ano as the threshold column
        filtered_df = filtered_df[filtered_df["total_final_nm_ano"] >= filters["min_potential"]]
    
    # Filter by zero values
    if not filters.get("show_zero_values", False):
        # Remove municipalities where all selected residues are zero
        if filters.get("selected_residues"):
            residue_columns = [r for r in filters["selected_residues"] if r in filtered_df.columns]
            if residue_columns:
                # Keep rows where at least one selected residue > 0
                mask = (filtered_df[residue_columns] > 0).any(axis=1)
                filtered_df = filtered_df[mask]
        else:
            # Default: filter by total potential
            filtered_df = filtered_df[filtered_df["total_final_nm_ano"] > 0]
    
    # Sort results
    sort_column = "total_final_nm_ano"  # Default
    if filters.get("sort_by") == "Municipality Name":
        sort_column = "nm_mun"
    elif filters.get("sort_by") == "Selected Residue" and filters.get("selected_residues"):
        # Sort by first selected residue
        first_residue = filters["selected_residues"][0]
        if first_residue in filtered_df.columns:
            sort_column = first_residue
    
    ascending = True if sort_column == "nm_mun" else False
    filtered_df = filtered_df.sort_values(sort_column, ascending=ascending)
    
    # Limit results
    if filters.get("max_results"):
        filtered_df = filtered_df.head(filters["max_results"])
    
    # Set display_value based on selected residue type for map visualization
    selected_residues = filters.get("selected_residues", [])
    if len(selected_residues) == 1 and selected_residues[0] in filtered_df.columns:
        # Single residue selected - use that column for display
        filtered_df['display_value'] = filtered_df[selected_residues[0]]
    elif filters.get("view_mode") == "Agricultural":
        filtered_df['display_value'] = filtered_df.get('total_agricola_nm_ano', filtered_df['total_final_nm_ano'])
    elif filters.get("view_mode") == "Livestock":
        filtered_df['display_value'] = filtered_df.get('total_pecuaria_nm_ano', filtered_df['total_final_nm_ano'])
    elif filters.get("view_mode") == "Urban":
        # Sum urban sources
        urban_cols = ['rsu_potencial_nm_habitante_ano', 'rpo_potencial_nm_habitante_ano']
        urban_total = 0
        for col in urban_cols:
            if col in filtered_df.columns:
                urban_total += filtered_df[col].fillna(0)
        filtered_df['display_value'] = urban_total
    else:
        # Default to total potential
        filtered_df['display_value'] = filtered_df['total_final_nm_ano']
    
    return filtered_df


def get_residue_info(residue_key: str) -> Dict[str, str]:
    """Returns metadata for a residue type"""
    all_residues = {**RESIDUE_TYPES, **AGGREGATE_TYPES}
    return all_residues.get(residue_key, {
        'label': residue_key,
        'category': 'Unknown',
        'icon': '❓',
        'description': 'Unknown residue type',
        'unit': 'Nm³/ano'
    })