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
            'Bio_Final': 'total_final',
            'Bio_Agric': 'total_agricola', 
            'Bio_Pecuar': 'total_pecuaria',
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
        top_municipios = gdf_filtered.nlargest(max_municipalities, 'total_final')
    else:
        top_municipios = gdf_filtered
    
    if len(top_municipios) == 0:
        return m
    
    # Definir cores baseado na coluna de display
    if 'display_value' in top_municipios.columns:
        potencial_values = top_municipios['display_value']
    else:
        potencial_values = top_municipios['total_final']
    
    if potencial_values.max() > 0:
        quantiles = potencial_values.quantile([0, 0.25, 0.5, 0.75, 1.0]).values
        colors = ['#cccccc', '#c2e699', '#78c679', '#31a354', '#006837']
        
        def get_color(potencial):
            if potencial == 0:
                return colors[0]
            elif potencial <= quantiles[1]:
                return colors[1]
            elif potencial <= quantiles[2]:
                return colors[2]
            elif potencial <= quantiles[3]:
                return colors[3]
            else:
                return colors[4]
        
        # Criar grupo para municípios (camada base)
        municipios_group = folium.FeatureGroup(name="📍 Municípios (Biogás)", show=True)
        
        # Adicionar marcadores ao grupo
        for _, row in top_municipios.iterrows():
            if pd.isna(row['lat']) or pd.isna(row['lon']):
                continue
                
            potencial = row.get('display_value', row['total_final'])
            
            popup_html = f"""
            <div style='width: 250px; font-family: Arial;'>
                <h4>{row['nm_mun']}</h4>
                <b>Valor Exibido:</b> {potencial:,.0f} Nm³/ano<br>
                <b>Total Geral:</b> {row['total_final']:,.0f} Nm³/ano<br>
                <b>Agrícola:</b> {row.get('total_agricola', 0):,.0f} Nm³/ano<br>
                <b>Pecuária:</b> {row.get('total_pecuaria', 0):,.0f} Nm³/ano<br>
                <b>Código:</b> {row['cd_mun']}<br>
                <b>Área:</b> {row.get('area_km2', 0):,.1f} km²
            </div>
            """
            
            radius = max(4, min(15, (potencial / potencial_values.max()) * 15)) if potencial_values.max() > 0 else 4
            
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=radius,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"{row['nm_mun']}: {potencial:,.0f} Nm³/ano",
                color='black',
                weight=1,
                fillColor=get_color(potencial),
                fillOpacity=0.7
            ).add_to(municipios_group)
        
        # Adicionar grupo dos municípios ao mapa
        municipios_group.add_to(m)
        
        # Legenda interativa avançada
        if potencial_values.max() > 0:
            create_interactive_legend(m, top_municipios, colors, potencial_values)
    
    # Adicionar camadas adicionais se disponíveis
    if additional_layers and layer_controls:
        add_additional_layers_to_map(m, additional_layers, layer_controls)
    
    return m

def create_interactive_legend(m: folium.Map, municipios_data: pd.DataFrame, colors: List[str], potencial_values: pd.Series) -> None:
    """Cria legenda interativa detalhada com estatísticas"""
    
    # Verificações de segurança
    if municipios_data.empty or len(colors) == 0:
        return
    
    try:
        # Valores padrão para estatísticas
        total_municipios = len(municipios_data)
        max_potencial = float(potencial_values.max()) if not potencial_values.empty else 0
        
        # Determinar camada ativa
        current_layer = 'Total Geral'
        if 'display_value' in municipios_data.columns:
            # Verificar se é uma fonte específica
            if municipios_data['display_value'].equals(municipios_data.get('total_agricola', pd.Series())):
                current_layer = 'Agrícola'
            elif municipios_data['display_value'].equals(municipios_data.get('total_pecuaria', pd.Series())):
                current_layer = 'Pecuária'
        
        # Criar HTML da legenda simplificada
        legend_html = f"""
        <div id='interactive-legend' style='
            position: fixed; top: 10px; right: 10px; width: 280px; 
            background: white; border: 1px solid #ccc; z-index: 9999; 
            border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            font-family: Arial, sans-serif; font-size: 12px;'>
            
            <!-- Cabeçalho -->
            <div style='padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; border-radius: 8px 8px 0 0; font-weight: 600;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span>📊 Análise de Biogás</span>
                    <button id='legend-toggle' onclick='toggleLegend()' 
                            style='border: none; background: rgba(255,255,255,0.2); color: white;
                                   cursor: pointer; font-size: 12px; border-radius: 4px; padding: 2px 6px;'>
                        ▼
                    </button>
                </div>
            </div>
            
            <div id='legend-content' style='padding: 12px;'>
                
                <!-- Camada Ativa -->
                <div style='margin-bottom: 12px; padding: 8px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #006837;'>
                    <div style='font-weight: 600; color: #495057; margin-bottom: 4px;'>
                        Camada Ativa
                    </div>
                    <div style='font-size: 14px; color: #212529;'>
                        🎯 {current_layer}
                    </div>
                    <div style='font-size: 10px; color: #6c757d; margin-top: 4px;'>
                        Máximo: {max_potencial:,.0f} Nm³/ano
                    </div>
                </div>
                
                <!-- Escala de Cores -->
                <div style='margin-bottom: 12px;'>
                    <div style='font-weight: 500; margin-bottom: 6px; color: #495057;'>
                        Escala de Intensidade
                    </div>
                    <div style='display: flex; align-items: center; gap: 4px; margin-bottom: 4px;'>
                        <span style='color:{colors[4] if len(colors) > 4 else "#006837"}; font-size: 18px;'>●</span>
                        <span style='font-size: 11px;'>Alto (&gt; 75%)</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 4px; margin-bottom: 4px;'>
                        <span style='color:{colors[3] if len(colors) > 3 else "#31a354"}; font-size: 18px;'>●</span>
                        <span style='font-size: 11px;'>Médio-Alto (50-75%)</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 4px; margin-bottom: 4px;'>
                        <span style='color:{colors[2] if len(colors) > 2 else "#78c679"}; font-size: 18px;'>●</span>
                        <span style='font-size: 11px;'>Médio (25-50%)</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 4px; margin-bottom: 4px;'>
                        <span style='color:{colors[1] if len(colors) > 1 else "#c2e699"}; font-size: 18px;'>●</span>
                        <span style='font-size: 11px;'>Baixo (1-25%)</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 4px;'>
                        <span style='color:{colors[0] if len(colors) > 0 else "#cccccc"}; font-size: 18px;'>●</span>
                        <span style='font-size: 11px;'>Zero</span>
                    </div>
                </div>
                
                <!-- Estatísticas Resumidas -->
                <div style='margin-bottom: 12px;'>
                    <div style='font-weight: 500; margin-bottom: 6px; color: #495057;'>
                        Estatísticas da Visualização
                    </div>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px;'>
                        <div style='background: #e8f5e8; padding: 6px; border-radius: 4px; text-align: center;'>
                            <div style='font-weight: 600; color: #155724;'>{total_municipios:,}</div>
                            <div style='color: #155724;'>Municípios</div>
                        </div>
                        <div style='background: #f8d7da; padding: 6px; border-radius: 4px; text-align: center;'>
                            <div style='font-weight: 600; color: #721c24;'>{max_potencial:,.0f}</div>
                            <div style='color: #721c24;'>Máximo</div>
                        </div>
                    </div>
                </div>
                
                <!-- Dicas de Uso -->
                <div style='padding: 8px; background: #e9ecef; border-radius: 4px; font-size: 10px; color: #495057;'>
                    <div style='font-weight: 500; margin-bottom: 2px;'>💡 Dicas:</div>
                    <div>• Use os controles da sidebar para alterar a visualização</div>
                    <div>• Clique nos municípios para ver detalhes</div>
                    <div>• Use o controle de camadas para contexto geográfico</div>
                </div>
                
            </div>
        </div>
        
        <!-- JavaScript para funcionalidade -->
        <script>
            let isLegendExpanded = true;
            
            function toggleLegend() {{
                const content = document.getElementById('legend-content');
                const button = document.getElementById('legend-toggle');
                
                if (isLegendExpanded) {{
                    content.style.display = 'none';
                    button.innerHTML = '▲';
                    isLegendExpanded = false;
                }} else {{
                    content.style.display = 'block';
                    button.innerHTML = '▼';
                    isLegendExpanded = true;
                }}
            }}
        </script>
        """
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
    except Exception as e:
        # Em caso de erro, criar uma legenda básica
        simple_legend_html = """
        <div style='position: fixed; top: 10px; right: 10px; width: 200px; 
                    background: white; border: 1px solid #ccc; z-index: 9999; 
                    font-size: 12px; padding: 8px; border-radius: 4px;'>
            <b>Potencial de Biogás</b><br>
            <div style='margin: 2px 0;'><span style='color:#006837; font-size: 16px;'>●</span> Alto</div>
            <div style='margin: 2px 0;'><span style='color:#31a354; font-size: 16px;'>●</span> Médio-Alto</div>
            <div style='margin: 2px 0;'><span style='color:#78c679; font-size: 16px;'>●</span> Médio</div>
            <div style='margin: 2px 0;'><span style='color:#c2e699; font-size: 16px;'>●</span> Baixo</div>
            <div style='margin: 2px 0;'><span style='color:#cccccc; font-size: 16px;'>●</span> Zero</div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(simple_legend_html))

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
            for col in ['total_final', 'total_agricola', 'total_pecuaria']:
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