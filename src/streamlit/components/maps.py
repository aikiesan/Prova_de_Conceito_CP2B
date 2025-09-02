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
            
            # Stroke otimizado para separação sem sobreposição
            stroke_color = '#333333'  # Cinza escuro para melhor contraste
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"🏛️ {municipio_nome}: {potencial:,.0f} Nm³/ano",
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
    
    actual_controls = layer_controls.get('layer_controls', {})
    
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

def render_map(municipios_data: pd.DataFrame, selected_municipios: List[str] = None, layer_controls: Dict[str, bool] = None, filters: Dict[str, Any] = None) -> None:
    """Renderiza mapa com dados pré-filtrados do dashboard"""
    
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
    
    # Aplicar filtro de municípios selecionados (se houver)
    if selected_municipios:
        gdf_filtered = gdf_filtered[gdf_filtered['cd_mun'].isin(selected_municipios)]
    
    # Filtrar apenas os municípios que estão nos dados pré-filtrados
    municipios_filtrados_ids = municipios_data['cd_mun'].tolist()
    gdf_filtered = gdf_filtered[gdf_filtered['cd_mun'].isin(municipios_filtrados_ids)]

    # --- FIM DA CORREÇÃO NA LÓGICA DE JUNÇÃO ---
    
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