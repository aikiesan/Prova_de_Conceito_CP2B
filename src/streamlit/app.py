"""
CP2B - Sistema de Análise Geoespacial para Biogás
Aplicação principal do dashboard - CARREGA TODOS OS 645 MUNICÍPIOS
"""

import streamlit as st
import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Imports dos componentes
import sys
import os

# Add both local and project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)

sys.path.extend([current_dir, parent_dir, project_root])

try:
    from components.navigation import render_navigation_sidebar, get_page_config
    from components.minimal_filters import render_sidebar_filters, apply_residue_filters
    from components.filters import RESIDUE_TYPES, AGGREGATE_TYPES
    from components.maps import render_map, render_layer_controls_below_map
    from components.charts import top_municipios_bar
    from components.tables import render_table
    from components.executive_dashboard import render_executive_dashboard
    from components.residue_analysis import render_residue_analysis_dashboard
    from components.advanced_simulations import render_advanced_simulations_page
except ImportError:
    # Fallback for Streamlit Cloud
    from src.streamlit.components.navigation import render_navigation_sidebar, get_page_config
    from src.streamlit.components.minimal_filters import render_sidebar_filters, apply_residue_filters
    from src.streamlit.components.filters import RESIDUE_TYPES, AGGREGATE_TYPES
    from src.streamlit.components.maps import render_map, render_layer_controls_below_map
    from src.streamlit.components.charts import top_municipios_bar
    from src.streamlit.components.tables import render_table
    from src.streamlit.components.executive_dashboard import render_executive_dashboard
    from src.streamlit.components.residue_analysis import render_residue_analysis_dashboard
    from src.streamlit.components.advanced_simulations import render_advanced_simulations_page

try:
    from utils.database import (
        query_df, MunicipalQueries, get_cache_stats, 
        clear_cache, initialize_database
    )
    from utils.calculations import (
        recompute_total_by_sources, render_scenario_simulator, apply_scenario_to_data
    )
    from utils.styling_simple import (
        inject_global_css, create_gradient_header, create_section_header, 
        create_metric_card, create_theme_toggle, create_dashboard_header,
        create_map_section
    )
except ImportError:
    # Fallback for Streamlit Cloud
    from src.streamlit.utils.database import (
        query_df, MunicipalQueries, get_cache_stats, 
        clear_cache, initialize_database
    )
    from src.streamlit.utils.calculations import (
        recompute_total_by_sources, render_scenario_simulator, apply_scenario_to_data
    )
    from src.streamlit.utils.styling_simple import (
        inject_global_css, create_gradient_header, create_section_header, 
        create_metric_card, create_theme_toggle, create_dashboard_header,
        create_map_section
    )

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CP2BDashboard:
    """Classe principal do dashboard CP2B"""
    
    def __init__(self):
        """Inicializar dashboard com configurações padrão"""
        self._configure_page()
        self._initialize_session_state()
    
    def _configure_page(self) -> None:
        """Configurar página do Streamlit"""
        # Configurar estado inicial da sidebar baseado no modo fullscreen
        initial_sidebar_state = "collapsed" if st.session_state.get('fullscreen_mode', False) else "expanded"
        
        st.set_page_config(
            page_title="CP2B - Sistema de Análise Geoespacial para Biogás",
            page_icon="🌱",
            layout="wide",
            initial_sidebar_state=initial_sidebar_state
        )
    
    def _initialize_session_state(self) -> None:
        """Inicializar estado da sessão"""
        default_state = {
            'data_loaded': False,
            'last_error': None,
            'selected_municipios': [],
            'current_filters': {},
            'show_debug': False,
            'data_refresh_needed': False,
            'show_all_municipalities': True  # Nova opção para mostrar todos
        }
        
        for key, value in default_state.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @st.cache_data(ttl=300)
    def load_municipal_data(_self, include_zero_potential: bool = True) -> Optional[pd.DataFrame]:
        """
        Carrega TODOS os 645 municípios (incluindo potencial zero)
        
        Args:
            include_zero_potential: Se True, inclui municípios com potencial = 0
        """
        try:
            logger.info(f"Carregando dados - incluir potencial zero: {include_zero_potential}")
            
            if include_zero_potential:
                # CARREGAR TODOS OS 645 MUNICÍPIOS
                df = MunicipalQueries.get_all_municipalities()
                logger.info(f"Carregados TODOS os municípios: {len(df)}")
            else:
                # Apenas com potencial > 0 (comportamento antigo)
                df = MunicipalQueries.get_municipalities_with_potential()
                logger.info(f"Carregados municípios com potencial: {len(df)}")
            
            if df.empty:
                st.error("Nenhum dado encontrado na base de dados")
                return None
            
            # Limpeza rigorosa de dados - remover NaN completamente
            # Primeiro, substituir NaN por 0 em colunas numéricas
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
            df[numeric_columns] = df[numeric_columns].fillna(0)
            
            # Converter código do município para string
            df['cd_mun'] = df['cd_mun'].astype(str)
            
            # Verificar se há linhas com dados inválidos
            df = df.dropna(subset=['cd_mun', 'nm_mun'])  # Remover se não tem código ou nome
            
            # Remover valores infinitos
            df = df.replace([float('inf'), float('-inf')], 0)
            
            # Garantir que todas as colunas de biogás existem
            biogas_columns = [
                'biogas_cana_nm_ano', 'biogas_soja_nm_ano', 'biogas_milho_nm_ano', 'biogas_bovinos_nm_ano',
                'biogas_cafe_nm_ano', 'biogas_citros_nm_ano', 'biogas_suino_nm_ano', 'biogas_aves_nm_ano',
                'biogas_piscicultura_nm_ano', 'rsu_potencial_nm_habitante_ano', 'rpo_potencial_nm_habitante_ano'
            ]
            
            for col in biogas_columns:
                if col not in df.columns:
                    df[col] = 0
            
            logger.info(f"Dados processados: {len(df)} municípios")
            st.session_state.data_loaded = True
            st.session_state.last_error = None
            
            return df
            
        except Exception as e:
            error_msg = f"Erro ao carregar dados: {str(e)}"
            logger.error(error_msg)
            st.session_state.last_error = error_msg
            return None
    
    def parse_selected_municipalities(self, selected_items: List[str]) -> List[str]:
        """Extrai códigos IBGE dos municípios selecionados"""
        codes = []
        for item in selected_items:
            if item and isinstance(item, str) and item.endswith(")"):
                try:
                    # Formato esperado: "Nome (Código) - Potencial Nm³/ano"
                    if " - " in item:
                        # Novo formato com potencial
                        municipality_part = item.split(" - ")[0]
                        code = municipality_part.split("(")[-1].rstrip(")")
                    else:
                        # Formato antigo: "Nome (Código)"
                        code = item.split("(")[-1].rstrip(")")
                    
                    if code.isdigit():
                        codes.append(code)
                except Exception as e:
                    logger.warning(f"Erro ao extrair código: {e}")
        return codes
    
    def apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Aplica filtros aos dados dos municípios"""
        if df.empty:
            return df
        
        try:
            filtered_df = df.copy()
            original_count = len(filtered_df)
            
            # Filtro por municípios selecionados
            if filters.get("selected_muns"):
                codes = self.parse_selected_municipalities(filters["selected_muns"])
                if codes:
                    filtered_df = filtered_df[filtered_df["cd_mun"].isin(codes)]
                    st.session_state.selected_municipios = codes
                    logger.info(f"Filtro municipal: {original_count} -> {len(filtered_df)} municípios")
            
            # Filtro por faixa de potencial
            min_total = filters.get("total_min", 0)
            max_total = filters.get("total_max", float('inf'))
            
            if min_total > 0 or max_total < float('inf'):
                filtered_df = filtered_df[
                    (filtered_df["total_final_nm_ano"] >= min_total) & 
                    (filtered_df["total_final_nm_ano"] <= max_total)
                ]
                logger.info(f"Filtro potencial: {len(filtered_df)} municípios na faixa {min_total}-{max_total}")
            
            # Recalcular total baseado nas fontes selecionadas
            if filters.get("sources"):
                calculation_mode = filters.get("calculation_mode", "Fontes Selecionadas")
                
                if calculation_mode == "Fontes Selecionadas":
                    filtered_df["total_final_nm_ano"] = filtered_df.apply(
                        lambda row: recompute_total_by_sources(row, filters["sources"]), 
                        axis=1
                    )
                    logger.info("Totais recalculados baseado nas fontes selecionadas")
                # Senão, mantém valores originais do banco
            
            # Aplicar ordenação
            sort_by = filters.get("sort_by", "total_final_nm_ano")
            sort_ascending = filters.get("sort_ascending", False)
            
            if sort_by in filtered_df.columns:
                filtered_df = filtered_df.sort_values(sort_by, ascending=sort_ascending)
            
            # Aplicar limite de resultados
            max_results = filters.get("max_results")
            if max_results and len(filtered_df) > max_results:
                filtered_df = filtered_df.head(max_results)
                logger.info(f"Limitado a {max_results} resultados")
            
            # Aplicar modo de visualização
            viz_mode = filters.get('visualization', {})
            
            if viz_mode.get('mode') == "Por Categoria":
                category = viz_mode.get('category')
                if category == "Agrícola":
                    filtered_df['display_value'] = filtered_df.get('total_agricola_nm_ano', 0)
                elif category == "Pecuária":
                    filtered_df['display_value'] = filtered_df.get('total_pecuaria_nm_ano', 0)
                elif category == "Urbano":
                    filtered_df['display_value'] = filtered_df.get('total_ch4_rsu_rpo', 0)
                else:
                    filtered_df['display_value'] = filtered_df['total_final_nm_ano']
            
            elif viz_mode.get('mode') == "Por Fonte Específica":
                source = viz_mode.get('source')
                if source and source in filtered_df.columns:
                    filtered_df['display_value'] = filtered_df[source]
                else:
                    filtered_df['display_value'] = filtered_df['total_final_nm_ano']
            
            else:  # Total Geral
                filtered_df['display_value'] = filtered_df['total_final_nm_ano']
            
            st.session_state.current_filters = filters
            return filtered_df
            
        except Exception as e:
            logger.error(f"Erro ao aplicar filtros: {e}")
            return df
    
    def render_data_mode_selector(self) -> bool:
        """Renderiza seletor de modo de dados"""
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            show_all = st.checkbox(
                "📍 Mostrar TODOS os 645 municípios",
                value=st.session_state.get('show_all_municipalities', True),
                help="Inclui municípios com potencial zero para análise completa"
            )
            st.session_state.show_all_municipalities = show_all
        
        with col2:
            if st.session_state.get('show_debug', False):
                if not show_all:
                    st.info("Exibindo apenas municípios com potencial > 0")
                else:
                    st.success("Exibindo todos os municípios de São Paulo")
        
        with col3:
            if st.button("🔄 Recarregar"):
                st.cache_data.clear()
                st.rerun()
        
        return show_all
    
    def apply_dashboard_filters(self, df: pd.DataFrame, selected_residues: list, show_zero_values: bool, max_municipalities: int, selection_mode: str = "🎯 Individual") -> pd.DataFrame:
        """Aplica filtros do dashboard com suporte a múltiplos resíduos"""
        
        filtered_df = df.copy()
        
        if selection_mode == "🔄 Múltiplos" and len(selected_residues) > 1:
            # Modo múltiplos resíduos - calcular somatória
            filtered_df['display_value'] = 0.0
            
            # Somar cada resíduo selecionado
            for residue_column in selected_residues:
                if residue_column == "urban_combined":
                    # Combinar RSU + RPO para resíduos urbanos
                    if 'rsu_potencial_nm_habitante_ano' in filtered_df.columns and 'rpo_potencial_nm_habitante_ano' in filtered_df.columns:
                        filtered_df['display_value'] += (
                            filtered_df['rsu_potencial_nm_habitante_ano'].fillna(0) + 
                            filtered_df['rpo_potencial_nm_habitante_ano'].fillna(0)
                        )
                elif residue_column in filtered_df.columns:
                    filtered_df['display_value'] += filtered_df[residue_column].fillna(0)
            
            # Armazenar quais resíduos foram combinados para referência
            filtered_df['combined_residues'] = str(selected_residues)
            
        else:
            # Modo individual (comportamento original)
            selected_residue = selected_residues[0] if selected_residues else "total_final_nm_ano"
            
            if selected_residue == "urban_combined":
                # Combinar RSU + RPO para resíduos urbanos
                if 'rsu_potencial_nm_habitante_ano' in filtered_df.columns and 'rpo_potencial_nm_habitante_ano' in filtered_df.columns:
                    filtered_df['display_value'] = (
                        filtered_df['rsu_potencial_nm_habitante_ano'].fillna(0) + 
                        filtered_df['rpo_potencial_nm_habitante_ano'].fillna(0)
                    )
                else:
                    filtered_df['display_value'] = filtered_df['total_final_nm_ano']
            elif selected_residue in filtered_df.columns:
                filtered_df['display_value'] = filtered_df[selected_residue]
            else:
                filtered_df['display_value'] = filtered_df['total_final_nm_ano']
        
        # Filtrar municípios com potencial zero se necessário
        if not show_zero_values:
            filtered_df = filtered_df[filtered_df['display_value'] > 0]
        
        # Limitar número de municípios
        if len(filtered_df) > max_municipalities:
            filtered_df = filtered_df.nlargest(max_municipalities, 'display_value')
        
        return filtered_df
    
    def calculate_residue_breakdown(self, df: pd.DataFrame, selected_residues: list) -> dict:
        """Calcula breakdown individual de cada resíduo selecionado"""
        breakdown = {}
        
        for residue_column in selected_residues:
            if residue_column == "urban_combined":
                # Combinar RSU + RPO
                if 'rsu_potencial_nm_habitante_ano' in df.columns and 'rpo_potencial_nm_habitante_ano' in df.columns:
                    total = (df['rsu_potencial_nm_habitante_ano'].fillna(0) + df['rpo_potencial_nm_habitante_ano'].fillna(0)).sum()
                    breakdown['Resíduos Urbanos'] = total
                else:
                    breakdown['Resíduos Urbanos'] = 0
            elif residue_column in df.columns:
                breakdown[residue_column] = df[residue_column].fillna(0).sum()
        
        return breakdown
    
    def render_summary_metrics(self, df: pd.DataFrame, show_all_mode: bool) -> None:
        """Renderiza cards de resumo"""
        
        # Estatísticas básicas
        total_municipios = len(df)
        with_potential = len(df[df['total_final_nm_ano'] > 0])
        without_potential = total_municipios - with_potential
        
        # Cards modernos com ícones
        col1, col2, col3, col4 = st.columns(4)
        
        total_potential = df['total_final_nm_ano'].sum() if not df.empty else 0
        
        with col1:
            if show_all_mode:
                st.metric(
                    "🏛️ Total de Municípios",
                    f"{total_municipios:,}",
                    delta=f"{with_potential} com potencial",
                    help=f"Total: {total_municipios} | Com potencial: {with_potential} | Zero: {without_potential}"
                )
            else:
                st.metric(
                    "🏛️ Municípios com Potencial",
                    f"{total_municipios:,}",
                    help="Apenas municípios com potencial > 0"
                )
        
        with col2:
            # Converter para milhões para melhor visualização
            potential_millions = total_potential / 1_000_000
            st.metric(
                "⚡ Potencial Total",
                f"{potential_millions:.1f}M Nm³/ano",
                help="Potencial total de biogás de todos os municípios"
            )
        
        with col3:
            if with_potential > 0:
                avg_potential = df[df['total_final_nm_ano'] > 0]['total_final_nm_ano'].mean()
                avg_thousands = avg_potential / 1_000
                st.metric(
                    "📊 Média Municipal",
                    f"{avg_thousands:.0f}k Nm³/ano",
                    help=f"Média de {with_potential} municípios com potencial"
                )
            else:
                st.metric("📊 Média Municipal", "0 Nm³/ano", help="Sem dados")
        
        with col4:
            max_potential = df['total_final_nm_ano'].max() if not df.empty else 0
            max_city = ""
            if not df.empty and max_potential > 0:
                max_city = df.loc[df['total_final_nm_ano'].idxmax(), 'nm_mun']
                max_millions = max_potential / 1_000_000
                st.metric(
                    "🥇 Maior Potencial",
                    f"{max_millions:.1f}M Nm³/ano",
                    help=f"Município: {max_city}"
                )
            else:
                st.metric("🥇 Maior Potencial", "0 Nm³/ano", help="Sem dados")
    
    def render_error_handling(self) -> bool:
        """Interface de tratamento de erros"""
        if st.session_state.get('last_error'):
            st.error(f"Erro na aplicação: {st.session_state.last_error}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Tentar Novamente"):
                    st.session_state.data_refresh_needed = True
                    st.rerun()
            
            with col2:
                if st.button("🗂️ Limpar Cache"):
                    st.cache_data.clear()
                    clear_cache()
                    st.rerun()
                    
            with col3:
                if st.button("🐛 Debug"):
                    st.session_state.show_debug = True
                    st.rerun()
            return True
        return False
    
    def run(self) -> None:
        """Executa a aplicação principal com navegação por páginas"""
        
        try:
            # Inicializar banco com validação robusta
            if not initialize_database():
                st.error("❌ Falha na inicialização do banco de dados")
                from utils.database import DB_PATH
                if not DB_PATH.exists():
                    st.error(f"Arquivo não encontrado: {DB_PATH}")
                    st.info("Execute: `python -m src.database.data_loader`")
                else:
                    st.info(f"Arquivo existe: {DB_PATH}")
                    st.info("Tente: Limpar Cache ou Recarregar dados")
                st.stop()
            
            # Navigation sidebar
            with st.sidebar:
                current_page = render_navigation_sidebar()
            
            # Get page configuration
            page_config = get_page_config(current_page)
            
            # Apply CSS theme
            dark_mode = st.session_state.get('dark_mode', False)
            inject_global_css(dark_mode)
            
            # Minimal page header (only for non-dashboard pages)
            if current_page != "dashboard":
                create_gradient_header(
                    page_config['title'],
                    page_config['subtitle'],
                    "🌱"
                )
            
            # Load data
            if st.session_state.get('data_refresh_needed', False):
                st.cache_data.clear()
                st.session_state.data_refresh_needed = False
            
            # Load all municipalities data
            df = self.load_municipal_data(include_zero_potential=True)
            
            if df is None:
                st.error("❌ Não foi possível carregar os dados")
                return
            
            # Store data stats in session state
            st.session_state.total_municipalities = len(df)
            st.session_state.total_potential = df['total_final_nm_ano'].sum()
            st.session_state.data_loaded = True
            
            # Render page content based on current page
            if current_page == "dashboard":
                self.render_dashboard_page(df, page_config)
            elif current_page == "simulations":
                self.render_simulations_page(df, page_config) 
            elif current_page == "analysis":
                self.render_analysis_page(df, page_config)
            elif current_page == "data":
                self.render_data_page(df, page_config)
            elif current_page == "debug":
                self.render_debug_page(df, page_config)
                    
        except Exception as e:
            error_msg = f"Erro crítico: {str(e)}"
            logger.error(error_msg, exc_info=True)
            st.error(error_msg)
            if st.session_state.get('show_debug', False):
                st.exception(e)
    
    def render_dashboard_page(self, df: pd.DataFrame, page_config: dict) -> None:
        """Renders the main dashboard page with map as THE primary feature"""
        
        # Opções de resíduos
        residue_options = {
            "⚡ Potencial Total": "total_final_nm_ano",
            "🌾 Total Agrícola": "total_agricola_nm_ano",
            "🐄 Total Pecuária": "total_pecuaria_nm_ano", 
            "🗑️ Resíduos Urbanos": "urban_combined",
            "🌾 Cana-de-açúcar": "biogas_cana_nm_ano",
            "🌱 Soja": "biogas_soja_nm_ano",
            "🌽 Milho": "biogas_milho_nm_ano",
            "☕ Café": "biogas_cafe_nm_ano",
            "🍊 Citros": "biogas_citros_nm_ano",
            "🐄 Bovinos": "biogas_bovinos_nm_ano",
            "🐷 Suínos": "biogas_suino_nm_ano",
            "🐔 Aves": "biogas_aves_nm_ano",
            "🐟 Piscicultura": "biogas_piscicultura_nm_ano",
            "🗑️ RSU (Municipal)": "rsu_potencial_nm_habitante_ano",
            "🍃 RPO (Jardim/Poda)": "rpo_potencial_nm_habitante_ano",
            "🌲 Silvicultura": "silvicultura_nm_ano"
        }
        
        # HEADER ORGANIZADO COM SELEÇÃO MÚLTIPLA E MODO FULLSCREEN
        selected_residues, show_zero_values, max_municipalities, selection_mode, fullscreen_mode = create_dashboard_header(residue_options)
        
        # APLICAR FILTROS COM SUPORTE A MÚLTIPLOS RESÍDUOS
        filtered_df = self.apply_dashboard_filters(df, selected_residues, show_zero_values, max_municipalities, selection_mode)
        
        # Atualizar contadores no session state para o header
        if selection_mode == "🔄 Múltiplos" and len(selected_residues) > 1:
            # Para múltiplos resíduos, contar municípios que têm pelo menos um dos resíduos > 0
            potential_count = len(filtered_df[filtered_df['display_value'] > 0])
        else:
            # Para seleção individual
            selected_residue = selected_residues[0] if selected_residues else "total_final_nm_ano"
            if selected_residue in df.columns:
                potential_count = len(df[df[selected_residue] > 0])
            elif selected_residue == "urban_combined":
                potential_count = len(df[(df.get('rsu_potencial_nm_habitante_ano', 0) > 0) | (df.get('rpo_potencial_nm_habitante_ano', 0) > 0)])
            else:
                potential_count = len(df[df['total_final_nm_ano'] > 0])
        
        st.session_state.potential_count = potential_count
        
        # Update session state with count for sidebar display
        st.session_state.filtered_count = len(filtered_df)
        
        if filtered_df.empty:
            st.warning("🔍 Nenhum dado encontrado com os filtros aplicados.")
            return
        
        # APLICAR CSS FULLSCREEN SE NECESSÁRIO
        if fullscreen_mode:
            st.markdown("""
            <style>
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                max-width: 100% !important;
            }
            .stSidebar {
                display: none !important;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # MAPA PRINCIPAL COM SEÇÃO ESTILIZADA
        try:
            # Título dinâmico baseado no modo de seleção
            if selection_mode == "🔄 Múltiplos" and len(selected_residues) > 1:
                reverse_residue_options = {v: k for k, v in residue_options.items()}
                residue_names = [reverse_residue_options.get(res, res).replace("⚡", "").replace("🌾", "").replace("🐄", "").replace("🗑️", "").replace("🐔", "").replace("🌱", "").replace("🌽", "").replace("☕", "").replace("🍊", "").replace("🐷", "").replace("🐟", "").replace("🌲", "").replace("🍃", "").strip() for res in selected_residues]
                if len(residue_names) <= 3:
                    map_title = f"🗺️ Combinação: {' + '.join(residue_names)}"
                else:
                    map_title = f"🗺️ Combinação: {' + '.join(residue_names[:2])} (+{len(residue_names)-2} mais)"
            else:
                # Modo individual
                reverse_residue_options = {v: k for k, v in residue_options.items()}
                residue_name = reverse_residue_options.get(selected_residues[0], selected_residues[0]).replace("⚡", "").replace("🌾", "").replace("🐄", "").replace("🗑️", "").replace("🐔", "").replace("🌱", "").replace("🌽", "").replace("☕", "").replace("🍊", "").replace("🐷", "").replace("🐟", "").replace("🌲", "").replace("🍃", "").strip()
                map_title = f"🗺️ {residue_name}"
            
            # Adicionar indicador de modo fullscreen ao título
            if fullscreen_mode:
                map_title += " - 🖥️ Modo Tela Cheia"
            
            # Seção do mapa
            if not fullscreen_mode:
                create_map_section(map_title)
            else:
                # Em modo fullscreen, apenas título simples
                st.markdown(f"## {map_title}")
                st.markdown("---")
            
            # PRIMEIRO: RENDERIZAR MAPA (FOCO PRINCIPAL)
            # Inicializar estado das camadas se não existir
            if 'layer_controls_state' not in st.session_state:
                st.session_state.layer_controls_state = {
                    'limite_sp': False,
                    'regioes_admin': False, 
                    'areas_urbanas': False,
                    'rodovias_estaduais': False,
                    'gasodutos_transporte': False,
                    'gasodutos_distribuicao': False,
                    'plantas_biogas': False
                }
            
            # Usar estado atual das camadas para o mapa
            layer_controls_result = {'layer_controls': st.session_state.layer_controls_state}
            
            render_map(
                filtered_df,  # Dados já filtrados pelo dashboard
                selected_municipios=st.session_state.get('selected_municipios', []),
                layer_controls=layer_controls_result,  # Estado atual das camadas
                filters={
                    'pre_filtered': True,  # Indica que dados já vêm filtrados
                    'selection_mode': selection_mode,
                    'selected_residues': selected_residues,
                    'combined_residues': selection_mode == "🔄 Múltiplos" and len(selected_residues) > 1,
                    'fullscreen_mode': fullscreen_mode  # Passar modo fullscreen para o mapa
                }
            )
            
            st.caption("💡 Clique nos pontos do mapa para mais informações sobre cada município")
            
            # DEPOIS: CONTROLES DE CAMADAS ABAIXO DO MAPA
            if not fullscreen_mode:
                updated_controls = render_layer_controls_below_map(filtered_df)
                # Atualizar estado da sessão com as novas seleções
                if updated_controls.get('layer_controls'):
                    st.session_state.layer_controls_state.update(updated_controls['layer_controls'])
        
            # MOSTRAR BREAKDOWN EM MODO NÃO-FULLSCREEN
            if not fullscreen_mode:
                
                # Mostrar breakdown de múltiplos resíduos se aplicável
                if selection_mode == "🔄 Múltiplos" and len(selected_residues) > 1:
                    st.markdown("### 📊 **Breakdown dos Resíduos Combinados**")
                    
                    breakdown = self.calculate_residue_breakdown(filtered_df, selected_residues)
                    
                    if breakdown:
                        cols = st.columns(min(len(breakdown), 4))
                        
                        for idx, (residue_name, value) in enumerate(breakdown.items()):
                            with cols[idx % 4]:
                                # Limpar nome do resíduo
                                clean_name = residue_name.replace('biogas_', '').replace('_nm_ano', '').replace('_', ' ').title()
                                st.metric(
                                    label=clean_name,
                                    value=f"{value/1_000_000:.1f}M Nm³/ano",
                                    help=f"Contribuição de {clean_name} para o total combinado"
                                )
                        
                        # Mostrar total combinado
                        total_combined = sum(breakdown.values())
                        st.metric(
                            label="🔄 **Total Combinado**",
                            value=f"{total_combined/1_000_000:.1f}M Nm³/ano",
                            delta=f"{len(selected_residues)} resíduos selecionados"
                        )
                    else:
                        st.warning("Nenhum resíduo encontrado para os filtros aplicados")
                    
                    st.markdown("---")
                
                # Remover mensagens desnecessárias para interface limpa
            else:
                # Apenas informações essenciais em fullscreen
                if selection_mode == "🔄 Múltiplos" and len(selected_residues) > 1:
                    breakdown = self.calculate_residue_breakdown(filtered_df, selected_residues)
                    if breakdown:
                        total_combined = sum(breakdown.values())
                        st.info(f"🔄 **Combinando {len(selected_residues)} resíduos** | Total: {total_combined/1_000_000:.1f}M Nm³/ano")
                
                st.info("🖥️ **Modo Tela Cheia Ativo** - Desmarque '🖥️ Mapa Grande' no header para ver controles adicionais")
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar o mapa: {e}")
            if st.session_state.get('show_debug', False):
                st.exception(e)
        
        # Seções expansíveis organizadas - OCULTAR EM FULLSCREEN
        if not fullscreen_mode:
            st.markdown("---")
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                with st.expander("🏆 **Top 10 Municípios**", expanded=False):
                    if not filtered_df.empty:
                        top_data = filtered_df.nlargest(10, 'total_final_nm_ano')
                        
                        for idx, (_, row) in enumerate(top_data.iterrows(), 1):
                            col1, col2, col3 = st.columns([1, 4, 2])
                            
                            with col1:
                                st.markdown(f"**#{idx}**")
                            
                            with col2:
                                st.markdown(f"**{row['nm_mun']}**")
                            
                            with col3:
                                potential_k = row['total_final_nm_ano'] / 1_000
                                st.markdown(f"`{potential_k:,.0f}k Nm³/ano`")
                    else:
                        st.info("Nenhum município encontrado")
            
            with col_exp2:
                with st.expander("📊 **Métricas Rápidas**", expanded=False):
                    if not filtered_df.empty:
                        # Mostrar métricas baseadas no resíduo selecionado
                        if 'display_value' in filtered_df.columns:
                            total_potential = filtered_df['display_value'].sum()
                            max_potential = filtered_df['display_value'].max()
                            avg_potential = filtered_df[filtered_df['display_value'] > 0]['display_value'].mean() if len(filtered_df[filtered_df['display_value'] > 0]) > 0 else 0
                        else:
                            total_potential = filtered_df['total_final_nm_ano'].sum()
                            max_potential = filtered_df['total_final_nm_ano'].max()
                            avg_potential = filtered_df[filtered_df['total_final_nm_ano'] > 0]['total_final_nm_ano'].mean() if len(filtered_df[filtered_df['total_final_nm_ano'] > 0]) > 0 else 0
                        
                        st.metric("⚡ Total", f"{total_potential/1_000_000:.1f}M Nm³/ano")
                        st.metric("📈 Máximo", f"{max_potential/1_000:.0f}k Nm³/ano")
                        st.metric("📊 Média", f"{avg_potential/1_000:.0f}k Nm³/ano")
                    else:
                        st.info("Nenhum dado encontrado")
            
            # Análises detalhadas em seção separada
            with st.expander("📈 **Análises Detalhadas**", expanded=False):
                if not filtered_df.empty:
                    render_executive_dashboard(filtered_df)
                else:
                    st.info("Nenhum dado disponível para análise")
        
        # Ações rápidas compactas - OCULTAR EM FULLSCREEN
        if not fullscreen_mode:
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📥 Download", use_container_width=True):
                    # Get columns without duplicates for CSV
                    csv_columns = ['nm_mun', 'cd_mun']
                    if 'selected_residues' in locals():
                        for residue in selected_residues:
                            if residue not in csv_columns and residue in filtered_df.columns:
                                csv_columns.append(residue)
                    if 'total_final_nm_ano' not in csv_columns:
                        csv_columns.append('total_final_nm_ano')
                    
                    csv_columns = [col for col in csv_columns if col in filtered_df.columns]
                    csv = filtered_df[csv_columns].to_csv(index=False)
                    st.download_button(
                        "⬇️ CSV",
                        csv,
                        f"cp2b_biogas_dados.csv",
                        "text/csv"
                    )
            
            with col2:
                if st.button("🎯 Simulações", use_container_width=True):
                    st.session_state.current_page = 'simulations'
                    st.rerun()
            
            with col3:
                if st.button("📈 Análises", use_container_width=True):
                    st.session_state.current_page = 'analysis'  
                    st.rerun()
            
            with col4:
                if st.button("📋 Dados", use_container_width=True):
                    st.session_state.current_page = 'data'
                    st.rerun()
    
    def render_simulations_page(self, df: pd.DataFrame, page_config: dict) -> None:
        """Renders the advanced simulations page with substrate combinations and hotspot detection"""
        
        # Get filters from sidebar for data filtering
        filters = render_sidebar_filters("simulations")
        filtered_df = apply_residue_filters(df, filters)
        st.session_state.filtered_count = len(filtered_df)
        
        if filtered_df.empty:
            st.warning("🔍 No data matches your current filter selection.")
            st.info("💡 Try adjusting your filters to see simulation options.")
            return
        
        # Render the advanced simulations interface
        try:
            render_advanced_simulations_page(filtered_df)
            
        except Exception as e:
            st.error(f"❌ Advanced Simulation Error: {e}")
            
            # Fallback to basic simulation interface
            st.markdown("---")
            st.warning("🔄 Fallback to Basic Simulation Mode")
            
            # Basic simulation fallback
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📍 Municipalities", len(filtered_df))
            with col2:
                total_potential = filtered_df['total_final_nm_ano'].sum()
                st.metric("⚡ Base Potential", f"{total_potential/1_000_000:.1f}M Nm³/ano")
            with col3:
                st.metric("🎯 Basic Mode", "Active")
            
            # Basic scenario simulator
            scenario_config = render_scenario_simulator()
            
            if not filtered_df.empty:
                scenario_df = apply_scenario_to_data(filtered_df, scenario_config)
                
                st.markdown("## 📊 Basic Scenario Impact")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    original_total = filtered_df['total_final_nm_ano'].sum()
                    st.metric("📈 Original", f"{original_total/1_000_000:.1f}M Nm³/ano")
                
                with col2:
                    scenario_total = scenario_df['total_final_scenario'].sum()
                    st.metric("🎯 Scenario", f"{scenario_total/1_000_000:.1f}M Nm³/ano")
                
                with col3:
                    if original_total > 0:
                        impact_percent = ((scenario_total - original_total) / original_total) * 100
                        st.metric("📊 Impact", f"{impact_percent:+.1f}%", 
                                delta=f"{(scenario_total - original_total)/1_000_000:+.1f}M Nm³/ano")
            
            if st.session_state.get('show_debug', False):
                st.exception(e)
    
    def render_analysis_page(self, df: pd.DataFrame, page_config: dict) -> None:
        """Renders the detailed analysis page"""
        
        # Get filters from sidebar
        filters = render_sidebar_filters("analysis")
        filtered_df = apply_residue_filters(df, filters)
        st.session_state.filtered_count = len(filtered_df)
        
        if filtered_df.empty:
            st.warning("🔍 Nenhum dado encontrado com os filtros atuais.")
            return
        
        # Quick metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Municípios", len(filtered_df))
        with col2:
            total_potential = filtered_df['total_final_nm_ano'].sum()
            st.metric("⚡ Potencial Total", f"{total_potential/1_000_000:.1f}M Nm³/ano")
        with col3:
            st.metric("📈 Modo Análise", "Ativo")
        
        st.markdown("---")
        
        # Main analysis content
        try:
            render_residue_analysis_dashboard(filtered_df)
            
            st.markdown("---")
            
            # Charts section
            create_section_header("Gráficos Detalhados", "📊", "success")
            chart_data = filtered_df[filtered_df['total_final_nm_ano'] > 0]
            if not chart_data.empty:
                top_municipios_bar(chart_data)
            else:
                st.info("Nenhum município com potencial > 0 para análise gráfica")
                
        except Exception as e:
            st.error(f"❌ Erro na Análise: {e}")
            if st.session_state.get('show_debug', False):
                st.exception(e)
    
    def render_data_page(self, df: pd.DataFrame, page_config: dict) -> None:
        """Renders the data explorer page"""
        
        # Get filters from sidebar
        filters = render_sidebar_filters("data")
        filtered_df = apply_residue_filters(df, filters)
        st.session_state.filtered_count = len(filtered_df)
        
        if filtered_df.empty:
            st.warning("🔍 Nenhum dado encontrado com os filtros atuais.")
            return
        
        # Quick metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📍 Municípios", len(filtered_df))
        with col2:
            total_potential = filtered_df['total_final_nm_ano'].sum()
            st.metric("⚡ Potencial Total", f"{total_potential/1_000_000:.1f}M Nm³/ano")
        with col3:
            st.metric("📋 Explorador de Dados", "Ativo")
        
        st.markdown("---")
        
        create_section_header("Explorador de Dados", "📋", "info")
        
        # Show all residue columns if selected
        if filters.get('selected_residues'):
            # Start with basic info columns
            display_columns = ['nm_mun', 'cd_mun']
            
            # Add selected residue columns (avoid duplicates)
            for residue in filters['selected_residues']:
                if residue not in display_columns:
                    display_columns.append(residue)
            
            # Add total at the end if not already included
            if 'total_final_nm_ano' not in display_columns:
                display_columns.append('total_final_nm_ano')
            
            # Filter only existing columns
            available_columns = [col for col in display_columns if col in filtered_df.columns]
        else:
            # Default columns
            available_columns = [
                'nm_mun', 'cd_mun', 'total_final_nm_ano', 
                'total_agricola_nm_ano', 'total_pecuaria_nm_ano', 'area_km2'
            ]
            available_columns = [col for col in available_columns if col in filtered_df.columns]
        
        try:
            render_table(filtered_df[available_columns])
            
            # Export options
            st.markdown("### 📤 Opções de Exportação")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 Download CSV", use_container_width=True):
                    csv = filtered_df[available_columns].to_csv(index=False)
                    st.download_button(
                        "⬇️ Baixar CSV",
                        csv,
                        f"cp2b_dados_{filters.get('view_mode', 'all').lower()}.csv",
                        "text/csv",
                        use_container_width=True
                    )
            
            with col2:
                st.metric("📊 Registros", len(filtered_df))
            
            with col3:
                st.metric("📋 Colunas", len(available_columns))
                
        except Exception as e:
            st.error(f"❌ Erro no Explorador de Dados: {e}")
            if st.session_state.get('show_debug', False):
                st.exception(e)
    
    def render_debug_page(self, df: pd.DataFrame, page_config: dict) -> None:
        """Renders the debug and system info page"""
        
        create_section_header("System Information", "🔧", "danger")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Database Info:**")
            st.write(f"Total records: {len(df)}")
            st.write(f"Data columns: {len(df.columns)}")
            st.write(f"With potential > 0: {len(df[df['total_final_nm_ano'] > 0])}")
            st.write(f"Zero potential: {len(df[df['total_final_nm_ano'] == 0])}")
        
        with col2:
            st.markdown("**Available Residue Types:**")
            for category in ['Agricultural', 'Livestock', 'Urban', 'Forestry']:
                residues = [k for k, v in RESIDUE_TYPES.items() if v['category'] == category]
                st.write(f"{category}: {len(residues)} types")
        
        st.markdown("### 📊 Data Sample")
        st.dataframe(df.head(20))
        
        if st.button("🗂️ Clear All Caches"):
            st.cache_data.clear()
            clear_cache()
            st.success("All caches cleared!")
            st.rerun()


def main():
    """Função principal"""
    dashboard = CP2BDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()