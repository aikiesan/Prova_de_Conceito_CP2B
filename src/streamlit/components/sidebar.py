"""
Sidebar elaborada com filtros avançados para análise de biogás
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any
from utils.database import query_df, MunicipalQueries
import logging

logger = logging.getLogger(__name__)

class SidebarFilters:
    """Classe para gerenciar filtros da sidebar"""
    
    # Mapeamento das fontes de biogás com metadados
    BIOGAS_SOURCES = {
        'total_ch4_rsu_rpo': {
            'label': 'RSU + RPO (Resíduos Urbanos)',
            'category': 'Urbano',
            'icon': '🗑️',
            'description': 'Resíduos Sólidos Urbanos e de Poda'
        },
        'biogas_cana': {
            'label': 'Cana-de-açúcar',
            'category': 'Agrícola',
            'icon': '🌾',
            'description': 'Bagaço e palha da cana'
        },
        'biogas_soja': {
            'label': 'Soja',
            'category': 'Agrícola', 
            'icon': '🌱',
            'description': 'Resíduos da cultura da soja'
        },
        'biogas_milho': {
            'label': 'Milho',
            'category': 'Agrícola',
            'icon': '🌽',
            'description': 'Resíduos da cultura do milho'
        },
        'biogas_cafe': {
            'label': 'Café',
            'category': 'Agrícola',
            'icon': '☕',
            'description': 'Polpa e casca do café'
        },
        'biogas_citros': {
            'label': 'Citros',
            'category': 'Agrícola',
            'icon': '🍊',
            'description': 'Resíduos de laranja e limão'
        },
        'biogas_bovino': {
            'label': 'Bovinos',
            'category': 'Pecuária',
            'icon': '🐄',
            'description': 'Esterco bovino'
        },
        'biogas_suinos': {
            'label': 'Suínos',
            'category': 'Pecuária',
            'icon': '🐷',
            'description': 'Dejetos de suínos'
        },
        'biogas_aves': {
            'label': 'Aves',
            'category': 'Pecuária',
            'icon': '🐔',
            'description': 'Dejetos de aves'
        },
        'biogas_piscicultura': {
            'label': 'Piscicultura',
            'category': 'Pecuária',
            'icon': '🐟',
            'description': 'Resíduos da aquicultura'
        }
    }
    
    # Totalizadores
    TOTALS = {
        'total_agricola': {
            'label': 'Total Agrícola',
            'icon': '🌾',
            'description': 'Soma de todas as fontes agrícolas'
        },
        'total_pecuaria': {
            'label': 'Total Pecuária', 
            'icon': '🐄',
            'description': 'Soma de todas as fontes pecuárias'
        },
        'total_final_nm_ano': {
            'label': 'TOTAL GERAL',
            'icon': '🎯',
            'description': 'Potencial total de biogás do município'
        }
    }

@st.cache_data(ttl=600)
def load_municipalities_for_sidebar() -> pd.DataFrame:
    """Carrega municípios para dropdown da sidebar com cache"""
    try:
        df = query_df("""
            SELECT cd_mun, nm_mun, total_final_nm_ano 
            FROM municipios 
            ORDER BY nm_mun ASC
        """)
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar municípios para sidebar: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_filter_statistics() -> Dict[str, Any]:
    """Obtém estatísticas para configurar filtros dinamicamente"""
    try:
        stats = MunicipalQueries.get_aggregated_stats()
        return {
            'total_municipalities': stats.get('total_municipalities', 645),
            'min_potential': stats.get('min_biogas_potential', 0),
            'max_potential': stats.get('max_biogas_potential', 1000000),
            'avg_potential': stats.get('avg_biogas_potential', 50000),
            'total_potential': stats.get('total_biogas_potential', 50000000)
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {
            'total_municipalities': 645,
            'min_potential': 0,
            'max_potential': 1000000,
            'avg_potential': 50000,
            'total_potential': 50000000
        }

def render_municipality_selector() -> List[str]:
    """Renderiza seletor de municípios com busca avançada"""
    
    st.sidebar.header("🎯 Seleção de Municípios")
    
    # Carregar dados
    df_muns = load_municipalities_for_sidebar()
    
    if df_muns.empty:
        st.sidebar.error("Erro ao carregar municípios")
        return []
    
    # Opções de seleção
    selection_mode = st.sidebar.radio(
        "Modo de Seleção:",
        ["Busca Manual", "Top Municípios", "Todos"],
        help="Escolha como selecionar os municípios para análise"
    )
    
    selected_muns = []
    
    if selection_mode == "Busca Manual":
        # Busca com filtro de texto
        search_term = st.sidebar.text_input(
            "🔍 Buscar Município:",
            placeholder="Digite parte do nome...",
            help="Busque municípios por nome"
        )
        
        if search_term:
            # Filtrar municípios que contêm o termo
            filtered_muns = df_muns[
                df_muns['nm_mun'].str.contains(search_term, case=False, na=False)
            ].head(20)  # Limitar a 20 resultados
            
            if not filtered_muns.empty:
                st.sidebar.info(f"Encontrados {len(filtered_muns)} municípios")
                mun_options = [
                    f"{row['nm_mun']} ({row['cd_mun']}) - {row['total_final_nm_ano']:,.0f} Nm³/ano" 
                    for _, row in filtered_muns.iterrows()
                ]
            else:
                st.sidebar.warning("Nenhum município encontrado")
                mun_options = []
        else:
            # Mostrar todos se não há termo de busca
            mun_options = [
                f"{row['nm_mun']} ({row['cd_mun']}) - {row['total_final_nm_ano']:,.0f} Nm³/ano" 
                for _, row in df_muns.head(50).iterrows()  # Limitar a 50 iniciais
            ]
        
        selected_muns = st.sidebar.multiselect(
            "Selecionar Municípios:",
            mun_options,
            help="Selecione um ou mais municípios para análise"
        )
    
    elif selection_mode == "Top Municípios":
        # Seleção por ranking
        top_n = st.sidebar.slider(
            "📊 Top N Municípios:",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            help="Selecionar os N municípios com maior potencial"
        )
        
        # Mostrar os top municípios
        top_muns = df_muns.nlargest(top_n, 'total_final_nm_ano')
        
        selected_muns = [
            f"{row['nm_mun']} ({row['cd_mun']}) - {row['total_final_nm_ano']:,.0f} Nm³/ano"
            for _, row in top_muns.iterrows()
        ]
        
        st.sidebar.success(f"✅ Selecionados top {top_n} municípios")
    
    else:  # Todos
        st.sidebar.info("🌍 Todos os municípios serão analisados")
        selected_muns = []  # Lista vazia significa "todos"
    
    return selected_muns

def render_potential_filters() -> Dict[str, float]:
    """Renderiza filtros de potencial de biogás"""
    
    st.sidebar.header("📊 Filtros de Potencial")
    
    # Obter estatísticas para configurar ranges
    stats = get_filter_statistics()
    
    # Filtro por faixa de potencial total
    st.sidebar.subheader("🎯 Potencial Total (Nm³/ano)")
    
    # Opções pré-definidas
    preset_ranges = {
        "Todos": (0, stats['max_potential']),
        "Alto (> 100k)": (100000, stats['max_potential']),
        "Médio (10k - 100k)": (10000, 100000),
        "Baixo (< 10k)": (0, 10000),
        "Customizado": None
    }
    
    range_preset = st.sidebar.selectbox(
        "Faixa Pré-definida:",
        list(preset_ranges.keys()),
        help="Selecione uma faixa comum ou customize"
    )
    
    if range_preset == "Customizado":
        # Slider customizado
        min_val, max_val = st.sidebar.slider(
            "Faixa Customizada:",
            min_value=0.0,
            max_value=float(stats['max_potential']),
            value=(0.0, float(stats['max_potential'])),
            step=1000.0,
            format="%.0f",
            help="Arraste para definir faixa customizada"
        )
    else:
        min_val, max_val = preset_ranges[range_preset]
    
    # Mostrar estatísticas da faixa selecionada
    if range_preset != "Todos":
        st.sidebar.info(f"📈 Faixa: {min_val:,.0f} - {max_val:,.0f} Nm³/ano")
    
    return {"total_min": min_val, "total_max": max_val}

def render_source_filters() -> Dict[str, bool]:
    """Renderiza filtros por fonte de biogás"""
    
    st.sidebar.header("🔬 Fontes de Biogás")
    
    # Controles gerais
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("✅ Marcar Todas", help="Selecionar todas as fontes"):
            for source in SidebarFilters.BIOGAS_SOURCES.keys():
                st.session_state[f"source_{source}"] = True
    
    with col2:
        if st.button("❌ Desmarcar Todas", help="Desselecionar todas as fontes"):
            for source in SidebarFilters.BIOGAS_SOURCES.keys():
                st.session_state[f"source_{source}"] = False
    
    # Organizar por categoria
    categories = {}
    for source_key, source_info in SidebarFilters.BIOGAS_SOURCES.items():
        category = source_info['category']
        if category not in categories:
            categories[category] = []
        categories[category].append((source_key, source_info))
    
    sources_selected = {}
    
    # Renderizar por categoria
    for category, sources in categories.items():
        
        st.sidebar.subheader(f"📋 {category}")
        
        # Controle de categoria
        category_key = f"category_{category.lower()}"
        
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            category_label = f"Todas as fontes {category.lower()}s"
        with col2:
            all_category = st.sidebar.checkbox(
                f"Todas as {category.lower()}",
                key=category_key,
                help=f"Selecionar todas as fontes {category.lower()}s"
            )
        
        # Se "todas da categoria" foi marcado/desmarcado
        if all_category:
            for source_key, _ in sources:
                st.session_state[f"source_{source_key}"] = True
        
        # Renderizar checkboxes individuais
        for source_key, source_info in sources:
            # Estado padrão: todas marcadas
            default_state = st.session_state.get(f"source_{source_key}", True)
            
            selected = st.sidebar.checkbox(
                f"{source_info['icon']} {source_info['label']}",
                value=default_state,
                key=f"source_{source_key}",
                help=source_info['description']
            )
            
            sources_selected[source_key] = selected
    
    # Resumo das seleções
    selected_count = sum(sources_selected.values())
    total_count = len(sources_selected)
    
    if selected_count == 0:
        st.sidebar.error("⚠️ Nenhuma fonte selecionada!")
    elif selected_count == total_count:
        st.sidebar.success(f"✅ Todas as {total_count} fontes selecionadas")
    else:
        st.sidebar.info(f"📊 {selected_count} de {total_count} fontes selecionadas")
    
    return sources_selected

def render_analysis_options() -> Dict[str, Any]:
    """Renderiza opções avançadas de análise"""
    
    st.sidebar.header("⚙️ Opções de Análise")
    
    # Modo de cálculo do total
    calculation_mode = st.sidebar.radio(
        "📊 Modo de Cálculo:",
        ["Fontes Selecionadas", "Total Original"],
        help="""
        Fontes Selecionadas: Recalcula total baseado apenas nas fontes marcadas
        Total Original: Usa o valor total original do banco de dados
        """
    )
    
    # Ordenação padrão
    sort_options = {
        'total_final_nm_ano': 'Potencial Total',
        'nm_mun': 'Nome do Município',
        'total_agricola': 'Total Agrícola', 
        'total_pecuaria': 'Total Pecuária',
        'area_km2': 'Área (km²)'
    }
    
    sort_by = st.sidebar.selectbox(
        "🔄 Ordenar Por:",
        list(sort_options.keys()),
        format_func=lambda x: sort_options[x],
        help="Como ordenar os resultados"
    )
    
    sort_ascending = st.sidebar.checkbox(
        "📈 Ordem Crescente",
        value=False,
        help="Marque para ordem crescente, desmarque para decrescente"
    )
    
    # Limite de resultados
    limit_results = st.sidebar.checkbox(
        "🔢 Limitar Resultados",
        value=False,
        help="Limitar número de municípios exibidos"
    )
    
    max_results = None
    if limit_results:
        max_results = st.sidebar.slider(
            "Máximo de Resultados:",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )
    
    return {
        'calculation_mode': calculation_mode,
        'sort_by': sort_by,
        'sort_ascending': sort_ascending,
        'max_results': max_results
    }

def render_visualization_mode() -> Dict[str, Any]:
    """Controla o modo de visualização do potencial - versão simplificada"""
    
    st.sidebar.header("🎨 Visualização")
    
    # Informação sobre a legenda interativa
    st.sidebar.info("📊 **Legenda Interativa:** Use a legenda no mapa (canto superior direito) para visualizar estatísticas detalhadas e trocar entre diferentes fontes.")
    
    # Controles básicos
    viz_mode = st.sidebar.radio(
        "Modo de Análise:",
        ["Total Geral", "Por Categoria", "Por Fonte Específica"],
        help="Escolha o tipo de análise. A legenda no mapa mostrará estatísticas específicas."
    )
    
    selected_category = None
    selected_source = None
    
    if viz_mode == "Por Categoria":
        selected_category = st.sidebar.selectbox(
            "Categoria:",
            ["Agrícola", "Pecuária", "Urbano"],
            help="Visualizar apenas uma categoria - veja estatísticas na legenda do mapa"
        )
        
        # Mostrar preview das fontes da categoria
        if selected_category == "Agrícola":
            st.sidebar.caption("🌾 Inclui: Cana, Soja, Milho, Café, Citros")
        elif selected_category == "Pecuária":
            st.sidebar.caption("🐄 Inclui: Bovinos, Suínos, Aves, Piscicultura")
        elif selected_category == "Urbano":
            st.sidebar.caption("🗑️ Inclui: RSU + RPO")
    
    elif viz_mode == "Por Fonte Específica":
        source_options = {
            'biogas_cana': '🌾 Cana-de-açúcar',
            'biogas_soja': '🌱 Soja',
            'biogas_milho': '🌽 Milho',
            'biogas_bovino': '🐄 Bovinos',
            'biogas_cafe': '☕ Café',
            'biogas_citros': '🍊 Citros',
            'biogas_suinos': '🐷 Suínos',
            'biogas_aves': '🐔 Aves',
            'biogas_piscicultura': '🐟 Piscicultura',
            'total_ch4_rsu_rpo': '🗑️ RSU + RPO'
        }
        
        selected_source = st.sidebar.selectbox(
            "Fonte Específica:",
            list(source_options.keys()),
            format_func=lambda x: source_options[x],
            help="Visualizar apenas uma fonte - estatísticas detalhadas na legenda do mapa"
        )
        
        # Mostrar dica sobre comparação
        st.sidebar.caption("💡 Compare diferentes fontes alterando esta seleção")
    
    else:  # Total Geral
        st.sidebar.caption("🎯 Visualizando potencial total de biogás por município")
    
    return {
        'mode': viz_mode,
        'category': selected_category,
        'source': selected_source
    }

def render_layer_controls() -> Dict[str, bool]:
    """Renderiza controles simplificados de camadas do mapa"""
    
    st.sidebar.header("🗺️ Contexto Geográfico")
    
    # Informação sobre controle avançado
    st.sidebar.info("🎛️ **Controle Avançado:** Use o painel de camadas no mapa para controle individual e detalhado.")
    
    # Controles simplificados
    layers = {}
    
    layers['limite_sp'] = st.sidebar.checkbox(
        "🔴 Mostrar Limite de SP", 
        value=False,
        help="Adiciona contorno do estado para contexto geográfico"
    )
    
    layers['plantas_biogas'] = st.sidebar.checkbox(
        "🏭 Mostrar Usinas Existentes", 
        value=False,
        help="Exibe plantas de biogás já em operação para comparação"
    )
    
    layers['regioes_admin'] = st.sidebar.checkbox(
        "🌍 Mostrar Regiões Admin.", 
        value=False,
        help="Adiciona divisões administrativas regionais"
    )
    
    # Status simplificado
    active_count = sum(layers.values())
    if active_count == 0:
        st.sidebar.caption("📍 Visualização focada nos municípios")
    elif active_count == 1:
        active_layer = [k for k, v in layers.items() if v][0]
        layer_names = {
            'limite_sp': 'Limite de SP',
            'plantas_biogas': 'Usinas Existentes', 
            'regioes_admin': 'Regiões Admin.'
        }
        st.sidebar.caption(f"📊 + {layer_names[active_layer]} para contexto")
    else:
        st.sidebar.caption(f"📊 + {active_count} camadas contextuais ativas")
    
    return layers

def render_export_options() -> Dict[str, bool]:
    """Renderiza opções de exportação"""
    
    st.sidebar.header("📤 Exportação")
    
    export_options = {
        'enable_csv': st.sidebar.checkbox(
            "📄 Habilitar Export CSV",
            help="Permite download dos dados filtrados em CSV"
        ),
        'enable_excel': st.sidebar.checkbox(
            "📊 Habilitar Export Excel", 
            help="Permite download em formato Excel"
        ),
        'enable_geojson': st.sidebar.checkbox(
            "🗺️ Habilitar Export GeoJSON",
            help="Exporta dados com geometrias para SIG"
        )
    }
    
    if any(export_options.values()):
        st.sidebar.info("✅ Opções de exportação estarão disponíveis após aplicar filtros")
    
    return export_options

def render_sidebar() -> Dict[str, Any]:
    """
    Renderiza sidebar completa e retorna todos os filtros aplicados
    
    Returns:
        Dicionário com todos os filtros e configurações selecionadas
    """
    
    # Logo/título da sidebar
    st.sidebar.title("🌱 CP2B Filters")
    st.sidebar.markdown("---")
    
    # Seção 1: Seleção de municípios
    selected_muns = render_municipality_selector()
    st.sidebar.markdown("---")
    
    # Seção 2: Filtros de potencial
    potential_filters = render_potential_filters()
    st.sidebar.markdown("---")
    
    # Seção 3: Fontes de biogás
    source_filters = render_source_filters()
    st.sidebar.markdown("---")
    
    # Seção 4: Controles de camadas do mapa
    layer_controls = render_layer_controls()
    st.sidebar.markdown("---")
    
    # Seção 5: Modo de visualização
    viz_options = render_visualization_mode()
    st.sidebar.markdown("---")
    
    # Seção 6: Opções de análise
    analysis_options = render_analysis_options()
    st.sidebar.markdown("---")
    
    # Seção 7: Opções de exportação
    export_options = render_export_options()
    st.sidebar.markdown("---")
    
    # Botão de reset
    if st.sidebar.button("🔄 Resetar Todos os Filtros", help="Limpa todos os filtros aplicados"):
        # Limpar session state relacionado aos filtros
        for key in list(st.session_state.keys()):
            if key.startswith(('source_', 'category_')):
                del st.session_state[key]
        st.rerun()
    
    # Informações da sessão (modo debug)
    if st.sidebar.checkbox("🐛 Modo Debug Sidebar"):
        st.sidebar.subheader("Debug Info")
        st.sidebar.json({
            'selected_municipalities': len(selected_muns),
            'potential_range': f"{potential_filters['total_min']:,.0f} - {potential_filters['total_max']:,.0f}",
            'sources_selected': sum(source_filters.values()),
            'calculation_mode': analysis_options['calculation_mode']
        })
    
    # Compilar todos os filtros
    all_filters = {
        'selected_muns': selected_muns,
        'total_min': potential_filters['total_min'],
        'total_max': potential_filters['total_max'],
        'sources': source_filters,
        'layer_controls': layer_controls,
        'visualization': viz_options,
        'calculation_mode': analysis_options['calculation_mode'],
        'sort_by': analysis_options['sort_by'],
        'sort_ascending': analysis_options['sort_ascending'],
        'max_results': analysis_options['max_results'],
        'export_options': export_options
    }
    
    return all_filters


