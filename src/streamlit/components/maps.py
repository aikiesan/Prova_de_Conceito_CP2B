import streamlit as st
import folium
from folium.plugins import MarkerCluster, HeatMap, MeasureControl
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
import leafmap.foliumap as leafmap
import branca.colormap as cm

ROOT = Path(__file__).resolve().parents[3]  # Go up 3 levels instead of 2
SHAPEFILE_PATH = ROOT / "shapefile" / "Municipios_SP_shapefile.shp"

# Caminhos para shapefiles adicionais
ADDITIONAL_SHAPEFILES = {
    # Camadas existentes
    'limite_sp': ROOT / "shapefile" / "Limite_SP.shp",
    'plantas_biogas': ROOT / "shapefile" / "Plantas_Biogas_SP.shp",
    'regioes_admin': ROOT / "shapefile" / "Regiao_Adm_SP.shp",

    # --- NOVAS CAMADAS ADICIONADAS ---
    'areas_urbanas': ROOT / "shapefile" / "Areas_Urbanas_SP.shp",
    'gasodutos_transporte': ROOT / "shapefile" / "Gasodutos_Transporte_SP.shp",
    'gasodutos_distribuicao': ROOT / "shapefile" / "Gasodutos_Distribuicao_SP.shp",
    'rodovias_estaduais': ROOT / "shapefile" / "Rodovias_Estaduais_SP.shp"
}

def load_and_process_shapefile():
    """Carrega shapefile com processamento otimizado"""
    try:
        if not SHAPEFILE_PATH.exists():
            return None
        
        gdf = gpd.read_file(SHAPEFILE_PATH)
        
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        
        gdf['cd_mun'] = gdf['CD_MUN'].astype(str)
        
        # Mapear colunas do shapefile
        biogas_mapping = {
            'Bio_Final': 'total_final_nm_ano',
            'Bio_Agric': 'total_agricola_nm_ano', 
            'Bio_Pecuar': 'total_pecuaria_nm_ano',
            'Bio_Cana': 'biogas_cana',
            'Bio_Soja': 'biogas_soja',
            'Bio_Milho': 'biogas_milho',
            'Bio_Bovino': 'biogas_bovino',
            'Bio_Cafe': 'biogas_cafe',
            'Bio_Citros': 'biogas_citros',
            'Bio_Suinos': 'biogas_suinos',
            'Bio_Aves': 'biogas_aves',
            'Bio_Peixes': 'biogas_piscicultura'
        }
        
        for shapefile_col, standard_col in biogas_mapping.items():
            if shapefile_col in gdf.columns:
                gdf[standard_col] = pd.to_numeric(gdf[shapefile_col], errors='coerce').fillna(0)
            else:
                gdf[standard_col] = 0
        
        gdf['nm_mun'] = gdf['NM_MUN']
        gdf['area_km2'] = pd.to_numeric(gdf.get('AREA_KM2', 0), errors='coerce').fillna(0)
        
        # Corrigir geometrias
        invalid_mask = ~gdf.geometry.is_valid
        if invalid_mask.any():
            gdf.loc[invalid_mask, 'geometry'] = gdf.loc[invalid_mask, 'geometry'].buffer(0)
        
        # Simplificar geometrias
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)
        
        # Calcular centroides
        gdf['centroid'] = gdf.geometry.centroid
        gdf['lat'] = gdf['centroid'].y
        gdf['lon'] = gdf['centroid'].x
        
        return gdf
        
    except Exception as e:
        st.error(f"Erro ao carregar shapefile: {e}")
        return None

@st.cache_data
def load_additional_shapefiles():
    """Carrega shapefiles adicionais com cache otimizado"""
    loaded = {}
    
    for name, path in ADDITIONAL_SHAPEFILES.items():
        try:
            if path.exists():
                gdf = gpd.read_file(path)
                
                # Garantir CRS correto
                if gdf.crs != 'EPSG:4326':
                    gdf = gdf.to_crs('EPSG:4326')
                
                # Simplificar geometrias para melhor performance
                gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)
                
                # Corrigir geometrias inválidas
                invalid_mask = ~gdf.geometry.is_valid
                if invalid_mask.any():
                    gdf.loc[invalid_mask, 'geometry'] = gdf.loc[invalid_mask, 'geometry'].buffer(0)
                
                loaded[name] = gdf
                
        except Exception as e:
            # Log silencioso - apenas para development se necessário
            continue
    
    return loaded

def create_detailed_popup(row: pd.Series, potencial: float, filters: Dict = None, municipio_nome: str = None) -> str:
    """Cria popup detalhado com TODOS os resíduos disponíveis no município"""
    
    if municipio_nome is None:
        # Fallback para compatibilidade
        municipio_nome = str(row.get('nm_mun', row.get('NM_MUN', 'Município'))).replace("'", "").replace('"', '')
    else:
        municipio_nome = str(municipio_nome).replace("'", "").replace('"', '')
    
    codigo_mun = str(row["cd_mun"])
    
    # Dados básicos
    agricola = row.get("total_agricola_nm_ano", 0)
    pecuaria = row.get("total_pecuaria_nm_ano", 0)
    total = row.get("total_final_nm_ano", 0)
    area = row.get("area_km2", 0)
    
    # TODOS os resíduos organizados por categoria
    all_residues_data = {
        '🌾 AGRÍCOLA': {
            'Cana-de-açúcar': row.get('biogas_cana_nm_ano', 0),
            'Soja': row.get('biogas_soja_nm_ano', 0),
            'Milho': row.get('biogas_milho_nm_ano', 0),
            'Café': row.get('biogas_cafe_nm_ano', 0),
            'Citros': row.get('biogas_citros_nm_ano', 0),
        },
        '🐄 PECUÁRIA': {
            'Bovinos': row.get('biogas_bovinos_nm_ano', 0),
            'Suínos': row.get('biogas_suino_nm_ano', 0),
            'Aves': row.get('biogas_aves_nm_ano', 0),
            'Piscicultura': row.get('biogas_piscicultura_nm_ano', 0),
        },
        '🏙️ URBANO': {
            'RSU': row.get('rsu_potencial_nm_habitante_ano', 0),
            'RPO': row.get('rpo_potencial_nm_habitante_ano', 0),
        }
    }
    
    # Início do HTML
    popup_html = f"<div style='width: 320px; padding: 8px; font-family: Arial;'><h4 style='margin: 0 0 8px 0; color: #2c3e50;'>🏛️ {municipio_nome}</h4><div style='background: #f0f4ff; padding: 6px; border-radius: 4px; margin-bottom: 8px;'><b>⚡ Potencial: {potencial:,.0f} Nm³/ano</b></div><div style='font-size: 11px; margin-bottom: 8px;'><div>🌾 Agrícola: {agricola:,.0f}</div><div>🐄 Pecuária: {pecuaria:,.0f}</div><div>📊 Total: {total:,.0f}</div><div>📍 Área: {area:,.1f} km²</div></div>"
    
    # Adicionar seções detalhadas por categoria
    popup_html += "<div style='font-size: 10px; border-top: 1px solid #ddd; padding-top: 6px;'><b>📋 Todos os Resíduos:</b>"
    
    for category, residues in all_residues_data.items():
        category_total = sum(residues.values())
        
        if category_total > 0:
            popup_html += f"<div style='margin: 4px 0; padding: 4px; background: #f9f9f9; border-radius: 3px;'><b>{category}</b> ({category_total:,.0f})"
            
            # Mostrar apenas resíduos com valor > 0
            for residue_name, value in residues.items():
                if value > 0:
                    popup_html += f"<div style='margin-left: 8px; font-size: 9px;'>{residue_name}: {value:,.0f}</div>"
            
            popup_html += "</div>"
    
    popup_html += f"</div><div style='text-align: center; margin-top: 6px; font-size: 9px; color: #666;'>Código: {codigo_mun}</div></div>"
    
    return popup_html

def create_clean_marker_map(gdf_filtered: gpd.GeoDataFrame, max_municipalities: int = 200, additional_layers: Dict = None, layer_controls: Dict = None, visualization_mode: str = "Compacto (Recomendado)", filters: Dict = None, map_center: tuple = None, map_zoom: int = None, highlight_codes: list = None, radius_analysis_info: dict = None, special_viz_mode: str = "Padrão", viz_settings: dict = None) -> folium.Map:
    """Cria mapa limpo com marcadores individuais para melhor leitura"""
    # Use provided center and zoom, or default to São Paulo
    if map_center:
        center_lat, center_lon = map_center
    else:
        center_lat, center_lon = -23.2, -47.8
    
    zoom_level = map_zoom if map_zoom else 7
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap',
        # Configurações otimizadas para melhor experiência
        min_zoom=6,      # Evita zoom muito distante
        max_zoom=18,     # Permite zoom detalhado
        zoom_control=True,
        scrollWheelZoom=True,
        doubleClickZoom=True,
        dragging=True
    )
    
    # Add measurement tool to the map
    MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)
    
    # --- MUDANÇA CRÍTICA DE ORDEM ---
    # Adicione as camadas de referência (fundo) PRIMEIRO
    if additional_layers and layer_controls:
        add_additional_layers_to_map(m, additional_layers, layer_controls)
    # ------------------------------------
    
    # Limitar municípios baseado na coluna de display_value se disponível
    if len(gdf_filtered) > max_municipalities:
        sort_column = 'display_value' if 'display_value' in gdf_filtered.columns else 'total_final_nm_ano'
        top_municipios = gdf_filtered.nlargest(max_municipalities, sort_column)
    else:
        top_municipios = gdf_filtered
    
    if len(top_municipios) == 0:
        return m
    
    # Usar display_value para coloração e tamanho dos marcadores
    if 'display_value' in top_municipios.columns:
        potencial_values = top_municipios['display_value']
    else:
        potencial_values = top_municipios['total_final_nm_ano']
    
    if potencial_values.max() > 0:
        # Sistema de cores mais intuitivo e moderno
        max_potencial = potencial_values.max()
        
        # Definir breakpoints baseados em análise de viabilidade econômica
        # Categorias inspiradas em semáforo + gradações para melhor interpretação
        breakpoints = {
            'zero': 0,
            'muito_baixo': max_potencial * 0.05,      # 5% do máximo
            'baixo': max_potencial * 0.15,            # 15% do máximo  
            'medio_baixo': max_potencial * 0.35,      # 35% do máximo
            'medio': max_potencial * 0.55,            # 55% do máximo
            'medio_alto': max_potencial * 0.75,       # 75% do máximo
            'alto': max_potencial * 0.90,             # 90% do máximo
        }
        
        # Paleta de cores moderna e intuitiva - do cinza ao laranja/vermelho
        # Usando sistema de cores que facilita interpretação visual
        colors = {
            'zero': '#e8e8e8',           # Cinza neutro para zero
            'muito_baixo': '#fff5f0',     # Quase branco - potencial mínimo
            'baixo': '#fdd49e',          # Laranja claro - atenção
            'medio_baixo': '#fdae6b',     # Laranja - potencial emergindo
            'medio': '#fd8d3c',          # Laranja médio - potencial moderado
            'medio_alto': '#e6550d',      # Laranja escuro - bom potencial
            'alto': '#a63603',           # Marrom - alto potencial
            'muito_alto': '#7f2704'      # Marrom escuro - potencial excepcional
        }
        
        def get_color(potencial):
            """Retorna cor baseada em thresholds intuitivos de viabilidade"""
            if potencial == 0:
                return colors['zero']
            elif potencial <= breakpoints['muito_baixo']:
                return colors['muito_baixo']
            elif potencial <= breakpoints['baixo']:
                return colors['baixo']
            elif potencial <= breakpoints['medio_baixo']:
                return colors['medio_baixo']
            elif potencial <= breakpoints['medio']:
                return colors['medio']
            elif potencial <= breakpoints['medio_alto']:
                return colors['medio_alto']
            elif potencial <= breakpoints['alto']:
                return colors['alto']
            else:
                return colors['muito_alto']
        
        # Criar grupo de marcadores sem clustering para melhor leitura visual
        municipios_group = folium.FeatureGroup(
            name="📍 Municípios (Biogás)",
            overlay=True,
            control=True,
            show=True
        )
        
        # Adicionar marcadores individuais sem agregação
        for _, row in top_municipios.iterrows():
            if pd.isna(row['lat']) or pd.isna(row['lon']):
                continue
                
            # Usar display_value se disponível, senão usar total_final_nm_ano
            if 'display_value' in row.index:
                potencial = row['display_value']
            else:
                potencial = row.get('total_final_nm_ano', 0)
            
            # Popup otimizado com detalhamento por resíduo
            # Corrigir nome do município - usar NM_MUN se nm_mun estiver zerado
            if row.get('nm_mun', '0') == '0' or str(row.get('nm_mun', '')).strip() == '':
                if 'NM_MUN' in row.index:
                    municipio_nome = row['NM_MUN']
                else:
                    municipio_nome = 'Município'
            else:
                municipio_nome = row['nm_mun']
            
            popup_html = create_detailed_popup(row, potencial, filters, municipio_nome)
            
            # Configurações baseadas no modo de visualização
            if visualization_mode == "Minimalista":
                max_radius = 5
                min_radius = 2
                stroke_weight = 0.5
                fill_opacity = 0.6
                border_opacity = 0.7
            elif visualization_mode == "Detalhado":
                max_radius = 12
                min_radius = 4
                stroke_weight = 1.5
                fill_opacity = 0.85
                border_opacity = 1.0
            else:  # Compacto (Recomendado)
                max_radius = 8
                min_radius = 3
                stroke_weight = 1.0
                fill_opacity = 0.75
                border_opacity = 0.9
            
            # Escala não-linear para melhor diferenciação visual
            if potencial_values.max() > 0:
                # Usar raiz quadrada para suavizar diferenças extremas
                normalized_value = (potencial / potencial_values.max()) ** 0.5
                radius = max(min_radius, min_radius + (max_radius - min_radius) * normalized_value)
            else:
                radius = min_radius
            
            # --- START: New highlight logic for multiple municipalities ---
            is_highlighted = False
            if highlight_codes:
                is_highlighted = str(row['cd_mun']) in [str(code) for code in highlight_codes]
            
            # Make highlighted markers stand out
            marker_radius = radius * 2.5 if is_highlighted else radius
            marker_weight = 3 if is_highlighted else stroke_weight
            marker_color = '#FF0000' if is_highlighted else '#333333'  # Red for highlight
            marker_fill_opacity = 1.0 if is_highlighted else fill_opacity
            
            # Add a pulsing effect to the highlighted marker with custom CSS
            if is_highlighted:
                # Create a DivIcon with a custom class for the pulsing animation
                icon_html = f'''
                <div class="pulsing-dot-container">
                  <div class="pulsing-dot" style="background-color: {get_color(potencial)};"></div>
                </div>
                '''
                pulsing_icon = folium.Marker(
                    location=[row['lat'], row['lon']],
                    icon=folium.DivIcon(html=icon_html),
                    tooltip=f"📍 SELECIONADO: {municipio_nome}"
                )
                pulsing_icon.add_to(municipios_group)
                tooltip_text = f"🎯 {municipio_nome}: {potencial:,.0f} Nm³/ano (SELECIONADO)"
            else:
                tooltip_text = f"🏛️ {municipio_nome}: {potencial:,.0f} Nm³/ano"
            # --- END: New highlight logic ---
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                # Use the new marker variables
                radius=marker_radius,
                weight=marker_weight,
                color=marker_color,
                fillOpacity=marker_fill_opacity,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=tooltip_text,
                fillColor=get_color(potencial),
                opacity=border_opacity,
                bubblingMouseEvents=False # Evita conflitos de eventos
            ).add_to(municipios_group)
        
        # Apply special visualizations based on mode
        if special_viz_mode and special_viz_mode != "Padrão":
            apply_special_visualizations(m, top_municipios, special_viz_mode, viz_settings, potencial_values)
        
        # Adicionar grupo de municípios ao mapa
        municipios_group.add_to(m)
        
        # Legenda interativa avançada
        if potencial_values.max() > 0:
            create_interactive_legend(m, top_municipios, list(colors.values()), potencial_values)
    
    # --- REMOVIDA CHAMADA ANTIGA ---
    # A chamada a add_additional_layers_to_map foi movida para o início da função
    # ------------------------------------
    
    # Adicionar o controle de camadas no final para que ele veja todas as camadas adicionadas
    folium.LayerControl(
        position='topright',
        collapsed=False
    ).add_to(m)
    
    # Adicionar JavaScript para desabilitar auto-pan nos popups
    disable_autopan_js = """
    <script>
    // Desabilitar auto-pan nos popups para evitar movimento do mapa
    window.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            var mapElements = document.querySelectorAll('div[id*="folium-map"]');
            mapElements.forEach(function(mapEl) {
                if (mapEl._leaflet_map) {
                    var map = mapEl._leaflet_map;
                    
                    // Override das configurações de popup
                    map.options.closePopupOnClick = false;
                    
                    // Interceptar abertura de popups
                    map.on('popupopen', function(e) {
                        var popup = e.popup;
                        if (popup) {
                            // Desabilitar o auto-pan
                            popup.options.autoPan = false;
                            popup.options.keepInView = false;
                        }
                    });
                }
            });
        }, 500);
    });
    </script>
    """
    
    # Usar Element do folium em vez de Template
    from folium import Element
    m.get_root().html.add_child(Element(disable_autopan_js))
    
    # --- NEW: Draw Radius Analysis Circle ---
    if radius_analysis_info and 'center' in radius_analysis_info and 'radius_km' in radius_analysis_info:
        folium.Circle(
            location=[radius_analysis_info['center']['lat'], radius_analysis_info['center']['lon']],
            radius=radius_analysis_info['radius_km'] * 1000,  # Convert km to meters
            color='#4A90E2',
            weight=3,
            fill=True,
            fill_color='#4A90E2',
            fill_opacity=0.1,
            popup=f"Raio de Análise: {radius_analysis_info['radius_km']} km<br/>Centro: {radius_analysis_info['center']['lat']:.4f}, {radius_analysis_info['center']['lon']:.4f}"
        ).add_to(m)
        
        # Add a center marker
        folium.Marker(
            location=[radius_analysis_info['center']['lat'], radius_analysis_info['center']['lon']],
            popup=f"Centro da Análise<br/>Raio: {radius_analysis_info['radius_km']} km",
            icon=folium.Icon(color='blue', icon='crosshairs', prefix='fa')
        ).add_to(m)
    # --- END NEW ---
    
    return m

def create_interactive_legend(m: folium.Map, municipios_data: pd.DataFrame, colors: List[str], potencial_values: pd.Series) -> None:
    """Cria legenda otimizada para melhor interpretação dos dados sem clustering"""
    
    if municipios_data.empty or len(colors) == 0:
        return
    
    try:
        max_potencial = float(potencial_values.max()) if not potencial_values.empty else 0
        total_municipios = len(municipios_data)
        
        # Calcular valores reais dos breakpoints para exibição
        breakpoints_display = {
            'muito_baixo': max_potencial * 0.05,
            'baixo': max_potencial * 0.15,
            'medio_baixo': max_potencial * 0.35,
            'medio': max_potencial * 0.55,
            'medio_alto': max_potencial * 0.75,
            'alto': max_potencial * 0.90,
        }
        
        # Legenda melhorada com valores reais e sem referências ao clustering
        legend_html = f"""
        <div style='position: fixed; top: 10px; right: 10px; width: 220px; 
                    background: rgba(255,255,255,0.96); backdrop-filter: blur(10px);
                    border: 1px solid rgba(0,0,0,0.1); z-index: 9999; 
                    border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
            
            <!-- Header melhorado -->
            <div style='padding: 12px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; border-radius: 12px 12px 0 0; font-weight: 600; font-size: 13px;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span style='font-size: 16px;'>🌱</span>
                    <span>Potencial de Biogás</span>
                </div>
                <div style='font-size: 10px; opacity: 0.9; margin-top: 2px;'>
                    Visualização Individual
                </div>
            </div>
            
            <!-- Escala de cores com valores reais -->
            <div style='padding: 16px;'>
                <div style='margin-bottom: 12px;'>
                    <div style='font-weight: 500; margin-bottom: 8px; color: #2d3748; font-size: 12px;'>
                        Intensidade (Nm³/ano)
                    </div>
                    <div style='display: flex; flex-direction: column; gap: 3px;'>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <div style='width: 14px; height: 14px; border-radius: 50%; background: #7f2704; border: 1px solid white;'></div>
                            <div style='flex: 1;'>
                                <span style='font-size: 11px; color: #2d3748; font-weight: 500;'>Excepcional</span>
                                <div style='font-size: 9px; color: #6b7280;'>&gt; {breakpoints_display['alto']:,.0f}</div>
                            </div>
                        </div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <div style='width: 14px; height: 14px; border-radius: 50%; background: #a63603; border: 1px solid white;'></div>
                            <div style='flex: 1;'>
                                <span style='font-size: 11px; color: #2d3748; font-weight: 500;'>Alto</span>
                                <div style='font-size: 9px; color: #6b7280;'>{breakpoints_display['medio_alto']:,.0f} - {breakpoints_display['alto']:,.0f}</div>
                            </div>
                        </div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <div style='width: 14px; height: 14px; border-radius: 50%; background: #e6550d; border: 1px solid white;'></div>
                            <div style='flex: 1;'>
                                <span style='font-size: 11px; color: #2d3748; font-weight: 500;'>Médio-Alto</span>
                                <div style='font-size: 9px; color: #6b7280;'>{breakpoints_display['medio']:,.0f} - {breakpoints_display['medio_alto']:,.0f}</div>
                            </div>
                        </div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <div style='width: 14px; height: 14px; border-radius: 50%; background: #fd8d3c; border: 1px solid white;'></div>
                            <div style='flex: 1;'>
                                <span style='font-size: 11px; color: #2d3748; font-weight: 500;'>Médio</span>
                                <div style='font-size: 9px; color: #6b7280;'>{breakpoints_display['medio_baixo']:,.0f} - {breakpoints_display['medio']:,.0f}</div>
                            </div>
                        </div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <div style='width: 14px; height: 14px; border-radius: 50%; background: #fdae6b; border: 1px solid white;'></div>
                            <div style='flex: 1;'>
                                <span style='font-size: 11px; color: #2d3748; font-weight: 500;'>Baixo</span>
                                <div style='font-size: 9px; color: #6b7280;'>{breakpoints_display['baixo']:,.0f} - {breakpoints_display['medio_baixo']:,.0f}</div>
                            </div>
                        </div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <div style='width: 14px; height: 14px; border-radius: 50%; background: #fdd49e; border: 1px solid white;'></div>
                            <div style='flex: 1;'>
                                <span style='font-size: 11px; color: #2d3748; font-weight: 500;'>Muito Baixo</span>
                                <div style='font-size: 9px; color: #6b7280;'>{breakpoints_display['muito_baixo']:,.0f} - {breakpoints_display['baixo']:,.0f}</div>
                            </div>
                        </div>
                        <div style='display: flex; align-items: center; gap: 8px;'>
                            <div style='width: 14px; height: 14px; border-radius: 50%; background: #e8e8e8; border: 1px solid #ccc;'></div>
                            <div style='flex: 1;'>
                                <span style='font-size: 11px; color: #2d3748; font-weight: 500;'>Zero</span>
                                <div style='font-size: 9px; color: #6b7280;'>Sem potencial</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Stats melhoradas -->
                <div style='padding: 10px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                            border-radius: 8px; font-size: 10px; border: 1px solid #e2e8f0;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 4px;'>
                        <span style='color: #4a5568;'>Municípios:</span>
                        <strong style='color: #2d3748;'>{total_municipios}</strong>
                    </div>
                    <div style='display: flex; justify-content: space-between;'>
                        <span style='color: #4a5568;'>Máximo:</span>
                        <strong style='color: #2d3748;'>{max_potencial:,.0f}</strong>
                    </div>
                </div>
                
                <!-- Dica de navegação -->
                <div style='margin-top: 8px; padding: 6px; background: #fffbeb; border-radius: 4px; 
                            border-left: 3px solid #f59e0b; font-size: 9px; color: #92400e;'>
                    💡 <strong>Dica:</strong> Clique nos pontos para detalhes
                </div>
            </div>
        </div>
        """
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
    except Exception:
        # Fallback melhorado
        simple_legend = f"""
        <div style='position: fixed; top: 10px; right: 10px; background: white; 
                    padding: 12px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    font-family: system-ui; font-size: 12px; z-index: 9999;'>
            <div style='font-weight: 600; margin-bottom: 8px; color: #2d3748;'>🌱 Biogás SP</div>
            <div style='margin-bottom: 4px;'><span style='color: #7f2704; font-size: 14px;'>●</span> Excepcional</div>
            <div style='margin-bottom: 4px;'><span style='color: #a63603; font-size: 14px;'>●</span> Alto</div>
            <div style='margin-bottom: 4px;'><span style='color: #fd8d3c; font-size: 14px;'>●</span> Médio</div>
            <div style='margin-bottom: 4px;'><span style='color: #fdd49e; font-size: 14px;'>●</span> Baixo</div>
            <div><span style='color: #e8e8e8; font-size: 14px;'>●</span> Zero</div>
            <div style='margin-top: 8px; font-size: 10px; color: #6b7280;'>{total_municipios} municípios</div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(simple_legend))

def add_additional_layers_to_map(folium_map: folium.Map, additional_layers: Dict, layer_controls: Dict) -> None:
    """Adiciona camadas de referência visual ao mapa."""
    
    # Robust handling when layer_controls is None or already the controls dict
    if layer_controls is None:
        actual_controls = {}
    else:
        actual_controls = layer_controls
    
    # Função auxiliar para limpar os dados e manter apenas a geometria
    def get_geometry_only(gdf):
        """Remove todas as colunas exceto geometry para evitar erros de serialização."""
        return gdf[['geometry']].copy()
    
    # Limite de SP
    if actual_controls.get('limite_sp', False) and 'limite_sp' in additional_layers:
        group = folium.FeatureGroup(name="🗺️ Limite de SP", show=True, overlay=True, control=True)
        try:
            folium.GeoJson(
                get_geometry_only(additional_layers['limite_sp']),
                style_function=lambda x: {'color': '#c91c1c', 'weight': 3, 'fillOpacity': 0, 'opacity': 0.8, 'dashArray': '5, 5'}
            ).add_to(group)
            group.add_to(folium_map)
        except Exception:
            pass

    # Regiões Administrativas
    if actual_controls.get('regioes_admin', False) and 'regioes_admin' in additional_layers:
        group = folium.FeatureGroup(name="🏛️ Regiões Administrativas", show=True, overlay=True, control=True)
        try:
            folium.GeoJson(
                get_geometry_only(additional_layers['regioes_admin']),
                style_function=lambda x: {'color': '#5a5a5a', 'weight': 2, 'fillColor': '#999999', 'fillOpacity': 0.15}
            ).add_to(group)
            group.add_to(folium_map)
        except Exception:
            pass

    # Plantas de Biogás
    if actual_controls.get('plantas_biogas', False) and 'plantas_biogas' in additional_layers:
        group = folium.FeatureGroup(name="🏭 Usinas de Biogás", show=True, overlay=True, control=True)
        try:
            for _, row in additional_layers['plantas_biogas'].iterrows():
                coords = row.geometry.centroid
                folium.Marker(
                    location=[coords.y, coords.x],
                    icon=folium.Icon(color='gray', icon='industry', prefix='fa', icon_color='#ffffff')
                ).add_to(group)
            group.add_to(folium_map)
        except Exception:
            pass

    # Áreas Urbanas
    if actual_controls.get('areas_urbanas', False) and 'areas_urbanas' in additional_layers:
        group = folium.FeatureGroup(name="🏙️ Áreas Urbanas", show=True, overlay=True, control=True)
        try:
            folium.GeoJson(
                get_geometry_only(additional_layers['areas_urbanas']),
                style_function=lambda x: {'fillColor': '#d3d3d3', 'fillOpacity': 0.4, 'color': '#a0a0a0', 'weight': 1, 'opacity': 0.6}
            ).add_to(group)
            group.add_to(folium_map)
        except Exception:
            pass

    # Gasodutos de Transporte
    if actual_controls.get('gasodutos_transporte', False) and 'gasodutos_transporte' in additional_layers:
        group = folium.FeatureGroup(name="🔵 Gasodutos (Transporte)", show=True, overlay=True, control=True)
        try:
            folium.GeoJson(
                get_geometry_only(additional_layers['gasodutos_transporte']),
                style_function=lambda x: {'color': '#003366', 'weight': 3, 'opacity': 0.8}
            ).add_to(group)
            group.add_to(folium_map)
        except Exception:
            pass
            
    # Gasodutos de Distribuição
    if actual_controls.get('gasodutos_distribuicao', False) and 'gasodutos_distribuicao' in additional_layers:
        group = folium.FeatureGroup(name="⚪ Gasodutos (Distribuição)", show=True, overlay=True, control=True)
        try:
            folium.GeoJson(
                get_geometry_only(additional_layers['gasodutos_distribuicao']),
                style_function=lambda x: {'color': '#3399CC', 'weight': 2, 'opacity': 0.8, 'dashArray': '5, 5'}
            ).add_to(group)
            group.add_to(folium_map)
        except Exception:
            pass

    # Rodovias Estaduais
    if actual_controls.get('rodovias_estaduais', False) and 'rodovias_estaduais' in additional_layers:
        group = folium.FeatureGroup(name="🚗 Rodovias Estaduais", show=True, overlay=True, control=True)
        try:
            folium.GeoJson(
                get_geometry_only(additional_layers['rodovias_estaduais']),
                style_function=lambda x: {'color': '#4a4a4a', 'weight': 2.5, 'opacity': 0.7}
            ).add_to(group)
            group.add_to(folium_map)
        except Exception:
            pass

def render_layer_controls_below_map(municipios_data: pd.DataFrame) -> Dict[str, bool]:
    """
    Renderiza controles de camadas de forma direta e visível usando colunas.
    """
    st.markdown("---")
    st.markdown("##### 🗺️ Camadas de Referência")

    # Mapeamento de nomes de exibição para chaves internas
    AVAILABLE_LAYERS = {
        # Coluna 1
        "🗺️ Limite de São Paulo": "limite_sp",
        "🏛️ Regiões Administrativas": "regioes_admin",
        "🏙️ Áreas Urbanas": "areas_urbanas",
        "🚗 Rodovias Estaduais": "rodovias_estaduais",
        # Coluna 2
        "🔵 Gasodutos (Transporte)": "gasodutos_transporte",
        "⚪ Gasodutos (Distribuição)": "gasodutos_distribuicao",
        "🏭 Usinas de Biogás": "plantas_biogas",
    }
    
    # Dividir as chaves para as colunas
    keys = list(AVAILABLE_LAYERS.keys())
    col1_keys = keys[:4]
    col2_keys = keys[4:]

    layer_controls = {}
    
    col1, col2 = st.columns(2)

    with col1:
        for display_name in col1_keys:
            internal_key = AVAILABLE_LAYERS[display_name]
            # Usar estado atual da sessão como valor padrão
            current_value = st.session_state.get('layer_controls_state', {}).get(internal_key, False)
            layer_controls[internal_key] = st.checkbox(display_name, value=current_value, key=f"cb_{internal_key}")
    
    with col2:
        for display_name in col2_keys:
            internal_key = AVAILABLE_LAYERS[display_name]
            # Usar estado atual da sessão como valor padrão
            current_value = st.session_state.get('layer_controls_state', {}).get(internal_key, False)
            layer_controls[internal_key] = st.checkbox(display_name, value=current_value, key=f"cb_{internal_key}")
    
    # Status info
    display_count = len(municipios_data[municipios_data['display_value'] > 0]) if 'display_value' in municipios_data.columns else len(municipios_data)
    active_count = sum(1 for active in layer_controls.values() if active)
    
    if active_count > 0:
        st.info(f"📊 **{len(municipios_data)} municípios** | **{active_count} camadas ativas**")
    else:
        st.info(f"📊 **{len(municipios_data)} municípios** | **Nenhuma camada selecionada**")
            
    return {'layer_controls': layer_controls}


def render_layer_controls() -> Dict[str, bool]:
    """Renderiza controles de camadas adicionais (versão antiga - manter para compatibilidade)"""
    st.subheader("🗺️ Camadas Adicionais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        limite_sp = st.checkbox("🔴 Limite de SP", value=True, help="Contorno do estado de São Paulo")
        plantas_biogas = st.checkbox("🏭 Usinas Existentes", value=False, help="Plantas de biogás em operação")
    
    with col2:
        regioes_admin = st.checkbox("🌍 Regiões Admin.", value=False, help="Regiões administrativas do estado")
        # Reservado para futuras camadas
        # outras_camadas = st.checkbox("📍 Outras", value=False)
    
    return {
        'limite_sp': limite_sp,
        'plantas_biogas': plantas_biogas,
        'regioes_admin': regioes_admin
    }

def render_map(
    municipios_data: pd.DataFrame,
    layer_controls: Dict[str, bool] = None,
    filters: Dict[str, Any] = None,
    map_center: List[float] = None,  # NEW: Desired center [lat, lon]
    map_zoom: int = 7,              # NEW: Desired zoom level
    highlight_codes: list = None,   # NEW: List of municipality codes to highlight
    radius_analysis_info: dict = None,  # NEW: Radius analysis info with center and radius
    zen_mode: bool = False,         # NEW: Zen mode flag
    special_viz_mode: str = "Padrão",  # NEW: Special visualization mode
    viz_settings: dict = None       # NEW: Visualization settings
) -> Optional[Dict[str, Any]]:
    """
    [MODIFIED] Renderiza mapa e RETORNA o código do município clicado.
    """
    
    # Verificar se dados já vêm pré-filtrados
    is_pre_filtered = filters and filters.get('pre_filtered', False)
    
    
    # Carregar shapefile principal
    gdf = load_and_process_shapefile()
    
    if gdf is None:
        st.error("Não foi possível carregar o mapa")
        return
    
    # Processar camadas adicionais baseado nos controles recebidos
    additional_layers = {}
    if layer_controls:
        with st.spinner("Carregando camadas adicionais..."):
            shapefile_layers = load_additional_shapefiles()
            
            # Extrair controles do resultado da função
            actual_controls = layer_controls.get('layer_controls', {}) if isinstance(layer_controls, dict) else layer_controls
            
            # Mapear diretamente os controles para as camadas
            active_layers = []
            for control_key, is_enabled in actual_controls.items():
                if is_enabled and control_key in shapefile_layers:
                    additional_layers[control_key] = shapefile_layers[control_key]
                    layer_name_map = {
                        'plantas_biogas': '🏭 Plantas de Biogás Existentes',
                        'regioes_admin': '🏛️ Regiões Administrativas', 
                        'limite_sp': '🗺️ Limite de São Paulo'
                    }
                    active_layers.append(layer_name_map.get(control_key, control_key))
            
            # Mostrar status das camadas ativadas (somente se houver)
            if active_layers:
                st.success(f"✅ Camadas ativadas: {', '.join(active_layers)}")
    
    # --- INÍCIO DA CORREÇÃO NA LÓGICA DE JUNÇÃO ---

    # 1. Preparar os dados para a junção
    # Garantir que a chave de junção ('cd_mun') seja do mesmo tipo em ambos os DataFrames (string)
    gdf['cd_mun'] = gdf['cd_mun'].astype(str)
    municipios_data['cd_mun'] = municipios_data['cd_mun'].astype(str)
    
    # Selecionar apenas as colunas necessárias do shapefile para evitar conflitos
    # Mantemos a geometria e o nome do município originais
    gdf_base = gdf[['cd_mun', 'NM_MUN', 'geometry', 'centroid', 'lat', 'lon', 'area_km2']].copy()

    # 2. Realizar a junção (Merge)
    # Usamos 'left' merge para manter todos os municípios do shapefile e adicionar os dados
    # do dashboard onde houver correspondência de 'cd_mun'.
    gdf_filtered = gdf_base.merge(
        municipios_data,
        on='cd_mun',
        how='left'  # Mantém todos os municípios do shapefile
    )

    # 3. Tratar valores nulos após a junção
    # Para municípios que não tinham dados no dashboard, as colunas ficarão com NaN (Not a Number).
    # Vamos preencher com 0 para evitar erros no mapa.
    colunas_de_dados = municipios_data.columns.drop('cd_mun')  # Pega todas as colunas de dados
    for col in colunas_de_dados:
        if col in gdf_filtered.columns:
            gdf_filtered[col] = gdf_filtered[col].fillna(0)

    # 4. Garantir que a coluna de nome final seja a do shapefile
    # Criamos 'nm_mun' explicitamente a partir de 'NM_MUN' para uso no restante do código
    gdf_filtered['nm_mun'] = gdf_filtered['NM_MUN']
    
    # All municipalities should be shown from the start - no filtering needed
    
    # Filtrar apenas os municípios que estão nos dados pré-filtrados
    municipios_filtrados_ids = municipios_data['cd_mun'].tolist()
    gdf_filtered = gdf_filtered[gdf_filtered['cd_mun'].isin(municipios_filtrados_ids)]

    # --- FIM DA CORREÇÃO NA LÓGICA DE JUNÇÃO ---
    
    # Criar e renderizar mapa com dados pré-filtrados
    try:
        # Use the new map_center and map_zoom arguments
        # If no center is provided, calculate it from the data as a fallback.
        if map_center is None:
            map_center = [-22.5, -48.5]  # Default for São Paulo
        
        # Convert to tuple format expected by create_clean_marker_map
        map_center_tuple = tuple(map_center) if map_center else None
        
        biogas_map = create_clean_marker_map(
            gdf_filtered, 
            500,  # Usar limite alto já que dados vêm filtrados
            additional_layers=additional_layers,
            layer_controls=layer_controls,
            visualization_mode="Compacto (Recomendado)",
            filters={'pre_filtered': True},  # Indicar que dados já estão filtrados
            map_center=map_center_tuple,
            map_zoom=map_zoom,
            highlight_codes=highlight_codes,
            radius_analysis_info=radius_analysis_info,
            special_viz_mode=special_viz_mode,
            viz_settings=viz_settings
        )
        
        # CONTAINER DO MAPA COM AJUSTE DE ALTURA BASEADO NO MODO
        fullscreen_mode = filters.get('fullscreen_mode', False) if filters else False
        map_height = 800 if fullscreen_mode else 600  # Altura maior em fullscreen
        
        map_container = st.container()
        with map_container:
            # Key simples baseada no número de municípios filtrados
            import hashlib
            
            # Criar hash baseado nos dados filtrados
            active_layers_count = len(additional_layers) if additional_layers else 0
            data_signature = f"{len(municipios_data)}_{active_layers_count}_{fullscreen_mode}"
            map_key = f"biogas_map_{hashlib.md5(data_signature.encode()).hexdigest()[:8]}"
            
            # CSS adicional para fullscreen
            if fullscreen_mode:
                st.markdown("""
                <style>
                div[data-testid="stApp"] > div:first-child {
                    padding-top: 0rem;
                }
                .streamlit-folium {
                    width: 100% !important;
                }
                </style>
                """, unsafe_allow_html=True)
            
            map_data = st_folium(
                biogas_map,
                width=None,
                # MODIFICATION: Change height to a large number.
                # The CSS class 'map-container' will control the actual visible height.
                height=800,
                use_container_width=True,
                returned_objects=["last_object_clicked_popup", "last_clicked"],
                key="main_map"
            )
            
            # MODIFICATION 2: Process both municipality clicks and map clicks
            result_data = {}
            
            # Handle municipality selection (popup clicks)
            if map_data and map_data.get("last_object_clicked_popup"):
                popup_html = map_data["last_object_clicked_popup"]
                try:
                    # Extract the city code from the popup's HTML
                    code_str = popup_html.split("Código: ")[1].split("</div>")[0]
                    if code_str.isdigit():
                        result_data["selected_municipality"] = code_str
                except (IndexError, ValueError):
                    pass
            
            # Handle raw map clicks (for radius analysis)
            if map_data and map_data.get("last_clicked"):
                result_data["last_clicked"] = map_data["last_clicked"]
            
            return result_data  # Always return dict, even if empty
            
    except Exception as e:
        st.error(f"Erro ao renderizar mapa: {e}")
        return None  # Return None if there's an error


def create_heatmap_visualization(municipios_data: pd.DataFrame, 
                               value_column: str = 'total_final_nm_ano',
                               title: str = "Mapa de Calor - Potencial de Biogás") -> None:
    """
    Cria visualização de mapa de calor usando leafmap
    
    Args:
        municipios_data: DataFrame com dados dos municípios
        value_column: Coluna a ser usada para intensidade do mapa de calor
        title: Título do mapa
    """
    try:
        # Carregar shapefile para obter coordenadas
        gdf = load_and_process_shapefile()
        if gdf is None:
            st.error("Não foi possível carregar dados geográficos para o mapa de calor")
            return
        
        # Preparar dados para junção
        gdf['cd_mun'] = gdf['cd_mun'].astype(str)
        municipios_data['cd_mun'] = municipios_data['cd_mun'].astype(str)
        
        # Juntar dados
        heatmap_data = gdf.merge(municipios_data, on='cd_mun', how='inner')
        
        # Filtrar apenas municípios com dados válidos
        heatmap_data = heatmap_data.dropna(subset=[value_column])
        heatmap_data = heatmap_data[heatmap_data[value_column] > 0]
        
        if len(heatmap_data) == 0:
            st.warning("Nenhum dado disponível para o mapa de calor")
            return
        
        # Criar mapa com leafmap
        center_lat = heatmap_data['lat'].mean()
        center_lon = heatmap_data['lon'].mean()
        
        m = leafmap.Map(
            location=[center_lat, center_lon], 
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Preparar dados para heatmap (formato: [[lat, lon, weight], ...])
        heat_data = []
        for _, row in heatmap_data.iterrows():
            # Normalizar os valores para melhor visualização
            weight = float(row[value_column])
            heat_data.append([row['lat'], row['lon'], weight])
        
        # Adicionar heatmap ao mapa
        HeatMap(
            heat_data,
            name="Potencial de Biogás",
            radius=25,
            blur=15,
            gradient={
                0.0: 'blue',
                0.3: 'cyan', 
                0.5: 'lime',
                0.7: 'yellow',
                1.0: 'red'
            }
        ).add_to(m)
        
        # Adicionar controle de camadas
        folium.LayerControl().add_to(m)
        
        # Mostrar estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Municípios no Mapa", len(heatmap_data))
        with col2:
            st.metric("Valor Máximo", f"{heatmap_data[value_column].max():.1f}")
        with col3:
            st.metric("Valor Médio", f"{heatmap_data[value_column].mean():.1f}")
        
        # Renderizar mapa
        st_folium(m, width=None, height=600, use_container_width=True)
        
        # Informações sobre o mapa de calor
        with st.expander("ℹ️ Como interpretar o mapa de calor"):
            st.markdown("""
            **Cores do Mapa de Calor:**
            - 🔵 **Azul**: Baixo potencial de biogás
            - 🟡 **Amarelo**: Potencial médio de biogás  
            - 🔴 **Vermelho**: Alto potencial de biogás
            
            **Características:**
            - Áreas mais "quentes" (vermelhas) indicam maior concentração de potencial
            - O raio de influência mostra a densidade regional
            - Útil para identificar clusters e padrões geográficos
            """)
            
    except Exception as e:
        st.error(f"Erro ao criar mapa de calor: {e}")
        if st.session_state.get('show_debug', False):
            st.exception(e)


def create_clustered_map(municipios_data: pd.DataFrame,
                        selected_municipios: List[str] = None,
                        value_column: str = 'total_final_nm_ano',
                        title: str = "Mapa com Agrupamento de Marcadores") -> None:
    """
    Cria mapa com clustering de marcadores para melhor performance
    
    Args:
        municipios_data: DataFrame com dados dos municípios
        selected_municipios: Lista de códigos de municípios selecionados
        value_column: Coluna para determinar cor/tamanho dos marcadores
        title: Título do mapa
    """
    try:
        # Carregar e processar dados geográficos
        gdf = load_and_process_shapefile()
        if gdf is None:
            st.error("Não foi possível carregar dados geográficos")
            return
        
        # Preparar dados
        gdf['cd_mun'] = gdf['cd_mun'].astype(str)
        municipios_data['cd_mun'] = municipios_data['cd_mun'].astype(str)
        
        # Juntar dados
        map_data = gdf.merge(municipios_data, on='cd_mun', how='inner')
        
        # Debug: Mostrar colunas disponíveis
        if st.session_state.get('show_debug', False):
            st.write("Debug - Colunas disponíveis:", list(map_data.columns))
        
        # Aplicar filtro de municípios selecionados
        if selected_municipios:
            map_data = map_data[map_data['cd_mun'].isin(selected_municipios)]
        
        # Filtrar apenas municípios com dados válidos
        map_data = map_data.dropna(subset=[value_column])
        
        if len(map_data) == 0:
            st.warning("Nenhum dado disponível para o mapa")
            return
        
        # Criar mapa base
        center_lat = map_data['lat'].mean()
        center_lon = map_data['lon'].mean()
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=7,
            tiles='OpenStreetMap'
        )
        
        # Add measurement tool to the map
        MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)
        
        # Criar cluster de marcadores
        marker_cluster = MarkerCluster(
            name="Municípios",
            overlay=True,
            control=True,
            icon_create_function=None
        ).add_to(m)
        
        # Criar colormap baseado nos valores
        min_val = map_data[value_column].min()
        max_val = map_data[value_column].max()
        
        # Definir colormap
        colormap = cm.LinearColormap(
            colors=['blue', 'cyan', 'lime', 'yellow', 'red'],
            vmin=min_val,
            vmax=max_val,
            caption=f'Potencial de Biogás (Nm³/ano)'
        )
        
        # Adicionar marcadores ao cluster
        for _, row in map_data.iterrows():
            # Determinar cor baseada no valor
            color = colormap(row[value_column])
            
            # Obter nome do município (pode ser nm_mun ou NM_MUN)
            mun_name = row.get('nm_mun', row.get('NM_MUN', f"Município {row.get('cd_mun', 'N/A')}"))
            
            # Criar popup com informações detalhadas
            popup_html = f"""
            <div style="font-family: Arial; width: 200px;">
                <h4>{mun_name}</h4>
                <hr>
                <b>Potencial Total:</b> {row[value_column]:.1f} Nm³/ano<br>
                <b>Código:</b> {row.get('cd_mun', 'N/A')}<br>
                <b>Área:</b> {row.get('area_km2', 'N/A')} km²
            </div>
            """
            
            # Adicionar marcador
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=8,
                popup=folium.Popup(popup_html, max_width=250),
                color='white',
                weight=2,
                fillColor=color,
                fillOpacity=0.7,
                tooltip=f"{mun_name}: {row[value_column]:.1f}"
            ).add_to(marker_cluster)
        
        # Adicionar colormap ao mapa
        colormap.add_to(m)
        
        # Adicionar controle de camadas
        folium.LayerControl().add_to(m)
        
        # Mostrar estatísticas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Municípios", len(map_data))
        with col2:
            st.metric("Potencial Total", f"{map_data[value_column].sum():.0f}")
        with col3:
            st.metric("Maior Potencial", f"{max_val:.1f}")
        with col4:
            st.metric("Menor Potencial", f"{min_val:.1f}")
        
        # Renderizar mapa
        st_folium(m, width=None, height=600, use_container_width=True)
        
        # Informações sobre clustering
        with st.expander("ℹ️ Como usar o mapa com agrupamento"):
            st.markdown("""
            **Recursos do Mapa:**
            - 🔍 **Zoom**: Aproxime para ver marcadores individuais
            - 📊 **Clusters**: Números mostram quantos municípios estão agrupados
            - 🎨 **Cores**: Indicam intensidade do potencial de biogás
            - 💡 **Clique**: Nos marcadores para ver detalhes do município
            
            **Vantagens:**
            - Melhor performance com muitos dados
            - Visão clara em diferentes níveis de zoom
            - Fácil identificação de padrões regionais
            """)
            
    except Exception as e:
        st.error(f"Erro ao criar mapa com clustering: {e}")
        if st.session_state.get('show_debug', False):
            st.exception(e)


def render_advanced_map_section(municipios_data: pd.DataFrame, 
                               selected_municipios: List[str] = None,
                               layer_controls: Dict[str, bool] = None,
                               filters: Dict[str, Any] = None) -> None:
    """
    Renderiza seção com diferentes tipos de visualização de mapa
    
    Args:
        municipios_data: DataFrame com dados dos municípios
        selected_municipios: Lista de códigos de municípios selecionados  
        layer_controls: Controles de camadas adicionais
        filters: Filtros aplicados aos dados
    """
    
    st.markdown("### 🗺️ Visualizações Avançadas do Mapa")
    
    # Seletor de tipo de visualização
    viz_type = st.selectbox(
        "Escolha o tipo de visualização:",
        options=[
            "Mapa Padrão",
            "Mapa de Calor", 
            "Mapa com Clustering",
            "Comparação Lado a Lado"
        ],
        help="Diferentes tipos de visualização revelam padrões distintos nos dados"
    )
    
    # Seletor de variável para visualizar
    numeric_columns = [col for col in municipios_data.columns 
                      if municipios_data[col].dtype in ['int64', 'float64'] 
                      and col not in ['cd_mun', 'lat', 'lon']]
    
    if numeric_columns:
        value_column = st.selectbox(
            "Variável para visualizar:",
            options=numeric_columns,
            index=0 if 'total_final_nm_ano' not in numeric_columns else numeric_columns.index('total_final_nm_ano'),
            help="Escolha qual variável usar para colorir/dimensionar os elementos do mapa"
        )
    else:
        st.error("Nenhuma variável numérica encontrada nos dados")
        return
    
    # Renderizar visualização selecionada
    if viz_type == "Mapa Padrão":
        st.info("📍 Mapa padrão com polígonos dos municípios")
        render_map(municipios_data, layer_controls, filters)
        
    elif viz_type == "Mapa de Calor":
        st.info("🔥 Mapa de calor mostra densidade e intensidade dos dados")
        create_heatmap_visualization(municipios_data, value_column)
        
    elif viz_type == "Mapa com Clustering":
        st.info("🎯 Marcadores agrupados para melhor performance e clareza")
        create_clustered_map(municipios_data, None, value_column)
        
    elif viz_type == "Comparação Lado a Lado":
        st.info("📊 Compare diferentes visualizações simultaneamente")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Mapa de Calor**")
            create_heatmap_visualization(municipios_data, value_column)
            
        with col2:
            st.markdown("**Mapa com Clustering**") 
            create_clustered_map(municipios_data, None, value_column)


def apply_special_visualizations(folium_map, gdf_data, viz_mode, viz_settings, potencial_values):
    """Apply special visualizations to the map based on selected mode"""
    import numpy as np
    from scipy.spatial.distance import cdist
    from sklearn.cluster import KMeans
    
    if not viz_settings:
        viz_settings = {}
    
    if viz_mode == "Hotspots":
        create_hotspot_visualization(folium_map, gdf_data, potencial_values, viz_settings.get('threshold', 75))
    
    elif viz_mode == "Clusters":
        if viz_settings.get('cluster_analysis', False):
            create_cluster_visualization(folium_map, gdf_data, potencial_values)
    
    elif viz_mode == "Densidade":
        if viz_settings.get('density_heatmap', False):
            create_density_heatmap(folium_map, gdf_data, potencial_values)
    
    elif viz_mode == "Corredores":
        create_corridor_visualization(folium_map, gdf_data, potencial_values)


def create_hotspot_visualization(folium_map, gdf_data, potencial_values, threshold_percentile=75):
    """Create hotspot visualization highlighting high-potential areas"""
    threshold_value = np.percentile(potencial_values, threshold_percentile)
    
    # Create hotspot group
    hotspot_group = folium.FeatureGroup(
        name=f"🔥 Hotspots (>{threshold_percentile}º percentil)",
        overlay=True,
        control=True,
        show=True
    )
    
    # Add hotspot areas
    for _, row in gdf_data.iterrows():
        if pd.isna(row['lat']) or pd.isna(row['lon']):
            continue
            
        potencial = row.get('display_value', row.get('total_final_nm_ano', 0))
        
        if potencial >= threshold_value:
            # Create pulsing hotspot marker
            municipio_nome = row.get('nm_mun', row.get('NOME_MUNICIPIO', 'N/A'))
            
            # Add hotspot circle
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=15,
                color='#ff0000',
                weight=3,
                fillColor='#ff4444',
                fillOpacity=0.3,
                popup=f"🔥 HOTSPOT: {municipio_nome}<br>Potencial: {potencial:,.0f} Nm³/ano",
                tooltip=f"🔥 Hotspot: {municipio_nome}"
            ).add_to(hotspot_group)
            
            # Add glow effect
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=25,
                color='#ff6666',
                weight=1,
                fillColor='#ff0000',
                fillOpacity=0.1,
            ).add_to(hotspot_group)
    
    hotspot_group.add_to(folium_map)


def create_cluster_visualization(folium_map, gdf_data, potencial_values, n_clusters=5):
    """Create cluster visualization using K-means clustering"""
    # Prepare data for clustering
    valid_data = gdf_data.dropna(subset=['lat', 'lon'])
    if len(valid_data) < n_clusters:
        return
    
    # Features for clustering: location + potential
    features = valid_data[['lat', 'lon']].values
    potentials = valid_data.get('display_value', valid_data.get('total_final_nm_ano', pd.Series([0] * len(valid_data)))).values.reshape(-1, 1)
    
    # Normalize features
    features_normalized = (features - features.mean(axis=0)) / features.std(axis=0)
    potentials_normalized = (potentials - potentials.mean()) / potentials.std()
    
    # Combine features
    X = np.hstack([features_normalized, potentials_normalized])
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X)
    
    # Create cluster group
    cluster_group = folium.FeatureGroup(
        name=f"🎯 Clusters (K={n_clusters})",
        overlay=True,
        control=True,
        show=True
    )
    
    # Color palette for clusters
    cluster_colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628']
    
    # Add cluster markers
    for i in range(n_clusters):
        cluster_data = valid_data[clusters == i]
        if len(cluster_data) == 0:
            continue
            
        color = cluster_colors[i % len(cluster_colors)]
        
        # Calculate cluster centroid
        centroid_lat = cluster_data['lat'].mean()
        centroid_lon = cluster_data['lon'].mean()
        avg_potential = cluster_data.get('display_value', cluster_data.get('total_final_nm_ano', pd.Series([0] * len(cluster_data)))).mean()
        
        # Add cluster centroid
        folium.Marker(
            location=[centroid_lat, centroid_lon],
            icon=folium.DivIcon(
                html=f'''<div style="background-color: {color}; 
                         border-radius: 50%; width: 30px; height: 30px; 
                         display: flex; align-items: center; justify-content: center;
                         color: white; font-weight: bold; font-size: 12px;
                         border: 2px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                         {i+1}</div>'''
            ),
            popup=f"Cluster {i+1}<br>Municípios: {len(cluster_data)}<br>Potencial Médio: {avg_potential:,.0f} Nm³/ano",
            tooltip=f"Cluster {i+1}: {len(cluster_data)} municípios"
        ).add_to(cluster_group)
        
        # Add cluster boundary (convex hull approximation)
        if len(cluster_data) >= 3:
            coords = [[row['lat'], row['lon']] for _, row in cluster_data.iterrows()]
            try:
                folium.Polygon(
                    locations=coords,
                    color=color,
                    weight=2,
                    fillColor=color,
                    fillOpacity=0.1
                ).add_to(cluster_group)
            except:
                pass
    
    cluster_group.add_to(folium_map)


def create_density_heatmap(folium_map, gdf_data, potencial_values):
    """Create density heatmap overlay"""
    # Prepare heatmap data
    heat_data = []
    max_potential = potencial_values.max()
    
    for _, row in gdf_data.iterrows():
        if pd.isna(row['lat']) or pd.isna(row['lon']):
            continue
            
        potencial = row.get('display_value', row.get('total_final_nm_ano', 0))
        if potencial > 0:
            # Normalize intensity between 0.1 and 1.0
            intensity = max(0.1, min(1.0, potencial / max_potential))
            heat_data.append([row['lat'], row['lon'], intensity])
    
    if heat_data:
        # Add heatmap layer
        HeatMap(
            heat_data,
            name="🔥 Mapa de Densidade",
            min_opacity=0.2,
            max_zoom=18,
            radius=25,
            blur=15,
            overlay=True,
            control=True,
            show=True
        ).add_to(folium_map)


def create_corridor_visualization(folium_map, gdf_data, potencial_values, threshold_percentile=60):
    """Create visualization of high-potential corridors connecting adjacent municipalities"""
    from scipy.spatial.distance import cdist
    
    # Filter high-potential municipalities
    threshold_value = np.percentile(potencial_values, threshold_percentile)
    high_potential = gdf_data[gdf_data.get('display_value', gdf_data.get('total_final_nm_ano', pd.Series([0] * len(gdf_data)))) >= threshold_value].copy()
    
    if len(high_potential) < 2:
        return
    
    # Create corridor group
    corridor_group = folium.FeatureGroup(
        name="🛣️ Corredores de Alto Potencial",
        overlay=True,
        control=True,
        show=True
    )
    
    # Calculate distances between municipalities
    coords = high_potential[['lat', 'lon']].values
    distances = cdist(coords, coords, metric='euclidean')
    
    # Create connections for nearby municipalities (within reasonable distance)
    max_distance = 0.5  # approximately 50km in degrees
    
    added_connections = set()
    
    for i in range(len(high_potential)):
        for j in range(i + 1, len(high_potential)):
            if distances[i, j] <= max_distance:
                # Avoid duplicate connections
                connection_key = tuple(sorted([i, j]))
                if connection_key in added_connections:
                    continue
                    
                added_connections.add(connection_key)
                
                # Get municipality data
                mun1 = high_potential.iloc[i]
                mun2 = high_potential.iloc[j]
                
                # Calculate corridor strength based on combined potential
                potential1 = mun1.get('display_value', mun1.get('total_final_nm_ano', 0))
                potential2 = mun2.get('display_value', mun2.get('total_final_nm_ano', 0))
                corridor_strength = (potential1 + potential2) / 2
                
                # Line width based on corridor strength
                max_strength = potencial_values.max()
                line_weight = max(2, min(8, int((corridor_strength / max_strength) * 6) + 2))
                
                # Add corridor line
                folium.PolyLine(
                    locations=[[mun1['lat'], mun1['lon']], [mun2['lat'], mun2['lon']]],
                    color='#ff6b35',
                    weight=line_weight,
                    opacity=0.7,
                    popup=f"Corredor: {mun1.get('nm_mun', 'N/A')} ↔ {mun2.get('nm_mun', 'N/A')}<br>Força: {corridor_strength:,.0f} Nm³/ano",
                    tooltip=f"Corredor de {corridor_strength:,.0f} Nm³/ano"
                ).add_to(corridor_group)
    
    corridor_group.add_to(folium_map)