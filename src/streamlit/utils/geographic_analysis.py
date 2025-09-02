"""
Geographic Analysis Utilities for CP2B Dashboard
Real coordinate-based distance calculations and hotspot detection
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import streamlit as st

try:
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False


class GeographicAnalyzer:
    """Geographic analysis utilities for municipality data"""
    
    def __init__(self):
        self.coordinates_cache = None
        self.shapefile_path = Path("shapefile/Municipios_SP_shapefile.shp")
    
    @st.cache_data
    def load_municipality_coordinates(_self) -> pd.DataFrame:
        """Load municipality coordinates from shapefile"""
        
        try:
            if not _self.shapefile_path.exists():
                st.error(f"❌ Shapefile not found at: {_self.shapefile_path}")
                return pd.DataFrame()
            
            # Load shapefile
            gdf = gpd.read_file(_self.shapefile_path)
            
            # Convert to projected CRS for accurate centroids, then back to lat/lng
            gdf_proj = gdf.to_crs('EPSG:3857')  # Web Mercator
            centroids = gdf_proj.geometry.centroid.to_crs('EPSG:4326')  # Back to WGS84
            
            # Extract coordinates
            coords_df = pd.DataFrame({
                'nm_mun': gdf['NM_MUN'].str.upper().str.strip(),  # Normalize names
                'lat': centroids.y,
                'lng': centroids.x,
                'area_km2': gdf.get('AREA_KM2', 0)
            })
            
            return coords_df
            
        except Exception as e:
            st.error(f"❌ Error loading coordinates: {e}")
            return pd.DataFrame()
    
    def get_municipality_coordinates(self, municipality_name: str) -> Optional[Tuple[float, float]]:
        """Get lat/lng coordinates for a specific municipality"""
        
        if self.coordinates_cache is None:
            self.coordinates_cache = self.load_municipality_coordinates()
        
        if self.coordinates_cache.empty:
            return None
        
        # Normalize municipality name for matching
        norm_name = municipality_name.upper().strip()
        
        match = self.coordinates_cache[self.coordinates_cache['nm_mun'] == norm_name]
        
        if not match.empty:
            row = match.iloc[0]
            return (float(row['lat']), float(row['lng']))
        
        return None
    
    def calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates in kilometers"""
        
        if GEOPY_AVAILABLE:
            return geodesic(coord1, coord2).kilometers
        else:
            # Fallback: Haversine formula approximation
            return self._haversine_distance(coord1, coord2)
    
    def _haversine_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Haversine formula for distance calculation (fallback)"""
        
        lat1, lng1 = np.radians(coord1)
        lat2, lng2 = np.radians(coord2)
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlng/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371.0
        
        return c * r
    
    def find_nearby_municipalities(self, 
                                   center_municipality: str, 
                                   radius_km: float, 
                                   df: pd.DataFrame) -> List[Dict]:
        """Find municipalities within radius of center municipality"""
        
        center_coords = self.get_municipality_coordinates(center_municipality)
        if not center_coords:
            return []
        
        nearby = []
        
        for _, row in df.iterrows():
            mun_name = row['nm_mun']
            if mun_name == center_municipality:
                continue
                
            mun_coords = self.get_municipality_coordinates(mun_name)
            if not mun_coords:
                continue
            
            distance = self.calculate_distance(center_coords, mun_coords)
            
            if distance <= radius_km:
                nearby.append({
                    'municipality': mun_name,
                    'distance_km': distance,
                    'coordinates': mun_coords,
                    'biogas_potential': row.get('total_final_nm_ano', 0),
                    'data': row.to_dict()
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance_km'])
        
        return nearby
    
    def detect_geographic_hotspots(self, 
                                   df: pd.DataFrame, 
                                   radius_km: float = 50, 
                                   min_cluster_size: int = 3,
                                   min_potential: float = 1_000_000) -> List[Dict]:
        """Detect geographic hotspots using real distance calculations"""
        
        if not GEOPY_AVAILABLE:
            st.warning("⚠️ Using simplified geographic analysis. Install geopy for precise results.")
        
        # Filter municipalities with sufficient potential
        potential_df = df[df['total_final_nm_ano'] >= min_potential].copy()
        
        if len(potential_df) < min_cluster_size:
            return []
        
        hotspots = []
        processed_municipalities = set()
        
        # Load coordinates
        if self.coordinates_cache is None:
            self.coordinates_cache = self.load_municipality_coordinates()
        
        if self.coordinates_cache.empty:
            return []
        
        for _, center_row in potential_df.iterrows():
            center_name = center_row['nm_mun']
            
            if center_name in processed_municipalities:
                continue
            
            # Find nearby municipalities
            nearby = self.find_nearby_municipalities(center_name, radius_km, potential_df)
            
            # Include center municipality
            center_coords = self.get_municipality_coordinates(center_name)
            if center_coords:
                nearby.insert(0, {
                    'municipality': center_name,
                    'distance_km': 0.0,
                    'coordinates': center_coords,
                    'biogas_potential': center_row['total_final_nm_ano'],
                    'data': center_row.to_dict()
                })
            
            # Check if we have enough municipalities for a cluster
            if len(nearby) >= min_cluster_size:
                
                # Calculate cluster metrics
                total_potential = sum(m['biogas_potential'] for m in nearby)
                municipalities = [m['municipality'] for m in nearby]
                
                # Analyze dominant residues
                dominant_residues = self._analyze_dominant_residues(nearby)
                
                # Calculate synergy score based on residue diversity and proximity
                synergy_score = self._calculate_synergy_score(nearby, radius_km)
                
                hotspot = {
                    'id': len(hotspots) + 1,
                    'center': center_name,
                    'center_coordinates': center_coords,
                    'municipalities': municipalities,
                    'municipality_count': len(municipalities),
                    'total_potential': total_potential,
                    'avg_potential': total_potential / len(municipalities),
                    'dominant_residues': dominant_residues,
                    'synergy_score': synergy_score,
                    'cluster_radius': max(m['distance_km'] for m in nearby),
                    'municipality_data': nearby
                }
                
                hotspots.append(hotspot)
                
                # Mark all municipalities in this cluster as processed
                processed_municipalities.update(municipalities)
        
        # Sort hotspots by total potential
        hotspots.sort(key=lambda x: x['total_potential'], reverse=True)
        
        return hotspots
    
    def _analyze_dominant_residues(self, municipalities: List[Dict]) -> List[str]:
        """Analyze which residue types are dominant in the cluster"""
        
        residue_columns = [
            'biogas_cana_nm_ano', 'biogas_soja_nm_ano', 'biogas_milho_nm_ano',
            'biogas_bovinos_nm_ano', 'biogas_suino_nm_ano', 'biogas_aves_nm_ano',
            'biogas_cafe_nm_ano', 'biogas_citros_nm_ano', 'biogas_piscicultura_nm_ano'
        ]
        
        residue_labels = {
            'biogas_cana_nm_ano': 'Cana',
            'biogas_soja_nm_ano': 'Soja', 
            'biogas_milho_nm_ano': 'Milho',
            'biogas_bovinos_nm_ano': 'Bovino',
            'biogas_suino_nm_ano': 'Suíno',
            'biogas_aves_nm_ano': 'Aves',
            'biogas_cafe_nm_ano': 'Café',
            'biogas_citros_nm_ano': 'Citros',
            'biogas_piscicultura_nm_ano': 'Peixes'
        }
        
        residue_totals = {}
        
        for municipality in municipalities:
            data = municipality['data']
            for col in residue_columns:
                if col in data and data[col] and data[col] > 0:
                    residue_totals[col] = residue_totals.get(col, 0) + data[col]
        
        # Find top 3 residues
        sorted_residues = sorted(residue_totals.items(), key=lambda x: x[1], reverse=True)
        
        dominant = []
        for col, total in sorted_residues[:3]:
            if total > 0:
                dominant.append(residue_labels.get(col, col))
        
        return dominant
    
    def _calculate_synergy_score(self, municipalities: List[Dict], max_radius: float) -> float:
        """Calculate synergy score for a cluster"""
        
        if len(municipalities) < 2:
            return 0.0
        
        # Base score from cluster size (normalized)
        size_score = min(len(municipalities) / 10.0, 1.0)
        
        # Compactness score (inverse of average distance)
        avg_distance = np.mean([m['distance_km'] for m in municipalities[1:]])  # Skip center (distance=0)
        compactness_score = max(0, (max_radius - avg_distance) / max_radius)
        
        # Diversity score (number of different residue types)
        residue_columns = [
            'biogas_cana_nm_ano', 'biogas_soja_nm_ano', 'biogas_milho_nm_ano',
            'biogas_bovinos_nm_ano', 'biogas_suino_nm_ano', 'biogas_aves_nm_ano',
            'biogas_cafe_nm_ano', 'biogas_citros_nm_ano', 'biogas_piscicultura_nm_ano'
        ]
        
        residue_presence = set()
        for municipality in municipalities:
            data = municipality['data']
            for col in residue_columns:
                if col in data and data[col] and data[col] > 0:
                    residue_presence.add(col)
        
        diversity_score = len(residue_presence) / len(residue_columns)
        
        # Potential score (normalized by maximum possible in region)
        total_potential = sum(m['biogas_potential'] for m in municipalities)
        potential_score = min(total_potential / 10_000_000, 1.0)  # Normalize to 10M as max
        
        # Combined score
        synergy_score = (
            0.25 * size_score +
            0.25 * compactness_score +
            0.25 * diversity_score +
            0.25 * potential_score
        )
        
        return synergy_score
    
    def get_cluster_map_data(self, hotspot: Dict) -> pd.DataFrame:
        """Prepare data for mapping a specific hotspot cluster"""
        
        municipalities = hotspot['municipality_data']
        
        map_data = []
        for mun in municipalities:
            coords = mun['coordinates']
            map_data.append({
                'municipality': mun['municipality'],
                'lat': coords[0],
                'lng': coords[1],
                'distance_km': mun['distance_km'],
                'biogas_potential': mun['biogas_potential'],
                'size': min(mun['biogas_potential'] / 1_000_000 * 10, 50)  # Scale for visualization
            })
        
        return pd.DataFrame(map_data)


def create_geographic_analyzer() -> GeographicAnalyzer:
    """Factory function to create GeographicAnalyzer instance"""
    return GeographicAnalyzer()