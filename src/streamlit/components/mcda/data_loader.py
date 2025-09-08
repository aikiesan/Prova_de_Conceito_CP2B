# CP2B MCDA Data Loader
# Carrega e processa dados do projeto CP2B para integração com dashboard

import pandas as pd
import geopandas as gpd
import streamlit as st
import json
from typing import Dict, Any, Optional
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


@st.cache_data
def load_cp2b_geoparquet() -> gpd.GeoDataFrame:
    """
    Carrega dados CP2B do arquivo GeoParquet otimizado
    
    Returns:
        gpd.GeoDataFrame: Dados com geometrias processadas
    """
    try:
        geoparquet_path = f"{CP2B_DATA_PATH}/CP2B_Processed_Geometries.geoparquet"
        
        if not os.path.exists(geoparquet_path):
            logger.warning(f"⚠️ GeoParquet não encontrado em {geoparquet_path}")
            logger.info("🔄 Tentando carregar dados do CSV como fallback...")
            return load_cp2b_complete_database()
        
        logger.info(f"🔄 Carregando GeoParquet otimizado: {geoparquet_path}")
        gdf = gpd.read_parquet(geoparquet_path)
        
        logger.info(f"✅ GeoParquet carregado: {len(gdf)} propriedades com geometrias")
        return gdf
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar GeoParquet: {str(e)}")
        logger.info("🔄 Tentando carregar dados do CSV como fallback...")
        return load_cp2b_complete_database()

@st.cache_data
def load_cp2b_complete_database() -> pd.DataFrame:
    """
    Carrega o banco de dados completo CP2B com cache otimizado
    
    Returns:
        pd.DataFrame: Dados completos das propriedades SICAR com scores MCDA
    """
    try:
        logger.info("Carregando banco de dados CP2B completo...")
        
        # Carrega arquivo principal consolidado
        df = pd.read_csv(f"{CP2B_DATA_PATH}/CP2B_Complete_Database.csv")
        
        logger.info(f"✅ CP2B: {len(df)} propriedades carregadas com sucesso")
        return df
        
    except FileNotFoundError:
        logger.error("❌ Arquivo CP2B_Complete_Database.csv não encontrado")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dados CP2B: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_cp2b_spatial_data() -> pd.DataFrame:
    """
    Carrega dados espaciais simplificados para detecção de clique
    
    Returns:
        pd.DataFrame: Geometrias simplificadas das propriedades
    """
    try:
        logger.info("Carregando dados espaciais CP2B...")
        
        # Para MVP, vamos carregar dados básicos de localização
        # Futuramente podemos otimizar com geometrias simplificadas
        df = pd.read_csv(f"{CP2B_DATA_PATH}/CP2B_Complete_Database.csv")
        
        # Selecionar apenas colunas essenciais para performance
        spatial_cols = [
            'cod_imovel', 'municipio', 'mcda_score', 'ranking',
            'biomass_score', 'infra_score', 'restriction_score'
        ]
        
        # Filtrar colunas existentes
        available_cols = [col for col in spatial_cols if col in df.columns]
        df_spatial = df[available_cols].copy()
        
        logger.info(f"✅ Dados espaciais CP2B: {len(df_spatial)} propriedades preparadas")
        return df_spatial
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar dados espaciais CP2B: {str(e)}")
        return pd.DataFrame()

def get_property_details(cod_imovel: str) -> Optional[Dict[str, Any]]:
    """
    Busca detalhes completos de uma propriedade usando um caminho absoluto e inquebrável.
    """
    try:
        # --- THIS IS THE UNBREAKABLE PATH LOGIC ---
        current_file_path = Path(__file__)
        streamlit_root = current_file_path.parent.parent.parent
        csv_path = streamlit_root / "CP2B_Resultados_Finais.csv"

        df = pd.read_csv(csv_path, low_memory=False)
        
        if df.empty:
            return None

        search_code = str(cod_imovel).strip()
        df['cod_imovel'] = df['cod_imovel'].astype(str).str.strip()
        
        property_data = df[df['cod_imovel'] == search_code]
        
        if property_data.empty:
            logger.warning(f"Propriedade {search_code} não encontrada em {csv_path}.")
            return None
            
        property_dict = property_data.iloc[0].to_dict()
        
        # Adiciona dados processados para relatório
        property_dict.update({
            'formatted_score': f"{property_dict.get('mcda_score', 0):.1f}",
            'rank_position': f"#{int(property_dict.get('ranking', 0))}º lugar" if pd.notna(property_dict.get('ranking')) else 'N/A',
            'formatted_biomass': f"{property_dict.get('biomass_score', 0):,.0f} ha",
        })
        
        logger.info(f"✅ Detalhes da propriedade {search_code} carregados com sucesso.")
        return property_dict
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar propriedade {cod_imovel}: {str(e)}")
        return None

def get_cp2b_summary_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas resumo dos dados CP2B
    
    Returns:
        Dict com estatísticas do projeto CP2B
    """
    try:
        df = load_cp2b_complete_database()
        
        if df.empty:
            return {
                'total_properties': 0,
                'municipalities': 0,
                'avg_score': 0,
                'max_score': 0,
                'status': 'error'
            }
        
        stats = {
            'total_properties': len(df),
            'municipalities': df['municipio'].nunique() if 'municipio' in df.columns else 0,
            'avg_score': df['mcda_score'].mean() if 'mcda_score' in df.columns else 0,
            'max_score': df['mcda_score'].max() if 'mcda_score' in df.columns else 0,
            'min_score': df['mcda_score'].min() if 'mcda_score' in df.columns else 0,
            'top_municipalities': df['municipio'].value_counts().head(5).to_dict() if 'municipio' in df.columns else {},
            'status': 'success'
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro ao calcular estatísticas CP2B: {str(e)}")
        return {'status': 'error', 'error': str(e)}

def search_properties(search_term: str, limit: int = 10) -> pd.DataFrame:
    """
    Busca propriedades por termo de pesquisa
    
    Args:
        search_term: Termo para busca (código, município, etc.)
        limit: Número máximo de resultados
        
    Returns:
        DataFrame com propriedades encontradas
    """
    try:
        df = load_cp2b_complete_database()
        
        if df.empty or not search_term.strip():
            return pd.DataFrame()
            
        search_lower = search_term.lower().strip()
        
        # Busca em múltiplas colunas
        conditions = []
        
        if 'cod_imovel' in df.columns:
            conditions.append(df['cod_imovel'].str.lower().str.contains(search_lower, na=False))
            
        if 'municipio' in df.columns:
            conditions.append(df['municipio'].str.lower().str.contains(search_lower, na=False))
        
        if not conditions:
            return pd.DataFrame()
            
        # Combina condições com OR
        combined_condition = conditions[0]
        for condition in conditions[1:]:
            combined_condition |= condition
            
        results = df[combined_condition].head(limit)
        
        logger.info(f"✅ Busca '{search_term}': {len(results)} propriedades encontradas")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro na busca por '{search_term}': {str(e)}")
        return pd.DataFrame()

# Função para inicializar dados CP2B no session_state
def initialize_cp2b_session_state():
    """Inicializa variáveis do CP2B no session state"""
    
    if 'cp2b_data_loaded' not in st.session_state:
        st.session_state.cp2b_data_loaded = False
        
    if 'cp2b_selected_property' not in st.session_state:
        st.session_state.cp2b_selected_property = None
        
    if 'cp2b_search_query' not in st.session_state:
        st.session_state.cp2b_search_query = ''
        
    if 'cp2b_filter_score_min' not in st.session_state:
        st.session_state.cp2b_filter_score_min = 0
        
    if 'cp2b_filter_municipality' not in st.session_state:
        st.session_state.cp2b_filter_municipality = 'Todos'