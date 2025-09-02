"""
Enhanced User-Friendly Filters for CP2B Dashboard
Advanced search, filtering, and user interface improvements for better data exploration
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import re
from datetime import datetime

class EnhancedFilters:
    """Enhanced filtering system with user-friendly search and advanced controls"""
    
    def __init__(self):
        """Initialize enhanced filters"""
        # São Paulo administrative regions
        self.sp_regions = {
            'Grande São Paulo': ['São Paulo', 'Guarulhos', 'São Bernardo do Campo', 'Santo André', 'Osasco', 'São Caetano do Sul', 'Mauá', 'Diadema', 'Carapicuíba'],
            'Vale do Paraíba': ['São José dos Campos', 'Taubaté', 'Jacareí', 'Guaratinguetá', 'Pindamonhangaba', 'Caraguatatuba', 'Campos do Jordão'],
            'Litoral': ['Santos', 'São Vicente', 'Guarujá', 'Praia Grande', 'Cubatão', 'Bertioga', 'Itanhaém', 'Mongaguá', 'Peruíbe'],
            'Campinas': ['Campinas', 'Sorocaba', 'Jundiaí', 'Piracicaba', 'Limeira', 'Rio Claro', 'Americana', 'Santa Bárbara d\'Oeste'],
            'Ribeirão Preto': ['Ribeirão Preto', 'Araraquara', 'São Carlos', 'Franca', 'Barretos', 'Sertãozinho', 'Jaboticabal'],
            'Vale do Paranapanema': ['Marília', 'Assis', 'Ourinhos', 'Tupã', 'Avaré', 'Botucatu', 'Itapetininga'],
            'Noroeste': ['São José do Rio Preto', 'Araçatuba', 'Presidente Prudente', 'Birigui', 'Catanduva', 'Votuporanga'],
            'Norte': ['Franca', 'Mococa', 'São Joaquim da Barra', 'Ituverava', 'Orlândia', 'Batatais']
        }
        
        # Economic categories
        self.economic_categories = {
            'Grande': {'min_pop': 500000, 'label': '🏙️ Grande (500k+)'},
            'Médio': {'min_pop': 100000, 'max_pop': 499999, 'label': '🏘️ Médio (100k-500k)'},
            'Pequeno': {'min_pop': 20000, 'max_pop': 99999, 'label': '🏡 Pequeno (20k-100k)'},
            'Micro': {'max_pop': 19999, 'label': '🏠 Micro (<20k)'}
        }

    def render_smart_search(self, df: pd.DataFrame, key_prefix: str = "search") -> Dict[str, Any]:
        """Render intelligent municipality search with autocomplete-like functionality"""
        
        st.markdown("### 🔍 **Busca Inteligente de Municípios**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Text input for municipality search
            search_term = st.text_input(
                "Digite o nome do município:",
                value="",
                key=f"{key_prefix}_search_input",
                help="Digite pelo menos 2 letras para buscar municípios",
                placeholder="Ex: São Paulo, Campinas, Santos..."
            )
            
        with col2:
            search_mode = st.selectbox(
                "Modo de busca:",
                ["Contém", "Inicia com", "Exato"],
                key=f"{key_prefix}_search_mode",
                help="Como fazer a busca no nome"
            )
        
        # Get matching municipalities
        matching_municipalities = self._get_matching_municipalities(df, search_term, search_mode)
        
        # Display search results
        if search_term and len(search_term) >= 2:
            if len(matching_municipalities) > 0:
                st.success(f"✅ Encontrados {len(matching_municipalities)} municípios")
                
                # Show results in a selectbox or multiselect
                col1, col2 = st.columns(2)
                
                with col1:
                    selection_mode = st.radio(
                        "Modo de seleção:",
                        ["Único", "Múltiplo"],
                        key=f"{key_prefix}_selection_mode",
                        horizontal=True
                    )
                
                with col2:
                    show_details = st.checkbox(
                        "Mostrar detalhes",
                        key=f"{key_prefix}_show_details",
                        help="Mostra potencial de biogás na lista"
                    )
                
                # Municipality selection
                if selection_mode == "Único":
                    selected_municipalities = self._render_single_selection(
                        matching_municipalities, show_details, key_prefix
                    )
                else:
                    selected_municipalities = self._render_multiple_selection(
                        matching_municipalities, show_details, key_prefix
                    )
                    
            else:
                st.warning(f"❌ Nenhum município encontrado para '{search_term}'")
                selected_municipalities = []
        else:
            selected_municipalities = []
            if search_term and len(search_term) < 2:
                st.info("💡 Digite pelo menos 2 letras para buscar")
        
        return {
            'search_term': search_term,
            'search_mode': search_mode,
            'selection_mode': selection_mode if search_term else "Único",
            'selected_municipalities': selected_municipalities,
            'matching_count': len(matching_municipalities) if search_term else 0
        }

    def render_regional_filters(self, df: pd.DataFrame, key_prefix: str = "region") -> Dict[str, Any]:
        """Render regional and geographic filters"""
        
        st.markdown("### 🗺️ **Filtros Regionais**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Administrative regions
            selected_regions = st.multiselect(
                "Regiões Administrativas:",
                options=list(self.sp_regions.keys()),
                key=f"{key_prefix}_admin_regions",
                help="Selecione uma ou mais regiões administrativas"
            )
            
        with col2:
            # Distance-based filtering (if you have coordinates)
            use_distance_filter = st.checkbox(
                "Filtro por distância",
                key=f"{key_prefix}_use_distance",
                help="Filtrar por distância de um ponto central"
            )
            
        distance_filters = {}
        if use_distance_filter:
            col1, col2, col3 = st.columns(3)
            with col1:
                center_lat = st.number_input(
                    "Latitude central:",
                    value=-23.5505,  # São Paulo default
                    format="%.4f",
                    key=f"{key_prefix}_center_lat"
                )
            with col2:
                center_lon = st.number_input(
                    "Longitude central:",
                    value=-46.6333,  # São Paulo default
                    format="%.4f",
                    key=f"{key_prefix}_center_lon"
                )
            with col3:
                max_distance = st.slider(
                    "Distância máxima (km):",
                    min_value=10,
                    max_value=500,
                    value=100,
                    key=f"{key_prefix}_max_distance"
                )
                
            distance_filters = {
                'center_lat': center_lat,
                'center_lon': center_lon,
                'max_distance': max_distance
            }
        
        return {
            'selected_regions': selected_regions,
            'use_distance_filter': use_distance_filter,
            'distance_filters': distance_filters
        }

    def render_demographic_economic_filters(self, df: pd.DataFrame, key_prefix: str = "demo") -> Dict[str, Any]:
        """Render demographic and economic filters"""
        
        st.markdown("### 📊 **Filtros Demográficos e Econômicos**")
        
        # Population-based filters
        st.markdown("**Por População:**")
        col1, col2 = st.columns(2)
        
        with col1:
            use_pop_categories = st.checkbox(
                "Usar categorias predefinidas",
                key=f"{key_prefix}_use_pop_categories",
                help="Filtrar por categorias de tamanho populacional"
            )
            
        population_filters = {}
        if use_pop_categories:
            with col2:
                selected_pop_categories = st.multiselect(
                    "Categorias:",
                    options=[info['label'] for info in self.economic_categories.values()],
                    key=f"{key_prefix}_pop_categories"
                )
                population_filters['categories'] = selected_pop_categories
        else:
            # Custom population range
            col1, col2 = st.columns(2)
            with col1:
                min_population = st.number_input(
                    "População mínima:",
                    min_value=0,
                    value=0,
                    step=1000,
                    key=f"{key_prefix}_min_pop"
                )
            with col2:
                max_population = st.number_input(
                    "População máxima:",
                    min_value=min_population,
                    value=1000000,
                    step=10000,
                    key=f"{key_prefix}_max_pop"
                )
            population_filters = {
                'min_population': min_population,
                'max_population': max_population
            }
        
        # Area-based filters
        st.markdown("**Por Área Municipal:**")
        if 'area_km2' in df.columns:
            area_range = st.slider(
                "Área (km²):",
                min_value=float(df['area_km2'].min()) if 'area_km2' in df.columns else 0,
                max_value=float(df['area_km2'].max()) if 'area_km2' in df.columns else 1000,
                value=(0.0, float(df['area_km2'].max()) if 'area_km2' in df.columns else 1000),
                key=f"{key_prefix}_area_range"
            )
        else:
            area_range = (0, 1000)
            st.info("ℹ️ Dados de área não disponíveis")
        
        return {
            'use_pop_categories': use_pop_categories,
            'population_filters': population_filters,
            'area_range': area_range
        }

    def render_advanced_range_sliders(self, df: pd.DataFrame, key_prefix: str = "ranges") -> Dict[str, Any]:
        """Render multiple range sliders for different biogas sources"""
        
        st.markdown("### 📈 **Filtros Avançados por Potencial**")
        
        # Get available columns for sliders
        biogas_columns = [col for col in df.columns if 'biogas_' in col or 'potencial' in col or 'total_' in col]
        biogas_columns = [col for col in biogas_columns if df[col].dtype in ['int64', 'float64']]
        
        range_filters = {}
        
        # Main categories
        categories = {
            '⚡ Total Geral': ['total_final_nm_ano'],
            '🌾 Agrícola': [col for col in biogas_columns if any(crop in col for crop in ['cana', 'soja', 'milho', 'cafe', 'citros'])],
            '🐄 Pecuária': [col for col in biogas_columns if any(animal in col for animal in ['bovinos', 'suino', 'aves', 'piscicultura'])],
            '🏙️ Urbano': [col for col in biogas_columns if any(urban in col for urban in ['rsu', 'rpo'])]
        }
        
        # Render sliders for each category
        for category_name, columns in categories.items():
            available_columns = [col for col in columns if col in df.columns and not df[col].isna().all()]
            
            if available_columns:
                with st.expander(f"{category_name}", expanded=False):
                    for col in available_columns:
                        if len(df[col].dropna()) > 0:
                            min_val = float(df[col].min())
                            max_val = float(df[col].max())
                            
                            if max_val > min_val:  # Only show slider if there's variation
                                # Create user-friendly column name
                                display_name = self._format_column_name(col)
                                
                                range_val = st.slider(
                                    f"{display_name}:",
                                    min_value=min_val,
                                    max_value=max_val,
                                    value=(min_val, max_val),
                                    key=f"{key_prefix}_{col}",
                                    help=f"Faixa: {min_val:,.0f} - {max_val:,.0f} Nm³/ano"
                                )
                                
                                range_filters[col] = range_val
        
        return range_filters

    def render_quick_filters(self, df: pd.DataFrame, key_prefix: str = "quick") -> Dict[str, Any]:
        """Render quick filter buttons for common scenarios"""
        
        st.markdown("### ⚡ **Filtros Rápidos**")
        st.markdown("*Clique para aplicar filtros comuns:*")
        
        col1, col2, col3, col4 = st.columns(4)
        
        quick_filters = {}
        
        with col1:
            if st.button("🏆 Top 50", key=f"{key_prefix}_top50", help="50 maiores potenciais"):
                quick_filters['type'] = 'top_n'
                quick_filters['value'] = 50
                
        with col2:
            if st.button("🌾 Só Agrícola", key=f"{key_prefix}_agri_only", help="Apenas potencial agrícola"):
                quick_filters['type'] = 'agricultural_only'
                
        with col3:
            if st.button("🐄 Só Pecuária", key=f"{key_prefix}_livestock_only", help="Apenas potencial pecuário"):
                quick_filters['type'] = 'livestock_only'
                
        with col4:
            if st.button("🏙️ Só Urbano", key=f"{key_prefix}_urban_only", help="Apenas potencial urbano"):
                quick_filters['type'] = 'urban_only'
        
        # Additional quick filters row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⚡ Alto Potencial", key=f"{key_prefix}_high_potential", help="Potencial > 100k Nm³/ano"):
                quick_filters['type'] = 'high_potential'
                quick_filters['value'] = 100000
                
        with col2:
            if st.button("🎯 Potencial Médio", key=f"{key_prefix}_medium_potential", help="Potencial 10k-100k Nm³/ano"):
                quick_filters['type'] = 'medium_potential'
                
        with col3:
            if st.button("📍 Grande SP", key=f"{key_prefix}_gsp", help="Região Metropolitana"):
                quick_filters['type'] = 'region'
                quick_filters['value'] = 'Grande São Paulo'
                
        with col4:
            if st.button("🔄 Limpar Filtros", key=f"{key_prefix}_clear", help="Remover todos os filtros"):
                quick_filters['type'] = 'clear_all'
        
        return quick_filters

    # Helper methods
    def _get_matching_municipalities(self, df: pd.DataFrame, search_term: str, search_mode: str) -> List[Dict]:
        """Get municipalities matching search criteria"""
        if not search_term or len(search_term) < 2:
            return []
        
        # Normalize search term
        search_normalized = self._normalize_text(search_term)
        
        matches = []
        for _, row in df.iterrows():
            municipality_name = str(row.get('nm_mun', ''))
            municipality_normalized = self._normalize_text(municipality_name)
            
            # Apply search mode
            is_match = False
            if search_mode == "Contém":
                is_match = search_normalized in municipality_normalized
            elif search_mode == "Inicia com":
                is_match = municipality_normalized.startswith(search_normalized)
            elif search_mode == "Exato":
                is_match = municipality_normalized == search_normalized
            
            if is_match:
                matches.append({
                    'name': municipality_name,
                    'code': str(row.get('cd_mun', '')),
                    'total_potential': row.get('total_final_nm_ano', 0),
                    'row_data': row
                })
        
        # Sort by total potential (descending)
        matches.sort(key=lambda x: x['total_potential'], reverse=True)
        return matches

    def _normalize_text(self, text: str) -> str:
        """Normalize text for search (remove accents, lowercase, etc.)"""
        # Remove accents and convert to lowercase
        import unicodedata
        text = str(text).lower()
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii')
        return text

    def _render_single_selection(self, municipalities: List[Dict], show_details: bool, key_prefix: str) -> List[str]:
        """Render single municipality selection"""
        if show_details:
            options = [
                f"{mun['name']} ({mun['code']}) - {mun['total_potential']:,.0f} Nm³/ano"
                for mun in municipalities
            ]
        else:
            options = [f"{mun['name']} ({mun['code']})" for mun in municipalities]
        
        selected = st.selectbox(
            "Selecione o município:",
            options=["Nenhum"] + options,
            key=f"{key_prefix}_single_select"
        )
        
        if selected != "Nenhum":
            # Extract municipality code
            code = selected.split("(")[1].split(")")[0]
            return [code]
        return []

    def _render_multiple_selection(self, municipalities: List[Dict], show_details: bool, key_prefix: str) -> List[str]:
        """Render multiple municipality selection"""
        if show_details:
            options = [
                f"{mun['name']} ({mun['code']}) - {mun['total_potential']:,.0f} Nm³/ano"
                for mun in municipalities
            ]
        else:
            options = [f"{mun['name']} ({mun['code']})" for mun in municipalities]
        
        selected = st.multiselect(
            "Selecione os municípios:",
            options=options,
            key=f"{key_prefix}_multi_select",
            help=f"Selecione até {min(10, len(municipalities))} municípios"
        )
        
        # Extract municipality codes
        codes = []
        for selection in selected:
            code = selection.split("(")[1].split(")")[0]
            codes.append(code)
        return codes

    def _format_column_name(self, column: str) -> str:
        """Format column name for display"""
        name_mapping = {
            'biogas_cana_nm_ano': '🌾 Cana-de-açúcar',
            'biogas_soja_nm_ano': '🌱 Soja',
            'biogas_milho_nm_ano': '🌽 Milho',
            'biogas_cafe_nm_ano': '☕ Café',
            'biogas_citros_nm_ano': '🍊 Citros',
            'biogas_bovinos_nm_ano': '🐄 Bovinos',
            'biogas_suino_nm_ano': '🐷 Suínos',
            'biogas_aves_nm_ano': '🐔 Aves',
            'biogas_piscicultura_nm_ano': '🐟 Piscicultura',
            'rsu_potencial_nm_habitante_ano': '🗑️ RSU',
            'rpo_potencial_nm_habitante_ano': '🌿 RPO',
            'total_final_nm_ano': '⚡ Total Geral',
            'total_agricola_nm_ano': '🌾 Total Agrícola',
            'total_pecuaria_nm_ano': '🐄 Total Pecuária'
        }
        return name_mapping.get(column, column.replace('_', ' ').title())

    def apply_all_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply all filter types to the dataframe"""
        if df.empty:
            return df
        
        filtered_df = df.copy()
        
        # Apply search filters
        if filters.get('search', {}).get('selected_municipalities'):
            selected_codes = filters['search']['selected_municipalities']
            filtered_df = filtered_df[filtered_df['cd_mun'].astype(str).isin(selected_codes)]
        
        # Apply regional filters
        if filters.get('regional', {}).get('selected_regions'):
            selected_regions = filters['regional']['selected_regions']
            region_municipalities = []
            for region in selected_regions:
                if region in self.sp_regions:
                    region_municipalities.extend(self.sp_regions[region])
            
            if region_municipalities:
                filtered_df = filtered_df[filtered_df['nm_mun'].isin(region_municipalities)]
        
        # Apply demographic filters
        demo_filters = filters.get('demographic', {})
        if demo_filters.get('population_filters'):
            pop_filters = demo_filters['population_filters']
            if 'min_population' in pop_filters and 'populacao' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['populacao'] >= pop_filters['min_population']]
            if 'max_population' in pop_filters and 'populacao' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['populacao'] <= pop_filters['max_population']]
        
        # Apply range filters
        range_filters = filters.get('ranges', {})
        for column, (min_val, max_val) in range_filters.items():
            if column in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df[column] >= min_val) & (filtered_df[column] <= max_val)
                ]
        
        # Apply quick filters
        quick_filter = filters.get('quick_filter', {})
        if quick_filter.get('type'):
            filter_type = quick_filter['type']
            
            if filter_type == 'top_n':
                n = quick_filter.get('value', 50)
                filtered_df = filtered_df.nlargest(n, 'total_final_nm_ano')
            elif filter_type == 'high_potential':
                threshold = quick_filter.get('value', 100000)
                filtered_df = filtered_df[filtered_df['total_final_nm_ano'] >= threshold]
            elif filter_type == 'medium_potential':
                filtered_df = filtered_df[
                    (filtered_df['total_final_nm_ano'] >= 10000) & 
                    (filtered_df['total_final_nm_ano'] < 100000)
                ]
            elif filter_type == 'agricultural_only':
                if 'total_agricola_nm_ano' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['total_agricola_nm_ano'] > 0]
            elif filter_type == 'livestock_only':
                if 'total_pecuaria_nm_ano' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['total_pecuaria_nm_ano'] > 0]
            elif filter_type == 'urban_only':
                urban_cols = ['rsu_potencial_nm_habitante_ano', 'rpo_potencial_nm_habitante_ano']
                urban_mask = False
                for col in urban_cols:
                    if col in filtered_df.columns:
                        urban_mask |= (filtered_df[col] > 0)
                filtered_df = filtered_df[urban_mask]
        
        return filtered_df


def render_enhanced_filters_sidebar(df: pd.DataFrame) -> Dict[str, Any]:
    """Main function to render all enhanced filters in sidebar"""
    
    enhanced_filters = EnhancedFilters()
    
    st.sidebar.markdown("## 🔍 **Filtros Avançados**")
    
    # Initialize filters dictionary
    all_filters = {}
    
    # Smart search
    with st.sidebar.expander("🔍 Busca de Municípios", expanded=False):
        search_filters = enhanced_filters.render_smart_search(df, "sidebar_search")
        all_filters['search'] = search_filters
    
    # Regional filters
    with st.sidebar.expander("🗺️ Filtros Regionais", expanded=False):
        regional_filters = enhanced_filters.render_regional_filters(df, "sidebar_region")
        all_filters['regional'] = regional_filters
    
    # Demographic filters
    with st.sidebar.expander("📊 Filtros Demográficos", expanded=False):
        demo_filters = enhanced_filters.render_demographic_economic_filters(df, "sidebar_demo")
        all_filters['demographic'] = demo_filters
    
    # Range sliders
    with st.sidebar.expander("📈 Filtros por Potencial", expanded=False):
        range_filters = enhanced_filters.render_advanced_range_sliders(df, "sidebar_ranges")
        all_filters['ranges'] = range_filters
    
    # Quick filters
    with st.sidebar.expander("⚡ Filtros Rápidos", expanded=True):
        quick_filters = enhanced_filters.render_quick_filters(df, "sidebar_quick")
        if quick_filters:
            all_filters['quick_filter'] = quick_filters
    
    # Apply all filters
    if any(all_filters.values()):
        filtered_df = enhanced_filters.apply_all_filters(df, all_filters)
        
        # Show filter summary
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📋 **Resumo dos Filtros**")
        st.sidebar.info(f"🎯 **{len(filtered_df)} municípios** de {len(df)} total")
        
        if len(filtered_df) < len(df):
            reduction = (1 - len(filtered_df) / len(df)) * 100
            st.sidebar.success(f"✅ Redução: {reduction:.1f}%")
    else:
        filtered_df = df
    
    return {
        'filtered_data': filtered_df,
        'applied_filters': all_filters,
        'filter_summary': {
            'original_count': len(df),
            'filtered_count': len(filtered_df),
            'reduction_percent': (1 - len(filtered_df) / len(df)) * 100 if len(df) > 0 else 0
        }
    }