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
    from components.sidebar import render_sidebar
    from components.maps import render_map
    from components.charts import top_municipios_bar
    from components.tables import render_table
    from components.executive_dashboard import render_executive_dashboard
    from components.residue_analysis import render_residue_analysis_dashboard
except ImportError:
    # Fallback for Streamlit Cloud
    from src.streamlit.components.sidebar import render_sidebar
    from src.streamlit.components.maps import render_map
    from src.streamlit.components.charts import top_municipios_bar
    from src.streamlit.components.tables import render_table
    from src.streamlit.components.executive_dashboard import render_executive_dashboard
    from src.streamlit.components.residue_analysis import render_residue_analysis_dashboard

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
        create_metric_card, create_theme_toggle
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
        create_metric_card, create_theme_toggle
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
        st.set_page_config(
            page_title="CP2B - Sistema de Análise Geoespacial para Biogás",
            page_icon="🌱",
            layout="wide",
            initial_sidebar_state="expanded"
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
            
            # Limpeza de dados
            df = df.fillna(0)
            df['cd_mun'] = df['cd_mun'].astype(str)
            
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
        """Executa a aplicação principal"""
        
        try:
            # Inicializar banco com validação robusta
            if not initialize_database():
                st.error("❌ Falha na inicialização do banco de dados")
                
                # Diagnóstico melhorado
                from utils.database import DB_PATH
                if not DB_PATH.exists():
                    st.error(f"Arquivo não encontrado: {DB_PATH}")
                    st.info("Execute: `python -m src.database.data_loader`")
                else:
                    st.info(f"Arquivo existe: {DB_PATH}")
                    st.info("Tente: Limpar Cache ou Recarregar dados")
                
                st.stop()
            
            # Toggle de tema
            dark_mode = create_theme_toggle()
            
            # Aplicar CSS com tema selecionado
            inject_global_css(dark_mode)
            
            # Cabeçalho principal
            create_gradient_header(
                "CP2B - Sistema de Análise Geoespacial para Biogás", 
                "Plataforma inteligente para análise do potencial de biogás em São Paulo",
                "🌱"
            )
            
            # Controle de modo de dados
            show_all_municipalities = self.render_data_mode_selector()
            st.markdown("---")
            
            # Verificar erros
            if self.render_error_handling():
                return
            
            # Sidebar com filtros
            with st.sidebar:
                filters = render_sidebar()
                
                st.markdown("---")
                st.subheader("⚙️ Controles do Sistema")
                
                st.session_state.show_debug = st.checkbox("Modo Debug")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗂️ Cache"):
                        clear_cache()
                        st.success("Limpo!")
                
                with col2:
                    if st.button("📊 Stats"):
                        try:
                            stats = get_cache_stats()
                            st.json(stats)
                        except:
                            st.error("Erro")
            
            # Carregar dados
            if st.session_state.get('data_refresh_needed', False):
                st.cache_data.clear()
                st.session_state.data_refresh_needed = False
            
            # Carregar com base no modo selecionado
            df = self.load_municipal_data(include_zero_potential=show_all_municipalities)
            
            if df is None:
                st.stop()
            
            # Aplicar filtros
            filtered_df = self.apply_filters(df, filters)
            
            if filtered_df.empty:
                if st.session_state.get('show_debug', False):
                    st.warning("Nenhum município encontrado com os filtros aplicados")
                    st.info("Ajuste os filtros na sidebar ou mude o modo de dados")
                return
            
            # Métricas de resumo
            self.render_summary_metrics(filtered_df, show_all_municipalities)
            st.markdown("---")
            
            # Layout em tabs - Adicionada nova aba para análise de resíduos
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "🗺️ Mapa Interativo", 
                "🎯 Simulador", 
                "📈 Dashboard Executivo",
                "🔬 Análise Resíduos",
                "📊 Análises", 
                "📋 Tabela", 
                "🔧 Debug"
            ])
            
            with tab1:
                create_section_header("Mapa Interativo", "🗺️", "info")
                
                # Informações sobre os dados do mapa
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.session_state.get('show_debug', False):
                        with_potential_count = len(filtered_df[filtered_df['total_final_nm_ano'] > 0])
                        zero_potential_count = len(filtered_df[filtered_df['total_final_nm_ano'] == 0])
                        
                        st.info(
                            f"📊 Dados do mapa: {len(filtered_df)} municípios total | "
                            f"{with_potential_count} com potencial | "
                            f"{zero_potential_count} potencial zero"
                        )
                
                with col2:
                    map_all_data = st.checkbox(
                        "🗺️ Todos no mapa",
                        value=True,
                        help="Mostra todos os municípios filtrados no mapa"
                    )
                
                try:
                    # Decidir quais dados enviar para o mapa
                    if map_all_data:
                        map_data = filtered_df
                    else:
                        # Apenas com potencial > 0
                        map_data = filtered_df[filtered_df['total_final_nm_ano'] > 0]
                        if len(map_data) == 0:
                            if st.session_state.get('show_debug', False):
                                st.warning("Nenhum município com potencial > 0 para exibir no mapa")
                            map_data = filtered_df.head(10)  # Fallback
                    
                    render_map(
                        map_data,
                        selected_municipios=st.session_state.get('selected_municipios', []),
                        layer_controls=filters.get('layer_controls', {}),
                        filters=filters
                    )
                    
                except Exception as e:
                    st.error(f"Erro no mapa: {e}")
                    if st.session_state.get('show_debug'):
                        st.exception(e)
            
            with tab2:
                create_section_header("Simulador de Cenários", "🎯", "warning")
                
                # Renderizar simulador
                scenario_config = render_scenario_simulator()
                
                if not filtered_df.empty:
                    # Aplicar cenário aos dados
                    scenario_df = apply_scenario_to_data(filtered_df, scenario_config)
                    
                    # Comparação de resultados
                    st.markdown("### 📊 Impacto do Cenário")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        original_total = filtered_df['total_final_nm_ano'].sum()
                        st.metric(
                            "Potencial Original",
                            f"{original_total:,.0f} Nm³/ano",
                            help="Potencial total com fatores atuais"
                        )
                    
                    with col2:
                        scenario_total = scenario_df['total_final_scenario'].sum()
                        st.metric(
                            "Potencial Cenário",
                            f"{scenario_total:,.0f} Nm³/ano",
                            help=f"Potencial com cenário {scenario_config['scenario_type']}"
                        )
                    
                    with col3:
                        if original_total > 0:
                            impact_percent = ((scenario_total - original_total) / original_total) * 100
                            st.metric(
                                "Impacto",
                                f"{impact_percent:+.1f}%",
                                delta=f"{scenario_total - original_total:+,.0f} Nm³/ano",
                                help="Variação percentual do potencial"
                            )
                        else:
                            st.metric("Impacto", "N/A")
                    
                    # Top municípios mais impactados
                    if 'total_final_scenario' in scenario_df.columns:
                        scenario_df['scenario_impact'] = scenario_df['total_final_scenario'] - scenario_df['total_final_nm_ano']
                        scenario_df['scenario_impact_percent'] = (scenario_df['scenario_impact'] / scenario_df['total_final_nm_ano'] * 100).fillna(0)
                        
                        st.markdown("### 🚀 Municípios com Maior Impacto")
                        
                        # Top 10 com maior impacto absoluto
                        top_impact = scenario_df.nlargest(10, 'scenario_impact')[
                            ['nm_mun', 'total_final_nm_ano', 'total_final_scenario', 'scenario_impact', 'scenario_impact_percent']
                        ].copy()
                        
                        top_impact.columns = ['Município', 'Original (Nm³/ano)', 'Cenário (Nm³/ano)', 'Diferença (Nm³/ano)', 'Impacto (%)']
                        
                        # Formatação
                        for col in ['Original (Nm³/ano)', 'Cenário (Nm³/ano)', 'Diferença (Nm³/ano)']:
                            top_impact[col] = top_impact[col].apply(lambda x: f"{x:,.0f}")
                        top_impact['Impacto (%)'] = top_impact['Impacto (%)'].apply(lambda x: f"{x:+.1f}%")
                        
                        st.dataframe(top_impact, hide_index=True)
                else:
                    st.info("Aplique filtros para ver o simulador de cenários")
            
            with tab3:
                # Dashboard Executivo
                render_executive_dashboard(filtered_df)
            
            with tab4:
                # Nova aba de análise detalhada de resíduos
                render_residue_analysis_dashboard(filtered_df)
            
            with tab5:
                create_section_header("Análises Detalhadas", "📊", "success")
                
                # Só mostrar gráfico se houver dados com potencial
                chart_data = filtered_df[filtered_df['total_final_nm_ano'] > 0]
                if not chart_data.empty:
                    top_municipios_bar(chart_data)
                else:
                    if st.session_state.get('show_debug', False):
                        st.info("Nenhum município com potencial > 0 para análise gráfica")
            
            with tab6:
                create_section_header("Dados Tabulares", "📋", "info")
                columns = ['nm_mun', 'cd_mun', 'total_final_nm_ano', 'total_agricola_nm_ano', 'total_pecuaria_nm_ano', 'area_km2']
                available_columns = [col for col in columns if col in filtered_df.columns]
                render_table(filtered_df[available_columns])
            
            with tab7:
                if st.session_state.get('show_debug'):
                    create_section_header("Sistema e Debug", "🔧", "danger")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Dados:**")
                        st.write(f"Shape original: {df.shape}")
                        st.write(f"Shape filtrado: {filtered_df.shape}")
                        st.write(f"Modo: {'Todos' if show_all_municipalities else 'Apenas com potencial'}")
                    
                    with col2:
                        st.write("**Estatísticas:**")
                        st.write(f"Com potencial: {len(filtered_df[filtered_df['total_final_nm_ano'] > 0])}")
                        st.write(f"Potencial zero: {len(filtered_df[filtered_df['total_final_nm_ano'] == 0])}")
                        st.write(f"Range: {filtered_df['total_final_nm_ano'].min():.0f} - {filtered_df['total_final_nm_ano'].max():.0f}")
                    
                    st.subheader("Amostra dos Dados")
                    st.dataframe(filtered_df.head(10))
                else:
                    st.info("Ative 'Modo Debug' na sidebar para ver informações técnicas")
                    
        except Exception as e:
            error_msg = f"Erro crítico: {str(e)}"
            logger.error(error_msg, exc_info=True)
            st.error(error_msg)


def main():
    """Função principal"""
    dashboard = CP2BDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()