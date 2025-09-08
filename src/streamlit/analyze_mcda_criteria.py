#!/usr/bin/env python3
# Análise dos critérios atuais MCDA para ajuste técnico-econômico

import pandas as pd
import geopandas as gpd
import numpy as np
from components.mcda.data_loader import load_mcda_geoparquet_by_radius

print("ANALISE DE CRITERIOS MCDA - AJUSTE TECNICO-ECONOMICO")
print("=" * 60)

# Analisar cada cenário
scenarios = ['10km', '30km', '50km']
analysis_results = {}

for radius in scenarios:
    print(f"\n>>> CENARIO {radius} <<<")
    print("-" * 30)
    
    # Carregar dados
    gdf = load_mcda_geoparquet_by_radius(radius)
    if gdf.empty:
        continue
        
    # Analisar distribuição de scores
    mcda_scores = gdf['mcda_score'].dropna()
    biomass_scores = gdf['biomass_score'].dropna()
    
    print(f"DISTRIBUICAO DE SCORES MCDA:")
    print(f"  Minimo:     {mcda_scores.min():.1f}")
    print(f"  Maximo:     {mcda_scores.max():.1f}")
    print(f"  Mediana:    {mcda_scores.median():.1f}")
    print(f"  Media:      {mcda_scores.mean():.1f}")
    print(f"  Quartis:")
    print(f"    Q1 (25%): {mcda_scores.quantile(0.25):.1f}")
    print(f"    Q3 (75%): {mcda_scores.quantile(0.75):.1f}")
    print(f"  Percentis:")
    print(f"    P90:      {mcda_scores.quantile(0.90):.1f}")
    print(f"    P95:      {mcda_scores.quantile(0.95):.1f}")
    print(f"    P99:      {mcda_scores.quantile(0.99):.1f}")
    
    # Analisar biomass scores (potencial real)
    print(f"\nDISTRIBUICAO BIOMASSA (ha ou score):")
    print(f"  Minimo:     {biomass_scores.min():.1f}")
    print(f"  Maximo:     {biomass_scores.max():.1f}")
    print(f"  Mediana:    {biomass_scores.median():.1f}")
    print(f"  Media:      {biomass_scores.mean():.1f}")
    print(f"  P90:        {biomass_scores.quantile(0.90):.1f}")
    print(f"  P95:        {biomass_scores.quantile(0.95):.1f}")
    
    # Analisar critérios atuais vs propostos
    current_viable = len(gdf[gdf['mcda_score'] > 60])
    current_excellent = len(gdf[gdf['mcda_score'] > 80])
    
    # Propor novos critérios mais rigorosos
    p95_threshold = mcda_scores.quantile(0.95)  # Top 5%
    p90_threshold = mcda_scores.quantile(0.90)  # Top 10%
    p75_threshold = mcda_scores.quantile(0.75)  # Top 25%
    
    new_excellent = len(gdf[gdf['mcda_score'] > p95_threshold])
    new_very_good = len(gdf[gdf['mcda_score'] > p90_threshold])
    new_viable = len(gdf[gdf['mcda_score'] > p75_threshold])
    
    print(f"\nCOMPARACAO DE CRITERIOS:")
    print(f"  ATUAL (Score > 60):")
    print(f"    Viaveis:    {current_viable:,} ({current_viable/len(gdf)*100:.1f}%)")
    print(f"  ATUAL (Score > 80):")
    print(f"    Excelentes: {current_excellent:,} ({current_excellent/len(gdf)*100:.1f}%)")
    print(f"  ")
    print(f"  PROPOSTO (Percentis):")
    print(f"    Excelentes (P95): {new_excellent:,} ({new_excellent/len(gdf)*100:.1f}%) - Threshold: {p95_threshold:.1f}")
    print(f"    Muito Bom (P90):  {new_very_good:,} ({new_very_good/len(gdf)*100:.1f}%) - Threshold: {p90_threshold:.1f}")
    print(f"    Viavel (P75):     {new_viable:,} ({new_viable/len(gdf)*100:.1f}%) - Threshold: {p75_threshold:.1f}")
    
    # Analisar potencial de biogás se houver coluna específica
    biogas_col = f'total_biogas_nm3_year_{radius}'
    if biogas_col in gdf.columns:
        biogas_potential = gdf[biogas_col].dropna()
        print(f"\nPOTENCIAL DE BIOGAS (Nm3/ano):")
        print(f"  Mediana:    {biogas_potential.median():,.0f}")
        print(f"  Media:      {biogas_potential.mean():,.0f}")
        print(f"  P90:        {biogas_potential.quantile(0.90):,.0f}")
        print(f"  P95:        {biogas_potential.quantile(0.95):,.0f}")
        
        # Critérios técnicos mínimos para viabilidade
        # Baseado em literatura: plantas < 100 kW raramente são viáveis
        # 1 Nm3/h = 8760 Nm3/ano, 1 Nm3 CH4 ≈ 10 kWh
        # Planta mínima viável: ~250 kW = 25 Nm3/h = 219,000 Nm3/ano
        min_viable_biogas = 219000  # Nm3/ano para 250 kW
        med_viable_biogas = 438000  # Nm3/ano para 500 kW  
        large_viable_biogas = 876000  # Nm3/ano para 1 MW
        
        biogas_viable_min = len(gdf[gdf[biogas_col] > min_viable_biogas])
        biogas_viable_med = len(gdf[gdf[biogas_col] > med_viable_biogas])
        biogas_viable_large = len(gdf[gdf[biogas_col] > large_viable_biogas])
        
        print(f"  CRITERIO TECNICO BIOGAS:")
        print(f"    >250kW (219k Nm3): {biogas_viable_min:,} ({biogas_viable_min/len(gdf)*100:.1f}%)")
        print(f"    >500kW (438k Nm3): {biogas_viable_med:,} ({biogas_viable_med/len(gdf)*100:.1f}%)")
        print(f"    >1MW (876k Nm3):   {biogas_viable_large:,} ({biogas_viable_large/len(gdf)*100:.1f}%)")
    
    # Salvar para comparação
    analysis_results[radius] = {
        'current_viable_60': current_viable,
        'current_excellent_80': current_excellent,
        'p95_threshold': p95_threshold,
        'p90_threshold': p90_threshold,
        'p75_threshold': p75_threshold,
        'new_excellent': new_excellent,
        'new_very_good': new_very_good,
        'new_viable': new_viable,
        'total_properties': len(gdf)
    }

# Propor critérios finais consolidados
print(f"\n" + "=" * 60)
print("PROPOSTA DE CRITERIOS TECNICOS CONSOLIDADOS")
print("=" * 60)

print(f"""
CRITERIOS PROPOSTOS (baseados em percentis e literatura técnica):

1. EXCELENTE (Top 5% - P95):
   - 10km: Score > {analysis_results['10km']['p95_threshold']:.1f}
   - 30km: Score > {analysis_results['30km']['p95_threshold']:.1f}
   - 50km: Score > {analysis_results['50km']['p95_threshold']:.1f}
   - Plantas > 1MW, infraestrutura excelente

2. MUITO BOM (Top 10% - P90):
   - 10km: Score > {analysis_results['10km']['p90_threshold']:.1f}
   - 30km: Score > {analysis_results['30km']['p90_threshold']:.1f}
   - 50km: Score > {analysis_results['50km']['p90_threshold']:.1f}
   - Plantas 500kW-1MW, boa infraestrutura

3. VIAVEL (Top 25% - P75):
   - 10km: Score > {analysis_results['10km']['p75_threshold']:.1f}
   - 30km: Score > {analysis_results['30km']['p75_threshold']:.1f}
   - 50km: Score > {analysis_results['50km']['p75_threshold']:.1f}
   - Plantas > 250kW, infraestrutura adequada

4. LIMITADO (P50-P75): Viabilidade condicionada
5. INVIAVEL (< P50): Não recomendado

IMPACTO DA MUDANCA:
""")

for radius in scenarios:
    result = analysis_results[radius]
    print(f"{radius}:")
    print(f"  Atual:    {result['current_viable_60']:,} viáveis ({result['current_viable_60']/result['total_properties']*100:.1f}%)")
    print(f"  Proposto: {result['new_viable']:,} viáveis ({result['new_viable']/result['total_properties']*100:.1f}%)")
    reduction = result['current_viable_60'] - result['new_viable']
    print(f"  Reducao:  -{reduction:,} ({reduction/result['current_viable_60']*100:.1f}% menos)")

print(f"\nJUSTIFICATIVA TECNICA:")
print(f"- Plantas < 250kW raramente são economicamente viáveis")
print(f"- Logística > 50km aumenta custos exponencialmente")  
print(f"- Critério baseado em percentis evita inflação artificial")
print(f"- Foco em localizações realmente promissoras")