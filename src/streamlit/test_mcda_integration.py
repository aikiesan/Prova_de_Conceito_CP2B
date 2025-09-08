# Teste de Integração MCDA - Validação dos 3 Cenários
# Execute este script para testar se a implementação está funcionando

import streamlit as st
import pandas as pd
import geopandas as gpd
from components.mcda import (
    load_mcda_geoparquet_by_radius,
    get_mcda_summary_stats_by_radius,
    MCDA_SCENARIOS
)

st.set_page_config(page_title="Teste MCDA", layout="wide")

st.title("🧪 Teste de Integração MCDA - 3 Cenários")
st.markdown("---")

# Teste de carregamento dos 3 cenários
st.markdown("## 📊 Teste de Carregamento dos Cenários")

results = {}

for radius in MCDA_SCENARIOS.keys():
    st.markdown(f"### Testando cenário {radius}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Teste de carregamento de dados
        with st.spinner(f"Carregando dados {radius}..."):
            try:
                gdf = load_mcda_geoparquet_by_radius(radius)
                if not gdf.empty:
                    st.success(f"✅ Dados {radius} carregados: {len(gdf)} propriedades")
                    results[f'{radius}_data'] = len(gdf)
                    
                    # Mostrar colunas disponíveis
                    st.info(f"📋 Colunas: {list(gdf.columns)}")
                else:
                    st.error(f"❌ Erro ao carregar dados {radius}")
                    results[f'{radius}_data'] = 0
            except Exception as e:
                st.error(f"❌ Exceção ao carregar {radius}: {str(e)}")
                results[f'{radius}_data'] = 0
    
    with col2:
        # Teste de estatísticas
        with st.spinner(f"Calculando estatísticas {radius}..."):
            try:
                stats = get_mcda_summary_stats_by_radius(radius)
                if stats['status'] == 'success':
                    st.success(f"✅ Estatísticas {radius} calculadas")
                    st.json({
                        'total_properties': stats['total_properties'],
                        'viable_properties': stats['viable_properties'], 
                        'viable_percentage': stats['viable_percentage'],
                        'excellent_properties': stats['excellent_properties'],
                        'avg_score': stats['avg_score'],
                        'max_score': stats['max_score']
                    })
                    results[f'{radius}_stats'] = 'success'
                else:
                    st.error(f"❌ Erro nas estatísticas {radius}")
                    results[f'{radius}_stats'] = 'error'
            except Exception as e:
                st.error(f"❌ Exceção nas estatísticas {radius}: {str(e)}")
                results[f'{radius}_stats'] = 'error'
    
    st.markdown("---")

# Resumo final
st.markdown("## 📈 Resumo dos Testes")

summary_df = pd.DataFrame([
    {
        'Cenário': '10km',
        'Dados Carregados': results.get('10km_data', 0),
        'Estatísticas': '✅' if results.get('10km_stats') == 'success' else '❌',
        'Status': '✅ OK' if results.get('10km_data', 0) > 0 and results.get('10km_stats') == 'success' else '❌ Falha'
    },
    {
        'Cenário': '30km', 
        'Dados Carregados': results.get('30km_data', 0),
        'Estatísticas': '✅' if results.get('30km_stats') == 'success' else '❌',
        'Status': '✅ OK' if results.get('30km_data', 0) > 0 and results.get('30km_stats') == 'success' else '❌ Falha'
    },
    {
        'Cenário': '50km',
        'Dados Carregados': results.get('50km_data', 0), 
        'Estatísticas': '✅' if results.get('50km_stats') == 'success' else '❌',
        'Status': '✅ OK' if results.get('50km_data', 0) > 0 and results.get('50km_stats') == 'success' else '❌ Falha'
    }
])

st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Verificação de arquivos
st.markdown("## 📁 Verificação de Arquivos")

import os
for radius, filename in MCDA_SCENARIOS.items():
    if os.path.exists(filename):
        file_size = os.path.getsize(filename) / (1024*1024)  # MB
        st.success(f"✅ {filename} - {file_size:.1f} MB")
    else:
        st.error(f"❌ {filename} - Arquivo não encontrado")

if st.button("🔄 Executar Novamente"):
    st.rerun()