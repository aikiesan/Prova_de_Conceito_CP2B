import streamlit as st
import pandas as pd

def render_control_panel(df, residue_options):
    """Renders the enhanced control panel with filtering options."""
    st.subheader("Filtros de Visualização")
    
    # Residue type selection
    residue_display = [name for name, key in residue_options.items()]
    selected_residues = st.multiselect(
        "Tipos de Resíduos:",
        options=residue_display,
        default=["⚡ Potencial Total"],
        format_func=lambda x: x,
        key="residue_select"
    )
    
    # Convert display names back to keys
    residue_keys = [residue_options[name] for name in selected_residues]
    st.session_state.selected_residues = residue_keys
    
    # Display settings
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "Modo de Seleção:",
            options=["Individual", "Múltiplos"],
            key="selection_mode"
        )
    with col2:
        st.slider(
            "Máx. Municípios:",
            min_value=10,
            max_value=1000,
            value=500,
            step=10,
            key="max_municipalities"
        )
    
    st.checkbox("Mostrar valores zero", key="show_zero_values")
    
    # Advanced filters
    with st.expander("Filtros Avançados"):
        st.slider(
            "População Mínima:",
            min_value=0,
            max_value=int(df['populacao_2022'].max()) if not df.empty else 100000,
            value=0,
            step=1000,
            key="min_population"
        )
        
        st.slider(
            "Potencial Mínimo (Nm³/ano):",
            min_value=0,
            max_value=int(df['total_final_nm_ano'].max()) if not df.empty else 1000000,
            value=0,
            step=10000,
            key="min_potential"
        )
    
    # Layer controls
    st.subheader("Camadas do Mapa")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Limite Estadual", value=True, key="layer_limite_sp")
    with col2:
        st.checkbox("Municípios", value=True, key="layer_municipalities")
    
    st.checkbox("Mapa de Calor", key="heatmap_layer")
    st.checkbox("Agrupar Marcadores", key="cluster_layer")

def render_search_panel(df, residue_options):
    """Renders the search panel with autocomplete functionality."""
    st.subheader("Busca de Municípios")
    
    # Search input
    search_query = st.text_input(
        "Digite o nome ou código do município:",
        key="search_query",
        placeholder="Ex: São Paulo ou 3550308"
    )
    
    # Search results
    if st.session_state.search_results:
        st.info(f"{len(st.session_state.search_results)} resultados encontrados")
        for result in st.session_state.search_results[:5]:  # Show top 5 results
            if st.button(f"{result['nome_municipio']} ({result['cd_mun']})", 
                         key=f"search_result_{result['cd_mun']}", 
                         use_container_width=True):
                st.session_state.selected_municipality_code = result['cd_mun']
                st.session_state.highlight_codes = [result['cd_mun']]
                st.rerun()
    
    # Quick filters
    st.subheader("Filtros Rápidos")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Top 10 Potencial", use_container_width=True):
            st.session_state.selected_residues = ['total_final_nm_ano']
            st.session_state.max_municipalities = 10
            st.rerun()
    with col2:
        if st.button("Maiores Populações", use_container_width=True):
            # This would need implementation to sort by population
            st.rerun()

def render_analysis_panel(df, analysis_types):
    """Renders the analysis tools panel."""
    st.subheader("Ferramentas de Análise")
    
    analysis_type = st.selectbox(
        "Tipo de Análise:",
        options=list(analysis_types.keys()),
        key="analysis_type"
    )
    
    if analysis_types[analysis_type] == "comparison":
        st.info("Selecione municípios para comparar")
        selected_municipalities = st.multiselect(
            "Municípios para comparar:",
            options=[f"{row['nome_municipio']} ({row['cd_mun']})" for _, row in df.iterrows()],
            key="comparison_municipalities"
        )
        
        if st.button("Gerar Comparativo", use_container_width=True):
            # Generate comparison chart
            pass
            
    elif analysis_types[analysis_type] == "cluster":
        st.slider("Número de Clusters:", 2, 10, 5, key="cluster_count")
        if st.button("Identificar Clusters", use_container_width=True):
            # Perform clustering analysis
            pass