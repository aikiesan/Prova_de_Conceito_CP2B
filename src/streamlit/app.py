# app.py - Enhanced WebGIS Application

import streamlit as st
import pandas as pd
import logging
from datetime import datetime

# --- 1. IMPORTS ---
from utils.styling import inject_custom_css
from utils.database import initialize_database, MunicipalQueries
from components.control_panel import render_control_panel, render_search_panel, render_analysis_panel
from components.maps import render_map
from components.navigation import render_webgis_navigation, inject_webgis_styles

# CP2B MCDA Imports
from components.mcda import (
    load_cp2b_complete_database,
    load_mcda_geoparquet_by_radius,
    get_property_details,
    get_mcda_summary_stats_by_radius,
    initialize_cp2b_session_state,
    render_mcda_map,
    render_mcda_map_sidebar,
    apply_mcda_filters,
    load_properties_geoparquet,
    load_properties_geoparquet_by_radius,
    render_interactive_mcda_map,
    render_property_report_page,
    MCDA_SCENARIOS
)

# --- 2. PAGE CONFIGURATION & INITIALIZATION ---
st.set_page_config(page_title="CP2B Dashboard", page_icon="🌱", layout="wide")

# Initialize session state FIRST
def initialize_session_state():
    """Initializes all session state variables."""
    defaults = {
        'data': pd.DataFrame(), 'data_loaded': False, 'selection_mode': 'Individual',
        'selected_residues': ['total_final_nm_ano'], 'max_municipalities': 500,
        'show_zero_values': False, 'layer_controls': {'limite_sp': True, 'municipalities': True},
        'radius_analysis_active': False, 'radius_km': 50, 'zen_mode': False,
        'selected_municipality_code': None, 'highlight_codes': None,
        'radius_analysis_center': None, 'radius_analysis_results': None,
        'map_center': [-22.5, -48.5], 'map_zoom': 7, 'show_panel': True,
        'active_panel': 'search',  # 'search', 'filters', 'analysis'
        'search_query': '', 'search_results': [],
        'analysis_type': 'comparison', 'comparison_municipalities': [],
        'temporal_years': [2020, 2021, 2022], 'cluster_count': 5,
        'map_layers': {'base_map': 'OpenStreetMap', 'heatmap': False, 'clusters': False},
        # New navigation state
        'current_page': 'dashboard',  # 'dashboard', 'analysis', 'simulation'
        'current_view': 'overview'    # Different for each page
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Initialize session state before using it
initialize_session_state()

# CP2B MCDA session state will be initialized only when needed

# Enhanced full-width header and navigation
st.markdown("""
<style>
/* Hide Streamlit's default header and make full width */
.stApp > header {
    display: none;
}
.main > div {
    padding-top: 0rem;
    padding-left: 0rem;
    padding-right: 0rem;
}
.block-container {
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
    max-width: 100%;
}
.streamlit-folium {
    border-radius: 0 !important;
}

/* Header overlays sidebar for prominence */
.stApp > div:first-child {
    z-index: 10001;
    position: relative;
}

/* Enhanced layer toggle styles */
.stCheckbox {
    margin-bottom: 4px;
}

.stCheckbox > div {
    display: flex;
    align-items: center;
    padding: 6px 8px;
    border-radius: 6px;
    transition: all 0.2s ease;
    border: 1px solid transparent;
}

.stCheckbox > div:hover {
    background-color: rgba(44, 85, 48, 0.05);
    border: 1px solid rgba(44, 85, 48, 0.1);
}

.stCheckbox > div[data-checked="true"] {
    background-color: rgba(44, 85, 48, 0.1);
    border: 1px solid rgba(44, 85, 48, 0.2);
}

.stCheckbox label {
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #2c5530 !important;
}

/* Sidebar styling - ensure scrollability */
.stSidebar > div {
    padding-top: 80px;
    max-height: 100vh;
    overflow-y: auto;
}

.stSidebar .stMarkdown h2 {
    font-size: 1.1rem;
    margin-top: 0;
    color: #2c5530;
}

.stSidebar .stMarkdown h3 {
    font-size: 0.9rem;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    color: #4a5568;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
}

/* Remove white space below content */
.main .block-container {
    padding-bottom: 0rem;
    margin-bottom: 0rem;
}

.stApp {
    margin: 0;
    padding: 0;
}

/* Ensure map takes full height */
.streamlit-folium {
    min-height: calc(100vh - 150px) !important;
}

/* Floating menu styles */
.floating-menu {
    position: fixed;
    top: 140px;
    left: 20px;
    width: 320px;
    max-height: calc(100vh - 160px);
    overflow-y: auto;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    padding: 20px;
    transition: all 0.3s ease;
}

.floating-menu.hidden {
    transform: translateX(-350px);
    opacity: 0;
}

.menu-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c5530;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e2e8f0;
}
</style>

<div style='background: linear-gradient(135deg, #2c5530 0%, #4a7c59 100%); 
     color: white; padding: 45px 0; margin: -1rem -1rem 0rem -1rem;'>
    <div style='max-width: 1200px; margin: 0 auto; padding: 25px 20px 0 20px; text-align: center;'>
        <h1 style='margin: 0; font-size: 1.8rem; font-weight: 700;'>🌱 CP2B WebGIS Dashboard</h1>
        <p style='margin: 4px 0 0 0; opacity: 0.9; font-size: 1rem;'>
            Potencial de Biogás - Estado de São Paulo • Sistema de Análise Geoespacial
        </p>
    </div>
</div>

<div style='background: rgba(44, 85, 48, 0.1); border-bottom: 2px solid rgba(44, 85, 48, 0.2); 
     padding: 12px 0; margin: 0rem -1rem 1.5rem -1rem;'>
    <div style='max-width: 1200px; margin: 0 auto; padding: 0 20px;'>
""", unsafe_allow_html=True)

# Navigation buttons in contained layout
col1, col2, col3, col4, col5, col6 = st.columns([1.3, 1.3, 1.3, 1.3, 1.3, 4.5])

with col1:
    dashboard_type = "primary" if st.session_state.get('current_page', 'dashboard') == "dashboard" else "secondary"
    if st.button("🗺️ Mapa Principal", use_container_width=True, type=dashboard_type):
        st.session_state.current_page = "dashboard"
        st.session_state.current_view = "overview"
        st.rerun()

with col2:
    analysis_type = "primary" if st.session_state.get('current_page', 'dashboard') == "analysis" else "secondary"
    if st.button("🔬 Análise Detalhada", use_container_width=True, type=analysis_type):
        st.session_state.current_page = "analysis"
        st.session_state.current_view = "overview"
        st.rerun()

with col3:
    simulation_type = "primary" if st.session_state.get('current_page', 'dashboard') == "simulation" else "secondary"
    if st.button("🌱 Simulações", use_container_width=True, type=simulation_type):
        st.session_state.current_page = "simulation"
        st.session_state.current_view = "scenarios"
        st.rerun()

with col4:
    mcda_type = "primary" if st.session_state.get('current_page', 'dashboard') == "mcda" else "secondary"
    if st.button("🎯 MCDA-RMC", use_container_width=True, type=mcda_type):
        st.session_state.current_page = "mcda"
        st.session_state.current_view = "map"
        st.rerun()

with col5:
    # Show current active page
    current_page = st.session_state.get('current_page', 'dashboard')
    page_names = {
        'dashboard': '🗺️ Mapa',
        'analysis': '🔬 Análise', 
        'simulation': '🌱 Simulação',
        'mcda': '🎯 MCDA'
    }
    st.markdown(f'<div style="padding: 8px; text-align: center; background: rgba(44, 85, 48, 0.1); border-radius: 6px; color: #2c5530; font-weight: 600;">{page_names.get(current_page, "🗺️ Mapa")} Ativo</div>', unsafe_allow_html=True)

with col6:
    # Get the actual count from loaded data
    muni_count = len(st.session_state.data) if hasattr(st.session_state, 'data') and not st.session_state.data.empty else 0
    st.markdown(f"""
    <div style='padding: 8px 0; text-align: right; color: #4a5568; font-size: 0.9rem;'>
        📊 {muni_count} Municípios Carregados
    </div>
    """, unsafe_allow_html=True)

# Close the navigation container
st.markdown("</div></div>", unsafe_allow_html=True)

# Add sub-navigation based on current page
current_page = st.session_state.get('current_page', 'dashboard')

if current_page == 'analysis':
    st.markdown("### 🔬 Análise Detalhada por Resíduos")
    analysis_cols = st.columns(5)
    
    with analysis_cols[0]:
        if st.button("📊 Visão Geral", use_container_width=True, 
                    type="primary" if st.session_state.get('current_view') == "overview" else "secondary"):
            st.session_state.current_view = "overview"
            st.rerun()
    
    with analysis_cols[1]:
        if st.button("🔬 Comparação Detalhada", use_container_width=True,
                    type="primary" if st.session_state.get('current_view') == "comparison" else "secondary"):
            st.session_state.current_view = "comparison"
            st.rerun()
    
    with analysis_cols[2]:
        if st.button("🗺️ Distribuição Geográfica", use_container_width=True,
                    type="primary" if st.session_state.get('current_view') == "geographic" else "secondary"):
            st.session_state.current_view = "geographic"
            st.rerun()
    
    with analysis_cols[3]:
        if st.button("🔗 Análise de Correlação", use_container_width=True,
                    type="primary" if st.session_state.get('current_view') == "correlation" else "secondary"):
            st.session_state.current_view = "correlation"
            st.rerun()
    
    with analysis_cols[4]:
        if st.button("📈 Visualizações Avançadas", use_container_width=True,
                    type="primary" if st.session_state.get('current_view') == "advanced_viz" else "secondary"):
            st.session_state.current_view = "advanced_viz"
            st.rerun()

elif current_page == 'simulation':
    st.markdown("### 🌱 Simulações Avançadas - Laboratório de Experimentação")
    sim_cols = st.columns(4)
    
    with sim_cols[0]:
        if st.button("🔬 Combinações de Substratos", use_container_width=True,
                    type="primary" if st.session_state.get('current_view') == "substrate_combinations" else "secondary"):
            st.session_state.current_view = "substrate_combinations"
            st.rerun()
    
    with sim_cols[1]:
        if st.button("🗺️ Hotspots Regionais", use_container_width=True,
                    type="primary" if st.session_state.get('current_view') == "regional_hotspots" else "secondary"):
            st.session_state.current_view = "regional_hotspots"
            st.rerun()
    
    with sim_cols[2]:
        if st.button("📊 Cenários Personalizados", use_container_width=True,
                    type="primary" if st.session_state.get('current_view') == "custom_scenarios" else "secondary"):
            st.session_state.current_view = "custom_scenarios"
            st.rerun()
    
    with sim_cols[3]:
        if st.button("🎯 Análise de Sinergia", use_container_width=True,
                    type="primary" if st.session_state.get('current_view') == "synergy_analysis" else "secondary"):
            st.session_state.current_view = "synergy_analysis"
            st.rerun()

# Add some spacing
st.markdown("---")

# Original styling (keeping for compatibility)
inject_custom_css()
initialize_database()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONSTANTS ---
RESIDUE_OPTIONS = {
    "⚡ Potencial Total": "total_final_nm_ano", "🌾 Total Agrícola": "total_agricola_nm_ano",
    "🐄 Total Pecuária": "total_pecuaria_nm_ano", "🗑️ Resíduos Urbanos": "urban_combined",
    "🌾 Cana-de-açúcar": "biogas_cana_nm_ano", "🌱 Soja": "biogas_soja_nm_ano",
    "🌽 Milho": "biogas_milho_nm_ano", "☕ Café": "biogas_cafe_nm_ano",
    "🍊 Citros": "biogas_citros_nm_ano", "🐄 Bovinos": "biogas_bovinos_nm_ano",
    "🐷 Suínos": "biogas_suino_nm_ano", "🐔 Aves": "biogas_aves_nm_ano",
    "🐟 Piscicultura": "biogas_piscicultura_nm_ano", "🗑️ RSU (Municipal)": "rsu_potencial_nm_habitante_ano",
    "🍃 RPO (Jardim/Poda)": "rpo_potencial_nm_habitante_ano", "🌲 Silvicultura": "silvicultura_nm_ano"
}

ANALYSIS_TYPES = {
    "📊 Comparação entre Municípios": "comparison",
    "📈 Tendência Temporal": "temporal",
    "🧮 Análise de Cluster": "cluster",
    "📋 Relatório Detalhado": "report"
}

# Session state already initialized above

# --- 4. DATA LOADING ---
@st.cache_data
def load_data():
    """Loads the main municipal dataframe."""
    logger.info("Cache miss. Loading municipal data from database...")
    try:
        df = MunicipalQueries.get_all_municipalities()
        if df is not None and not df.empty:
            logger.info(f"Successfully loaded {len(df)} municipalities.")
            # Add additional calculated fields if needed
            df['total_urban_nm_ano'] = df.get('rsu_potencial_nm_habitante_ano', 0) + df.get('rpo_potencial_nm_habitante_ano', 0)
            return df
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
    return pd.DataFrame()

# --- 5. HELPER FUNCTIONS ---
def apply_dashboard_filters(df: pd.DataFrame, state: st.session_state) -> pd.DataFrame:
    """Apply filters to the dataframe based on control panel selections."""
    if df is None or df.empty: 
        return pd.DataFrame()
    
    df_filtered = df.copy()
    
    # Apply residue selection
    if state.selection_mode == "Múltiplos" and len(state.selected_residues) > 1:
        df_filtered['display_value'] = df_filtered[state.selected_residues].sum(axis=1)
    else:
        residue = state.selected_residues[0] if state.selected_residues else 'total_final_nm_ano'
        df_filtered['display_value'] = df_filtered[residue]
    
    # Filter zero values if needed
    if not state.show_zero_values:
        df_filtered = df_filtered[df_filtered['display_value'] > 0]
    
    # Apply search filter if there's a query
    if state.search_query:
        search_lower = state.search_query.lower()
        df_filtered = df_filtered[
            df_filtered.get('nome_municipio', df_filtered.get('NOME_MUNICIPIO', df_filtered.get('municipio', pd.Series([''])))).astype(str).str.lower().str.contains(search_lower) |
            df_filtered['cd_mun'].astype(str).str.contains(search_lower)
        ]
        # Get municipality name column dynamically
        name_col = None
        for col in ['nome_municipio', 'NOME_MUNICIPIO', 'municipio']:
            if col in df_filtered.columns:
                name_col = col
                break
        
        if name_col:
            state.search_results = df_filtered[['cd_mun', name_col]].head(10).to_dict('records')
        else:
            state.search_results = df_filtered[['cd_mun']].head(10).to_dict('records')
    
    return df_filtered.sort_values('display_value', ascending=False).head(state.max_municipalities)

def render_details_panel_content(df: pd.DataFrame, municipality_code: str):
    """Renders the content for the municipality details view."""
    mun_data = df[df['cd_mun'] == municipality_code].iloc[0]
    
    # Back button
    if st.button("⬅️ Voltar"):
        st.session_state.selected_municipality_code = None
        st.session_state.highlight_codes = None
        st.rerun()
    
    st.markdown(f"<div class='floating-panel-header'>🏛️ {mun_data['nome_municipio']}</div>", unsafe_allow_html=True)
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("População (2022)", f"{mun_data.get('populacao_2022', 'N/A'):,}")
    with col2:
        st.metric("Código IBGE", mun_data['cd_mun'])
    with col3:
        st.metric("Área (km²)", f"{mun_data.get('area_km2', 'N/A'):,.1f}")

    # Potential metrics
    st.markdown("---")
    st.markdown("**Potencial de Biogás (Nm³/ano)**")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", f"{mun_data.get('total_final_nm_ano', 0):,.0f}")
    with col2:
        st.metric("Agrícola", f"{mun_data.get('total_agricola_nm_ano', 0):,.0f}")
    with col3:
        st.metric("Pecuária", f"{mun_data.get('total_pecuaria_nm_ano', 0):,.0f}")
    with col4:
        st.metric("Urbano", f"{mun_data.get('urban_combined', 0):,.0f}")

    # Detailed breakdown
    st.markdown("---")
    st.markdown("**Detalhamento por Fonte**")
    
    # Agricultural sources
    ag_sources = {
        "Cana-de-açúcar": mun_data.get('biogas_cana_nm_ano', 0),
        "Soja": mun_data.get('biogas_soja_nm_ano', 0),
        "Milho": mun_data.get('biogas_milho_nm_ano', 0),
        "Café": mun_data.get('biogas_cafe_nm_ano', 0),
        "Citros": mun_data.get('biogas_citros_nm_ano', 0)
    }
    
    # Livestock sources
    livestock_sources = {
        "Bovinos": mun_data.get('biogas_bovinos_nm_ano', 0),
        "Suínos": mun_data.get('biogas_suino_nm_ano', 0),
        "Aves": mun_data.get('biogas_aves_nm_ano', 0),
        "Piscicultura": mun_data.get('biogas_piscicultura_nm_ano', 0)
    }
    
    # Urban sources
    urban_sources = {
        "RSU": mun_data.get('rsu_potencial_nm_habitante_ano', 0),
        "RPO": mun_data.get('rpo_potencial_nm_habitante_ano', 0)
    }
    
    # Display sources with values > 0
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Agrícola**")
        for source, value in ag_sources.items():
            if value > 0:
                st.metric(source, f"{value:,.0f}")
    
    with col2:
        st.markdown("**Pecuária**")
        for source, value in livestock_sources.items():
            if value > 0:
                st.metric(source, f"{value:,.0f}")
    
    with col3:
        st.markdown("**Urbano**")
        for source, value in urban_sources.items():
            if value > 0:
                st.metric(source, f"{value:,.0f}")

    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Análise Comparativa", use_container_width=True):
            st.session_state.comparison_municipalities.append(municipality_code)
            st.session_state.active_panel = 'analysis'
            st.rerun()
    with col2:
        if st.button("🗺️ Zoom no Mapa", use_container_width=True):
            st.session_state.map_center = [mun_data['lat'], mun_data['lon']]
            st.session_state.map_zoom = 10
            st.rerun()

# --- PAGE RENDERING FUNCTIONS ---
def render_analysis_page(data: pd.DataFrame, view: str):
    """Render analysis page content based on current view"""
    if view == "overview":
        st.markdown("## 📊 Visão Geral dos Resíduos")
        col1, col2, col3 = st.columns(3)
        with col1:
            total_potential = data['total_final_nm_ano'].sum() / 1_000_000
            st.metric("Potencial Total", f"{total_potential:.1f}M Nm³/ano")
        with col2:
            agricultural = data['total_agricola_nm_ano'].sum() / 1_000_000
            st.metric("Potencial Agrícola", f"{agricultural:.1f}M Nm³/ano")
        with col3:
            livestock = data['total_pecuaria_nm_ano'].sum() / 1_000_000
            st.metric("Potencial Pecuário", f"{livestock:.1f}M Nm³/ano")
        
        # Charts and analysis here
        st.plotly_chart(create_overview_charts(data), use_container_width=True)
        
    elif view == "comparison":
        st.markdown("## 🔬 Comparação Detalhada")
        st.info("Análise comparativa entre diferentes tipos de resíduos")
        # Add comparison logic here
        
    elif view == "geographic":
        st.markdown("## 🗺️ Distribuição Geográfica")
        # Render mini maps or geographic analysis
        st.info("Análise da distribuição espacial dos potenciais")
        
    elif view == "correlation":
        st.markdown("## 🔗 Análise de Correlação")
        st.info("Correlações entre diferentes variáveis")
        
    elif view == "advanced_viz":
        st.markdown("## 📈 Visualizações Avançadas")
        st.info("Visualizações interativas e avançadas")

def render_simulation_page(data: pd.DataFrame, view: str):
    """Render simulation page content based on current view"""
    if view == "substrate_combinations":
        st.markdown("## 🔬 Combinações de Substratos")
        st.info("Simule diferentes combinações de substratos orgânicos")
        
    elif view == "regional_hotspots":
        st.markdown("## 🗺️ Hotspots Regionais")
        st.info("Identifique regiões com maior potencial")
        
    elif view == "custom_scenarios":
        st.markdown("## 📊 Cenários Personalizados")
        st.info("Crie cenários personalizados de análise")
        
    elif view == "synergy_analysis":
        st.markdown("## 🎯 Análise de Sinergia")
        st.info("Analise sinergias entre diferentes tipos de resíduos")

def create_overview_charts(data: pd.DataFrame):
    """Create overview charts for analysis page"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Create subplots with proper specs for mixed chart types
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Top 10 Municípios por Potencial', 'Distribuição por Tipo de Resíduo'),
        specs=[[{"type": "xy"}, {"type": "domain"}]],  # xy for bar chart, domain for pie chart
        horizontal_spacing=0.1
    )
    
    # Add bar chart with dynamic column names
    if 'total_final_nm_ano' in data.columns:
        top_municipalities = data.nlargest(10, 'total_final_nm_ano')
        
        # Get municipality name column
        name_col = None
        for col in ['nome_municipio', 'NOME_MUNICIPIO', 'municipio', 'nm_mun']:
            if col in data.columns:
                name_col = col
                break
        
        if name_col:
            x_values = top_municipalities[name_col].str[:15] + "..."  # Truncate long names
        else:
            x_values = [f"Mun {i+1}" for i in range(len(top_municipalities))]
        
        fig.add_trace(
            go.Bar(
                x=x_values, 
                y=top_municipalities['total_final_nm_ano']/1_000_000,  # Convert to millions
                name="Potencial (M Nm³/ano)",
                marker_color='rgba(44, 85, 48, 0.8)',
                text=top_municipalities['total_final_nm_ano']/1_000_000,
                texttemplate='%{text:.1f}M',
                textposition='outside'
            ),
            row=1, col=1
        )
    
    # Calculate totals for pie chart
    urban_total = 0
    if 'rsu_potencial_nm_habitante_ano' in data.columns:
        urban_total += data['rsu_potencial_nm_habitante_ano'].sum()
    if 'rpo_potencial_nm_habitante_ano' in data.columns:
        urban_total += data['rpo_potencial_nm_habitante_ano'].sum()
    
    # Get totals for pie chart
    agricultural_total = data['total_agricola_nm_ano'].sum() if 'total_agricola_nm_ano' in data.columns else 0
    livestock_total = data['total_pecuaria_nm_ano'].sum() if 'total_pecuaria_nm_ano' in data.columns else 0
    
    # Only show non-zero values in pie chart
    labels = []
    values = []
    colors = []
    
    if agricultural_total > 0:
        labels.append('Agrícola')
        values.append(agricultural_total)
        colors.append('#2c5530')
    
    if livestock_total > 0:
        labels.append('Pecuária')
        values.append(livestock_total)
        colors.append('#4a7c59')
    
    if urban_total > 0:
        labels.append('Urbano')
        values.append(urban_total)
        colors.append('#6b9b76')
    
    if values:  # Only add pie chart if we have data
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors),
                textinfo='label+percent',
                textfont_size=12,
                hole=0.3  # Make it a donut chart for better appearance
            ),
            row=1, col=2
        )
    
    # Update layout
    fig.update_layout(
        height=450,
        showlegend=False,
        title_x=0.5,
        font=dict(size=11)
    )
    
    # Update x-axis for bar chart
    fig.update_xaxes(tickangle=45, row=1, col=1)
    fig.update_yaxes(title_text="Potencial (Milhões Nm³/ano)", row=1, col=1)
    
    return fig

# --- CP2B MCDA PAGE RENDERING ---
def render_mcda_page(view: str):
    """Render CP2B MCDA page based on current view"""
    
    # Initialize CP2B session state only when MCDA page is accessed
    initialize_cp2b_session_state()
    
    if view == "map":
        # === RENDER MCDA MAP VIEW ===
        st.markdown("## 🎯 Análise MCDA - Região Metropolitana de Campinas")
        st.markdown("### Localização Ótima de Plantas de Biogás")
        
        # === SELETOR DE RAIOS MCDA ===
        st.markdown("---")
        st.markdown("### 🔄 Cenários de Análise MCDA")
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
        
        with col1:
            # Seletor de raios
            selected_radius = st.selectbox(
                "Raio de Captação:",
                options=list(MCDA_SCENARIOS.keys()),
                index=list(MCDA_SCENARIOS.keys()).index(st.session_state.get('cp2b_selected_radius', '30km')),
                help="Selecione o raio de captação de resíduos para análise MCDA",
                key="radius_selector"
            )
            
            # Atualizar session state se mudou
            if selected_radius != st.session_state.get('cp2b_selected_radius'):
                st.session_state.cp2b_selected_radius = selected_radius
                st.rerun()
        
        with col2:
            # Estatísticas do cenário selecionado
            stats = get_mcda_summary_stats_by_radius(selected_radius)
            if stats['status'] == 'success':
                st.metric("Propriedades", f"{stats['total_properties']:,}")
            else:
                st.metric("Propriedades", "0")
        
        with col3:
            if stats['status'] == 'success':
                st.metric("Viáveis (Critério Técnico)", f"{stats['viable_properties']:,}")
            else:
                st.metric("Viáveis (Critério Técnico)", "0")
                
        with col4:
            if stats['status'] == 'success' and stats['viable_properties'] > 0:
                threshold = stats['thresholds']['viable']
                st.success(f"✅ {selected_radius}: {stats['viable_percentage']}% viáveis (Score >{threshold:.1f})")
            else:
                st.info(f"ℹ️ Carregando dados do cenário {selected_radius}...")
                
        # Info box com critérios técnicos
        if stats['status'] == 'success':
            with st.expander("📋 Metodologia MCDA"):
                st.markdown(f"""
                **Cenário {selected_radius}** - {stats['thresholds']['justification']}
                
                **Componentes da Análise:**
                - **Potencial de Biomassa (40%)**: Resíduos agrícolas, pecuários e urbanos
                - **Infraestrutura (35%)**: Proximidade de rodovias, energia e gasodutos  
                - **Restrições Ambientais (25%)**: Distância de áreas protegidas e urbanas
                
                Critérios definidos usando percentis estatísticos para realismo técnico-econômico.
                """)
                
                # Mostrar comparação entre cenários
                if st.button("🔄 Comparar com outros cenários"):
                    comparison_data = []
                    for comp_radius in ['10km', '30km', '50km']:
                        comp_stats = get_mcda_summary_stats_by_radius(comp_radius)
                        if comp_stats['status'] == 'success':
                            comparison_data.append({
                                'Cenário': comp_radius,
                                'Viáveis': f"{comp_stats['viable_properties']:,} ({comp_stats['viable_percentage']:.1f}%)",
                                'Muito Bom': f"{comp_stats['very_good_properties']:,} ({comp_stats['very_good_percentage']:.1f}%)",
                                'Excelente': f"{comp_stats['excellent_properties']:,} ({comp_stats['excellent_percentage']:.1f}%)",
                                'Threshold Viável': f">{comp_stats['thresholds']['viable']:.1f}"
                            })
                    
                    if comparison_data:
                        st.markdown("### 📊 Comparação de Cenários")
                        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
        
        # Load data using the NEW function with radius selection
        with st.spinner(f"Carregando dados MCDA para raio {selected_radius}..."):
            cp2b_geodata = load_mcda_geoparquet_by_radius(selected_radius)
            
        if cp2b_geodata.empty:
            st.error(f"❌ Não foi possível carregar os dados MCDA para o raio {selected_radius}.")
            st.info("📁 Verifique se os arquivos GeoParquet estão no diretório correto:")
            for radius, filename in MCDA_SCENARIOS.items():
                file_path = f"./src/streamlit/{filename}"
                st.info(f"📄 {radius}: {filename}")
            return
            
        # Render sidebar controls
        with st.sidebar:
            filters = render_mcda_map_sidebar(cp2b_geodata)
            
        # Apply filters
        filtered_geodata = apply_mcda_filters(cp2b_geodata, filters)
        
        # Display dynamic metrics based on selected radius and filters
        st.markdown("---")
        st.markdown(f"### 📊 Métricas do Cenário {selected_radius} (Filtrado)")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Propriedades Filtradas", f"{len(filtered_geodata):,}")
        with col2:
            avg_score = filtered_geodata['mcda_score'].mean() if not filtered_geodata.empty and 'mcda_score' in filtered_geodata.columns else 0
            st.metric("Score MCDA Médio", f"{avg_score:.1f}")
        with col3:
            municipalities = filtered_geodata['municipio'].nunique() if not filtered_geodata.empty and 'municipio' in filtered_geodata.columns else 0
            st.metric("Municípios", municipalities)
        with col4:
            if not filtered_geodata.empty and 'mcda_score' in filtered_geodata.columns:
                max_score = filtered_geodata['mcda_score'].max()
                excellent_count = len(filtered_geodata[filtered_geodata['mcda_score'] > 80])
                st.metric("Excelentes (>80)", f"{excellent_count:,}")
                
        # Removed redundant info boxes - information is already shown above
                
        # Alerta sobre critérios realistas
        if stats['status'] == 'success':
            total_viable = stats['viable_properties']
            if selected_radius == '50km':
                if total_viable > 1000:
                    st.warning(f"⚠️ **Atenção**: Mesmo com critérios rigorosos, {total_viable:,} propriedades aparecem como viáveis para {selected_radius}. Considere que logística >50km pode inviabilizar muitos projetos na prática.")
            elif selected_radius == '30km':
                if total_viable > 2000:
                    st.info(f"ℹ️ **Cenário Intermediário**: {total_viable:,} propriedades viáveis para {selected_radius}. Balance entre potencial e custos logísticos.")
            else:  # 10km
                st.success(f"✅ **Cenário Otimizado**: {total_viable:,} propriedades viáveis para {selected_radius}. Logística eficiente e custos controlados.")
        
        # Create map using the VISIBLE and optimized function
        st.markdown("---")
        st.info("📍 **Mapa Interativo:** Clique em um polígono colorido para selecionar uma propriedade e gerar o relatório detalhado.")
        
        # Use the interactive map with visible polygons
        clicked_property = render_interactive_mcda_map(filtered_geodata, filters)
        
        # Process map click - navigate to report automatically
        if clicked_property:
            st.session_state.cp2b_selected_property = clicked_property
            st.session_state.current_view = "report"
            st.rerun()
        
        # Navigation instruction only - top 10 table removed
        st.markdown("---")
        
    elif view == "report":
        # === RENDER ENHANCED PROPERTY REPORT VIEW ===
        selected_property_id = st.session_state.get('cp2b_selected_property')
        selected_radius = st.session_state.get('cp2b_selected_radius', '30km')
        
        if not selected_property_id:
            st.error("❌ Nenhuma propriedade selecionada para relatório")
            if st.button("⬅️ Voltar ao Mapa"):
                st.session_state.current_view = "map"
                st.rerun()
            return
            
        # Get property details
        property_data = get_property_details(selected_property_id)
        
        if not property_data:
            st.error(f"❌ Propriedade {selected_property_id} não encontrada")
            if st.button("⬅️ Voltar ao Mapa"):
                st.session_state.current_view = "map"
                st.rerun()
            return
            
        # Try to render simple report first (more reliable), then enhanced as fallback
        try:
            from components.mcda import render_simple_property_report
            render_simple_property_report(property_data, selected_radius)
        except (ImportError, AttributeError):
            try:
                from components.mcda import render_enhanced_property_report
                render_enhanced_property_report(property_data, selected_radius)
            except (ImportError, AttributeError):
                st.warning("⚠️ Relatórios aprimorados não disponíveis. Usando versão padrão.")
                render_property_report_page(property_data)

# --- 6. MAIN APPLICATION ---
def main():
    """The main function to run the dashboard."""
    # Session state already initialized at the top

    if not st.session_state.data_loaded:
        with st.spinner("Conectando ao banco de dados e carregando dados..."):
            try:
                df = load_data()
                if not df.empty:
                    st.session_state.data = df
                    st.session_state.data_loaded = True
                else:
                    st.error("Could not load municipal data. The application cannot continue.")
                    st.stop()
            except Exception as e:
                st.error(f"Error loading data: {e}")
                st.stop()

    # ==========================================================================
    # CORE APP LOGIC
    # ==========================================================================

    # Apply filters to data
    filtered_df = apply_dashboard_filters(st.session_state.data, st.session_state)

    # === MAIN CONTENT RENDERING BASED ON CURRENT PAGE ===
    current_page = st.session_state.get('current_page', 'dashboard')
    current_view = st.session_state.get('current_view', 'overview')
    
    if current_page == 'dashboard':
        # --- RENDER THE MAP (BASE LAYER) ---
        # Prepare visualization settings
        viz_settings = {
            'threshold': st.session_state.get('hotspot_threshold', 75),
            'cluster_analysis': st.session_state.get('cluster_analysis', False),
            'density_heatmap': st.session_state.get('density_heatmap', False)
        }

        map_interaction = render_map(
            filtered_df,
            map_center=st.session_state.map_center,
            map_zoom=st.session_state.map_zoom,
            highlight_codes=st.session_state.highlight_codes,
            layer_controls=st.session_state.layer_controls,
            special_viz_mode=st.session_state.get('visualization_mode', 'Padrão'),
            viz_settings=viz_settings
        )
        
    elif current_page == 'analysis':
        render_analysis_page(filtered_df, current_view)
        map_interaction = None
        
    elif current_page == 'simulation':
        render_simulation_page(filtered_df, current_view)
        map_interaction = None
        
    elif current_page == 'mcda':
        # === RENDER CP2B MCDA PAGE ===
        render_mcda_page(current_view)
        map_interaction = None

    # --- RENDER THE FIXED CONTROL PANEL (ALWAYS VISIBLE SIDEBAR) ---
    # Sidebar is now always visible for better UX
    with st.sidebar:
        st.markdown("## 🎛️ Controles do Mapa")
        st.markdown("---")
        
        # Search section
        st.markdown("### 🔍 Busca de Municípios")
        search_query = st.text_input("Nome ou código do município:", 
                                   value=st.session_state.get('search_query', ''),
                                   placeholder="Digite o nome ou código...")
        
        if search_query != st.session_state.get('search_query', ''):
            st.session_state.search_query = search_query
            st.rerun()
        
        # Simplified Filter section
        st.markdown("### ⚙️ Filtros")
        
        # Initialize residue filters if not exists
        if 'residue_filters' not in st.session_state:
            st.session_state.residue_filters = {
                'total_final_nm_ano': True,
                'total_agricola_nm_ano': False,
                'total_pecuaria_nm_ano': False,
                'total_urbano_nm_ano': False
            }
        
        # Accessible dropdown selection for residue types
        st.markdown("**🌾 Filtros de Resíduos**")
        
        # Enhanced dropdown with clear accessibility labels
        selected_residue = st.selectbox(
            "Selecione o tipo de resíduo para análise:",
            options=list(RESIDUE_OPTIONS.keys()),
            index=list(RESIDUE_OPTIONS.values()).index(st.session_state.get('selected_residues', ['total_final_nm_ano'])[0]) if st.session_state.get('selected_residues') else 0,
            help="Escolha o tipo de resíduo orgânico para visualizar no mapa. Use as teclas de seta para navegar rapidamente entre as opções.",
            key="residue_dropdown"
        )
        
        # Update selected_residues based on dropdown selection
        new_residue = RESIDUE_OPTIONS[selected_residue]
        if new_residue != st.session_state.get('selected_residues', ['total_final_nm_ano'])[0]:
            st.session_state.selected_residues = [new_residue]
        
        # Selection mode for advanced users
        selection_mode = st.radio(
            "Modo de seleção:",
            options=["Individual", "Múltiplos"],
            index=0 if st.session_state.get('selection_mode', 'Individual') == 'Individual' else 1,
            help="Individual: visualiza um tipo por vez. Múltiplos: soma vários tipos selecionados.",
            horizontal=True,
            key="selection_mode_radio"
        )
        st.session_state.selection_mode = selection_mode
        
        # Multi-select option for advanced mode
        if selection_mode == "Múltiplos":
            current_labels = [k for k, v in RESIDUE_OPTIONS.items() if v in st.session_state.get('selected_residues', [])]
            
            selected_labels = st.multiselect(
                "Selecione múltiplos tipos para somar:",
                options=list(RESIDUE_OPTIONS.keys()),
                default=current_labels,
                help="Mantenha Ctrl pressionado para selecionar múltiplos itens. A análise mostrará a soma dos tipos selecionados.",
                key="multi_residue_select"
            )
            
            # Update for multiple selection
            if selected_labels:
                new_residues = [RESIDUE_OPTIONS[label] for label in selected_labels]
                if new_residues != st.session_state.get('selected_residues', []):
                    st.session_state.selected_residues = new_residues
        
        # Show current selection status
        if st.session_state.get('selection_mode') == "Múltiplos" and len(st.session_state.get('selected_residues', [])) > 1:
            st.caption(f"📊 Somando {len(st.session_state.selected_residues)} tipos de resíduos")
        else:
            selected_label = next((k for k, v in RESIDUE_OPTIONS.items() if v == st.session_state.get('selected_residues', ['total_final_nm_ano'])[0]), "Total")
            st.caption(f"📍 Analisando: {selected_label}")
        
        # Municipality limit
        st.markdown("### 📊 Controles de Visualização")
        max_munis = st.slider("Máximo de municípios no mapa:", 
                             min_value=50, max_value=645, 
                             value=st.session_state.get('max_municipalities', 500),
                             step=50)
        
        if max_munis != st.session_state.get('max_municipalities', 500):
            st.session_state.max_municipalities = max_munis
            st.rerun()
        
        # Show zero values toggle
        show_zeros = st.checkbox("Mostrar municípios com potencial zero", 
                               value=st.session_state.get('show_zero_values', False))
        
        if show_zeros != st.session_state.get('show_zero_values', False):
            st.session_state.show_zero_values = show_zeros
            st.rerun()
        
        # Accessible layer controls - matching residue filter approach
        st.markdown("### 🗺️ Camadas")
        
        # Initialize layer controls if not exists
        if 'layer_controls' not in st.session_state:
            st.session_state.layer_controls = {
                'limite_sp': True,
                'municipalities': True,
                'plantas_biogas': False,
                'areas_urbanas': False,
                'regioes_admin': False,
                'gasodutos_transporte': False,
                'gasodutos_distribuicao': False,
                'rodovias_estaduais': False
            }
        
        # Layer options for dropdown selection
        LAYER_OPTIONS = {
            "🏛️ Limite de São Paulo": "limite_sp",
            "📍 Regiões Administrativas": "regioes_admin", 
            "⚡ Usinas de Biogás": "plantas_biogas",
            "🏙️ Áreas Urbanas": "areas_urbanas",
            "🛣️ Rodovias Estaduais": "rodovias_estaduais",
            "🚰 Gasodutos de Transporte": "gasodutos_transporte",
            "🔀 Gasodutos de Distribuição": "gasodutos_distribuicao"
        }
        
        # Primary layer selection dropdown
        currently_active_layers = [k for k, v in LAYER_OPTIONS.items() if st.session_state.layer_controls.get(v, False)]
        default_layer = currently_active_layers[0] if currently_active_layers else "🏛️ Limite de São Paulo"
        
        selected_layer = st.selectbox(
            "Selecione a camada principal para visualizar:",
            options=list(LAYER_OPTIONS.keys()),
            index=list(LAYER_OPTIONS.keys()).index(default_layer) if default_layer in LAYER_OPTIONS else 0,
            help="Escolha a camada mais importante para o mapa. Use as setas do teclado para navegar rapidamente.",
            key="primary_layer_dropdown"
        )
        
        # Always show municipalities and selected primary layer
        st.session_state.layer_controls['municipalities'] = True
        for layer_key in LAYER_OPTIONS.values():
            st.session_state.layer_controls[layer_key] = False
        st.session_state.layer_controls[LAYER_OPTIONS[selected_layer]] = True
        
        # Layer mode selection
        layer_mode = st.radio(
            "Modo de visualização:",
            options=["Simples", "Avançado"],
            index=0 if st.session_state.get('layer_mode', 'Simples') == 'Simples' else 1,
            help="Simples: mostra apenas a camada selecionada. Avançado: permite múltiplas camadas sobrepostas.",
            horizontal=True,
            key="layer_mode_radio"
        )
        st.session_state.layer_mode = layer_mode
        
        # Multi-layer selection for advanced mode
        if layer_mode == "Avançado":
            current_active = [k for k, v in LAYER_OPTIONS.items() if st.session_state.layer_controls.get(v, False)]
            
            selected_layers = st.multiselect(
                "Selecione múltiplas camadas para sobrepor:",
                options=list(LAYER_OPTIONS.keys()),
                default=current_active,
                help="Mantenha Ctrl pressionado para selecionar múltiplas camadas. Elas serão sobrepostas no mapa.",
                key="multi_layer_select"
            )
            
            # Update layer controls for multiple selection
            for layer_key in LAYER_OPTIONS.values():
                st.session_state.layer_controls[layer_key] = False
            
            for selected in selected_layers:
                if selected in LAYER_OPTIONS:
                    st.session_state.layer_controls[LAYER_OPTIONS[selected]] = True
                    
            # Always keep municipalities visible
            st.session_state.layer_controls['municipalities'] = True
        
        # Show current layer status
        active_layers = [k for k, v in LAYER_OPTIONS.items() if st.session_state.layer_controls.get(v, False)]
        if st.session_state.get('layer_mode') == "Avançado" and len(active_layers) > 1:
            st.caption(f"🗺️ Sobrepostas: {len(active_layers)} camadas")
        else:
            if active_layers:
                st.caption(f"🗺️ Ativa: {active_layers[0]}")
            else:
                st.caption("🗺️ Apenas municípios visíveis")
        
        # Special Visualizations Section
        st.markdown("### 🎯 Visualizações Especiais")
        
        # Initialize visualization settings
        if 'visualization_mode' not in st.session_state:
            st.session_state.visualization_mode = "Padrão"
        if 'hotspot_threshold' not in st.session_state:
            st.session_state.hotspot_threshold = 75
        if 'cluster_analysis' not in st.session_state:
            st.session_state.cluster_analysis = False
        if 'density_heatmap' not in st.session_state:
            st.session_state.density_heatmap = False
        
        # Visualization mode selector
        viz_mode = st.selectbox(
            "Modo de visualização:",
            options=["Padrão", "Hotspots", "Clusters", "Densidade", "Corredores"],
            index=["Padrão", "Hotspots", "Clusters", "Densidade", "Corredores"].index(st.session_state.visualization_mode),
            help="Escolha diferentes modos de visualização para análise espacial avançada",
            key="viz_mode_select"
        )
        st.session_state.visualization_mode = viz_mode
        
        # Conditional controls based on visualization mode
        if viz_mode == "Hotspots":
            threshold = st.slider(
                "Limite para hotspots (percentil):",
                min_value=50, max_value=95, 
                value=st.session_state.hotspot_threshold,
                help="Municípios acima deste percentil serão destacados como hotspots",
                key="hotspot_slider"
            )
            st.session_state.hotspot_threshold = threshold
            
        elif viz_mode == "Clusters":
            cluster_enabled = st.checkbox(
                "Ativar análise de clusters",
                value=st.session_state.cluster_analysis,
                help="Identifica grupos de municípios com características similares",
                key="cluster_checkbox"
            )
            st.session_state.cluster_analysis = cluster_enabled
            
        elif viz_mode == "Densidade":
            density_enabled = st.checkbox(
                "Mostrar mapa de calor",
                value=st.session_state.density_heatmap,
                help="Visualiza densidade de potencial com gradiente de cores",
                key="density_checkbox"
            )
            st.session_state.density_heatmap = density_enabled
            
        elif viz_mode == "Corredores":
            st.info("💡 Identifica corredores de alta produção conectando municípios adjacentes")
        
        # Show current visualization status
        if viz_mode != "Padrão":
            st.caption(f"🎯 Visualização ativa: {viz_mode}")

    # Sidebar is now always visible - no toggle needed

    # Handle map interactions if needed
    if map_interaction and map_interaction.get('selected_municipality'):
        clicked_code = map_interaction['selected_municipality']
        if st.session_state.selected_municipality_code != clicked_code:
            st.session_state.selected_municipality_code = clicked_code
            st.session_state.highlight_codes = [clicked_code]
            st.rerun()

if __name__ == "__main__":
    main()