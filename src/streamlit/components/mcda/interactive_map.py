# interactive_map.py - FINAL, GUARANTEED VERSION

import streamlit as st
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import st_folium
from typing import Optional, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
MAP_CONFIG = {
    'center_rmc': [-22.9, -47.1],
    'default_zoom': 10,
    'polygon_weight': 0.5,
    'polygon_opacity': 0.7,
    'polygon_fill_opacity': 0.6,
}

# --- 1. DATA LOADING (OPTIMIZED) ---
@st.cache_data
def load_properties_geoparquet() -> gpd.GeoDataFrame:
    """
    Loads pre-processed properties using an unbreakable, absolute path.
    """
    try:
        logger.info("🔄 Loading pre-processed GeoParquet file using absolute path...")
        # --- THIS IS THE UNBREAKABLE PATH LOGIC ---
        # 1. Get the path of the current file (interactive_map.py)
        current_file_path = Path(__file__)
        # 2. Go up two directories (mcda -> components -> streamlit) to find the root folder
        streamlit_root = current_file_path.parent.parent.parent
        # 3. Construct the full path to the data file
        geoparquet_path = streamlit_root / "CP2B_Processed_Geometries.geoparquet"
        
        gdf = gpd.read_parquet(geoparquet_path)
        gdf = gdf.set_geometry('geometry')
        gdf.sindex
        logger.info(f"✅ {len(gdf)} properties loaded from GeoParquet.")
        return gdf
    except FileNotFoundError:
        logger.error("❌ GeoParquet file not found! Run preprocess_data.py first.")
        st.error("Arquivo de dados otimizado (GeoParquet) não encontrado. Execute o script `preprocess_data.py` primeiro.")
        return gpd.GeoDataFrame()
    except Exception as e:
        logger.error(f"❌ Error loading GeoParquet: {e}")
        return gpd.GeoDataFrame()

# --- 2. MAP CREATION (OPTIMIZED) ---
def create_optimized_interactive_map(gdf_properties: gpd.GeoDataFrame, max_properties: int = 8000) -> folium.Map:
    """Creates a visible map using a single, efficient GeoJson layer."""
    m = folium.Map(location=MAP_CONFIG['center_rmc'], zoom_start=MAP_CONFIG['default_zoom'], tiles='OpenStreetMap')

    if gdf_properties.empty:
        return m

    df_display = gdf_properties.sort_values('mcda_score', ascending=False).head(max_properties)
    logger.info(f"🗺️ Displaying {len(df_display)} top properties on the map.")

    geojson_data = df_display.to_json()

    style_function = lambda x: {
        'fillColor': get_score_color(x['properties']['mcda_score']),
        'color': '#000000',
        'weight': MAP_CONFIG['polygon_weight'],
        'fillOpacity': MAP_CONFIG['polygon_fill_opacity'],
    }

    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['municipio', 'mcda_score', 'ranking'],
            aliases=['Município:', 'Score MCDA:', 'Ranking:'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
        )
    ).add_to(m)

    add_legend_to_map(m)
    folium.LayerControl().add_to(m)
    logger.info("✅ Optimized visible map created successfully.")
    return m

# --- 3. CLICK DETECTION (OPTIMIZED) ---
def detect_clicked_property_optimized(click_lat: float, click_lon: float, gdf_properties: gpd.GeoDataFrame) -> Optional[str]:
    """Detects clicked property using a fast spatial index."""
    if gdf_properties.empty or not hasattr(gdf_properties, 'sindex'):
        return None
        
    click_point = Point(click_lon, click_lat)
    
    possible_matches_index = list(gdf_properties.sindex.intersection(click_point.bounds))
    if not possible_matches_index:
        return None

    possible_matches = gdf_properties.iloc[possible_matches_index]
    precise_matches = possible_matches[possible_matches.contains(click_point)]
    
    if not precise_matches.empty:
        cod_imovel = precise_matches.iloc[0]['cod_imovel']
        logger.info(f"✅ Click detected on property: {cod_imovel}")
        return cod_imovel
        
    return None

# --- 4. MAIN RENDERING FUNCTION (CALLED BY APP.PY) ---
def render_interactive_mcda_map(df_properties: gpd.GeoDataFrame, filters: Dict[str, Any] = None) -> Optional[str]:
    """Renders the fully optimized map and handles all interactions."""
    try:
        if df_properties.empty:
            st.warning("⚠️ Nenhuma propriedade encontrada para exibir no mapa.")
            return None

        max_props = filters.get('max_properties', 8000) if filters else 8000
        m = create_optimized_interactive_map(df_properties, max_properties=max_props)

        map_data = st_folium(
            m,
            width=None,
            height=650,
            returned_objects=["last_clicked"],
            key="final_optimized_map"
        )

        clicked_property = None
        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            
            with st.spinner("🔍 Identificando propriedade..."):
                clicked_property = detect_clicked_property_optimized(lat, lon, df_properties)
                
            if clicked_property:
                prop_info = df_properties[df_properties['cod_imovel'] == clicked_property].iloc[0]
                st.success(f"✅ Propriedade selecionada: {prop_info.get('municipio', 'N/A')} (Score: {prop_info.get('mcda_score', 0):.1f})")
                st.balloons()
            else:
                st.info("ℹ️ Clique diretamente sobre um polígono colorido para selecionar.")

        return clicked_property

    except Exception as e:
        logger.error(f"❌ Erro ao renderizar mapa interativo: {str(e)}")
        st.error(f"Ocorreu um erro ao carregar o mapa: {str(e)}")
        return None

# --- 5. HELPER UTILITIES ---
def get_score_color(score: float) -> str:
    """Returns color based on MCDA score."""
    if score >= 80: return '#00AA00'
    elif score >= 65: return '#66BB00'
    elif score >= 50: return '#BBBB00'
    elif score >= 35: return '#FF8800'
    else: return '#FF4444'

def add_legend_to_map(m: folium.Map):
    """Adds a color legend to the map."""
    legend_html = """
     <div style="position: fixed; 
     bottom: 50px; right: 50px; width: 180px; 
     background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
     padding: 10px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.2);">
     <h4 style='margin-top:0; color: #2c5530;'>Score MCDA</h4>
     <p style="margin:2px;"><i class="fa fa-square" style="color:#00AA00"></i> 80-100: Excelente</p>
     <p style="margin:2px;"><i class="fa fa-square" style="color:#66BB00"></i> 65-79: Muito Bom</p>
     <p style="margin:2px;"><i class="fa fa-square" style="color:#BBBB00"></i> 50-64: Bom</p>
     <p style="margin:2px;"><i class="fa fa-square" style="color:#FF8800"></i> 35-49: Regular</p>
     <p style="margin:2px;"><i class="fa fa-square" style="color:#FF4444"></i> 0-34: Baixo</p>
     </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))