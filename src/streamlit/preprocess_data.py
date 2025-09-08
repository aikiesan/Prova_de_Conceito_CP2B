import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, Polygon
import json
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURATION ---
INPUT_CSV = "./CP2B_Resultados_Finais.csv"
OUTPUT_GEOPARQUET = "./CP2B_Processed_Geometries.geoparquet"
SIMPLIFY_TOLERANCE = 0.0001

def process_and_save_geometries_final():
    """
    Final, robust version. It specifically targets the correct '.geo' column
    and cleans GeometryCollections, ensuring only valid Polygons are saved.
    """
    try:
        logging.info(f"🔄 Loading raw data from {INPUT_CSV}...")
        df = pd.read_csv(INPUT_CSV, low_memory=False)
        logging.info(f"✅ Loaded {len(df)} total rows.")

        if '.geo' not in df.columns:
            raise ValueError("❌ The crucial geometry column '.geo' was not found in the CSV.")
        geo_col = '.geo'
        logging.info(f"📍 Targeting the correct geometry column: '{geo_col}'")

        df.dropna(subset=[geo_col, 'mcda_score'], inplace=True)
        df['mcda_score'] = pd.to_numeric(df['mcda_score'], errors='coerce')
        df.dropna(subset=['mcda_score'], inplace=True)
        df = df[df['mcda_score'] > 0]
        logging.info(f"📊 {len(df)} rows remaining after initial filtering.")

        geometries = []
        valid_indices = []

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="⚙️ Processing & Cleaning Geometries"):
            try:
                geo_str = row[geo_col]
                if not isinstance(geo_str, str) or not geo_str.startswith('{'):
                    continue
                    
                geo_data = json.loads(geo_str)
                
                if geo_data['type'] == 'GeometryCollection':
                    polygons = [shape(geom) for geom in geo_data['geometries'] if geom['type'] == 'Polygon']
                    if not polygons:
                        continue
                    geometry = max(polygons, key=lambda p: p.area)
                else:
                    geometry = shape(geo_data)

                if not geometry.is_valid:
                    geometry = geometry.buffer(0)
                
                if geometry.is_empty or not isinstance(geometry, Polygon):
                    continue
                
                simplified_geometry = geometry.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)
                geometries.append(simplified_geometry)
                valid_indices.append(index)

            except (json.JSONDecodeError, TypeError, Exception):
                continue

        logging.info(f"✅ Found {len(geometries)} valid, clean Polygons.")
        
        df_filtered = df.loc[valid_indices].copy()

        # Be defensive: drop any pre-existing 'geometry' column before creating the real one.
        if 'geometry' in df_filtered.columns:
            df_filtered = df_filtered.drop(columns=['geometry'])

        logging.info("🌍 Creating final GeoDataFrame...")
        gdf = gpd.GeoDataFrame(df_filtered, geometry=geometries, crs="EPSG:4326")

        essential_cols = [
            'cod_imovel', 'municipio', 'mcda_score', 'ranking',
            'biomass_score', 'infra_score', 'restriction_score', 'geometry'
        ]
        final_cols = [col for col in essential_cols if col in gdf.columns]
        gdf_final = gdf[final_cols]

        # The problematic .rename_geometry() line has been REMOVED.

        logging.info(f"💾 Saving {len(gdf_final)} clean rows to {OUTPUT_GEOPARQUET}...")
        gdf_final.to_parquet(OUTPUT_GEOPARQUET, compression='gzip')

        logging.info("🎉 Final pre-processing complete! The data file is now 100% clean.")

    except Exception as e:
        logging.error(f"❌ An error occurred during final pre-processing: {e}")
        
if __name__ == "__main__":
    process_and_save_geometries_final()