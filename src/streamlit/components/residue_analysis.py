"""
Dashboard de Análise Detalhada por Resíduos - CP2B
Sistema especializado para análise comparativa de diferentes tipos de resíduos e potencial de biogás
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import logging
from .comparative_charts import render_comparative_analysis_dashboard

logger = logging.getLogger(__name__)

class ResidueAnalyzer:
    """Analisador especializado para diferentes tipos de resíduos"""
    
    # Mapeamento detalhado dos resíduos
    RESIDUE_MAPPING = {
        'biogas_cana_nm_ano': {
            'label': 'Cana-de-açúcar',
            'category': 'Agrícola',
            'icon': '🌾',
            'color': '#10b981',
            'description': 'Bagaço e palha da cana-de-açúcar',
            'unit': 'Nm³/ano',
            'typical_range': (0, 50000)
        },
        'biogas_soja_nm_ano': {
            'label': 'Soja',
            'category': 'Agrícola',
            'icon': '🌱',
            'color': '#059669',
            'description': 'Resíduos da cultura da soja',
            'unit': 'Nm³/ano',
            'typical_range': (0, 30000)
        },
        'biogas_milho_nm_ano': {
            'label': 'Milho',
            'category': 'Agrícola',
            'icon': '🌽',
            'color': '#fbbf24',
            'description': 'Sabugo, palha e restos da cultura do milho',
            'unit': 'Nm³/ano',
            'typical_range': (0, 25000)
        },
        'biogas_cafe_nm_ano': {
            'label': 'Café',
            'category': 'Agrícola',
            'icon': '☕',
            'color': '#92400e',
            'description': 'Polpa, casca e mucilagem do café',
            'unit': 'Nm³/ano',
            'typical_range': (0, 15000)
        },
        'biogas_citros_nm_ano': {
            'label': 'Citros',
            'category': 'Agrícola',
            'icon': '🍊',
            'color': '#f59e0b',
            'description': 'Bagaço de laranja, limão e outros cítricos',
            'unit': 'Nm³/ano',
            'typical_range': (0, 20000)
        },
        'biogas_bovinos_nm_ano': {
            'label': 'Bovinos',
            'category': 'Pecuária',
            'icon': '🐄',
            'color': '#dc2626',
            'description': 'Esterco e dejetos de bovinos',
            'unit': 'Nm³/ano',
            'typical_range': (0, 100000)
        },
        'biogas_suino_nm_ano': {
            'label': 'Suínos',
            'category': 'Pecuária',
            'icon': '🐷',
            'color': '#be185d',
            'description': 'Dejetos de suinocultura',
            'unit': 'Nm³/ano',
            'typical_range': (0, 80000)
        },
        'biogas_aves_nm_ano': {
            'label': 'Aves',
            'category': 'Pecuária',
            'icon': '🐔',
            'color': '#c2410c',
            'description': 'Cama de frango e dejetos avícolas',
            'unit': 'Nm³/ano',
            'typical_range': (0, 60000)
        },
        'biogas_piscicultura_nm_ano': {
            'label': 'Piscicultura',
            'category': 'Pecuária',
            'icon': '🐟',
            'color': '#0ea5e9',
            'description': 'Resíduos da aquicultura e piscicultura',
            'unit': 'Nm³/ano',
            'typical_range': (0, 15000)
        },
        'rsu_potencial_nm_habitante_ano': {
            'label': 'RSU (Resíduos Sólidos Urbanos)',
            'category': 'Urbano',
            'icon': '🗑️',
            'color': '#6366f1',
            'description': 'Lixo orgânico doméstico e comercial',
            'unit': 'Nm³/hab/ano',
            'typical_range': (0, 50)
        },
        'rpo_potencial_nm_habitante_ano': {
            'label': 'RPO (Resíduos de Poda e Orgânicos)',
            'category': 'Urbano',
            'icon': '🌿',
            'color': '#16a34a',
            'description': 'Resíduos de poda urbana e orgânicos',
            'unit': 'Nm³/hab/ano',
            'typical_range': (0, 30)
        }
    }

def render_residue_overview_cards(df: pd.DataFrame) -> None:
    """Renderiza cards de visão geral por categoria de resíduo"""
    
    st.subheader("📊 Visão Geral por Categoria")
    
    if df.empty:
        st.warning("Nenhum dado disponível para análise")
        return
    
    # Calcular totais por categoria
    agricultural_total = sum([
        df.get('biogas_cana_nm_ano', 0).sum(),
        df.get('biogas_soja_nm_ano', 0).sum(),
        df.get('biogas_milho_nm_ano', 0).sum(),
        df.get('biogas_cafe_nm_ano', 0).sum(),
        df.get('biogas_citros_nm_ano', 0).sum()
    ])
    
    livestock_total = sum([
        df.get('biogas_bovinos_nm_ano', 0).sum(),
        df.get('biogas_suino_nm_ano', 0).sum(),
        df.get('biogas_aves_nm_ano', 0).sum(),
        df.get('biogas_piscicultura_nm_ano', 0).sum()
    ])
    
    urban_total = sum([
        df.get('rsu_potencial_nm_habitante_ano', 0).sum(),
        df.get('rpo_potencial_nm_habitante_ano', 0).sum()
    ])
    
    total_potential = agricultural_total + livestock_total + urban_total
    
    # Cards por categoria
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌾 Setor Agrícola",
            f"{agricultural_total / 1_000_000:.1f}M Nm³/ano",
            delta=f"{(agricultural_total / total_potential * 100) if total_potential > 0 else 0:.1f}% do total",
            help="Total de biogás de todos os resíduos agrícolas"
        )
    
    with col2:
        st.metric(
            "🐄 Setor Pecuário",
            f"{livestock_total / 1_000_000:.1f}M Nm³/ano",
            delta=f"{(livestock_total / total_potential * 100) if total_potential > 0 else 0:.1f}% do total",
            help="Total de biogás de todos os resíduos pecuários"
        )
    
    with col3:
        st.metric(
            "🏙️ Setor Urbano",
            f"{urban_total / 1_000:.0f}k Nm³/ano",
            delta=f"{(urban_total / total_potential * 100) if total_potential > 0 else 0:.1f}% do total",
            help="Total de biogás de resíduos urbanos (RSU + RPO)"
        )
    
    with col4:
        st.metric(
            "🎯 Potencial Total",
            f"{total_potential / 1_000_000:.1f}M Nm³/ano",
            help="Soma de todos os resíduos analisados"
        )

def render_residue_comparison_chart(df: pd.DataFrame) -> None:
    """Renderiza gráfico de comparação entre diferentes resíduos"""
    
    st.subheader("🔬 Comparação Detalhada por Tipo de Resíduo")
    
    if df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    # Preparar dados para visualização
    residue_data = []
    analyzer = ResidueAnalyzer()
    
    for residue_key, residue_info in analyzer.RESIDUE_MAPPING.items():
        if residue_key in df.columns:
            total_potential = df[residue_key].sum()
            municipalities_with_potential = (df[residue_key] > 0).sum()
            avg_potential = df[df[residue_key] > 0][residue_key].mean() if municipalities_with_potential > 0 else 0
            max_potential = df[residue_key].max()
            
            residue_data.append({
                'residue': residue_info['label'],
                'category': residue_info['category'],
                'icon': residue_info['icon'],
                'color': residue_info['color'],
                'total_potential': total_potential,
                'municipalities_count': municipalities_with_potential,
                'avg_potential': avg_potential,
                'max_potential': max_potential,
                'unit': residue_info['unit']
            })
    
    if not residue_data:
        st.error("Nenhum dado de resíduos encontrado")
        return
    
    residue_df = pd.DataFrame(residue_data)
    
    # Controles de visualização
    col1, col2 = st.columns([2, 1])
    
    with col1:
        chart_type = st.selectbox(
            "Tipo de Análise:",
            ["Potencial Total", "Número de Municípios", "Potencial Médio", "Potencial Máximo"],
            help="Escolha o aspecto a ser analisado"
        )
    
    with col2:
        show_category_colors = st.checkbox(
            "Cores por Categoria",
            value=True,
            help="Agrupar cores por categoria (Agrícola, Pecuária, Urbano)"
        )
    
    # Mapear tipo de análise para coluna
    analysis_mapping = {
        "Potencial Total": "total_potential",
        "Número de Municípios": "municipalities_count", 
        "Potencial Médio": "avg_potential",
        "Potencial Máximo": "max_potential"
    }
    
    y_column = analysis_mapping[chart_type]
    
    # Criar gráfico
    if show_category_colors:
        # Definir cores por categoria
        category_colors = {
            'Agrícola': '#10b981',
            'Pecuária': '#dc2626', 
            'Urbano': '#6366f1'
        }
        
        fig = px.bar(
            residue_df,
            x='residue',
            y=y_column,
            color='category',
            color_discrete_map=category_colors,
            title=f"Análise por Resíduo: {chart_type}",
            labels={
                'residue': 'Tipo de Resíduo',
                y_column: chart_type,
                'category': 'Categoria'
            }
        )
    else:
        # Usar cores específicas de cada resíduo
        fig = px.bar(
            residue_df,
            x='residue',
            y=y_column,
            color='residue',
            color_discrete_sequence=residue_df['color'].tolist(),
            title=f"Análise por Resíduo: {chart_type}"
        )
        
        # Remover legenda quando usar cores individuais
        fig.update_layout(showlegend=False)
    
    # Personalizar layout
    fig.update_layout(
        xaxis_title="Tipo de Resíduo",
        yaxis_title=chart_type,
        height=500,
        xaxis_tickangle=-45
    )
    
    # Adicionar anotações com ícones (texto)
    for i, row in residue_df.iterrows():
        fig.add_annotation(
            x=row['residue'],
            y=row[y_column] + (row[y_column] * 0.05),  # 5% acima da barra
            text=row['icon'],
            showarrow=False,
            font=dict(size=20)
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de detalhes
    with st.expander("📋 Detalhes Numéricos"):
        display_df = residue_df.copy()
        
        # Formatar valores
        display_df['total_potential'] = display_df['total_potential'].apply(lambda x: f"{x:,.0f}")
        display_df['avg_potential'] = display_df['avg_potential'].apply(lambda x: f"{x:,.0f}")
        display_df['max_potential'] = display_df['max_potential'].apply(lambda x: f"{x:,.0f}")
        
        # Renomear colunas
        display_df = display_df.rename(columns={
            'residue': 'Resíduo',
            'category': 'Categoria', 
            'total_potential': 'Potencial Total',
            'municipalities_count': 'Municípios',
            'avg_potential': 'Média',
            'max_potential': 'Máximo'
        })
        
        st.dataframe(
            display_df[['Resíduo', 'Categoria', 'Potencial Total', 'Municípios', 'Média', 'Máximo']],
            hide_index=True
        )

def render_geographical_residue_distribution(df: pd.DataFrame) -> None:
    """Renderiza análise da distribuição geográfica por resíduo"""
    
    st.subheader("🗺️ Distribuição Geográfica por Resíduo")
    
    if df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    analyzer = ResidueAnalyzer()
    
    # Seleção de resíduo para análise
    residue_options = {}
    for key, info in analyzer.RESIDUE_MAPPING.items():
        if key in df.columns and df[key].sum() > 0:
            residue_options[key] = f"{info['icon']} {info['label']}"
    
    if not residue_options:
        st.error("Nenhum resíduo com dados disponível")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_residue = st.selectbox(
            "Selecione o Resíduo para Análise:",
            list(residue_options.keys()),
            format_func=lambda x: residue_options[x],
            help="Análise geográfica detalhada do resíduo selecionado"
        )
    
    with col2:
        show_top_n = st.slider(
            "Top Municípios:",
            min_value=5,
            max_value=50,
            value=15,
            help="Número de municípios com maior potencial"
        )
    
    if selected_residue:
        residue_info = analyzer.RESIDUE_MAPPING[selected_residue]
        
        # Filtrar e ordenar dados
        residue_data = df[df[selected_residue] > 0].copy()
        residue_data = residue_data.nlargest(show_top_n, selected_residue)
        
        if not residue_data.empty:
            # Gráfico de barras horizontais
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                y=residue_data['nm_mun'],
                x=residue_data[selected_residue],
                orientation='h',
                marker_color=residue_info['color'],
                text=residue_data[selected_residue].apply(lambda x: f"{x:,.0f}"),
                textposition='outside'
            ))
            
            fig.update_layout(
                title=f"{residue_info['icon']} Top {show_top_n} Municípios - {residue_info['label']}",
                xaxis_title=f"Potencial de Biogás ({residue_info['unit']})",
                yaxis_title="Municípios",
                height=max(400, show_top_n * 25),
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas do resíduo selecionado
            col1, col2, col3, col4 = st.columns(4)
            
            total_municipalities = len(df[df[selected_residue] > 0])
            total_potential = df[selected_residue].sum()
            avg_potential = df[df[selected_residue] > 0][selected_residue].mean()
            max_municipality = df.loc[df[selected_residue].idxmax()]
            
            with col1:
                st.metric(
                    "🏛️ Municípios",
                    f"{total_municipalities}",
                    help=f"Municípios com potencial de {residue_info['label']}"
                )
            
            with col2:
                st.metric(
                    "⚡ Total",
                    f"{total_potential:,.0f}",
                    help=f"Potencial total em {residue_info['unit']}"
                )
            
            with col3:
                st.metric(
                    "📊 Média",
                    f"{avg_potential:,.0f}",
                    help="Potencial médio por município"
                )
            
            with col4:
                st.metric(
                    "🥇 Líder",
                    max_municipality['nm_mun'],
                    delta=f"{max_municipality[selected_residue]:,.0f}",
                    help="Município com maior potencial"
                )
        
        else:
            st.info(f"Nenhum município tem potencial significativo para {residue_info['label']}")

def render_residue_correlation_analysis(df: pd.DataFrame) -> None:
    """Renderiza análise de correlação entre diferentes resíduos"""
    
    st.subheader("🔗 Análise de Correlação entre Resíduos")
    
    if df.empty:
        st.warning("Nenhum dado disponível")
        return
    
    analyzer = ResidueAnalyzer()
    
    # Preparar dados de correlação
    residue_columns = []
    residue_labels = []
    
    for key, info in analyzer.RESIDUE_MAPPING.items():
        if key in df.columns and df[key].sum() > 0:
            residue_columns.append(key)
            residue_labels.append(info['label'])
    
    if len(residue_columns) < 2:
        st.warning("São necessários pelo menos 2 tipos de resíduos para análise de correlação")
        return
    
    # Calcular matriz de correlação
    correlation_data = df[residue_columns].corr()
    
    # Renomear índices e colunas para labels legíveis
    correlation_data.index = residue_labels
    correlation_data.columns = residue_labels
    
    # Gráfico de heatmap
    fig = px.imshow(
        correlation_data,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        title="Matriz de Correlação entre Tipos de Resíduos",
        labels={'color': 'Correlação'}
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Tipos de Resíduos",
        yaxis_title="Tipos de Resíduos"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretação das correlações
    with st.expander("📖 Como Interpretar"):
        st.markdown("""
        **Interpretação da Matriz de Correlação:**
        
        - **Valores próximos a +1.0**: Correlação positiva forte (quando um aumenta, o outro também)
        - **Valores próximos a -1.0**: Correlação negativa forte (quando um aumenta, o outro diminui)
        - **Valores próximos a 0.0**: Sem correlação significativa
        
        **Insights Úteis:**
        - Correlações altas entre resíduos agrícolas podem indicar regiões especializadas
        - Correlações entre pecuária e agricultura podem mostrar sistemas integrados
        - Baixa correlação urbano vs. rural é esperada devido a diferentes características municipais
        """)
    
    # Top correlações
    st.subheader("🔍 Principais Correlações")
    
    # Extrair correlações (excluindo diagonal)
    correlations = []
    for i in range(len(correlation_data.index)):
        for j in range(i+1, len(correlation_data.columns)):
            correlations.append({
                'Resíduo 1': correlation_data.index[i],
                'Resíduo 2': correlation_data.columns[j],
                'Correlação': correlation_data.iloc[i, j],
                'Força': abs(correlation_data.iloc[i, j])
            })
    
    # Ordenar por força da correlação
    correlations_df = pd.DataFrame(correlations)
    correlations_df = correlations_df.sort_values('Força', ascending=False)
    
    # Mostrar top 10
    top_correlations = correlations_df.head(10).copy()
    top_correlations['Correlação'] = top_correlations['Correlação'].apply(lambda x: f"{x:.3f}")
    top_correlations = top_correlations.drop('Força', axis=1)
    
    st.dataframe(top_correlations, hide_index=True)

def render_residue_analysis_dashboard(df: pd.DataFrame) -> None:
    """Dashboard principal de análise de resíduos"""
    
    st.header("🔬 Análise Detalhada por Resíduos")
    st.markdown("---")
    
    if df.empty:
        st.error("❌ Nenhum dado disponível para análise")
        st.info("Verifique os filtros aplicados ou carregue dados na aplicação principal")
        return
    
    # Verificar se há dados de resíduos
    analyzer = ResidueAnalyzer()
    has_residue_data = any(
        col in df.columns and df[col].sum() > 0 
        for col in analyzer.RESIDUE_MAPPING.keys()
    )
    
    if not has_residue_data:
        st.warning("⚠️ Nenhum dado específico de resíduos encontrado nos dados fornecidos")
        return
    
    # Layout em tabs para diferentes análises
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral", 
        "🔬 Comparação Detalhada", 
        "🗺️ Distribuição Geográfica",
        "🔗 Análise de Correlação",
        "📈 Visualizações Avançadas"
    ])
    
    with tab1:
        render_residue_overview_cards(df)
        st.markdown("---")
        
        # Informações adicionais sobre os resíduos
        st.subheader("ℹ️ Informações sobre os Resíduos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🌾 Resíduos Agrícolas:**
            - Cana-de-açúcar: Bagaço e palha
            - Soja: Restos de cultura
            - Milho: Sabugo e palha
            - Café: Polpa e casca
            - Citros: Bagaço de frutas
            """)
        
        with col2:
            st.markdown("""
            **🐄 Resíduos Pecuários:**
            - Bovinos: Esterco
            - Suínos: Dejetos líquidos
            - Aves: Cama de frango
            - Piscicultura: Resíduos aquícolas
            """)
        
        with col3:
            st.markdown("""
            **🏙️ Resíduos Urbanos:**
            - RSU: Lixo orgânico doméstico
            - RPO: Poda urbana e orgânicos
            
            *Unidade diferente: Nm³/hab/ano*
            """)
    
    with tab2:
        render_residue_comparison_chart(df)
    
    with tab3:
        render_geographical_residue_distribution(df)
    
    with tab4:
        render_residue_correlation_analysis(df)
    
    with tab5:
        render_comparative_analysis_dashboard(df)
    
    # Footer com informações técnicas
    st.markdown("---")
    with st.expander("🔧 Informações Técnicas"):
        st.markdown("""
        **Metodologia de Análise:**
        - Dados processados a partir do banco Excel original
        - Cálculos baseados em fatores de conversão específicos por resíduo
        - Análises estatísticas descritivas e correlacionais
        
        **Limitações:**
        - Dados dependem da qualidade das fontes municipais
        - Fatores de conversão podem variar regionalmente
        - Análise não considera aspectos logísticos e econômicos
        """)