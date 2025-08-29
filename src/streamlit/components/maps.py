import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

ROOT = Path(__file__).resolve().parents[3]
SHAPEFILE_PATH = ROOT / "shapefile" / "Municipios_SP_shapefile.shp"

# Caminhos para shapefiles adicionais
ADDITIONAL_SHAPEFILES = {
    'limite_sp': ROOT / "shapefile" / "Limite_SP.shp",
    'plantas_biogas': ROOT / "shapefile" / "Plantas_Biogas_SP.shp",
    'regioes_admin': ROOT / "shapefile" / "Regiao_Adm_SP.shp"
}

@st.cache_data
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
            st.warning(f"⚠️ Erro ao carregar {name}: {e}")
            continue
    
    return loaded

def create_detailed_popup(row: pd.Series, potencial: float, filters: Dict = None) -> str:
    """Cria popup detalhado com TODOS os resíduos disponíveis no município"""
    
    municipio_nome = str(row['nm_mun']).replace("'", "").replace('"', '')
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

def create_clean_marker_map(gdf_filtered: gpd.GeoDataFrame, max_municipalities: int = 200, additional_layers: Dict = None, layer_controls: Dict = None, visualization_mode: str = "Compacto (Recomendado)", filters: Dict = None) -> folium.Map:
    """Cria mapa limpo com marcadores individuais para melhor leitura"""
    # Centro otimizado para São Paulo
    center_lat, center_lon = -23.2, -47.8
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles='OpenStreetMap',
        # Configurações otimizadas para melhor experiência
        min_zoom=6,      # Evita zoom muito distante
        max_zoom=18,     # Permite zoom detalhado
        zoom_control=True,
        scrollWheelZoom=True,
        doubleClickZoom=True,
        dragging=True
    )
    
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
            popup_html = create_detailed_popup(row, potencial, filters)
            
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
            
            # Stroke otimizado para separação sem sobreposição
            stroke_color = '#333333'  # Cinza escuro para melhor contraste
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"🏛️ {row['nm_mun']}: {potencial:,.0f} Nm³/ano",
                color=stroke_color,
                weight=stroke_weight,
                fillColor=get_color(potencial),
                fillOpacity=fill_opacity,
                opacity=border_opacity,
                bubblingMouseEvents=False # Evita conflitos de eventos
            ).add_to(municipios_group)
        
        # Adicionar grupo de municípios ao mapa
        municipios_group.add_to(m)
        
        # Legenda interativa avançada
        if potencial_values.max() > 0:
            create_interactive_legend(m, top_municipios, list(colors.values()), potencial_values)
    
    # Adicionar camadas adicionais se disponíveis
    if additional_layers and layer_controls:
        add_additional_layers_to_map(m, additional_layers, layer_controls)
    
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
    """Adiciona camadas adicionais ao mapa usando Feature Groups para controle individual"""
    
    # Criar grupos de camadas para controle individual
    layer_groups = {}
    
    # Adicionar limite de SP
    if layer_controls.get('limite_sp', False) and 'limite_sp' in additional_layers:
        try:
            limite_group = folium.FeatureGroup(name="🔴 Limite de SP", show=True)
            
            folium.GeoJson(
                additional_layers['limite_sp'],
                style_function=lambda x: {
                    'color': '#FF0000',
                    'weight': 2,
                    'fillOpacity': 0,
                    'opacity': 0.6,
                    'dashArray': '5, 5'  # Linha tracejada para não interferir
                },
                tooltip=folium.Tooltip("Limite do Estado de São Paulo")
            ).add_to(limite_group)
            
            limite_group.add_to(folium_map)
            layer_groups['limite_sp'] = limite_group
            
        except Exception as e:
            st.warning(f"Erro ao adicionar limite SP: {e}")
    
    # Adicionar usinas de biogás existentes
    if layer_controls.get('plantas_biogas', False) and 'plantas_biogas' in additional_layers:
        try:
            plantas_group = folium.FeatureGroup(name="🏭 Usinas Existentes", show=True)
            plantas_gdf = additional_layers['plantas_biogas']
            
            for idx, row in plantas_gdf.iterrows():
                # Extrair coordenadas do ponto
                if hasattr(row.geometry, 'x') and hasattr(row.geometry, 'y'):
                    lat, lon = row.geometry.y, row.geometry.x
                else:
                    # Se for polígono, usar centroide
                    centroid = row.geometry.centroid
                    lat, lon = centroid.y, centroid.x
                
                # Criar popup com informações da usina
                nome_usina = row.get('NOME', row.get('Nome', row.get('nome', 'Usina de Biogás')))
                tipo_usina = row.get('TIPO', row.get('Tipo', row.get('tipo', 'N/A')))
                
                popup_html = f"""
                <div style='width: 200px; font-family: Arial;'>
                    <h4>🏭 {nome_usina}</h4>
                    <b>Tipo:</b> {tipo_usina}<br>
                    <b>Coordenadas:</b> {lat:.4f}, {lon:.4f}
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=220),
                    tooltip=f"Usina: {nome_usina}",
                    icon=folium.Icon(
                        color='orange',
                        icon='industry',
                        prefix='fa'
                    )
                ).add_to(plantas_group)
            
            plantas_group.add_to(folium_map)
            layer_groups['plantas_biogas'] = plantas_group
                
        except Exception as e:
            st.warning(f"Erro ao adicionar plantas de biogás: {e}")
    
    # Adicionar regiões administrativas
    if layer_controls.get('regioes_admin', False) and 'regioes_admin' in additional_layers:
        try:
            regioes_group = folium.FeatureGroup(name="🌍 Regiões Admin.", show=True)
            
            # Cores diferentes para cada região
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
            
            regioes_gdf = additional_layers['regioes_admin']
            
            for idx, row in regioes_gdf.iterrows():
                color = colors[idx % len(colors)]
                nome_regiao = row.get('NOME', row.get('Nome', row.get('nome', f'Região {idx+1}')))
                
                folium.GeoJson(
                    row.geometry,
                    style_function=lambda x, color=color: {
                        'color': color,
                        'weight': 1,
                        'fillOpacity': 0.05,  # Muito transparente para não interferir
                        'opacity': 0.5
                    },
                    popup=folium.Popup(f"<b>Região Administrativa:</b><br>{nome_regiao}", max_width=200),
                    tooltip=f"Região: {nome_regiao}"
                ).add_to(regioes_group)
            
            regioes_group.add_to(folium_map)
            layer_groups['regioes_admin'] = regioes_group
                
        except Exception as e:
            st.warning(f"Erro ao adicionar regiões administrativas: {e}")
    
    # Adicionar controle de camadas se houver camadas
    if layer_groups:
        folium.LayerControl(
            position='topright',
            collapsed=False
        ).add_to(folium_map)

def render_layer_controls_below_map(municipios_data: pd.DataFrame) -> Dict[str, bool]:
    """Renderiza controles de camadas adicionais ABAIXO do mapa"""
    
    # Estilo para a seção de controles
    st.markdown("""
    <style>
    .map-controls-section {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .control-section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="control-section-title">🗺️ Camadas Adicionais</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Selecione camadas:**")
        layer_options = st.multiselect(
            "Escolha as camadas para exibir:",
            options=[
                "🏭 Plantas de Biogás Existentes",
                "🏛️ Regiões Administrativas", 
                "🗺️ Limite de São Paulo",
                "🌾 Áreas Agrícolas",
            ],
            default=[],
            key="map_layer_selector_below_map"
        )
    
    with col2:
        st.markdown("**📊 Status:**")
        display_count = len(municipios_data[municipios_data['display_value'] > 0]) if 'display_value' in municipios_data.columns else len(municipios_data)
        st.info(f"🎯 **Exibindo:** {len(municipios_data)} municípios ({display_count} com potencial)")
    
    # Converter multiselect para o formato esperado
    layer_mapping = {
        "🏭 Plantas de Biogás Existentes": "plantas_biogas",
        "🏛️ Regiões Administrativas": "regioes_admin",
        "🗺️ Limite de São Paulo": "limite_sp",
    }
    
    return {
        'selected_layers': layer_options,
        'layer_controls': {layer_mapping.get(layer, False): layer in layer_options for layer in layer_mapping}
    }


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

def render_map(municipios_data: pd.DataFrame, selected_municipios: List[str] = None, layer_controls: Dict[str, bool] = None, filters: Dict[str, Any] = None) -> None:
    """Renderiza mapa com dados pré-filtrados do dashboard"""
    
    # Verificar se dados já vêm pré-filtrados
    is_pre_filtered = filters and filters.get('pre_filtered', False)
    
    
    # Controles movidos para depois do mapa - apenas definir variáveis padrão
    layer_options = []  # Será definido depois do mapa
    
    # Os dados já vêm pré-filtrados do dashboard, apenas usar diretamente
    # Carregar shapefile principal
    gdf = load_and_process_shapefile()
    
    if gdf is None:
        st.error("Não foi possível carregar o mapa")
        return
    
    # Processar camadas adicionais
    additional_layers = {}
    if layer_options:
        with st.spinner("Carregando camadas adicionais..."):
            layer_mapping = {
                "🏭 Plantas de Biogás Existentes": "plantas_biogas",
                "🏛️ Regiões Administrativas": "regioes_admin",
                "🗺️ Limite de São Paulo": "limite_sp",
            }
            
            shapefile_layers = load_additional_shapefiles()
            for layer_name in layer_options:
                layer_key = layer_mapping.get(layer_name)
                if layer_key and layer_key in shapefile_layers:
                    additional_layers[layer_key] = shapefile_layers[layer_key]

    # Camadas carregadas silenciosamente
    
    # Processar dados pré-filtrados do dashboard
    if hasattr(municipios_data, 'to_dict'):
        municipios_dict = municipios_data.set_index('cd_mun').to_dict('index')
    else:
        municipios_dict = {str(m.get('cd_mun', m.get('CD_MUN'))): m for m in municipios_data}
    
    # Junção shapefile + dados pré-filtrados
    gdf_filtered = gdf.copy()
    
    # Transferir dados do SQLite para o GeoDataFrame
    for idx, row in gdf_filtered.iterrows():
        cd_mun = row['cd_mun']
        if cd_mun in municipios_dict:
            sqlite_data = municipios_dict[cd_mun]
            # Atualizar todas as colunas dos dados filtrados
            for col in municipios_data.columns:
                if col in sqlite_data and col != 'cd_mun':
                    try:
                        value = float(sqlite_data[col] or 0)
                        gdf_filtered.at[idx, col] = value
                    except (ValueError, TypeError):
                        gdf_filtered.at[idx, col] = 0
    
    # Aplicar filtro de municípios selecionados
    if selected_municipios:
        gdf_filtered = gdf_filtered[gdf_filtered['cd_mun'].isin(selected_municipios)]
    
    # Filtrar apenas os municípios que estão nos dados pré-filtrados
    municipios_filtrados_ids = municipios_data['cd_mun'].astype(str).tolist()
    gdf_filtered = gdf_filtered[gdf_filtered['cd_mun'].isin(municipios_filtrados_ids)]
    
    # Garantir que display_value existe no GeoDataFrame
    if 'display_value' not in gdf_filtered.columns and 'display_value' in municipios_data.columns:
        gdf_filtered = gdf_filtered.merge(
            municipios_data[['cd_mun', 'display_value']], 
            left_on='cd_mun', 
            right_on='cd_mun', 
            how='left'
        )
        gdf_filtered['display_value'] = gdf_filtered['display_value'].fillna(0)
    
    # Verificar compatibilidade de códigos automaticamente
    shapefile_ids = set(gdf['cd_mun'].astype(str))
    data_ids = set(municipios_data['cd_mun'].astype(str))
    intersection = shapefile_ids.intersection(data_ids)
    
    if len(intersection) == 0:
        
        # Corrigir formato dos códigos - remover .0 dos dados
        gdf_filtered = gdf.copy()
        municipios_data_copy = municipios_data.copy()
        
        # Normalizar códigos para string sem .0
        gdf_filtered['cd_mun_clean'] = gdf_filtered['cd_mun'].astype(str).str.replace('.0', '')
        municipios_data_copy['cd_mun_clean'] = municipios_data_copy['cd_mun'].astype(str).str.replace('.0', '')
        
        # Verificar match após limpeza
        clean_intersection = set(gdf_filtered['cd_mun_clean']).intersection(set(municipios_data_copy['cd_mun_clean']))
        
        # Merge com códigos limpos e resolver conflitos de colunas
        gdf_filtered = gdf_filtered.merge(
            municipios_data_copy,
            left_on='cd_mun_clean',
            right_on='cd_mun_clean',
            how='inner',
            suffixes=('_shp', '_data')
        )
        
        # Resolver conflitos de colunas comuns e garantir colunas essenciais
        if 'cd_mun_data' in gdf_filtered.columns and 'cd_mun_shp' in gdf_filtered.columns:
            gdf_filtered['cd_mun'] = gdf_filtered['cd_mun_shp']  # Manter o do shapefile
        
        if 'nm_mun_data' in gdf_filtered.columns and 'nm_mun_shp' in gdf_filtered.columns:
            gdf_filtered['nm_mun'] = gdf_filtered['nm_mun_shp']  # Manter o do shapefile
        elif 'nm_mun_data' in gdf_filtered.columns:
            gdf_filtered['nm_mun'] = gdf_filtered['nm_mun_data']
        elif 'nm_mun_shp' in gdf_filtered.columns:
            gdf_filtered['nm_mun'] = gdf_filtered['nm_mun_shp']
        
        # Garantir que colunas essenciais existam usando dados da origem correta
        essential_columns = ['total_final_nm_ano', 'total_agricola_nm_ano', 'total_pecuaria_nm_ano', 'display_value']
        for col in essential_columns:
            if col not in gdf_filtered.columns:
                # Tentar pegar da versão _data primeiro, depois _shp
                if f'{col}_data' in gdf_filtered.columns:
                    gdf_filtered[col] = gdf_filtered[f'{col}_data']
                elif f'{col}_shp' in gdf_filtered.columns:
                    gdf_filtered[col] = gdf_filtered[f'{col}_shp']
                else:
                    # Se não existir, criar com zeros
                    gdf_filtered[col] = 0.0
        
        # Garantir que lat/lon existam
        if 'lat' not in gdf_filtered.columns or 'lon' not in gdf_filtered.columns:
            if 'geometry' in gdf_filtered.columns:
                gdf_filtered['centroid'] = gdf_filtered.geometry.centroid
                gdf_filtered['lat'] = gdf_filtered['centroid'].y
                gdf_filtered['lon'] = gdf_filtered['centroid'].x
        
    
    # Verificação final das colunas essenciais (silenciosa)
    required_cols = ['nm_mun', 'cd_mun', 'total_final_nm_ano', 'display_value', 'lat', 'lon', 'geometry']
    missing_cols = [col for col in required_cols if col not in gdf_filtered.columns]
    
    if missing_cols:
        # Criar colunas em falta com valores padrão silenciosamente
        for col in missing_cols:
            if col in ['lat', 'lon']:
                if 'geometry' in gdf_filtered.columns:
                    centroids = gdf_filtered.geometry.centroid
                    if col == 'lat':
                        gdf_filtered['lat'] = centroids.y
                    else:
                        gdf_filtered['lon'] = centroids.x
                else:
                    gdf_filtered[col] = 0.0
            else:
                gdf_filtered[col] = 0.0 if col not in ['nm_mun', 'cd_mun'] else 'Unknown'
    
    # Criar e renderizar mapa com dados pré-filtrados
    try:
        biogas_map = create_clean_marker_map(
            gdf_filtered, 
            500,  # Usar limite alto já que dados vêm filtrados
            additional_layers=additional_layers,
            layer_controls=layer_controls,
            visualization_mode="Compacto (Recomendado)",
            filters={'pre_filtered': True}  # Indicar que dados já estão filtrados
        )
        
        
        # CONTAINER DO MAPA COM AJUSTE DE ALTURA BASEADO NO MODO
        fullscreen_mode = filters.get('fullscreen_mode', False)
        map_height = 800 if fullscreen_mode else 600  # Altura maior em fullscreen
        
        map_container = st.container()
        with map_container:
            # Key simples baseada no número de municípios filtrados
            import hashlib
            
            # Criar hash baseado nos dados filtrados
            data_signature = f"{len(municipios_data)}_{len(layer_options)}_{fullscreen_mode}"
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
                height=map_height,
                use_container_width=True,
                returned_objects=["last_object_clicked"],
                key=map_key  # Key única força regeneração total
            )
        
        # Informação do clique (removida para simplificar)
        pass
            
    except Exception as e:
        st.error(f"Erro ao renderizar mapa: {e}")
        # Debug removido para simplificar
        pass