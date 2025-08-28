import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
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
                st.success(f"✅ Carregado: {name} ({len(gdf)} features)")
                
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar {name}: {e}")
            continue
    
    return loaded

def create_clean_marker_map(gdf_filtered: gpd.GeoDataFrame, max_municipalities: int = 200, additional_layers: Dict = None, layer_controls: Dict = None) -> folium.Map:
    """Cria mapa limpo com marcadores"""
    center_lat, center_lon = -23.5, -47.5
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # Limitar municípios
    if len(gdf_filtered) > max_municipalities:
        top_municipios = gdf_filtered.nlargest(max_municipalities, 'total_final_nm_ano')
    else:
        top_municipios = gdf_filtered
    
    if len(top_municipios) == 0:
        return m
    
    # Definir cores baseado na coluna de display
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
        
        # Criar cluster para municípios (performance otimizada)
        marker_cluster = MarkerCluster(
            name="📍 Municípios (Biogás)",
            overlay=True,
            control=True,
            show=True,
            options={
                'disableClusteringAtZoom': 12,  # Desabilita clustering em zoom alto
                'maxClusterRadius': 60,         # Raio máximo do cluster
                'spiderfyOnMaxZoom': True,     # Expande marcadores sobrepostos
                'showCoverageOnHover': False,   # Não mostrar área de cobertura
                'zoomToBoundsOnClick': True    # Zoom ao clicar no cluster
            }
        )
        
        # Adicionar marcadores ao cluster
        for _, row in top_municipios.iterrows():
            if pd.isna(row['lat']) or pd.isna(row['lon']):
                continue
                
            potencial = row.get('display_value', row['total_final_nm_ano'])
            
            # Popup otimizado com design moderno
            popup_html = f"""
            <div style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                        width: 280px; padding: 12px; border-radius: 8px; background: #fff;'>
                <div style='border-bottom: 3px solid #667eea; padding-bottom: 8px; margin-bottom: 12px;'>
                    <h4 style='margin: 0; color: #2c3e50; font-size: 18px; font-weight: 600;'>
                        🏛️ {row['nm_mun']}
                    </h4>
                </div>
                
                <div style='display: grid; gap: 8px;'>
                    <div style='background: linear-gradient(135deg, #667eea20, #764ba220); 
                                padding: 8px; border-radius: 6px; border-left: 3px solid #667eea;'>
                        <strong style='color: #667eea; font-size: 12px;'>⚡ POTENCIAL EXIBIDO</strong><br>
                        <span style='font-size: 16px; font-weight: 700; color: #2c3e50;'>
                            {potencial:,.0f}
                        </span> <span style='color: #6b7280; font-size: 12px;'>Nm³/ano</span>
                    </div>
                    
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px;'>
                        <div>
                            <strong style='color: #48bb78;'>🌾 Agrícola:</strong><br>
                            <span style='font-weight: 600;'>{row.get("total_agricola", 0):,.0f}</span>
                        </div>
                        <div>
                            <strong style='color: #ed8936;'>🐄 Pecuária:</strong><br>
                            <span style='font-weight: 600;'>{row.get("total_pecuaria", 0):,.0f}</span>
                        </div>
                        <div>
                            <strong style='color: #4299e1;'>📊 Total:</strong><br>
                            <span style='font-weight: 600;'>{row["total_final_nm_ano"]:,.0f}</span>
                        </div>
                        <div>
                            <strong style='color: #9f7aea;'>📍 Área:</strong><br>
                            <span style='font-weight: 600;'>{row.get("area_km2", 0):,.1f} km²</span>
                        </div>
                    </div>
                    
                    <div style='text-align: center; margin-top: 8px; padding: 4px; 
                                background: #f8f9fa; border-radius: 4px; font-size: 10px; color: #6b7280;'>
                        🔢 Código Municipal: <strong>{row["cd_mun"]}</strong>
                    </div>
                </div>
            </div>
            """
            
            # Raio dinâmico melhorado
            radius = max(5, min(18, (potencial / potencial_values.max()) * 18)) if potencial_values.max() > 0 else 6
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=320),
                tooltip=f"🏛️ {row['nm_mun']}: {potencial:,.0f} Nm³/ano",
                color='#2c3e50',          # Borda mais elegante
                weight=2,                 # Borda mais definida
                fillColor=get_color(potencial),
                fillOpacity=0.8           # Mais opaco para melhor visibilidade
            ).add_to(marker_cluster)
        
        # Adicionar cluster ao mapa
        marker_cluster.add_to(m)
        
        # Legenda interativa avançada
        if potencial_values.max() > 0:
            create_interactive_legend(m, top_municipios, list(colors.values()), potencial_values)
    
    # Adicionar camadas adicionais se disponíveis
    if additional_layers and layer_controls:
        add_additional_layers_to_map(m, additional_layers, layer_controls)
    
    return m

def create_interactive_legend(m: folium.Map, municipios_data: pd.DataFrame, colors: List[str], potencial_values: pd.Series) -> None:
    """Cria legenda simplificada e performática"""
    
    if municipios_data.empty or len(colors) == 0:
        return
    
    try:
        max_potencial = float(potencial_values.max()) if not potencial_values.empty else 0
        total_municipios = len(municipios_data)
        
        # Legenda simplificada - apenas 30 linhas vs 150+ anteriores
        legend_html = f"""
        <div style='position: fixed; top: 10px; right: 10px; width: 200px; 
                    background: rgba(255,255,255,0.95); backdrop-filter: blur(8px);
                    border: 1px solid rgba(0,0,0,0.1); z-index: 9999; 
                    border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
            
            <!-- Header com gradiente moderno -->
            <div style='padding: 12px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; border-radius: 12px 12px 0 0; font-weight: 600; font-size: 13px;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <span style='font-size: 16px;'>📊</span>
                    <span>Potencial de Biogás</span>
                </div>
            </div>
            
            <!-- Escala de cores -->
            <div style='padding: 16px;'>
                <div style='margin-bottom: 12px;'>
                    <div style='font-weight: 500; margin-bottom: 8px; color: #2d3748; font-size: 12px;'>
                        Intensidade (Nm³/ano)
                    </div>
                    <div style='display: flex; flex-direction: column; gap: 4px;'>
                        <div style='display: flex; align-items: center; gap: 6px;'>
                            <div style='width: 12px; height: 12px; border-radius: 50%; background: #7f2704;'></div>
                            <span style='font-size: 11px; color: #4a5568;'>Excepcional (&gt;90%)</span>
                        </div>
                        <div style='display: flex; align-items: center; gap: 6px;'>
                            <div style='width: 12px; height: 12px; border-radius: 50%; background: #a63603;'></div>
                            <span style='font-size: 11px; color: #4a5568;'>Alto (75-90%)</span>
                        </div>
                        <div style='display: flex; align-items: center; gap: 6px;'>
                            <div style='width: 12px; height: 12px; border-radius: 50%; background: #e6550d;'></div>
                            <span style='font-size: 11px; color: #4a5568;'>Médio-Alto (55-75%)</span>
                        </div>
                        <div style='display: flex; align-items: center; gap: 6px;'>
                            <div style='width: 12px; height: 12px; border-radius: 50%; background: #fd8d3c;'></div>
                            <span style='font-size: 11px; color: #4a5568;'>Médio (35-55%)</span>
                        </div>
                        <div style='display: flex; align-items: center; gap: 6px;'>
                            <div style='width: 12px; height: 12px; border-radius: 50%; background: #fdae6b;'></div>
                            <span style='font-size: 11px; color: #4a5568;'>Baixo (15-35%)</span>
                        </div>
                        <div style='display: flex; align-items: center; gap: 6px;'>
                            <div style='width: 12px; height: 12px; border-radius: 50%; background: #fdd49e;'></div>
                            <span style='font-size: 11px; color: #4a5568;'>Muito Baixo (5-15%)</span>
                        </div>
                        <div style='display: flex; align-items: center; gap: 6px;'>
                            <div style='width: 12px; height: 12px; border-radius: 50%; background: #e8e8e8;'></div>
                            <span style='font-size: 11px; color: #4a5568;'>Zero</span>
                        </div>
                    </div>
                </div>
                
                <!-- Stats rápidas -->
                <div style='padding: 8px; background: #f7fafc; border-radius: 6px; font-size: 10px;'>
                    <div style='color: #2d3748;'><strong>{total_municipios}</strong> municípios</div>
                    <div style='color: #4a5568;'>Max: {max_potencial:,.0f}</div>
                </div>
            </div>
        </div>
        """
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
    except Exception:
        # Fallback ultra-simples
        simple_legend = f"""
        <div style='position: fixed; top: 10px; right: 10px; background: white; 
                    padding: 12px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    font-family: system-ui; font-size: 12px; z-index: 9999;'>
            <div style='font-weight: 600; margin-bottom: 8px; color: #2d3748;'>Biogás SP</div>
            <div><span style='color: #7f2704;'>●</span> Excepcional</div>
            <div><span style='color: #a63603;'>●</span> Alto</div>
            <div><span style='color: #fd8d3c;'>●</span> Médio</div>
            <div><span style='color: #fdd49e;'>●</span> Baixo</div>
            <div><span style='color: #e8e8e8;'>●</span> Zero</div>
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

def render_layer_controls() -> Dict[str, bool]:
    """Renderiza controles de camadas adicionais"""
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
    """Renderiza mapa com interface limpa e suporte a múltiplas camadas"""
    
    # Título dinâmico baseado no modo de visualização
    viz_mode = filters.get('visualization', {}) if filters else {}
    if viz_mode.get('mode') == "Por Categoria":
        title = f"🗺️ Potencial de Biogás - {viz_mode.get('category')}"
    elif viz_mode.get('mode') == "Por Fonte Específica":
        source_names = {
            'biogas_cana': 'Cana-de-açúcar',
            'biogas_soja': 'Soja',
            'biogas_milho': 'Milho',
            'biogas_bovino': 'Bovinos',
            'biogas_cafe': 'Café',
            'biogas_citros': 'Citros',
            'biogas_suinos': 'Suínos',
            'biogas_aves': 'Aves',
            'biogas_piscicultura': 'Piscicultura',
            'total_ch4_rsu_rpo': 'RSU + RPO'
        }
        source_name = source_names.get(viz_mode.get('source'), 'Fonte Específica')
        title = f"🗺️ Potencial de Biogás - {source_name}"
    else:
        title = "🗺️ Potencial Total de Biogás"
    
    st.subheader(title)
    
    # Carregar shapefile principal
    gdf = load_and_process_shapefile()
    
    if gdf is None:
        st.error("Não foi possível carregar o mapa")
        return
    
    # Carregar shapefiles adicionais se necessário
    additional_layers = {}
    if layer_controls and any(layer_controls.values()):
        with st.spinner("Carregando camadas adicionais..."):
            additional_layers = load_additional_shapefiles()
    
    # Controles do mapa
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        max_municipalities = st.slider(
            "Máximo de Municípios no Mapa:",
            min_value=50, max_value=645, value=200, step=25
        )

    with col2:
        # Mostrar status das camadas carregadas
        if additional_layers:
            layers_loaded = len(additional_layers)
            st.success(f"✅ {layers_loaded} camada(s) adicional(is) carregada(s)")
            st.info("🎛️ **Controle de Camadas:** Use o painel no canto superior direito do mapa para ativar/desativar camadas individualmente")
        else:
            st.info("📍 Apenas camada principal de municípios ativa")

    with col3:
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()
    
    # Processar dados
    if hasattr(municipios_data, 'to_dict'):
        municipios_dict = municipios_data.set_index('cd_mun').to_dict('index')
    else:
        municipios_dict = {str(m.get('cd_mun', m.get('CD_MUN'))): m for m in municipios_data}
    
    # Junção shapefile + dados
    gdf_filtered = gdf.copy()
    
    # Adicionar fonte de dados
    gdf_filtered['data_source'] = 'shapefile'
    gdf_filtered.loc[gdf_filtered['cd_mun'].isin(municipios_dict.keys()), 'data_source'] = 'sqlite'
    
    # Atualizar dados do SQLite
    for idx, row in gdf_filtered.iterrows():
        cd_mun = row['cd_mun']
        if cd_mun in municipios_dict:
            sqlite_data = municipios_dict[cd_mun]
            for col in ['total_final_nm_ano', 'total_agricola_nm_ano', 'total_pecuaria_nm_ano']:
                if col in sqlite_data:
                    gdf_filtered.at[idx, col] = float(sqlite_data[col] or 0)
    
    # Aplicar filtro de municípios selecionados
    if selected_municipios:
        gdf_filtered = gdf_filtered[gdf_filtered['cd_mun'].isin(selected_municipios)]
    
    # Estatísticas (removidas para simplificar)
    pass
    
    # Criar e renderizar mapa
    try:
        biogas_map = create_clean_marker_map(
            gdf_filtered, 
            max_municipalities, 
            additional_layers=additional_layers,
            layer_controls=layer_controls
        )
        
        map_data = st_folium(
            biogas_map, 
            width=None,
            height=600,
            use_container_width=True,
            returned_objects=["last_object_clicked"]
        )
        
        # Informação do clique (removida para simplificar)
        pass
            
    except Exception as e:
        st.error(f"Erro ao renderizar mapa: {e}")
        # Debug removido para simplificar
        pass