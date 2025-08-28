from pathlib import Path
import pandas as pd
import numpy as np
from .models import bulk_insert_municipios

ROOT = Path(__file__).resolve().parents[2]
RAW_XLSX = ROOT / "data" / "raw" / "Banco_De_Dados_Residuos_Biogas_Municipios_SP.xlsx"

# Mapeamento das colunas Excel → Schema SQLite (Nova estrutura simplificada)
COLUMN_MAP = {
    # Identificação
    "OBJECTID": "objectid",
    "CD_MUN": "cd_mun", 
    "NM_MUN": "nm_mun",
    "AREA_KM2": "area_km2",
    
    # Biogás por fonte pecuária (Nm³/ano)
    "Biogas_Bovinos_Nm_ano": "biogas_bovinos_nm_ano",
    "Biogas_Suino_Nm_ano": "biogas_suino_nm_ano",
    "Biogás Aves_Nm_ano": "biogas_aves_nm_ano",
    "Biogas_Piscicultura_Nm_ano": "biogas_piscicultura_nm_ano",
    "Total Pecuaria_Nm_ano": "total_pecuaria_nm_ano",
    
    # Silvicultura (Nm³/ano)
    "Silvicultura_Nm_ano": "silvicultura_nm_ano",
    
    # RSU e RPO por habitante (Nm³/habitante/ano)
    "RSU_Potencial_Nm_habitante_ano": "rsu_potencial_nm_habitante_ano",
    "RPO_Potencial_Nm_habitante_ano": "rpo_potencial_nm_habitante_ano",
    
    # Biogás agrícola (Nm³/ano)
    "Biogas_Cana_Nm_ano": "biogas_cana_nm_ano",
    "Biogas_Soja_Nm_ano": "biogas_soja_nm_ano",
    "Biogas_Milho_Nm_ano": "biogas_milho_nm_ano",
    "Biogas_Cafe_Nm_ano": "biogas_cafe_nm_ano",
    "Biogas_Citros_Nm_ano": "biogas_citros_nm_ano",
    "Total Agrícola_Nm_ano": "total_agricola_nm_ano",
    
    # Total final
    "TOTAL FINAL_Nm_ano": "total_final_nm_ano"
}

def clean_numeric_value(value):
    """Limpa e converte valores para numérico, tratando casos especiais"""
    if pd.isna(value) or value == '-' or value == '' or str(value).strip() == '':
        return 0.0
    
    try:
        # Se for string, remove espaços
        if isinstance(value, str):
            value = value.strip()
            if value == '-':
                return 0.0
        
        # Converte para float
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def clean_integer_value(value):
    """Limpa e converte valores para inteiro"""
    cleaned = clean_numeric_value(value)
    return int(cleaned)

def load_excel_to_sqlite() -> None:
    """Carrega dados do Excel para SQLite com limpeza completa"""
    
    if not RAW_XLSX.exists():
        raise FileNotFoundError(f"Arquivo Excel não encontrado: {RAW_XLSX}")
    
    print(f"Carregando dados de: {RAW_XLSX}")
    
    # Carregar Excel
    df = pd.read_excel(RAW_XLSX, engine="openpyxl")
    print(f"Linhas carregadas: {len(df)}")
    
    # Renomear colunas conforme mapeamento
    df = df.rename(columns={k: v for k, v in COLUMN_MAP.items() if k in df.columns})
    
    # Verificar colunas obrigatórias
    required_cols = ["cd_mun", "nm_mun"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente: {col}")
    
    # Limpeza de dados por tipo
    print("Limpando dados...")
    
    # Campos de identificação
    df["cd_mun"] = df["cd_mun"].astype(str)
    df["nm_mun"] = df["nm_mun"].astype(str)
    df["objectid"] = df.get("objectid", 0).apply(clean_integer_value)
    df["area_km2"] = df.get("area_km2", 0).apply(clean_numeric_value)
    
    # Todas as colunas de biogás são valores numéricos (float)
    biogas_cols = [
        "biogas_bovinos_nm_ano", "biogas_suino_nm_ano", "biogas_aves_nm_ano", 
        "biogas_piscicultura_nm_ano", "total_pecuaria_nm_ano",
        "silvicultura_nm_ano",
        "rsu_potencial_nm_habitante_ano", "rpo_potencial_nm_habitante_ano",
        "biogas_cana_nm_ano", "biogas_soja_nm_ano", "biogas_milho_nm_ano", 
        "biogas_cafe_nm_ano", "biogas_citros_nm_ano", "total_agricola_nm_ano",
        "total_final_nm_ano"
    ]
    
    for col in biogas_cols:
        df[col] = df.get(col, 0).apply(clean_numeric_value)
    
    # Converter para dicionários
    records = df.to_dict(orient="records")
    
    print(f"Inserindo {len(records)} registros no banco...")
    
    # Inserir no banco
    bulk_insert_municipios(records)
    
    print(f"✅ Importação concluída! {len(records)} municípios carregados.")

if __name__ == "__main__":
    try:
        load_excel_to_sqlite()
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        raise