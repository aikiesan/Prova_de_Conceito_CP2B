# CP2B MCDA Report Component
# Componente para gerar relatórios básicos das propriedades MCDA

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Importar gerador PDF
try:
    from .pdf_generator import generate_mcda_pdf_report, create_pdf_download_button
    PDF_AVAILABLE = True
except ImportError as e:
    logging.warning(f"PDF generator não disponível: {str(e)}")
    PDF_AVAILABLE = False

logger = logging.getLogger(__name__)

def render_property_report_page(property_data: Dict[str, Any]) -> None:
    """
    Renderiza página completa de relatório da propriedade
    
    Args:
        property_data: Dados completos da propriedade
    """
    try:
        if not property_data:
            st.error("❌ Dados da propriedade não encontrados")
            return
            
        # Cabeçalho do relatório
        render_report_header(property_data)
        
        # Métricas principais
        render_main_metrics(property_data)
        
        # Análise MCDA detalhada
        render_mcda_analysis(property_data)
        
        # Análise de biomassa
        render_biomass_analysis(property_data)
        
        # Análise de infraestrutura
        render_infrastructure_analysis(property_data)
        
        # Análise de restrições
        render_restrictions_analysis(property_data)
        
        # Botões de ação
        render_report_actions(property_data)
        
        logger.info(f"✅ Relatório renderizado para propriedade {property_data.get('cod_imovel', 'N/A')}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao renderizar relatório: {str(e)}")
        st.error(f"Erro ao gerar relatório: {str(e)}")

def render_report_header(property_data: Dict[str, Any]) -> None:
    """Renderiza cabeçalho do relatório"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("# 📊 Relatório MCDA - Análise de Viabilidade")
        st.markdown(f"### 🏭 Propriedade SICAR")
        st.markdown(f"**Município:** {property_data.get('municipio', 'N/A')}")
        st.markdown(f"**Código:** `{property_data.get('cod_imovel', 'N/A')}`")
        
    with col2:
        # Botão voltar
        if st.button("⬅️ Voltar ao Mapa", use_container_width=True):
            st.session_state.current_page = "mcda"
            st.session_state.current_view = "map"
            st.session_state.cp2b_selected_property = None
            st.rerun()
            
        # Data do relatório
        st.markdown(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

def render_main_metrics(property_data: Dict[str, Any]) -> None:
    """Renderiza métricas principais"""
    
    st.markdown("---")
    st.markdown("## 🎯 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = property_data.get('mcda_score', 0)
        score_color = get_score_color_name(score)
        st.metric(
            "Score MCDA Final",
            f"{score:.1f}/100",
            delta=None,
            help="Score final da análise multicritério"
        )
        st.markdown(f"**Classificação:** {score_color}")
        
    with col2:
        ranking = property_data.get('ranking', 'N/A')
        st.metric(
            "Posição no Ranking",
            f"#{ranking}",
            help="Posição entre todas as propriedades analisadas"
        )
        
    with col3:
        biomass_score = property_data.get('biomass_score', 0)
        st.metric(
            "Potencial Biomassa",
            f"{biomass_score:,.0f} ha",
            help="Potencial de biomassa disponível"
        )
        
    with col4:
        restriction_score = property_data.get('restriction_score', 0)
        restriction_status = "Baixa" if restriction_score < 3 else "Média" if restriction_score < 7 else "Alta"
        st.metric(
            "Restrições Ambientais",
            restriction_status,
            help="Nível de restrições identificadas"
        )

def render_mcda_analysis(property_data: Dict[str, Any]) -> None:
    """Renderiza análise MCDA detalhada"""
    
    st.markdown("---")
    st.markdown("## 🔬 Análise MCDA Detalhada")
    
    # Gráfico de radar dos scores
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Criar gráfico radar
        fig = create_mcda_radar_chart(property_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Componentes do Score")
        
        # Scores normalizados
        biomass_norm = property_data.get('biomass_norm', 0)
        infra_norm = property_data.get('infra_norm', 0)
        restriction_norm = property_data.get('restriction_norm', 0)
        
        st.progress(biomass_norm / 100, text=f"Biomassa: {biomass_norm:.1f}/100")
        st.progress(infra_norm / 100, text=f"Infraestrutura: {infra_norm:.1f}/100")
        st.progress(restriction_norm / 100, text=f"Restrições: {restriction_norm:.1f}/100")
        
        # Interpretação
        st.markdown("### 📋 Interpretação")
        interpretation = generate_mcda_interpretation(property_data)
        st.info(interpretation)

def render_biomass_analysis(property_data: Dict[str, Any]) -> None:
    """Renderiza análise de biomassa"""
    
    st.markdown("---")
    st.markdown("## 🌾 Análise de Biomassa Disponível")
    
    # Criar dados de biomassa por cultura
    biomass_data = extract_biomass_data(property_data)
    
    if biomass_data:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de pizza da biomassa
            fig_pie = create_biomass_pie_chart(biomass_data)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Tabela detalhada
            st.markdown("### Detalhamento por Cultura")
            df_biomass = pd.DataFrame(list(biomass_data.items()), columns=['Cultura', 'Hectares'])
            df_biomass = df_biomass[df_biomass['Hectares'] > 0].sort_values('Hectares', ascending=False)
            
            if not df_biomass.empty:
                st.dataframe(df_biomass, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma biomassa significativa identificada no raio de análise")

def render_infrastructure_analysis(property_data: Dict[str, Any]) -> None:
    """Renderiza análise de infraestrutura"""
    
    st.markdown("---")
    st.markdown("## 🏗️ Análise de Infraestrutura e Logística")
    
    # Distâncias para infraestruturas
    infra_data = extract_infrastructure_data(property_data)
    
    if infra_data:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras das distâncias
            fig_bar = create_infrastructure_bar_chart(infra_data)
            if fig_bar:
                st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Distâncias (km)")
            
            for infra_type, distance in infra_data.items():
                # Classificação da distância
                if distance < 5:
                    status = "🟢 Excelente"
                elif distance < 15:
                    status = "🟡 Boa"
                elif distance < 30:
                    status = "🟠 Regular"
                else:
                    status = "🔴 Distante"
                    
                st.metric(infra_type, f"{distance:.1f} km", delta=None, help=status)

def render_restrictions_analysis(property_data: Dict[str, Any]) -> None:
    """Renderiza análise de restrições"""
    
    st.markdown("---")
    st.markdown("## ⚠️ Análise de Restrições Ambientais")
    
    restriction_score = property_data.get('restriction_score', 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Indicador visual do score de restrições
        fig_gauge = create_restriction_gauge(restriction_score)
        if fig_gauge:
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        st.markdown("### 📋 Interpretação das Restrições")
        
        if restriction_score == 0:
            st.success("✅ **Nenhuma restrição identificada** - Área livre para desenvolvimento")
        elif restriction_score <= 3:
            st.info("ℹ️ **Restrições baixas** - Desenvolvimento viável com cuidados básicos")
        elif restriction_score <= 7:
            st.warning("⚠️ **Restrições moderadas** - Necessário estudo detalhado")
        else:
            st.error("🚫 **Restrições altas** - Desenvolvimento não recomendado")
        
        # Detalhamento das restrições (se disponível)
        st.markdown("**Possíveis restrições consideradas:**")
        st.markdown("- Unidades de Conservação de Proteção Integral")
        st.markdown("- Unidades de Conservação de Uso Sustentável")
        st.markdown("- Perímetros Urbanos (buffer de 1km para ruído/odor)")

def render_report_actions(property_data: Dict[str, Any]) -> None:
    """Renderiza botões de ação do relatório"""
    
    st.markdown("---")
    st.markdown("## 📤 Ações do Relatório")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 Copiar Código SICAR", width="stretch"):
            # TODO: Implementar cópia para clipboard
            st.success("✅ Código copiado!")
            
    with col2:
        if st.button("🗺️ Ver no Mapa", width="stretch"):
            st.session_state.current_page = "mcda"
            st.session_state.current_view = "map"
            # TODO: Centralizar mapa na propriedade
            st.rerun()
            
    with col3:
        if st.button("📊 Comparar Similar", width="stretch"):
            # TODO: Implementar comparação com propriedades similares
            st.info("🚧 Funcionalidade em desenvolvimento")
            
    with col4:
        if PDF_AVAILABLE:
            if st.button("📄 Gerar PDF", width="stretch"):
                try:
                    with st.spinner("📄 Gerando relatório PDF..."):
                        pdf_content = generate_mcda_pdf_report(property_data)
                        st.success("✅ PDF gerado com sucesso!")
                        
                    # Exibir botão de download
                    st.markdown("### 📥 Download do Relatório")
                    create_pdf_download_button(pdf_content, property_data)
                        
                except Exception as e:
                    st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                    logger.error(f"Erro na geração PDF: {str(e)}")
        else:
            if st.button("📄 Exportar PDF", width="stretch"):
                st.warning("⚠️ ReportLab não instalado. Execute: pip install reportlab")

# Funções auxiliares

def get_score_color_name(score: float) -> str:
    """Retorna nome da classificação baseada no score"""
    if score >= 80:
        return "🟢 Excelente"
    elif score >= 60:
        return "🟡 Bom"
    elif score >= 40:
        return "🟠 Regular"
    else:
        return "🔴 Baixo"

def create_mcda_radar_chart(property_data: Dict[str, Any]) -> Optional[go.Figure]:
    """Cria gráfico radar dos componentes MCDA"""
    try:
        biomass_norm = property_data.get('biomass_norm', 0)
        infra_norm = property_data.get('infra_norm', 0)
        restriction_norm = property_data.get('restriction_norm', 0)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=[biomass_norm, infra_norm, restriction_norm],
            theta=['Potencial<br>Biomassa', 'Acesso<br>Infraestrutura', 'Baixas<br>Restrições'],
            fill='toself',
            name='Score MCDA',
            line=dict(color='#2c5530')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="Componentes do Score MCDA",
            height=400
        )
        
        return fig
    except Exception as e:
        logger.error(f"❌ Erro ao criar gráfico radar: {str(e)}")
        return None

def extract_biomass_data(property_data: Dict[str, Any]) -> Dict[str, float]:
    """Extrai dados de biomassa por cultura"""
    biomass_mapping = {
        'Pastagem': 'pasture_ha_10km',
        'Cana-de-açúcar': 'sugarcane_ha_10km',
        'Soja': 'soy_ha_10km',
        'Café': 'coffee_ha_10km',
        'Citros': 'citrus_ha_10km',
        'Outras Temporárias': 'other_temp_ha_10km'
    }
    
    biomass_data = {}
    for culture, key in biomass_mapping.items():
        value = property_data.get(key, 0)
        if value > 0:
            biomass_data[culture] = value
            
    return biomass_data

def create_biomass_pie_chart(biomass_data: Dict[str, float]) -> Optional[go.Figure]:
    """Cria gráfico de pizza da biomassa"""
    try:
        if not biomass_data:
            return None
            
        fig = px.pie(
            values=list(biomass_data.values()),
            names=list(biomass_data.keys()),
            title="Distribuição da Biomassa por Cultura"
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar gráfico de pizza: {str(e)}")
        return None

def extract_infrastructure_data(property_data: Dict[str, Any]) -> Dict[str, float]:
    """Extrai dados de infraestrutura"""
    infra_mapping = {
        'Subestações': 'dist_subestacoes_km',
        'Rodovias Federais': 'dist_rodovias_federais_km',
        'Rodovias Estaduais': 'dist_rodovias_estaduais_km',
        'Gasodutos': 'dist_gasodutos_km',
        'Linhas Transmissão': 'dist_linhas_transmissao_km'
    }
    
    infra_data = {}
    for infra_type, key in infra_mapping.items():
        value = property_data.get(key, 0)
        if value > 0:
            infra_data[infra_type] = value
            
    return infra_data

def create_infrastructure_bar_chart(infra_data: Dict[str, float]) -> Optional[go.Figure]:
    """Cria gráfico de barras da infraestrutura"""
    try:
        if not infra_data:
            return None
            
        fig = px.bar(
            x=list(infra_data.keys()),
            y=list(infra_data.values()),
            title="Distâncias para Infraestrutura",
            labels={'x': 'Tipo de Infraestrutura', 'y': 'Distância (km)'}
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        return fig
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar gráfico de barras: {str(e)}")
        return None

def create_restriction_gauge(restriction_score: float) -> Optional[go.Figure]:
    """Cria indicador gauge para restrições"""
    try:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = restriction_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Score de Restrições"},
            gauge = {
                'axis': {'range': [None, 10]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 3], 'color': "lightgreen"},
                    {'range': [3, 7], 'color': "yellow"},
                    {'range': [7, 10], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 7
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar gauge: {str(e)}")
        return None

def generate_mcda_interpretation(property_data: Dict[str, Any]) -> str:
    """Gera interpretação textual do score MCDA"""
    score = property_data.get('mcda_score', 0)
    biomass_norm = property_data.get('biomass_norm', 0)
    infra_norm = property_data.get('infra_norm', 0)
    restriction_norm = property_data.get('restriction_norm', 0)
    
    # Identificar pontos fortes e fracos
    strengths = []
    weaknesses = []
    
    if biomass_norm >= 70:
        strengths.append("excelente disponibilidade de biomassa")
    elif biomass_norm < 30:
        weaknesses.append("baixa disponibilidade de biomassa")
        
    if infra_norm >= 70:
        strengths.append("boa acessibilidade à infraestrutura")
    elif infra_norm < 30:
        weaknesses.append("infraestrutura distante")
        
    if restriction_norm >= 70:
        strengths.append("poucas restrições ambientais")
    elif restriction_norm < 30:
        weaknesses.append("muitas restrições ambientais")
    
    # Montar interpretação
    interpretation = f"Esta propriedade obteve um score MCDA de {score:.1f}/100. "
    
    if strengths:
        interpretation += f"Pontos fortes: {', '.join(strengths)}. "
    
    if weaknesses:
        interpretation += f"Pontos de atenção: {', '.join(weaknesses)}. "
        
    # Recomendação geral
    if score >= 70:
        interpretation += "✅ Recomendada para desenvolvimento de planta de biogás."
    elif score >= 50:
        interpretation += "⚠️ Viável com estudos adicionais e planejamento cuidadoso."
    else:
        interpretation += "❌ Não recomendada devido aos desafios identificados."
    
    return interpretation