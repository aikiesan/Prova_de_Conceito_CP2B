"""
Scripts de migração para criar/atualizar estrutura do banco SQLite
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Caminho do banco
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "database.db"

def create_tables():
    """Cria as tabelas principais do sistema"""
    
    # Garantir que o diretório existe
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Tabela principal de municípios - Nova estrutura simplificada
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS municipios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objectid INTEGER,
            cd_mun TEXT UNIQUE NOT NULL,
            nm_mun TEXT NOT NULL,
            area_km2 REAL,
            
            -- Biogás por fonte (Nm³/ano)
            biogas_bovinos_nm_ano REAL DEFAULT 0,
            biogas_suino_nm_ano REAL DEFAULT 0,
            biogas_aves_nm_ano REAL DEFAULT 0,
            biogas_piscicultura_nm_ano REAL DEFAULT 0,
            total_pecuaria_nm_ano REAL DEFAULT 0,
            
            -- Silvicultura (Nm³/ano)
            silvicultura_nm_ano REAL DEFAULT 0,
            
            -- RSU e RPO por habitante (Nm³/habitante/ano)
            rsu_potencial_nm_habitante_ano REAL DEFAULT 0,
            rpo_potencial_nm_habitante_ano REAL DEFAULT 0,
            
            -- Biogás agrícola (Nm³/ano)
            biogas_cana_nm_ano REAL DEFAULT 0,
            biogas_soja_nm_ano REAL DEFAULT 0,
            biogas_milho_nm_ano REAL DEFAULT 0,
            biogas_cafe_nm_ano REAL DEFAULT 0,
            biogas_citros_nm_ano REAL DEFAULT 0,
            total_agricola_nm_ano REAL DEFAULT 0,
            
            -- Total final (Nm³/ano)
            total_final_nm_ano REAL DEFAULT 0,
            
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Tabela de fatores de conversão
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS fatores_conversao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_residuo TEXT UNIQUE NOT NULL,
            fator_producao REAL NOT NULL,
            rendimento_biogas REAL NOT NULL,
            teor_metano REAL NOT NULL,
            unidade TEXT NOT NULL,
            categoria TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Índices para performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_municipios_cd_mun ON municipios(cd_mun)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_municipios_nm_mun ON municipios(nm_mun)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_municipios_total_final ON municipios(total_final_nm_ano)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fatores_categoria ON fatores_conversao(categoria)")
        
        conn.commit()
        
    logger.info("Tabelas criadas com sucesso")

def run_migrations():
    """Executa todas as migrações necessárias"""
    try:
        logger.info("Iniciando migrações do banco de dados...")
        create_tables()
        logger.info("Migrações concluídas com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro nas migrações: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = run_migrations()
    if success:
        print("✅ Migrações executadas com sucesso")
    else:
        print("❌ Falha nas migrações")