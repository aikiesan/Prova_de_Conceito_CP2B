from pathlib import Path
import pandas as pd
import numpy as np
from .models import bulk_insert_municipios

ROOT = Path(__file__).resolve().parents[2]
RAW_XLSX = ROOT / "data" / "raw" / "Banco_De_Dados_Residuos_Biogas_Municipios_SP.xlsx"

# Mapeamento COMPLETO das colunas Excel → Schema SQLite
COLUMN_MAP = {
    # Identificação
    "OBJECTID": "objectid",
    "CD_MUN": "cd_mun", 
    "NM_MUN": "nm_mun",
    "AREA_KM2": "area_km2",
    
    # Culturas (toneladas/ano)
    "Arroz (em casca)": "arroz_casca",
    "Café (em grão) Total": "cafe_grao", 
    "Canadeaçúcar": "cana_acucar",
    "Laranja": "laranja",
    "Limão": "limao",
    "Milho (em grão)": "milho_grao",
    "Soja (em grão)": "soja_grao",
    "Sorgo (em grão)": "sorgo_grao",
    
    # Resíduos (toneladas/ano)
    "Resíduos Cana (ton/ano)": "residuos_cana",
    "Resíduos Soja (ton/ano)": "residuos_soja", 
    "Resíduos Milho (ton/ano)": "residuos_milho",
    "Resíduos Bovino (ton/ano)": "residuos_bovino",
    
    # Rebanhos (cabeças)
    "Bubalino": "bubalino",
    "Equino": "equino",
    "Suíno - total": "suino_total",
    "Suíno - matrizes de suínos": "suino_matrizes",
    "Caprino": "caprino", 
    "Ovino": "ovino",
    "Galináceos - total": "galinaceos_total",
    "Galináceos - galinhas": "galinaceos_galinhas",
    "Codornas": "codornas",
    
    # Silvicultura
    "Eucalipto Total (m³)": "eucalipto_total",
    "Pinus Total (m³)": "pinus_total", 
    "Biogás Silvicultura (Nm³/Ano)": "biogas_silvicultura",
    
    # RSU e RPO
    "RSU Orgânicos (ton/ano)": "rsu_organicos",
    "RPO Podas (ton/ano)": "rpo_podas",
    "RSU Potencial CH4 (m³/ano)": "rsu_potencial_ch4",
    "RPO Potencial CH4 (m³/ano)": "rpo_potencial_ch4", 
    "Total CH4 RSU+RPO (m³/ano)": "total_ch4_rsu_rpo",
    
    # Biogás por fonte (Nm³/ano)
    "Biogás Cana (Nm³/ano)": "biogas_cana",
    "Biogás Soja (Nm³/ano)": "biogas_soja",
    "Biogás Milho (Nm³/ano)": "biogas_milho", 
    "Biogás Bovino (Nm³/ano)": "biogas_bovino",
    "Biogás Café (Nm³/ano)": "biogas_cafe",
    "Biogás Citros (Nm³/ano)": "biogas_citros",
    "Biogás Suínos (Nm³/ano)": "biogas_suinos",
    "Biogás Aves (Nm³/ano)": "biogas_aves",
    "Biogás Piscicultura (Nm³/ano)": "biogas_piscicultura",
    
    # Totais finais
    "Total Agrícola (Nm³/ano)": "total_agricola",
    "Total Pecuária (Nm³/ano)": "total_pecuaria", 
    "TOTAL FINAL (Nm³/ano)": "total_final"
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
    
    # Culturas (float)
    cultura_cols = ["arroz_casca", "cafe_grao", "cana_acucar", "laranja", "limao", 
                   "milho_grao", "soja_grao", "sorgo_grao"]
    for col in cultura_cols:
        df[col] = df.get(col, 0).apply(clean_numeric_value)
    
    # Resíduos (float) 
    residuo_cols = ["residuos_cana", "residuos_soja", "residuos_milho", "residuos_bovino"]
    for col in residuo_cols:
        df[col] = df.get(col, 0).apply(clean_numeric_value)
    
    # Rebanhos (integer)
    rebanho_cols = ["bubalino", "equino", "suino_total", "suino_matrizes", 
                   "caprino", "ovino", "galinaceos_total", "galinaceos_galinhas", "codornas"]
    for col in rebanho_cols:
        df[col] = df.get(col, 0).apply(clean_integer_value)
    
    # Silvicultura (float)
    silv_cols = ["eucalipto_total", "pinus_total", "biogas_silvicultura"]
    for col in silv_cols:
        df[col] = df.get(col, 0).apply(clean_numeric_value)
    
    # RSU/RPO (float)
    rsu_cols = ["rsu_organicos", "rpo_podas", "rsu_potencial_ch4", 
               "rpo_potencial_ch4", "total_ch4_rsu_rpo"]
    for col in rsu_cols:
        df[col] = df.get(col, 0).apply(clean_numeric_value)
    
    # Biogás por fonte (float)
    biogas_cols = ["biogas_cana", "biogas_soja", "biogas_milho", "biogas_bovino",
                  "biogas_cafe", "biogas_citros", "biogas_suinos", "biogas_aves", 
                  "biogas_piscicultura"]
    for col in biogas_cols:
        df[col] = df.get(col, 0).apply(clean_numeric_value)
    
    # Totais (float)
    total_cols = ["total_agricola", "total_pecuaria", "total_final"]
    for col in total_cols:
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