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
        
        # Tabela principal de municípios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS municipios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            objectid INTEGER,
            cd_mun TEXT UNIQUE NOT NULL,
            nm_mun TEXT NOT NULL,
            area_km2 REAL,
            
            -- Culturas (toneladas/ano)
            arroz_casca REAL DEFAULT 0,
            cafe_grao REAL DEFAULT 0,
            cana_acucar REAL DEFAULT 0,
            laranja REAL DEFAULT 0,
            limao REAL DEFAULT 0,
            milho_grao REAL DEFAULT 0,
            soja_grao REAL DEFAULT 0,
            sorgo_grao REAL DEFAULT 0,
            
            -- Resíduos (toneladas/ano)
            residuos_cana REAL DEFAULT 0,
            residuos_soja REAL DEFAULT 0,
            residuos_milho REAL DEFAULT 0,
            residuos_bovino REAL DEFAULT 0,
            
            -- Rebanhos (cabeças)
            bubalino INTEGER DEFAULT 0,
            equino INTEGER DEFAULT 0,
            suino_total INTEGER DEFAULT 0,
            suino_matrizes INTEGER DEFAULT 0,
            caprino INTEGER DEFAULT 0,
            ovino INTEGER DEFAULT 0,
            galinaceos_total INTEGER DEFAULT 0,
            galinaceos_galinhas INTEGER DEFAULT 0,
            codornas INTEGER DEFAULT 0,
            
            -- Silvicultura
            eucalipto_total REAL DEFAULT 0,
            pinus_total REAL DEFAULT 0,
            biogas_silvicultura REAL DEFAULT 0,
            
            -- RSU e RPO
            rsu_organicos REAL DEFAULT 0,
            rpo_podas REAL DEFAULT 0,
            rsu_potencial_ch4 REAL DEFAULT 0,
            rpo_potencial_ch4 REAL DEFAULT 0,
            total_ch4_rsu_rpo REAL DEFAULT 0,
            
            -- Biogás por fonte (Nm³/ano)
            biogas_cana REAL DEFAULT 0,
            biogas_soja REAL DEFAULT 0,
            biogas_milho REAL DEFAULT 0,
            biogas_bovino REAL DEFAULT 0,
            biogas_cafe REAL DEFAULT 0,
            biogas_citros REAL DEFAULT 0,
            biogas_suinos REAL DEFAULT 0,
            biogas_aves REAL DEFAULT 0,
            biogas_piscicultura REAL DEFAULT 0,
            
            -- Totais finais
            total_agricola REAL DEFAULT 0,
            total_pecuaria REAL DEFAULT 0,
            total_final REAL DEFAULT 0,
            
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_municipios_total_final ON municipios(total_final)")
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