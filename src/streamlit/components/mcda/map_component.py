# CP2B MCDA Map Component
# Componente de mapa especializado para análise MCDA das propriedades CP2B

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configurações do mapa
MCDA_MAP_CONFIG = {
    'center_rmc': [-22.9, -47.1],  # Centro aproximado da RMC
    'default_zoom': 10,
    'tile_layer': 'OpenStreetMap',
    'max_properties_display': 1000,  # Limite para performance
}

def create_mcda_base_map(center: list = None, zoom: int = None) -> folium.Map:
    """
    Cria mapa base para análise MCDA
    
    Args:
        center: Coordenadas do centro [lat, lon]
        zoom: Nível de zoom inicial
        
    Returns:
        folium.Map: Mapa base configurado
    """
    center = center or MCDA_MAP_CONFIG['center_rmc']
    zoom = zoom or MCDA_MAP_CONFIG['default_zoom']
    
    # Criar mapa base
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )
    
    # Adicionar controle de layers
    folium.LayerControl().add_to(m)
    
    return m

def add_properties_to_map(m: folium.Map, df_properties: pd.DataFrame, max_display: int = None) -> folium.Map:
    """
    Adiciona propriedades ao mapa como pontos clicáveis
    
    Args:
        m: Mapa folium base
        df_properties: DataFrame com propriedades
        max_display: Máximo de propriedades a mostrar
        
    Returns:
        folium.Map: Mapa com propriedades adicionadas
    """
    try:
        max_display = max_display or MCDA_MAP_CONFIG['max_properties_display']
        
        if df_properties.empty:
            logger.warning("Nenhuma propriedade para exibir no mapa")
            return m
            
        # Limitar quantidade para performance
        df_display = df_properties.head(max_display)
        
        # Criar cluster de marcadores para melhor performance
        marker_cluster = MarkerCluster(
            name="Propriedades SICAR",
            overlay=True,
            control=True
        ).add_to(m)
        
        # Para MVP, vamos usar pontos simples
        # TODO: Implementar geometrias reais dos polígonos
        
        for idx, property_data in df_display.iterrows():
            # Por enquanto, usar coordenadas simuladas baseadas no município
            # TODO: Extrair coordenadas reais das geometrias .geo
            lat, lon = get_mock_coordinates(property_data.get('municipio', 'Campinas'))
            
            # Cor baseada no score MCDA
            score = property_data.get('mcda_score', 0)
            color = get_score_color(score)
            
            # Criar popup com informações básicas
            popup_html = create_property_popup(property_data)
            
            # Adicionar marcador
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                popup=folium.Popup(popup_html, max_width=300),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(marker_cluster)
            
        logger.info(f"✅ {len(df_display)} propriedades adicionadas ao mapa")
        return m
        
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar propriedades ao mapa: {str(e)}")
        return m

def get_score_color(score: float) -> str:
    """
    Retorna cor baseada no score MCDA
    
    Args:
        score: Score MCDA (0-100)
        
    Returns:
        str: Código da cor
    """
    if score >= 80:
        return '#00ff00'  # Verde - Excelente
    elif score >= 60:
        return '#ffff00'  # Amarelo - Bom
    elif score >= 40:
        return '#ff8000'  # Laranja - Regular
    else:
        return '#ff0000'  # Vermelho - Baixo

def get_mock_coordinates(municipio: str) -> tuple:
    """
    Retorna coordenadas simuladas baseadas no município (apenas para MVP)
    TODO: Substituir por coordenadas reais das geometrias
    
    Args:
        municipio: Nome do município
        
    Returns:
        tuple: (latitude, longitude)
    """
    # Coordenadas aproximadas dos municípios da RMC
    mock_coords = {
        'Campinas': [-22.9056, -47.0608],
        'Americana': [-22.7392, -47.3313],
        'Sumaré': [-22.8219, -47.2669],
        'Hortolândia': [-22.8583, -47.2200],
        'Indaiatuba': [-23.0922, -47.2178],
        'Santa Bárbara d\'Oeste': [-22.7539, -47.4147],
        'Nova Odessa': [-22.7856, -47.2950],
        'Valinhos': [-22.9706, -46.9956],
        'Vinhedo': [-23.0300, -46.9755],
        'Itatiba': [-23.0053, -46.8378],
        'Jaguariúna': [-22.7058, -46.9856],
        'Pedreira': [-22.7417, -46.9025],
        'Morungaba': [-22.8756, -46.7944],
        'Monte Mor': [-22.9456, -47.3106],
        'Paulínia': [-22.7611, -47.1544],
        'Cosmópolis': [-22.6458, -47.1917],
        'Artur Nogueira': [-22.5736, -47.1744],
        'Engenheiro Coelho': [-22.4856, -47.2133],
        'Holambra': [-22.6319, -47.0547],
        'Santo Antônio de Posse': [-22.6089, -46.9178],
    }
    
    # Retorna coordenadas do município ou coordenadas padrão de Campinas
    return mock_coords.get(municipio, [-22.9056, -47.0608])

def create_property_popup(property_data: Dict[str, Any]) -> str:
    """
    Cria HTML do popup para propriedade
    
    Args:
        property_data: Dados da propriedade
        
    Returns:
        str: HTML do popup
    """
    try:
        cod_imovel = property_data.get('cod_imovel', 'N/A')
        municipio = property_data.get('municipio', 'N/A')
        mcda_score = property_data.get('mcda_score', 0)
        ranking = property_data.get('ranking', 'N/A')
        
        popup_html = f"""
        <div style='font-family: Arial; max-width: 250px;'>
            <h4 style='margin-bottom: 10px; color: #2c5530;'>
                🏭 Propriedade SICAR
            </h4>
            
            <p style='margin: 5px 0;'>
                <strong>Município:</strong> {municipio}
            </p>
            
            <p style='margin: 5px 0;'>
                <strong>Score MCDA:</strong> 
                <span style='color: {get_score_color(mcda_score)}; font-weight: bold;'>
                    {mcda_score:.1f}/100
                </span>
            </p>
            
            <p style='margin: 5px 0;'>
                <strong>Ranking:</strong> #{ranking}
            </p>
            
            <div style='margin-top: 10px; text-align: center;'>
                <button onclick='selectProperty("{cod_imovel}")' 
                        style='background: #2c5530; color: white; border: none; 
                               padding: 8px 16px; border-radius: 4px; cursor: pointer;'>
                    📊 Ver Relatório Completo
                </button>
            </div>
            
            <p style='font-size: 0.8em; color: #666; margin-top: 8px;'>
                Código: {cod_imovel[:20]}...
            </p>
        </div>
        """
        
        return popup_html
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar popup: {str(e)}")
        return f"<div>Propriedade: {property_data.get('cod_imovel', 'N/A')}</div>"

def render_mcda_map(df_properties: pd.DataFrame, 
                   map_center: list = None,
                   map_zoom: int = None,
                   filters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Renderiza mapa MCDA completo no Streamlit
    
    Args:
        df_properties: DataFrame com propriedades
        map_center: Centro do mapa
        map_zoom: Zoom do mapa
        filters: Filtros aplicados
        
    Returns:
        Dict com informações de interação do mapa (futuro)
    """
    try:
        if df_properties.empty:
            st.warning("⚠️ Nenhuma propriedade encontrada para exibir no mapa")
            return None
            
        # Criar mapa base
        m = create_mcda_base_map(center=map_center, zoom=map_zoom)
        
        # Adicionar propriedades
        m = add_properties_to_map(m, df_properties)
        
        # Adicionar JavaScript para capturar cliques (futuro)
        # TODO: Implementar detecção de cliques em propriedades
        
        # Renderizar mapa no Streamlit
        map_data = st_folium(
            m, 
            width=None, 
            height=600,
            returned_objects=["last_clicked"]
        )
        
        # TODO: Processar cliques e retornar dados de interação
        interaction_data = None
        
        # Log de sucesso
        logger.info(f"✅ Mapa MCDA renderizado com {len(df_properties)} propriedades")
        
        return interaction_data
        
    except Exception as e:
        logger.error(f"❌ Erro ao renderizar mapa MCDA: {str(e)}")
        st.error(f"Erro ao carregar mapa: {str(e)}")
        return None

def render_mcda_map_sidebar(df_properties: pd.DataFrame) -> Dict[str, Any]:
    """
    Renderiza sidebar com controles do mapa MCDA
    
    Args:
        df_properties: DataFrame com propriedades
        
    Returns:
        Dict com filtros e configurações aplicadas
    """
    try:
        st.sidebar.markdown("## 🎯 Controles MCDA")
        st.sidebar.markdown("---")
        
        # Estatísticas gerais
        if not df_properties.empty:
            total_properties = len(df_properties)
            avg_score = df_properties['mcda_score'].mean() if 'mcda_score' in df_properties.columns else 0
            
            st.sidebar.metric("Total de Propriedades", f"{total_properties:,}")
            st.sidebar.metric("Score Médio", f"{avg_score:.1f}")
            
        # Filtros
        st.sidebar.markdown("### 🔍 Filtros")
        
        # Filtro por score mínimo
        score_min = st.sidebar.slider(
            "Score MCDA Mínimo:",
            min_value=0, 
            max_value=100, 
            value=st.session_state.get('cp2b_filter_score_min', 0),
            help="Mostra apenas propriedades com score igual ou superior"
        )
        
        # Filtro por município
        municipalities = ['Todos'] + sorted(df_properties['municipio'].unique().tolist()) if 'municipio' in df_properties.columns and not df_properties.empty else ['Todos']
        
        municipality_filter = st.sidebar.selectbox(
            "Filtrar por Município:",
            options=municipalities,
            index=0,
            help="Selecione um município específico para análise"
        )
        
        # Busca por código SICAR
        st.sidebar.markdown("### 🔎 Busca Direta")
        search_code = st.sidebar.text_input(
            "Código da Propriedade:",
            value=st.session_state.get('cp2b_search_query', ''),
            placeholder="Digite parte do código SICAR...",
            help="Busca por código específico da propriedade"
        )
        
        # Configurações de visualização
        st.sidebar.markdown("### ⚙️ Visualização")
        
        max_properties = st.sidebar.slider(
            "Limite Máximo (Manual):",
            min_value=500,
            max_value=12000,
            value=8000,
            step=500,
            help="Limite manual - o sistema de zoom pode usar menos automaticamente"
        )
        
        # Retornar configurações
        filters = {
            'score_min': score_min,
            'municipality': municipality_filter,
            'search_query': search_code,
            'max_properties': max_properties
        }
        
        return filters
        
    except Exception as e:
        logger.error(f"❌ Erro ao renderizar sidebar MCDA: {str(e)}")
        return {}

def apply_mcda_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplica filtros aos dados MCDA
    
    Args:
        df: DataFrame original
        filters: Dicionário com filtros
        
    Returns:
        pd.DataFrame: DataFrame filtrado
    """
    try:
        if df.empty:
            return df
            
        df_filtered = df.copy()
        
        # Filtro por score mínimo
        if 'score_min' in filters and 'mcda_score' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['mcda_score'] >= filters['score_min']]
            
        # Filtro por município
        if filters.get('municipality', 'Todos') != 'Todos' and 'municipio' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['municipio'] == filters['municipality']]
            
        # Busca por código
        if filters.get('search_query', '').strip() and 'cod_imovel' in df_filtered.columns:
            search_term = filters['search_query'].strip().lower()
            df_filtered = df_filtered[
                df_filtered['cod_imovel'].str.lower().str.contains(search_term, na=False)
            ]
            
        # Limite máximo
        if 'max_properties' in filters:
            df_filtered = df_filtered.head(filters['max_properties'])
            
        logger.info(f"✅ Filtros aplicados: {len(df_filtered)} propriedades restantes")
        return df_filtered
        
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar filtros MCDA: {str(e)}")
        return df