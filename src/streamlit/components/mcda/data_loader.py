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
CP2B_DATA_PATH = Path(__file__).parent.parent.parent  # Vai para o diretório streamlit


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
        
        # Tenta encontrar o arquivo no diretório atual
        current_path = Path.cwd()
        geoparquet_path = current_path / geoparquet_filename
        
        if not geoparquet_path.exists():
            logger.warning(f"⚠️ Arquivo {geoparquet_filename} não encontrado em {current_path}")
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