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

# Configuração de cenários MCDA
MCDA_SCENARIOS = {
    '10km': 'CP2B_MCDA_10km.geoparquet',
    '30km': 'CP2B_MCDA_30km.geoparquet', 
    '50km': 'CP2B_MCDA_50km.geoparquet'
}

# Configuração do caminho dos dados
CP2B_DATA_PATH = Path(__file__).parent.parent  # Vai para o diretório streamlit (onde estão os arquivos)


@st.cache_data
def load_mcda_geoparquet_by_radius(radius: str = '30km') -> gpd.GeoDataFrame:
    """
    Carrega dados MCDA do arquivo GeoParquet específico do raio
    
    Args:
        radius: Raio de análise ('10km', '30km', ou '50km')
    
    Returns:
        gpd.GeoDataFrame: Dados com geometrias e scores MCDA processados
    """
    try:
        if radius not in MCDA_SCENARIOS:
            logger.warning(f"⚠️ Raio '{radius}' inválido. Usando '30km' como padrão.")
            radius = '30km'
            
        geoparquet_filename = MCDA_SCENARIOS[radius]
        
        # Tenta encontrar o arquivo em múltiplos locais possíveis
        search_paths = [
            Path(__file__).parent.parent / geoparquet_filename,  # streamlit directory (correct path)
            Path.cwd() / "src" / "streamlit" / geoparquet_filename,  # From project root
            Path.cwd() / geoparquet_filename,  # Current working directory
            CP2B_DATA_PATH / geoparquet_filename,  # Data path fallback
        ]
        
        geoparquet_path = None
        for path in search_paths:
            if path.exists():
                geoparquet_path = path
                logger.info(f"✅ Arquivo MCDA encontrado em: {path}")
                break
        
        if geoparquet_path is None:
            logger.warning(f"⚠️ Arquivo {geoparquet_filename} não encontrado em nenhum dos caminhos:")
            for path in search_paths:
                logger.warning(f"   - {path}")
            logger.info("🔄 Tentando carregar dados antigos como fallback...")
            return load_cp2b_geoparquet_fallback()
        
        logger.info(f"🔄 Carregando GeoParquet MCDA {radius}: {geoparquet_path}")
        gdf = gpd.read_parquet(str(geoparquet_path))
        
        # Validação dos dados carregados
        if gdf.empty:
            logger.warning(f"⚠️ Arquivo {geoparquet_filename} está vazio")
            return load_cp2b_geoparquet_fallback()
            
        # Verificar e ajustar colunas de município
        if 'municipio' not in gdf.columns:
            if 'municipio_x' in gdf.columns:
                gdf['municipio'] = gdf['municipio_x']
                logger.info(f"✅ Coluna 'municipio' criada a partir de 'municipio_x'")
            elif 'municipio_y' in gdf.columns:
                gdf['municipio'] = gdf['municipio_y']
                logger.info(f"✅ Coluna 'municipio' criada a partir de 'municipio_y'")
            else:
                logger.warning(f"⚠️ Nenhuma coluna de município encontrada no arquivo {geoparquet_filename}")
                
        # Verificar se as colunas essenciais existem
        required_cols = ['cod_imovel', 'geometry']
        missing_cols = [col for col in required_cols if col not in gdf.columns]
        if missing_cols:
            logger.warning(f"⚠️ Colunas essenciais faltando no arquivo {geoparquet_filename}: {missing_cols}")
            
        logger.info(f"✅ GeoParquet MCDA {radius} carregado: {len(gdf)} propriedades")
        logger.info(f"📊 Colunas disponíveis: {list(gdf.columns)}")
        
        return gdf
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar GeoParquet MCDA {radius}: {str(e)}")
        logger.info("🔄 Tentando carregar dados antigos como fallback...")
        return load_cp2b_geoparquet_fallback()

@st.cache_data
def load_cp2b_geoparquet_fallback() -> gpd.GeoDataFrame:
    """
    Função de fallback para carregar dados antigos se os novos não estiverem disponíveis
    
    Returns:
        gpd.GeoDataFrame: Dados com geometrias processadas (versão antiga)
    """
    try:
        # Tenta carregar o arquivo antigo
        current_path = Path.cwd()
        old_geoparquet_path = current_path / "CP2B_Processed_Geometries.geoparquet"
        
        if old_geoparquet_path.exists():
            logger.info(f"🔄 Carregando GeoParquet antigo como fallback: {old_geoparquet_path}")
            gdf = gpd.read_parquet(str(old_geoparquet_path))
            logger.info(f"✅ GeoParquet antigo carregado: {len(gdf)} propriedades")
            return gdf
        else:
            logger.error("❌ Nenhum arquivo GeoParquet encontrado")
            return gpd.GeoDataFrame()
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar fallback: {str(e)}")
        return gpd.GeoDataFrame()

@st.cache_data  
def load_cp2b_geoparquet() -> gpd.GeoDataFrame:
    """
    Função mantida para compatibilidade - agora chama a nova função
    
    Returns:
        gpd.GeoDataFrame: Dados com geometrias processadas
    """
    return load_mcda_geoparquet_by_radius('30km')

@st.cache_data
def load_cp2b_complete_database() -> pd.DataFrame:
    """
    Carrega o banco de dados completo CP2B com cache otimizado
    
    Returns:
        pd.DataFrame: Dados completos das propriedades SICAR com scores MCDA
    """
    try:
        logger.info("Carregando banco de dados CP2B completo...")
        
        # Try to load from available parquet files first (more efficient and smaller)
        parquet_files = [
            "CP2B_Biomass_Potential_CORRECTED.parquet",
            "CP2B_Biomass_Potential_Analysis.parquet"
        ]
        
        for parquet_file in parquet_files:
            parquet_path = CP2B_DATA_PATH / parquet_file
            if parquet_path.exists():
                logger.info(f"Loading complete database from {parquet_file}")
                df = pd.read_parquet(parquet_path)
                logger.info(f"✅ CP2B: {len(df)} propriedades carregadas com sucesso (parquet)")
                return df
        
        # Fallback to CSV files
        csv_files = [
            "CP2B_Complete_Database.csv",
            "CP2B_Resultados_Finais.csv"
        ]
        
        for csv_file in csv_files:
            csv_path = CP2B_DATA_PATH / csv_file
            if csv_path.exists():
                logger.info(f"Loading complete database from {csv_file} (fallback)")
                df = pd.read_csv(csv_path)
                logger.info(f"✅ CP2B: {len(df)} propriedades carregadas com sucesso (csv)")
                return df
        
        logger.error("❌ Nenhum arquivo de dados CP2B encontrado")
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
        
        # Use the complete database function which has graceful fallback
        df = load_cp2b_complete_database()
        
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

def get_property_details(cod_imovel: str, radius: str = '30km') -> Optional[Dict[str, Any]]:
    """
    Busca detalhes completos de uma propriedade usando dados disponíveis com fallback gracioso.
    """
    try:
        # --- LOAD FROM MCDA GEOPARQUET FILES (CONTAINS SCORES) ---
        current_file_path = Path(__file__)
        streamlit_root = current_file_path.parent.parent.parent  # Go up from components/mcda/ to streamlit/
        
        logger.info(f"🔍 Looking for property {cod_imovel} with radius {radius}")
        logger.info(f"📁 Streamlit root path: {streamlit_root}")
        
        # First try to load from the specific radius MCDA file
        primary_mcda_file = f"CP2B_MCDA_{radius}.geoparquet"
        fallback_mcda_files = [
            "CP2B_MCDA_30km.geoparquet",  # Default fallback
            "CP2B_MCDA_10km.geoparquet",
            "CP2B_MCDA_50km.geoparquet"
        ]
        
        # Remove the primary file from fallbacks to avoid duplicates
        mcda_files = [primary_mcda_file] + [f for f in fallback_mcda_files if f != primary_mcda_file]
        
        df = None
        for mcda_file in mcda_files:
            mcda_path = streamlit_root / mcda_file
            logger.info(f"🔍 Checking path: {mcda_path}")
            if mcda_path.exists():
                logger.info(f"✅ Loading property details from {mcda_file}")
                gdf = gpd.read_parquet(mcda_path)
                # Convert to regular DataFrame for consistency, keeping all columns except geometry
                df = pd.DataFrame(gdf.drop(columns=['geometry']) if 'geometry' in gdf.columns else gdf)
                
                # Fix municipio column - MCDA files have municipio_x and municipio_y
                if 'municipio' not in df.columns:
                    if 'municipio_x' in df.columns:
                        df['municipio'] = df['municipio_x']
                        logger.info("✅ Using municipio_x as municipio column")
                    elif 'municipio_y' in df.columns:
                        df['municipio'] = df['municipio_y']
                        logger.info("✅ Using municipio_y as municipio column")
                        
                break
        
        # Fallback to parquet files if MCDA files not available
        if df is None:
            parquet_files = [
                "CP2B_Biomass_Potential_CORRECTED.parquet",
                "CP2B_Biomass_Potential_Analysis.parquet"
            ]
            
            for parquet_file in parquet_files:
                parquet_path = streamlit_root / parquet_file
                if parquet_path.exists():
                    logger.info(f"Loading property details from {parquet_file} (fallback - no MCDA scores)")
                    df = pd.read_parquet(parquet_path)
                    break
        
        # Final fallback to CSV
        if df is None:
            csv_path = streamlit_root / "CP2B_Resultados_Finais.csv"
            if csv_path.exists():
                logger.info("Loading property details from CSV (final fallback)")
                df = pd.read_csv(csv_path, low_memory=False)
            else:
                logger.warning(f"❌ No data files found for property details in {streamlit_root}")
                logger.warning(f"📁 Tried MCDA files: {mcda_files}")
                return None
        
        if df.empty:
            return None

        search_code = str(cod_imovel).strip()
        df['cod_imovel'] = df['cod_imovel'].astype(str).str.strip()
        
        # Debug logging
        logger.info(f"🔍 Searching for property: {search_code}")
        logger.info(f"📊 Total properties in dataset: {len(df)}")
        
        property_data = df[df['cod_imovel'] == search_code]
        
        if property_data.empty:
            logger.warning(f"❌ Propriedade {search_code} não encontrada.")
            logger.info(f"📝 Sample cod_imovel values: {df['cod_imovel'].head(5).tolist()}")
            # Check for similar codes
            similar = df[df['cod_imovel'].str.contains(search_code[:15], na=False, regex=False)]['cod_imovel'].head(3).tolist()
            if similar:
                logger.info(f"🔍 Similar codes found: {similar}")
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

def get_mcda_summary_stats_by_radius(radius: str = '30km') -> Dict[str, Any]:
    """
    Retorna estatísticas resumo dos dados MCDA por raio com critérios técnico-econômicos realistas
    
    Args:
        radius: Raio de análise ('10km', '30km', ou '50km')
    
    Returns:
        Dict com estatísticas do cenário MCDA específico baseado em critérios realistas
    """
    try:
        gdf = load_mcda_geoparquet_by_radius(radius)
        
        if gdf.empty:
            return {
                'radius': radius,
                'total_properties': 0,
                'municipalities': 0,
                'avg_score': 0,
                'max_score': 0,
                'viable_properties': 0,
                'excellent_properties': 0,
                'very_good_properties': 0,
                'status': 'error'
            }
        
        # CRITÉRIOS TÉCNICO-ECONÔMICOS REALISTAS baseados em análise estatística
        # e literatura científica sobre plantas de biogás
        REALISTIC_THRESHOLDS = {
            '10km': {
                'excellent': 61.3,  # P95 - Top 5% apenas
                'very_good': 57.1,  # P90 - Top 10%
                'viable': 50.9,     # P75 - Top 25%
                'justification': 'Raio ótimo - logística eficiente, menor custo transporte'
            },
            '30km': {
                'excellent': 65.5,  # P95 - Critério mais rigoroso para raio médio
                'very_good': 62.9,  # P90
                'viable': 58.6,     # P75 - Mais exigente que 10km
                'justification': 'Raio médio - balance entre potencial e logística'
            },
            '50km': {
                'excellent': 75.8,  # P95 - Muito rigoroso para raio alto
                'very_good': 72.8,  # P90
                'viable': 69.5,     # P75 - Altamente seletivo
                'justification': 'Raio alto - apenas locais excepcionais justificam logística'
            }
        }
        
        # Usar thresholds realistas baseados na análise
        thresholds = REALISTIC_THRESHOLDS.get(radius, REALISTIC_THRESHOLDS['30km'])
        
        # Calcular scores se existirem
        avg_score = 0
        max_score = 0
        min_score = 0
        viable_count = 0
        very_good_count = 0
        excellent_count = 0
        
        if 'mcda_score' in gdf.columns:
            scores = gdf['mcda_score']
            avg_score = scores.mean()
            max_score = scores.max()
            min_score = scores.min()
            
            # Aplicar critérios técnico-econômicos REALISTAS
            excellent_count = len(gdf[scores > thresholds['excellent']])
            very_good_count = len(gdf[scores > thresholds['very_good']]) 
            viable_count = len(gdf[scores > thresholds['viable']])
        
        # Critério adicional: Potencial mínimo de biogás para viabilidade técnica
        biogas_col = f'total_biogas_nm3_year_{radius}'
        biogas_viable_count = 0
        if biogas_col in gdf.columns:
            # Critério técnico: Planta mínima de 250kW = 219,000 Nm3/ano
            min_viable_biogas = 219000
            biogas_viable_count = len(gdf[gdf[biogas_col] > min_viable_biogas])
        
        stats = {
            'radius': radius,
            'total_properties': len(gdf),
            'municipalities': gdf['municipio'].nunique() if 'municipio' in gdf.columns else 0,
            'avg_score': round(avg_score, 1),
            'max_score': round(max_score, 1),
            'min_score': round(min_score, 1),
            
            # Classificação técnico-econômica REALISTA
            'excellent_properties': excellent_count,
            'very_good_properties': very_good_count,
            'viable_properties': viable_count,
            'biogas_viable_properties': biogas_viable_count,
            
            # Percentuais realistas
            'excellent_percentage': round((excellent_count / len(gdf)) * 100, 1) if len(gdf) > 0 else 0,
            'very_good_percentage': round((very_good_count / len(gdf)) * 100, 1) if len(gdf) > 0 else 0,
            'viable_percentage': round((viable_count / len(gdf)) * 100, 1) if len(gdf) > 0 else 0,
            'biogas_viable_percentage': round((biogas_viable_count / len(gdf)) * 100, 1) if len(gdf) > 0 else 0,
            
            # Thresholds utilizados
            'thresholds': thresholds,
            'top_municipalities': gdf['municipio'].value_counts().head(5).to_dict() if 'municipio' in gdf.columns else {},
            'status': 'success'
        }
        
        logger.info(f"✅ Estatísticas MCDA {radius} (CRITÉRIOS REALISTAS): {stats['total_properties']} propriedades, {stats['viable_properties']} viáveis ({stats['viable_percentage']}%)")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro ao calcular estatísticas MCDA {radius}: {str(e)}")
        return {'status': 'error', 'error': str(e), 'radius': radius}

def get_cp2b_summary_stats() -> Dict[str, Any]:
    """
    Função mantida para compatibilidade - agora retorna estatísticas do cenário 30km
    
    Returns:
        Dict com estatísticas do projeto CP2B
    """
    return get_mcda_summary_stats_by_radius('30km')

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
        
    # Nova variável para o seletor de raios MCDA
    if 'cp2b_selected_radius' not in st.session_state:
        st.session_state.cp2b_selected_radius = '30km'