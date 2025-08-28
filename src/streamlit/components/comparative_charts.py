"""
Gráficos Comparativos Avançados para Análise de Resíduos - CP2B
Visualizações especializadas para comparar diferentes aspectos dos resíduos de biogás
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

def render_residue_treemap(df: pd.DataFrame) -> None:
    """Renderiza treemap hierárquico mostrando proporção dos resíduos"""
    
    st.subheader("🌳 Visualização Hierárquica dos Resíduos")
    
    if df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    # Preparar dados para treemap
    treemap_data = []
    
    # Definir mapeamento de resíduos por categoria
    residue_categories = {
        'Agrícola': {
            'biogas_cana_nm_ano': '🌾 Cana',
            'biogas_soja_nm_ano': '🌱 Soja', 
            'biogas_milho_nm_ano': '🌽 Milho',
            'biogas_cafe_nm_ano': '☕ Café',
            'biogas_citros_nm_ano': '🍊 Citros'
        },
        'Pecuária': {
            'biogas_bovinos_nm_ano': '🐄 Bovinos',
            'biogas_suino_nm_ano': '🐷 Suínos',
            'biogas_aves_nm_ano': '🐔 Aves',
            'biogas_piscicultura_nm_ano': '🐟 Piscicultura'
        },
        'Urbano': {
            'rsu_potencial_nm_habitante_ano': '🗑️ RSU',
            'rpo_potencial_nm_habitante_ano': '🌿 RPO'
        }
    }
    
    # Calcular valores para cada resíduo
    for category, residues in residue_categories.items():
        for residue_key, residue_label in residues.items():
            if residue_key in df.columns:
                total_value = df[residue_key].sum()
                if total_value > 0:
                    treemap_data.append({
                        'Category': category,
                        'Residue': residue_label,
                        'Value': total_value,
                        'Full_Label': f"{category} - {residue_label}"
                    })
    
    if not treemap_data:
        st.warning("Nenhum dado de resíduos encontrado")
        return
    
    treemap_df = pd.DataFrame(treemap_data)
    
    # Criar treemap
    fig = px.treemap(
        treemap_df,
        path=[px.Constant("Biogás SP"), 'Category', 'Residue'],
        values='Value',
        title="Distribuição Proporcional do Potencial de Biogás por Resíduo",
        color='Value',
        color_continuous_scale='Viridis',
        labels={'Value': 'Potencial (Nm³/ano)'}
    )
    
    fig.update_layout(height=600)
    fig.update_traces(textinfo="label+value")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas do treemap
    col1, col2, col3 = st.columns(3)
    
    total_potential = treemap_df['Value'].sum()
    largest_category = treemap_df.groupby('Category')['Value'].sum().idxmax()
    largest_residue = treemap_df.loc[treemap_df['Value'].idxmax(), 'Residue']
    
    with col1:
        st.metric(
            "🎯 Total Geral",
            f"{total_potential / 1_000_000:.1f}M Nm³/ano",
            help="Soma de todos os resíduos"
        )
    
    with col2:
        category_total = treemap_df[treemap_df['Category'] == largest_category]['Value'].sum()
        st.metric(
            f"🏆 Categoria Líder",
            largest_category,
            delta=f"{(category_total / total_potential * 100):.1f}% do total",
            help="Categoria com maior potencial total"
        )
    
    with col3:
        residue_value = treemap_df[treemap_df['Residue'] == largest_residue]['Value'].iloc[0]
        st.metric(
            f"🥇 Resíduo Líder",
            largest_residue,
            delta=f"{(residue_value / total_potential * 100):.1f}% do total",
            help="Resíduo individual com maior potencial"
        )

def render_residue_sunburst(df: pd.DataFrame) -> None:
    """Renderiza gráfico sunburst mostrando hierarquia categoria > resíduo > municípios"""
    
    st.subheader("☀️ Análise Sunburst: Categoria → Resíduo → Top Municípios")
    
    if df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    # Controles
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_category = st.selectbox(
            "Categoria para Análise Detalhada:",
            ["Agrícola", "Pecuária", "Urbano"],
            help="Foco na categoria selecionada"
        )
    
    with col2:
        top_n_municipalities = st.slider(
            "Top Municípios por Resíduo:",
            min_value=3,
            max_value=10,
            value=5,
            help="Quantos municípios mostrar por resíduo"
        )
    
    # Definir resíduos da categoria selecionada
    category_residues = {
        'Agrícola': {
            'biogas_cana_nm_ano': '🌾 Cana',
            'biogas_soja_nm_ano': '🌱 Soja', 
            'biogas_milho_nm_ano': '🌽 Milho',
            'biogas_cafe_nm_ano': '☕ Café',
            'biogas_citros_nm_ano': '🍊 Citros'
        },
        'Pecuária': {
            'biogas_bovinos_nm_ano': '🐄 Bovinos',
            'biogas_suino_nm_ano': '🐷 Suínos',
            'biogas_aves_nm_ano': '🐔 Aves',
            'biogas_piscicultura_nm_ano': '🐟 Piscicultura'
        },
        'Urbano': {
            'rsu_potencial_nm_habitante_ano': '🗑️ RSU',
            'rpo_potencial_nm_habitante_ano': '🌿 RPO'
        }
    }
    
    residues = category_residues[selected_category]
    
    # Preparar dados para sunburst
    sunburst_data = []
    
    for residue_key, residue_label in residues.items():
        if residue_key in df.columns and df[residue_key].sum() > 0:
            # Top municípios para este resíduo
            top_municipalities = df[df[residue_key] > 0].nlargest(top_n_municipalities, residue_key)
            
            for _, municipality in top_municipalities.iterrows():
                sunburst_data.append({
                    'Category': selected_category,
                    'Residue': residue_label,
                    'Municipality': municipality['nm_mun'],
                    'Value': municipality[residue_key],
                    'ids': f"{selected_category}_{residue_label}_{municipality['nm_mun']}",
                    'parents': f"{selected_category}_{residue_label}"
                })
            
            # Total do resíduo
            sunburst_data.append({
                'Category': selected_category,
                'Residue': residue_label,
                'Municipality': '',
                'Value': df[residue_key].sum(),
                'ids': f"{selected_category}_{residue_label}",
                'parents': selected_category
            })
    
    # Total da categoria
    total_category_value = sum([df[key].sum() for key in residues.keys() if key in df.columns])
    sunburst_data.append({
        'Category': selected_category,
        'Residue': '',
        'Municipality': '',
        'Value': total_category_value,
        'ids': selected_category,
        'parents': ""
    })
    
    if not sunburst_data:
        st.warning(f"Nenhum dado encontrado para categoria {selected_category}")
        return
    
    sunburst_df = pd.DataFrame(sunburst_data)
    
    # Criar labels para o sunburst
    labels = []
    parents = []
    values = []
    
    # Categoria principal
    labels.append(selected_category)
    parents.append("")
    values.append(total_category_value)
    
    # Resíduos
    for residue_key, residue_label in residues.items():
        if residue_key in df.columns and df[residue_key].sum() > 0:
            labels.append(residue_label)
            parents.append(selected_category)
            values.append(df[residue_key].sum())
            
            # Top municípios
            top_municipalities = df[df[residue_key] > 0].nlargest(top_n_municipalities, residue_key)
            for _, municipality in top_municipalities.iterrows():
                labels.append(f"{municipality['nm_mun'][:15]}...") # Truncar nomes longos
                parents.append(residue_label)
                values.append(municipality[residue_key])
    
    # Criar gráfico sunburst
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        maxdepth=3,
        insidetextorientation='radial'
    ))
    
    fig.update_layout(
        title=f"Análise Hierárquica - {selected_category}",
        height=600,
        font_size=10
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_residue_radar_chart(df: pd.DataFrame) -> None:
    """Renderiza gráfico radar comparando perfil de resíduos por município"""
    
    st.subheader("🎯 Perfil Radar: Composição de Resíduos por Município")
    
    if df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    # Seleção de municípios para comparação
    col1, col2 = st.columns([2, 1])
    
    with col1:
        available_municipalities = df[df['total_final_nm_ano'] > 0].nlargest(50, 'total_final_nm_ano')
        municipality_options = {
            row['cd_mun']: f"{row['nm_mun']} ({row['total_final_nm_ano']:,.0f} Nm³/ano)"
            for _, row in available_municipalities.iterrows()
        }
        
        selected_municipalities = st.multiselect(
            "Selecione Municípios para Comparação:",
            list(municipality_options.keys()),
            default=list(municipality_options.keys())[:5],
            format_func=lambda x: municipality_options[x],
            help="Máximo recomendado: 5 municípios para melhor visualização"
        )
    
    with col2:
        normalize_values = st.checkbox(
            "Normalizar Valores",
            value=True,
            help="Normaliza valores por município para comparação de perfis"
        )
    
    if not selected_municipalities:
        st.info("Selecione pelo menos um município para análise")
        return
    
    # Definir categorias de resíduos para radar
    residue_categories = {
        '🌾 Cana': 'biogas_cana_nm_ano',
        '🌱 Soja': 'biogas_soja_nm_ano',
        '🌽 Milho': 'biogas_milho_nm_ano',
        '☕ Café': 'biogas_cafe_nm_ano',
        '🍊 Citros': 'biogas_citros_nm_ano',
        '🐄 Bovinos': 'biogas_bovinos_nm_ano',
        '🐷 Suínos': 'biogas_suino_nm_ano',
        '🐔 Aves': 'biogas_aves_nm_ano',
        '🐟 Piscicultura': 'biogas_piscicultura_nm_ano'
    }
    
    # Filtrar dados dos municípios selecionados
    selected_data = df[df['cd_mun'].isin(selected_municipalities)].copy()
    
    # Criar gráfico radar
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set1[:len(selected_municipalities)]
    
    for i, (_, municipality) in enumerate(selected_data.iterrows()):
        values = []
        categories = []
        
        for category_label, column_name in residue_categories.items():
            if column_name in df.columns:
                value = municipality.get(column_name, 0)
                
                if normalize_values and municipality['total_final_nm_ano'] > 0:
                    # Normalizar como percentual do total do município
                    value = (value / municipality['total_final_nm_ano']) * 100
                
                values.append(value)
                categories.append(category_label)
        
        # Fechar o radar (duplicar primeiro valor)
        values.append(values[0])
        categories.append(categories[0])
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=municipality['nm_mun'],
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    
    # Configurar layout do radar
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max([max(values[:-1]) for trace in fig.data]) if fig.data else 100]
            )),
        title=f"Perfil de Resíduos - {'Normalizado' if normalize_values else 'Valores Absolutos'}",
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise complementar
    if normalize_values:
        st.info("🔍 **Análise Normalizada**: Os valores mostram a composição percentual de cada tipo de resíduo no potencial total de cada município.")
    else:
        st.info("🔍 **Valores Absolutos**: Os valores mostram o potencial real em Nm³/ano de cada tipo de resíduo.")

def render_residue_scatter_matrix(df: pd.DataFrame) -> None:
    """Renderiza matriz de dispersão para análise de correlações"""
    
    st.subheader("🔗 Matriz de Dispersão: Correlações entre Resíduos")
    
    if df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    # Selecionar resíduos para análise
    available_residues = {
        'biogas_cana_nm_ano': '🌾 Cana',
        'biogas_soja_nm_ano': '🌱 Soja',
        'biogas_milho_nm_ano': '🌽 Milho',
        'biogas_bovinos_nm_ano': '🐄 Bovinos',
        'biogas_suino_nm_ano': '🐷 Suínos',
        'biogas_aves_nm_ano': '🐔 Aves'
    }
    
    # Filtrar apenas resíduos que existem no dataset
    valid_residues = {k: v for k, v in available_residues.items() if k in df.columns and df[k].sum() > 0}
    
    if len(valid_residues) < 2:
        st.warning("São necessários pelo menos 2 tipos de resíduos para análise de correlação")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_residues = st.multiselect(
            "Selecione Resíduos para Análise:",
            list(valid_residues.keys()),
            default=list(valid_residues.keys())[:4],
            format_func=lambda x: valid_residues[x],
            help="Máximo recomendado: 4-5 resíduos para visualização clara"
        )
    
    with col2:
        log_scale = st.checkbox(
            "Escala Logarítmica",
            help="Usar escala log para melhor visualização de dados com grandes variações"
        )
        
        show_correlation_values = st.checkbox(
            "Mostrar Valores de Correlação",
            value=True,
            help="Exibir coeficientes de correlação nos gráficos"
        )
    
    if len(selected_residues) < 2:
        st.info("Selecione pelo menos 2 resíduos para análise")
        return
    
    # Preparar dados
    scatter_data = df[selected_residues].copy()
    
    if log_scale:
        # Aplicar log scale (evitar log de zero)
        for col in scatter_data.columns:
            scatter_data[col] = np.log1p(scatter_data[col])  # log(1+x) para evitar log(0)
    
    # Renomear colunas para labels mais amigáveis
    scatter_data.columns = [valid_residues[col] for col in scatter_data.columns]
    
    # Criar matriz de scatter plots
    fig = px.scatter_matrix(
        scatter_data,
        title=f"Matriz de Correlação entre Resíduos{' (Escala Log)' if log_scale else ''}",
        height=600
    )
    
    fig.update_layout(
        font_size=10,
        title_x=0.5
    )
    
    # Configurar tamanho dos pontos
    fig.update_traces(marker=dict(size=3, opacity=0.6))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mostrar matriz de correlação numérica
    if show_correlation_values:
        st.subheader("📊 Coeficientes de Correlação")
        
        correlation_matrix = scatter_data.corr()
        
        # Criar heatmap da correlação
        fig_corr = px.imshow(
            correlation_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            title="Matriz de Correlação (Coeficientes de Pearson)",
            labels={'color': 'Correlação'}
        )
        
        fig_corr.update_layout(height=400)
        
        st.plotly_chart(fig_corr, use_container_width=True)

def render_comparative_analysis_dashboard(df: pd.DataFrame) -> None:
    """Dashboard principal de análises comparativas avançadas"""
    
    st.header("📊 Análises Comparativas Avançadas")
    st.markdown("---")
    
    if df.empty:
        st.error("❌ Nenhum dado disponível para análise comparativa")
        return
    
    # Layout em tabs para diferentes tipos de análise
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌳 Treemap",
        "☀️ Sunburst", 
        "🎯 Radar",
        "🔗 Correlações"
    ])
    
    with tab1:
        render_residue_treemap(df)
    
    with tab2:
        render_residue_sunburst(df)
    
    with tab3:
        render_residue_radar_chart(df)
    
    with tab4:
        render_residue_scatter_matrix(df)
    
    # Informações sobre as análises
    st.markdown("---")
    with st.expander("ℹ️ Sobre as Análises Comparativas"):
        st.markdown("""
        **🌳 Treemap**: Visualiza a proporção hierárquica dos diferentes resíduos, facilitando a identificação dos tipos mais relevantes.
        
        **☀️ Sunburst**: Análise em camadas mostrando categoria → resíduo → municípios top, ideal para entender a distribuição detalhada.
        
        **🎯 Radar**: Compara o perfil de composição de resíduos entre diferentes municípios, útil para identificar especializações regionais.
        
        **🔗 Correlações**: Matriz de dispersão e correlação para identificar relações entre diferentes tipos de resíduos.
        """)