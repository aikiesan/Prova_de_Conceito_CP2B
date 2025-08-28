"""
Utilitário de banco de dados otimizado para CP2B - Threading Fix
"""

import sqlite3
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from contextlib import contextmanager
import time
from datetime import datetime, timedelta
import threading

# Configuração de logging
logger = logging.getLogger(__name__)

# Caminho do banco de dados
DB_PATH = Path(__file__).resolve().parents[3] / "data" / "database.db"

class DatabaseError(Exception):
    """Exceção customizada para erros de banco de dados"""
    pass

# Thread-local storage para conexões SQLite
_thread_local = threading.local()



def get_thread_connection() -> sqlite3.Connection:
    """Obtém conexão SQLite específica da thread atual"""
    if not hasattr(_thread_local, 'connection') or _thread_local.connection is None:
        if not DB_PATH.exists():
            raise DatabaseError(f"Banco de dados não encontrado: {DB_PATH}")
        
        conn = sqlite3.connect(
            str(DB_PATH),
            timeout=30.0,
            check_same_thread=False  # Permite uso em threads diferentes
        )
        
        # Configurações de performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB
        
        conn.row_factory = sqlite3.Row
        _thread_local.connection = conn
    
    return _thread_local.connection

@contextmanager
def get_connection():
    """Context manager thread-safe para conexões SQLite"""
    try:
        conn = get_thread_connection()
        yield conn
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        raise DatabaseError(f"Erro na operação de banco: {e}")

# Cache simples sem threading issues
_simple_cache = {}
_cache_timestamps = {}

def simple_cache_get(key: str, ttl: int = 300) -> Optional[pd.DataFrame]:
    """Cache simples thread-safe"""
    if key in _simple_cache:
        if time.time() - _cache_timestamps[key] < ttl:
            return _simple_cache[key].copy()
        else:
            del _simple_cache[key]
            del _cache_timestamps[key]
    return None

def simple_cache_set(key: str, data: pd.DataFrame) -> None:
    """Armazena no cache simples"""
    _simple_cache[key] = data.copy()
    _cache_timestamps[key] = time.time()

def query_df(
    sql: str, 
    params: Union[tuple, dict] = (), 
    use_cache: bool = True,
    cache_ttl: int = 300
) -> pd.DataFrame:
    """
    Executa query SQL thread-safe retornando DataFrame
    """
    # Cache simples
    cache_key = f"{sql}_{str(params)}"
    if use_cache:
        cached_result = simple_cache_get(cache_key, cache_ttl)
        if cached_result is not None:
            return cached_result
    
    # Executar query
    start_time = time.time()
    try:
        with get_connection() as conn:
            df = pd.read_sql_query(sql, conn, params=params)
        
        execution_time = time.time() - start_time
        logger.info(f"Query executada em {execution_time:.3f}s, {len(df)} linhas")
        
        # Cache resultado
        if use_cache:
            simple_cache_set(cache_key, df)
        
        return df
        
    except Exception as e:
        logger.error(f"Erro ao executar query: {e}")
        raise DatabaseError(f"Falha na execução da query: {e}")

def execute_query(sql: str, params: Union[tuple, dict] = ()) -> int:
    """Executa query de modificação thread-safe"""
    try:
        with get_connection() as conn:
            cursor = conn.execute(sql, params)
            rows_affected = cursor.rowcount
            conn.commit()
            
        # Limpar cache após modificações
        _simple_cache.clear()
        _cache_timestamps.clear()
        
        return rows_affected
        
    except Exception as e:
        logger.error(f"Erro ao executar query de modificação: {e}")
        raise DatabaseError(f"Falha na execução: {e}")

class MunicipalQueries:
    """Classe com queries otimizadas para dados municipais"""
    
    @staticmethod
    def get_all_municipalities(limit: Optional[int] = None) -> pd.DataFrame:
        """Obtém TODOS os municípios incluindo os com potencial zero"""
        sql = """
        SELECT 
            cd_mun, nm_mun, area_km2, objectid,
            total_final_nm_ano, total_agricola_nm_ano, total_pecuaria_nm_ano,
            biogas_cana_nm_ano, biogas_soja_nm_ano, biogas_milho_nm_ano, biogas_bovinos_nm_ano,
            biogas_cafe_nm_ano, biogas_citros_nm_ano, biogas_suino_nm_ano, biogas_aves_nm_ano,
            biogas_piscicultura_nm_ano, silvicultura_nm_ano,
            rsu_potencial_nm_habitante_ano, rpo_potencial_nm_habitante_ano
        FROM municipios 
        ORDER BY total_final_nm_ano DESC
        """
        if limit:
            sql += f" LIMIT {limit}"
        
        return query_df(sql)
    
    @staticmethod
    def get_municipalities_with_potential() -> pd.DataFrame:
        """Obtém apenas municípios com potencial > 0"""
        sql = """
        SELECT 
            cd_mun, nm_mun, area_km2, objectid,
            total_final_nm_ano, total_agricola_nm_ano, total_pecuaria_nm_ano,
            biogas_cana_nm_ano, biogas_soja_nm_ano, biogas_milho_nm_ano, biogas_bovinos_nm_ano,
            biogas_cafe_nm_ano, biogas_citros_nm_ano, biogas_suino_nm_ano, biogas_aves_nm_ano,
            biogas_piscicultura_nm_ano, silvicultura_nm_ano,
            rsu_potencial_nm_habitante_ano, rpo_potencial_nm_habitante_ano
        FROM municipios 
        WHERE total_final_nm_ano > 0
        ORDER BY total_final_nm_ano DESC
        """
        return query_df(sql)
    
    @staticmethod
    def get_municipality_details(cd_mun: str) -> Optional[pd.DataFrame]:
        """Obtém detalhes completos de um município"""
        sql = "SELECT * FROM municipios WHERE cd_mun = ?"
        df = query_df(sql, (cd_mun,))
        return df if not df.empty else None
    
    @staticmethod
    def get_aggregated_stats() -> Dict[str, Any]:
        """Obtém estatísticas agregadas dos municípios"""
        sql = """
        SELECT 
            COUNT(*) as total_municipalities,
            COUNT(CASE WHEN total_final_nm_ano > 0 THEN 1 END) as municipalities_with_potential,
            SUM(total_final_nm_ano) as total_biogas_potential,
            AVG(total_final_nm_ano) as avg_biogas_potential,
            MAX(total_final_nm_ano) as max_biogas_potential,
            MIN(total_final_nm_ano) as min_biogas_potential,
            SUM(total_agricola_nm_ano) as total_agricultural,
            SUM(total_pecuaria_nm_ano) as total_livestock,
            SUM(area_km2) as total_area
        FROM municipios
        """
        df = query_df(sql)
        return df.iloc[0].to_dict() if not df.empty else {}

def clear_cache() -> None:
    """Limpa o cache simples"""
    _simple_cache.clear()
    _cache_timestamps.clear()
    logger.info("Cache limpo")

def get_cache_stats() -> Dict[str, Any]:
    """Obtém estatísticas do cache"""
    return {
        'cache_size': len(_simple_cache),
        'cached_queries': list(_simple_cache.keys())
    }

def initialize_database() -> bool:
    """Inicializa banco de dados com validação thread-safe"""
    try:
        if not DB_PATH.exists():
            logger.error(f"Banco não encontrado: {DB_PATH}")
            return False
        
        # Teste de conexão thread-safe
        with get_connection() as conn:
            tables_result = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            tables = [row[0] for row in tables_result]
            logger.info(f"Tabelas encontradas: {tables}")
            
            if 'municipios' not in tables:
                logger.error("Tabela municipios não encontrada")
                return False
            
            # Contar registros
            count_result = conn.execute("SELECT COUNT(*) FROM municipios").fetchone()
            municipios_count = count_result[0] if count_result else 0
            logger.info(f"Municípios no banco: {municipios_count}")
            
            if municipios_count == 0:
                logger.warning("Tabela municipios está vazia")
                return False
        
        logger.info("Banco inicializado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        return False

def close_all_connections() -> None:
    """Fecha conexões thread-local"""
    if hasattr(_thread_local, 'connection') and _thread_local.connection:
        _thread_local.connection.close()
        _thread_local.connection = None