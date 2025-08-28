"""
Dashboard executivo com métricas consolidadas e análises avançadas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Any
import numpy as np


def render_executive_summary_cards(df: pd.DataFrame) -> None:
    """Renderiza cards de resumo executivo"""
    
    if df.empty:
        st.warning("Nenhum dado disponível para o resumo executivo")
        return
    
    # Calcular métricas principais
    total_municipalities = len(df)
    municipalities_with_potential = len(df[df['total_final_nm_ano'] > 0])
    total_potential = df['total_final_nm_ano'].sum()
    avg_potential = df[df['total_final_nm_ano'] > 0]['total_final_nm_ano'].mean() if municipalities_with_potential > 0 else 0
    
    # Potencial por categoria
    agricultural_potential = df['total_agricola_nm_ano'].sum() if 'total_agricola_nm_ano' in df.columns else 0
    livestock_potential = df['total_pecuaria_nm_ano'].sum() if 'total_pecuaria_nm_ano' in df.columns else 0
    
    # Cards principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏛️ Total de Municípios",
            f"{total_municipalities:,}",
            delta=f"{municipalities_with_potential} com potencial",
            help=f"Total de municípios analisados ({municipalities_with_potential} têm potencial de biogás)"
        )
    
    with col2:
        st.metric(
            "⚡ Potencial Total",
            f"{total_potential/1e6:.1f} M Nm³/ano",
            delta=f"{total_potential:,.0f} Nm³/ano",
            help="Potencial total de biogás de todos os municípios"
        )
    
    with col3:
        st.metric(
            "📊 Média Municipal",
            f"{avg_potential:,.0f} Nm³/ano",
            delta=f"Top: {df['total_final_nm_ano'].max():,.0f}",
            help="Média do potencial entre municípios com potencial > 0"
        )
    
    with col4:
        if total_potential > 0:
            agricultural_percent = (agricultural_potential / total_potential) * 100
            st.metric(
                "🌾 Participação Agrícola",
                f"{agricultural_percent:.1f}%",
                delta=f"{agricultural_potential/1e6:.1f} M Nm³/ano",
                help="Percentual do potencial vindo de fontes agrícolas"
            )
        else:
            st.metric("🌾 Participação Agrícola", "0%")


def render_potential_distribution_chart(df: pd.DataFrame) -> None:
    """Gráfico de distribuição do potencial por faixas"""
    
    if df.empty or df['total_final_nm_ano'].sum() == 0:
        st.info("Nenhum dado de potencial para visualizar")
        return
    
    st.subheader("📊 Distribuição do Potencial por Faixas")
    
    # Definir faixas de potencial
    df_with_potential = df[df['total_final_nm_ano'] > 0].copy()
    
    if len(df_with_potential) == 0:
        st.info("Nenhum município com potencial > 0")
        return
    
    # Criar faixas
    bins = [0, 1000, 5000, 10000, 25000, 50000, 100000, float('inf')]
    labels = ['0-1k', '1k-5k', '5k-10k', '10k-25k', '25k-50k', '50k-100k', '100k+']
    
    df_with_potential['faixa_potencial'] = pd.cut(
        df_with_potential['total_final_nm_ano'], 
        bins=bins, 
        labels=labels, 
        include_lowest=True
    )
    
    # Contar municípios por faixa
    faixa_counts = df_with_potential['faixa_potencial'].value_counts().sort_index()
    
    # Calcular potencial total por faixa
    faixa_potential = df_with_potential.groupby('faixa_potencial')['total_final_nm_ano'].sum().sort_index()
    
    # Criar gráfico combinado
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Número de Municípios por Faixa', 'Potencial Total por Faixa (Nm³/ano)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Gráfico de barras - Número de municípios
    fig.add_trace(
        go.Bar(
            x=faixa_counts.index,
            y=faixa_counts.values,
            name="Municípios",
            marker_color='lightblue',
            text=faixa_counts.values,
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # Gráfico de barras - Potencial total
    fig.add_trace(
        go.Bar(
            x=faixa_potential.index,
            y=faixa_potential.values,
            name="Potencial (Nm³/ano)",
            marker_color='darkgreen',
            text=[f"{v/1e6:.1f}M" for v in faixa_potential.values],
            textposition='auto'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        title_text="Distribuição de Potencial de Biogás"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_source_breakdown_chart(df: pd.DataFrame) -> None:
    """Gráfico de breakdown por fonte de biogás"""
    
    st.subheader("🔬 Composição do Potencial por Fonte")
    
    # Definir fontes de biogás
    biogas_sources = {
        'biogas_cana': '🌾 Cana-de-açúcar',
        'biogas_soja': '🌱 Soja',
        'biogas_milho': '🌽 Milho',
        'biogas_cafe': '☕ Café',
        'biogas_citros': '🍊 Citros',
        'biogas_bovino': '🐄 Bovinos',
        'biogas_suinos': '🐷 Suínos',
        'biogas_aves': '🐔 Aves',
        'biogas_piscicultura': '🐟 Piscicultura'
    }
    
    # Calcular totais por fonte
    source_totals = {}
    for source_col, source_label in biogas_sources.items():
        if source_col in df.columns:
            total = df[source_col].sum()
            if total > 0:
                source_totals[source_label] = total
    
    if not source_totals:
        st.info("Nenhum dado de fonte específica disponível")
        return
    
    # Criar gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza
        fig_pie = px.pie(
            values=list(source_totals.values()),
            names=list(source_totals.keys()),
            title="Distribuição por Fonte (%)"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Gráfico de barras horizontais
        fig_bar = px.bar(
            x=list(source_totals.values()),
            y=list(source_totals.keys()),
            orientation='h',
            title="Potencial por Fonte (Nm³/ano)",
            labels={'x': 'Potencial (Nm³/ano)', 'y': 'Fonte'}
        )
        fig_bar.update_traces(
            text=[f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}k" for v in source_totals.values()],
            textposition='auto'
        )
        st.plotly_chart(fig_bar, use_container_width=True)


def render_regional_analysis(df: pd.DataFrame) -> None:
    """Análise regional do potencial"""
    
    st.subheader("🌍 Análise Regional")
    
    if df.empty:
        st.info("Nenhum dado para análise regional")
        return
    
    # Top 20 municípios
    top_municipalities = df.nlargest(20, 'total_final_nm_ano')[['nm_mun', 'total_final_nm_ano', 'total_agricola_nm_ano', 'total_pecuaria_nm_ano']]
    
    if len(top_municipalities) == 0:
        st.info("Nenhum município com potencial para análise")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico dos top municípios
        fig = px.bar(
            top_municipalities,
            x='total_final_nm_ano',
            y='nm_mun',
            orientation='h',
            title="Top 20 Municípios - Potencial Total",
            labels={'total_final_nm_ano': 'Potencial (Nm³/ano)', 'nm_mun': 'Município'},
            text='total_final_nm_ano'
        )
        fig.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='auto'
        )
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Tabela resumo dos top 10
        st.markdown("**Top 10 Resumo:**")
        top_10 = top_municipalities.head(10).copy()
        top_10['total_final_nm_ano'] = top_10['total_final_nm_ano'].apply(lambda x: f"{x:,.0f}")
        top_10['total_agricola_nm_ano'] = top_10['total_agricola_nm_ano'].apply(lambda x: f"{x:,.0f}")
        top_10['total_pecuaria_nm_ano'] = top_10['total_pecuaria_nm_ano'].apply(lambda x: f"{x:,.0f}")
        
        top_10.columns = ['Município', 'Total', 'Agrícola', 'Pecuária']
        st.dataframe(top_10, hide_index=True)


def render_viability_indicators(df: pd.DataFrame) -> None:
    """Indicadores de viabilidade"""
    
    st.subheader("💡 Indicadores de Viabilidade")
    
    if df.empty:
        st.info("Nenhum dado para análise de viabilidade")
        return
    
    # Definir critérios de viabilidade
    high_potential_threshold = 50000  # Nm³/ano
    medium_potential_threshold = 10000  # Nm³/ano
    
    # Classificar municípios
    df_analysis = df.copy()
    df_analysis['viability_class'] = pd.cut(
        df_analysis['total_final_nm_ano'],
        bins=[0, medium_potential_threshold, high_potential_threshold, float('inf')],
        labels=['Baixa', 'Média', 'Alta'],
        include_lowest=True
    )
    
    # Contar por classe
    viability_counts = df_analysis['viability_class'].value_counts()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alta_viabilidade = viability_counts.get('Alta', 0)
        st.metric(
            "🟢 Alta Viabilidade",
            f"{alta_viabilidade}",
            delta=f"> {high_potential_threshold:,} Nm³/ano",
            help=f"Municípios com potencial acima de {high_potential_threshold:,} Nm³/ano"
        )
    
    with col2:
        media_viabilidade = viability_counts.get('Média', 0)
        st.metric(
            "🟡 Média Viabilidade",
            f"{media_viabilidade}",
            delta=f"{medium_potential_threshold:,}-{high_potential_threshold:,} Nm³/ano",
            help=f"Municípios com potencial entre {medium_potential_threshold:,} e {high_potential_threshold:,} Nm³/ano"
        )
    
    with col3:
        baixa_viabilidade = viability_counts.get('Baixa', 0)
        st.metric(
            "🔴 Baixa Viabilidade",
            f"{baixa_viabilidade}",
            delta=f"< {medium_potential_threshold:,} Nm³/ano",
            help=f"Municípios com potencial abaixo de {medium_potential_threshold:,} Nm³/ano"
        )
    
    # Gráfico de viabilidade
    if len(viability_counts) > 0:
        fig = px.pie(
            values=viability_counts.values,
            names=viability_counts.index,
            title="Distribuição por Classe de Viabilidade",
            color_discrete_map={
                'Alta': '#00CC44',
                'Média': '#FFD700',
                'Baixa': '#FF4444'
            }
        )
        st.plotly_chart(fig, use_container_width=True)


def render_executive_dashboard(df: pd.DataFrame) -> None:
    """
    Renderiza dashboard executivo completo
    
    Args:
        df: DataFrame com dados dos municípios
    """
    
    st.title("📈 Dashboard Executivo - Biogás SP")
    st.markdown("---")
    
    if df.empty:
        st.error("Nenhum dado disponível para o dashboard executivo")
        return
    
    # Cards de resumo
    render_executive_summary_cards(df)
    st.markdown("---")
    
    # Layout em colunas para gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        render_potential_distribution_chart(df)
    
    with col2:
        render_source_breakdown_chart(df)
    
    st.markdown("---")
    
    # Análise regional
    render_regional_analysis(df)
    st.markdown("---")
    
    # Indicadores de viabilidade
    render_viability_indicators(df)
    
    # Insights e recomendações
    st.subheader("💡 Insights e Recomendações")
    
    total_potential = df['total_final_nm_ano'].sum()
    municipalities_with_potential = len(df[df['total_final_nm_ano'] > 0])
    
    insights = []
    
    if total_potential > 0:
        # Insight sobre potencial total
        insights.append(
            f"🎯 **Potencial Total:** O estado possui um potencial de {total_potential/1e6:.1f} milhões de Nm³/ano de biogás, "
            f"distribuído em {municipalities_with_potential} municípios."
        )
        
        # Insight sobre concentração
        top_10_potential = df.nlargest(10, 'total_final_nm_ano')['total_final_nm_ano'].sum()
        concentration_percent = (top_10_potential / total_potential) * 100
        insights.append(
            f"📊 **Concentração:** Os top 10 municípios concentram {concentration_percent:.1f}% do potencial total, "
            f"indicando oportunidades de foco em projetos de grande escala."
        )
        
        # Insight sobre fontes
        if 'total_agricola_nm_ano' in df.columns and 'total_pecuaria_nm_ano' in df.columns:
            agri_total = df['total_agricola_nm_ano'].sum()
            pecu_total = df['total_pecuaria_nm_ano'].sum()
            if agri_total + pecu_total > 0:
                agri_percent = (agri_total / (agri_total + pecu_total)) * 100
                insights.append(
                    f"🌾 **Composição:** {agri_percent:.1f}% do potencial vem de fontes agrícolas, "
                    f"{100-agri_percent:.1f}% de fontes pecuárias."
                )
    
    for insight in insights:
        st.markdown(insight)
    
    # Recomendações
    st.markdown("**Recomendações Estratégicas:**")
    recommendations = [
        "🎯 Priorizar projetos nos municípios de alta viabilidade (>50k Nm³/ano)",
        "🤝 Desenvolver clusters regionais para otimizar logística e custos",
        "📈 Implementar projetos piloto em municípios de média viabilidade",
        "🔬 Investir em P&D para melhorar fatores de conversão",
        "📊 Criar programa de incentivos específico por fonte de biomassa"
    ]
    
    for rec in recommendations:
        st.markdown(f"- {rec}")
