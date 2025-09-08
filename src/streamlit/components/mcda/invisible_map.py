# CP2B Invisible Polygons Map
# Mapa limpo com polígonos invisíveis para detecção de clique

import streamlit as st
import pandas as pd
import folium
import json
from shapely.geometry import Point, shape
from streamlit_folium import st_folium
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def create_invisible_polygons_map(df_properties: pd.DataFrame,
                                 center: list = None,
                                 zoom: int = None,
                                 zoom_bounds: dict = None) -> folium.Map:
    """
    Cria mapa limpo com polígonos invisíveis para detecção de clique
    
    Args:
        df_properties: DataFrame com propriedades e geometrias
        center: Centro do mapa [lat, lon]
        zoom: Nível de zoom
        
    Returns:
        folium.Map: Mapa com polígonos invisíveis
    """
    try:
        center = center or [-22.9, -47.1]  # Centro da RMC
        zoom = zoom or 10
        
        # Criar mapa base limpo
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        if df_properties.empty:
            logger.warning("⚠️ Nenhuma propriedade para adicionar")
            return m
        
        logger.info(f"🗺️ Adicionando {len(df_properties)} polígonos com bordas para detecção de clique")
        
        # Adicionar polígonos com bordas visíveis para todas as propriedades
        for idx, row in df_properties.iterrows():
            try:
                if 'geometry_json' not in row or pd.isna(row['geometry_json']):
                    continue
                    
                geo_json = json.loads(row['geometry_json'])
                cod_imovel = row.get('cod_imovel', 'N/A')
                municipio = row.get('municipio', 'N/A')
                score = row.get('mcda_score', 0)
                
                # Criar popup informativo (só aparece no clique)
                popup_content = create_minimal_popup(row)
                
                # Adicionar polígono com BORDAS OTIMIZADAS para performance
                border_only_polygon = folium.GeoJson(
                    geo_json,
                    style_function=lambda feature, score=score: {
                        'fillColor': 'transparent',      # Preenchimento invisível
                        'color': get_border_color(score), # Cor da borda baseada no score
                        'weight': 1,                     # Borda muito fina para performance
                        'fillOpacity': 0,                # Sem preenchimento
                        'opacity': 0.4                   # Borda mais transparente para performance
                    },
                    popup=folium.Popup(popup_content, max_width=280),
                    tooltip=None  # Remover tooltip para melhor performance
                )
                
                # Adicionar ao mapa
                border_only_polygon.add_to(m)
                
            except Exception as e:
                logger.debug(f"Erro ao adicionar polígono com borda {idx}: {str(e)}")
                continue
        
        # Adicionar apenas algumas referências visuais importantes
        add_visual_references(m)
        
        logger.info(f"✅ Mapa criado com {len(df_properties)} polígonos com bordas coloridas")
        return m
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar mapa com polígonos com bordas: {str(e)}")
        return folium.Map(location=center, zoom_start=zoom)

def get_border_color(score: float) -> str:
    """Retorna cor da borda baseada no score MCDA"""
    if score >= 80:
        return '#00AA00'  # Verde escuro - Excelente
    elif score >= 65:
        return '#66BB00'  # Verde - Muito Bom  
    elif score >= 50:
        return '#BBBB00'  # Amarelo - Bom
    elif score >= 35:
        return '#FF8800'  # Laranja - Regular
    else:
        return '#FF4444'  # Vermelho - Baixo

def create_minimal_popup(property_data: pd.Series) -> str:
    """Cria popup minimalista para polígono invisível"""
    try:
        cod_imovel = property_data.get('cod_imovel', 'N/A')
        municipio = property_data.get('municipio', 'N/A')
        mcda_score = property_data.get('mcda_score', 0)
        ranking = property_data.get('ranking', 'N/A')
        
        # Cor de fundo baseada no score
        if mcda_score >= 70:
            bg_color = '#d4edda'  # Verde claro
            text_color = '#155724'
        elif mcda_score >= 50:
            bg_color = '#fff3cd'  # Amarelo claro
            text_color = '#856404'
        else:
            bg_color = '#f8d7da'  # Vermelho claro
            text_color = '#721c24'
        
        popup_html = f"""
        <div style='font-family: Arial; max-width: 280px; padding: 15px; 
                    background: {bg_color}; border-radius: 10px; border: 2px solid {text_color};'>
            <h3 style='margin: 0 0 10px 0; color: {text_color}; text-align: center;'>
                🏭 Propriedade SICAR
            </h3>
            
            <div style='text-align: center; margin: 10px 0;'>
                <div style='font-size: 1.2em; font-weight: bold; color: {text_color};'>
                    Score MCDA: {mcda_score:.1f}/100
                </div>
                <div style='font-size: 0.9em; color: {text_color}; margin-top: 5px;'>
                    Ranking: #{ranking} | {municipio}
                </div>
            </div>
            
            <div style='margin: 15px 0; text-align: center; font-size: 0.9em;'>
                <div style='background: {text_color}; color: white; 
                           padding: 8px 12px; border-radius: 5px; 
                           font-weight: bold;'>
                    ✅ Propriedade Identificada!
                </div>
                <div style='margin-top: 8px; font-size: 0.8em; opacity: 0.9;'>
                    Veja os detalhes abaixo do mapa
                </div>
            </div>
            
            <div style='font-size: 0.7em; color: {text_color}; text-align: center; opacity: 0.8;'>
                {cod_imovel[:30]}...
            </div>
        </div>
        """
        
        return popup_html
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar popup: {str(e)}")
        return f"<div>Propriedade: {property_data.get('cod_imovel', 'N/A')}</div>"

def add_visual_references(m: folium.Map) -> None:
    """Adiciona referências visuais importantes ao mapa"""
    try:
        # Adicionar apenas marcadores para cidades principais da RMC
        main_cities = [
            {'name': 'Campinas', 'coords': [-22.9056, -47.0608], 'icon': '🏙️'},
            {'name': 'Americana', 'coords': [-22.7392, -47.3313], 'icon': '🏭'},
            {'name': 'Sumaré', 'coords': [-22.8219, -47.2669], 'icon': '🏪'},
            {'name': 'Indaiatuba', 'coords': [-23.0922, -47.2178], 'icon': '🏢'},
            {'name': 'Valinhos', 'coords': [-22.9706, -46.9956], 'icon': '🌳'},
        ]
        
        # Adicionar apenas marcador principal para referência
        folium.Marker(
            location=main_cities[0]['coords'],  # Só Campinas
            popup=folium.Popup(f"<b>🏙️ Campinas</b><br>Centro RMC", max_width=120),
            tooltip="🏙️ Campinas - Centro RMC",
            icon=folium.Icon(color='darkblue', icon='info-sign')
        ).add_to(m)
        
        # Adicionar legenda informativa com cores das bordas
        legend_html = """
        <div style='position: fixed; 
                    top: 10px; right: 10px; width: 280px; height: 180px; 
                    background-color: rgba(255, 255, 255, 0.95); 
                    border: 2px solid #2c5530; z-index: 9999; 
                    font-size: 11px; padding: 12px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);'>
            <h4 style='margin: 0 0 10px 0; color: #2c5530; text-align: center;'>🎯 Mapa Interativo CP2B</h4>
            
            <div style='margin-bottom: 8px;'>
                <b>🗺️ Cores das Bordas (Score MCDA):</b>
            </div>
            
            <div style='margin: 4px 0; font-size: 10px;'>
                <span style='color: #00AA00; font-weight: bold;'>█</span> 80-100: Excelente<br>
                <span style='color: #66BB00; font-weight: bold;'>█</span> 65-79: Muito Bom<br>
                <span style='color: #BBBB00; font-weight: bold;'>█</span> 50-64: Bom<br>
                <span style='color: #FF8800; font-weight: bold;'>█</span> 35-49: Regular<br>
                <span style='color: #FF4444; font-weight: bold;'>█</span> 0-34: Baixo
            </div>
            
            <div style='margin-top: 10px; text-align: center; font-size: 10px;'>
                🖱️ <b>Clique na propriedade → Popup → Relatório</b>
            </div>
        </div>
        """
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar referências visuais: {str(e)}")

def render_invisible_polygons_map(df_properties: pd.DataFrame,
                                 filters: Dict[str, Any] = None) -> Optional[str]:
    """
    Renderiza mapa com polígonos invisíveis e detecção de clique
    
    Args:
        df_properties: DataFrame com propriedades
        filters: Filtros aplicados
        
    Returns:
        str: cod_imovel da propriedade clicada ou None
    """
    try:
        if df_properties.empty:
            st.warning("⚠️ Nenhuma propriedade encontrada")
            return None
            
        # Aplicar filtros
        df_filtered = apply_invisible_map_filters(df_properties, filters) if filters else df_properties
        
        st.markdown("### 🗺️ Mapa da Região Metropolitana de Campinas")
        st.markdown("**🎯 Propriedades SICAR mostradas apenas pelas bordas coloridas - clique dentro de qualquer polígono para identificar a propriedade**")
        
        # Informações importantes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**📍 Propriedades carregadas:** {len(df_filtered):,}")
        with col2:
            avg_score = df_filtered['mcda_score'].mean() if 'mcda_score' in df_filtered.columns else 0
            st.info(f"**📊 Score médio:** {avg_score:.1f}/100")
        with col3:
            st.info(f"**🏙️ Municípios:** {df_filtered['municipio'].nunique() if 'municipio' in df_filtered.columns else 0}")
        
        # Criar mapa com polígonos invisíveis
        m = create_invisible_polygons_map(df_filtered)
        
        # Renderizar com detecção de clique otimizada e captura do zoom
        map_data = st_folium(
            m,
            width=None,
            height=700,
            returned_objects=["last_clicked", "zoom", "bounds"],  # Capturar zoom e bounds
            key=f"invisible_mcda_map_{len(df_filtered)}"  # Key dinâmica para evitar conflitos
        )
        
        # Aplicar filtro dinâmico baseado no zoom
        if map_data and map_data.get("zoom") and map_data.get("bounds"):
            current_zoom = map_data["zoom"]
            current_bounds = map_data["bounds"]
            
            # Recalcular propriedades baseado no zoom se necessário
            df_zoom_filtered = apply_zoom_based_filtering(
                df_properties, current_zoom, current_bounds, filters
            )
            
            # Se o número de propriedades mudou significativamente, recarregar o mapa
            if abs(len(df_zoom_filtered) - len(df_filtered)) > 500:
                st.info(f"🔄 Ajustando para {len(df_zoom_filtered)} propriedades baseado no zoom {current_zoom}")
                df_filtered = df_zoom_filtered
                # Recriar mapa com as novas propriedades
                m = create_invisible_polygons_map(df_filtered)
                map_data = st_folium(
                    m,
                    width=None,
                    height=700,
                    returned_objects=["last_clicked", "zoom", "bounds"],
                    key=f"invisible_mcda_map_zoom_{len(df_filtered)}_{current_zoom}"
                )
        
        # Processar cliques
        clicked_property = process_invisible_map_clicks(map_data, df_filtered)
        
        if clicked_property:
            # Mostrar informação da propriedade clicada
            prop_info = df_filtered[df_filtered['cod_imovel'] == clicked_property]
            if not prop_info.empty:
                prop = prop_info.iloc[0]
                st.success(f"✅ **Propriedade identificada:** {prop.get('municipio', 'N/A')} | Score: {prop.get('mcda_score', 0):.1f}/100")
                
                # Mostrar relatório completo automaticamente
                st.markdown("---")
                st.markdown("## 📊 Relatório Completo da Propriedade")
                
                # Importar e usar o componente de relatório
                from .report_component import render_property_report_page
                render_property_report_page(clicked_property)
                
        return clicked_property
        
    except Exception as e:
        logger.error(f"❌ Erro ao renderizar mapa invisível: {str(e)}")
        st.error(f"Erro: {str(e)}")
        return None

def process_invisible_map_clicks(map_data: dict, df_filtered: pd.DataFrame) -> Optional[str]:
    """Processa cliques no mapa com polígonos invisíveis"""
    try:
        if not map_data:
            return None
            
        clicked_property = None
        
        # Verificar clique em coordenadas
        if map_data.get("last_clicked"):
            click_data = map_data["last_clicked"]
            if click_data and isinstance(click_data, dict):
                lat = click_data.get("lat")
                lon = click_data.get("lng")
                
                if lat and lon:
                    # Detecção rápida sem spinner para evitar re-render
                    clicked_property = detect_property_at_coordinates(lat, lon, df_filtered)
                        
                    if clicked_property:
                        logger.info(f"✅ Propriedade detectada: {clicked_property}")
                        return clicked_property
                    else:
                        st.warning("⚠️ Nenhuma propriedade SICAR encontrada nesta localização")
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar cliques: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache por 5 minutos
def detect_property_at_coordinates(click_lat: float, click_lon: float, 
                                 _df_properties: pd.DataFrame) -> Optional[str]:
    """
    Detecta propriedade nas coordenadas clicadas
    Versão ultra-otimizada para performance
    """
    try:
        if _df_properties.empty:
            return None
            
        click_point = Point(click_lon, click_lat)
        
        # Busca otimizada - parar na primeira propriedade encontrada
        for idx in range(min(len(_df_properties), 2000)):  # Limitar busca
            try:
                row = _df_properties.iloc[idx]
                
                if 'geometry_shapely' not in row or pd.isna(row['geometry_shapely']):
                    continue
                    
                geometry = row['geometry_shapely']
                
                # Verificação rápida do bounding box antes da verificação completa
                bounds = geometry.bounds  # (minx, miny, maxx, maxy)
                if (bounds[0] <= click_lon <= bounds[2] and 
                    bounds[1] <= click_lat <= bounds[3]):
                    
                    # Só fazer verificação completa se estiver no bounding box
                    if geometry.contains(click_point):
                        cod_imovel = row.get('cod_imovel', None)
                        return cod_imovel
                    
            except Exception:
                continue  # Pular geometrias problemáticas
        
        return None
        
    except Exception:
        return None

def apply_zoom_based_filtering(df: pd.DataFrame, zoom_level: int, 
                             bounds: Dict[str, Any], filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplica filtro inteligente baseado no nível de zoom
    Zoom baixo (8-11): Menos propriedades, mais esparsas
    Zoom médio (12-14): Propriedades médias  
    Zoom alto (15+): Todas as propriedades na área visível
    """
    try:
        df_filtered = df.copy()
        
        # Aplicar filtros básicos primeiro
        if filters.get('score_min', 0) > 0 and 'mcda_score' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['mcda_score'] >= filters['score_min']]
            
        if filters.get('municipality', 'Todos') != 'Todos' and 'municipio' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['municipio'] == filters['municipality']]
        
        # Filtro por área visível se bounds estão disponíveis
        if bounds and 'geometry_shapely' in df_filtered.columns:
            south = bounds.get('_southWest', {}).get('lat')
            west = bounds.get('_southWest', {}).get('lng') 
            north = bounds.get('_northEast', {}).get('lat')
            east = bounds.get('_northEast', {}).get('lng')
            
            if all([south, west, north, east]):
                # Filtrar propriedades que intersectam com a área visível
                def intersects_bounds(geometry):
                    try:
                        bounds_geom = geometry.bounds  # (minx, miny, maxx, maxy)
                        return not (bounds_geom[0] > east or bounds_geom[2] < west or 
                                  bounds_geom[1] > north or bounds_geom[3] < south)
                    except:
                        return False
                
                df_filtered = df_filtered[df_filtered['geometry_shapely'].apply(intersects_bounds)]
        
        # Aplicar limite baseado no zoom
        if zoom_level <= 10:
            # Zoom muito baixo: máximo 1000 propriedades mais esparsas
            max_limit = min(1000, len(df_filtered))
            df_filtered = df_filtered.sample(n=max_limit) if len(df_filtered) > max_limit else df_filtered
        elif zoom_level <= 12:
            # Zoom baixo: máximo 2500 propriedades
            max_limit = min(2500, len(df_filtered))
            df_filtered = df_filtered.head(max_limit)
        elif zoom_level <= 14:
            # Zoom médio: máximo 5000 propriedades
            max_limit = min(5000, len(df_filtered))
            df_filtered = df_filtered.head(max_limit)
        else:
            # Zoom alto: mostrar todas as propriedades na área (até 8000)
            max_limit = min(8000, len(df_filtered))
            df_filtered = df_filtered.head(max_limit)
        
        logger.info(f"🔍 Zoom {zoom_level}: {len(df_filtered)} propriedades carregadas")
        return df_filtered
        
    except Exception as e:
        logger.error(f"❌ Erro no filtro por zoom: {str(e)}")
        return df.head(2000)  # Fallback seguro

def apply_invisible_map_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """Aplica filtros para o mapa invisível"""
    try:
        df_filtered = df.copy()
        
        # Aplicar filtros básicos
        if filters.get('score_min', 0) > 0 and 'mcda_score' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['mcda_score'] >= filters['score_min']]
            
        if filters.get('municipality', 'Todos') != 'Todos' and 'municipio' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['municipio'] == filters['municipality']]
            
        # Para polígonos com bordas, usar limite conservador para performance
        max_limit = filters.get('max_properties', 2000)  # Limite otimizado para performance
        df_filtered = df_filtered.head(max_limit)
            
        return df_filtered
        
    except Exception as e:
        logger.error(f"❌ Erro ao aplicar filtros: {str(e)}")
        return df