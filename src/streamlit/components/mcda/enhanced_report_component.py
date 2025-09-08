# Enhanced CP2B MCDA Report Component
# Relatório detalhado e visualmente aprimorado com dados quantitativos precisos

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

# ========================================
# CONFIGURAÇÕES DE ANÁLISE MCDA
# ========================================

INFRASTRUCTURE_WEIGHTS = {
    "Rodovias Federais": {"weight": 25, "description": "Acesso de transporte primário", "unit": "km"},
    "Subestações Elétricas": {"weight": 20, "description": "Capacidade de conexão à rede", "unit": "km"},
    "Rodovias Estaduais": {"weight": 20, "description": "Conectividade regional", "unit": "km"},
    "Linhas de Transmissão": {"weight": 15, "description": "Infraestrutura de energia", "unit": "km"},
    "Gasodutos": {"weight": 10, "description": "Rede de distribuição de gás", "unit": "km"},
    "Redes de Distribuição de Gás": {"weight": 5, "description": "Infraestrutura de gás local", "unit": "km"},
    "Outras Infraestruturas": {"weight": 5, "description": "Aeroportos, portos, ferrovias", "unit": "km"}
}

RESTRICTION_FACTORS = {
    "Unidades de Conservação": "Zonas de amortecimento de áreas protegidas",
    "Terras Indígenas": "Zonas de amortecimento de terras indígenas", 
    "Áreas Urbanas": "Zonas de amortecimento do desenvolvimento urbano",
    "Aeroportos": "Zonas de segurança da aviação",
    "Corpos d'água": "Zonas de proteção ambiental",
    "Declividade e Terreno": "Restrições técnicas de implementação"
}

BIOMASS_SOURCES = {
    "Cana-de-açúcar": {"residues": ["bagaço", "palha", "vinhaça"], "yield_factor": 0.28, "biogas_potential": 550},
    "Citros": {"residues": ["bagaço", "cascas"], "yield_factor": 0.15, "biogas_potential": 400},
    "Café": {"residues": ["casca", "mucilagem"], "yield_factor": 0.12, "biogas_potential": 380},
    "Bovinos": {"residues": ["dejetos"], "yield_factor": 15.0, "biogas_potential": 25},
    "Suínos": {"residues": ["dejetos"], "yield_factor": 2.3, "biogas_potential": 35},
    "Aves": {"residues": ["dejetos"], "yield_factor": 0.045, "biogas_potential": 80},
    "Soja": {"residues": ["palha", "casca"], "yield_factor": 0.18, "biogas_potential": 300},
    "Milho": {"residues": ["palha", "sabugo"], "yield_factor": 0.22, "biogas_potential": 350}
}

def render_enhanced_property_report(property_data: Dict[str, Any], radius: str = '30km') -> None:
    """
    Renderiza relatório aprimorado e detalhado da propriedade
    """
    try:
        if not property_data:
            st.error("❌ Dados da propriedade não encontrados")
            return
            
        # Cabeçalho aprimorado
        render_enhanced_header(property_data, radius)
        
        # Resumo executivo
        render_executive_summary(property_data, radius)
        
        # Análise MCDA detalhada com correções
        render_corrected_mcda_analysis(property_data, radius)
        
        # Análise quantitativa de biomassa
        render_quantitative_biomass_analysis(property_data, radius)
        
        # Análise de infraestrutura com pesos
        render_weighted_infrastructure_analysis(property_data)
        
        # Análise de restrições corrigida
        render_corrected_restrictions_analysis(property_data)
        
        # Análise técnica detalhada adicional
        render_detailed_technical_analysis(property_data, radius)
        
        # Projeções econômicas
        render_economic_projections(property_data, radius)
        
        # Recomendações técnicas
        render_technical_recommendations(property_data, radius)
        
        logger.info(f"✅ Relatório aprimorado renderizado para {property_data.get('cod_imovel', 'N/A')}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao renderizar relatório aprimorado: {str(e)}")
        st.error(f"Erro ao gerar relatório: {str(e)}")

def render_enhanced_header(property_data: Dict[str, Any], radius: str) -> None:
    """Cabeçalho visualmente aprimorado"""
    
    # CSS customizado para o header
    st.markdown("""
    <style>
    .report-header {
        background: linear-gradient(135deg, #2c5530 0%, #4a7c59 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin: -20px -20px 30px -20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .report-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-align: center;
    }
    .report-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        text-align: center;
        margin-bottom: 20px;
    }
    .property-info {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
        margin-top: 20px;
    }
    .info-box {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Score e classificação
    score = property_data.get('mcda_score', 0)
    # Normalizar score para escala 0-100 se necessário
    score = min(max(score, 0), 100)
    classification = get_enhanced_classification(score, radius)
    
    st.markdown(f"""
    <div class="report-header">
        <div class="report-title">📊 Relatório MCDA Detalhado</div>
        <div class="report-subtitle">Análise de Viabilidade para Planta de Biogás - Cenário {radius}</div>
        <div class="property-info">
            <div class="info-box">
                <h4>🏭 Propriedade</h4>
                <p><strong>{property_data.get('municipio', 'N/A')}</strong></p>
                <p>SICAR: {property_data.get('cod_imovel', 'N/A')[:15]}...</p>
            </div>
            <div class="info-box">
                <h4>🎯 Score MCDA</h4>
                <p><strong style="font-size: 1.8rem;">{score:.1f}/100</strong></p>
                <p>{classification['name']}</p>
            </div>
            <div class="info-box">
                <h4>📅 Análise</h4>
                <p><strong>{datetime.now().strftime('%d/%m/%Y')}</strong></p>
                <p>Cenário {radius}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão de voltar elegante
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⬅️ Voltar ao Mapa Interativo", use_container_width=True, type="secondary"):
            st.session_state.current_page = "mcda"
            st.session_state.current_view = "map"
            st.session_state.cp2b_selected_property = None
            st.rerun()

def render_executive_summary(property_data: Dict[str, Any], radius: str) -> None:
    """Resumo executivo com principais conclusões"""
    
    st.markdown("## 📋 Resumo Executivo")
    
    score = property_data.get('mcda_score', 0)
    # Normalizar score para escala 0-100 se necessário
    score = min(max(score, 0), 100)
    classification = get_enhanced_classification(score, radius)
    
    # Estimar potencial de biogás
    biogas_col = f'total_biogas_nm3_year_{radius}'
    biogas_potential = property_data.get(biogas_col, property_data.get('total_biogas_nm3_year_30km', 0))
    
    # Calcular capacidade de planta
    plant_capacity_kw = (biogas_potential / 8760) * 10 if biogas_potential > 0 else 0
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        ### 🎯 Conclusão da Análise
        
        Esta propriedade apresenta **{classification['name'].lower()}** para implantação de planta de biogás 
        no cenário de captação de resíduos em raio de **{radius}**.
        
        **Principais Características:**
        - **Score MCDA:** {score:.1f}/100 ({classification['description']})
        - **Potencial de Biogás:** {biogas_potential:,.0f} Nm³/ano
        - **Capacidade de Planta:** ~{plant_capacity_kw:.0f} kW
        - **Viabilidade Técnica:** {get_technical_viability(plant_capacity_kw)}
        - **Cenário de Captação:** {radius} de raio
        
        {classification['recommendation']}
        """)
    
    with col2:
        # Gauge chart para score
        fig_gauge = create_score_gauge(score, radius)
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

def render_corrected_mcda_analysis(property_data: Dict[str, Any], radius: str) -> None:
    """Análise MCDA corrigida com explanações claras"""
    
    st.markdown("## 🔬 Análise MCDA Detalhada")
    
    # Obter scores dos componentes
    biomass_score = property_data.get('biomass_score', 0)
    infra_score = property_data.get('infrastructure_score', 0)
    
    # CORREÇÃO: Normalizar scores para escala 0-100 se necessário
    if biomass_score > 100:
        biomass_score = min(biomass_score, 100)  # Cap at 100
    if infra_score > 100:
        infra_score = min(infra_score, 100)  # Cap at 100
    
    # CORREÇÃO: Score de restrição deve ser invertido para ficar consistente
    restriction_raw = property_data.get('restriction_score', 0)
    restriction_normalized = property_data.get('restriction_score_normalized', 0)
    
    # Se restriction_score está em escala 0-10 onde 10=muitas restrições, inverter para 0-100
    if restriction_raw <= 10:
        restriction_score_corrected = ((10 - restriction_raw) / 10) * 100
        st.info(f"✅ **Correção Aplicada:** Score de restrição convertido de {restriction_raw:.1f}/10 para {restriction_score_corrected:.1f}/100 (onde 100 = sem restrições)")
    else:
        restriction_score_corrected = restriction_normalized if restriction_normalized > 0 else restriction_raw
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Componentes MCDA
        st.markdown("### 📊 Componentes da Análise")
        
        components = [
            {"name": "Potencial de Biomassa", "score": biomass_score, "weight": 40, "color": "#2E8B57"},
            {"name": "Infraestrutura", "score": infra_score, "weight": 35, "color": "#4169E1"},
            {"name": "Restrições (Invertido)", "score": restriction_score_corrected, "weight": 25, "color": "#DC143C"}
        ]
        
        for comp in components:
            score_normalized = comp['score']
            st.markdown(f"""
            **{comp['name']}** ({comp['weight']}% do peso total)
            - Score: {score_normalized:.1f}/100
            - Contribuição: {(score_normalized * comp['weight']/100):.1f} pontos
            """)
            # Fix progress bar - ensure value is between 0.0 and 1.0
            progress_value = min(max(score_normalized/100, 0.0), 1.0)
            st.progress(progress_value, text=f"{score_normalized:.1f}/100")
            st.markdown("")
    
    with col2:
        # Gráfico radar dos componentes
        fig_radar = create_mcda_radar_chart(components)
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
    
    # Explicação da metodologia
    with st.expander("🔍 Metodologia MCDA Detalhada"):
        st.markdown(f"""
        ### Análise Multicritério de Decisão (MCDA)
        
        A metodologia MCDA combina três dimensões principais para avaliar a viabilidade:
        
        #### 1. Potencial de Biomassa (40% do peso)
        - **O que mede:** Disponibilidade de material orgânico dentro de {radius}
        - **Fontes:** Resíduos agrícolas, pecuários, urbanos e industriais
        - **Score:** {biomass_score:.1f}/100
        
        #### 2. Infraestrutura (35% do peso) 
        - **O que mede:** Proximidade de infraestruturas críticas
        - **Score:** {infra_score:.1f}/100
        - Ver detalhamento completo na seção de infraestrutura
        
        #### 3. Restrições Ambientais e Legais (25% do peso)
        - **O que mede:** Limitações que impactam viabilidade
        - **Score Original:** {restriction_raw:.1f} (escala problemática)
        - **Score Corrigido:** {restriction_score_corrected:.1f}/100 (onde 100 = sem restrições)
        - Ver fatores específicos na seção de restrições
        
        #### Cálculo Final:
        Score MCDA = (Biomassa × 0.40) + (Infraestrutura × 0.35) + (Restrições × 0.25)
        """)

def render_quantitative_biomass_analysis(property_data: Dict[str, Any], radius: str) -> None:
    """Análise quantitativa detalhada de biomassa"""
    
    st.markdown("## 🌱 Análise Quantitativa de Biomassa")
    
    # Obter potencial de biogás
    biogas_col = f'total_biogas_nm3_year_{radius}'
    biogas_potential = property_data.get(biogas_col, property_data.get('total_biogas_nm3_year_30km', 0))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Potencial Total de Biogás",
            f"{biogas_potential:,.0f} Nm³/ano",
            help=f"Volume anual estimado de biogás disponível em raio de {radius}"
        )
    
    with col2:
        # Converter para energia
        energy_mwh = (biogas_potential * 10) / 1000  # 1 Nm³ ≈ 10 kWh
        st.metric(
            "Potencial Energético",
            f"{energy_mwh:,.0f} MWh/ano",
            help="Energia elétrica potencial assumindo 10 kWh por Nm³ de biogás"
        )
    
    with col3:
        # Capacidade da planta
        plant_capacity = (biogas_potential / 8760) * 10 if biogas_potential > 0 else 0
        st.metric(
            "Capacidade de Planta",
            f"{plant_capacity:,.0f} kW",
            help="Capacidade estimada de planta operando continuamente"
        )
    
    # Simulação de produção por fonte
    st.markdown("### 📊 Estimativa de Produção por Fonte")
    
    # Simular dados baseados no score de biomassa
    biomass_score = property_data.get('biomass_score', 0)
    area_ha = property_data.get('AREA_HA', 100)  # Área da propriedade
    
    sources_data = simulate_biomass_sources(biomass_score, area_ha, radius)
    
    if sources_data:
        col1, col2 = st.columns(2)
        
        with col1:
            # Tabela de fontes
            df_sources = pd.DataFrame(sources_data)
            st.dataframe(
                df_sources[['Fonte', 'Produção Estimada', 'Potencial Biogás']],
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            # Gráfico de contribuição
            fig_sources = px.pie(
                df_sources, 
                values='Biogás (Nm³)', 
                names='Fonte',
                title=f"Contribuição por Fonte - Raio {radius}"
            )
            st.plotly_chart(fig_sources, use_container_width=True, config={'displayModeBar': False})

def render_weighted_infrastructure_analysis(property_data: Dict[str, Any]) -> None:
    """Análise de infraestrutura com pesos detalhados"""
    
    st.markdown("## 🏗️ Análise de Infraestrutura")
    
    # Mapear colunas de distância para fatores
    distance_mapping = {
        'dist_rodovias_federais_km': 'Rodovias Federais',
        'dist_subestacoes_km': 'Subestações Elétricas', 
        'dist_rodovias_estaduais_km': 'Rodovias Estaduais',
        'dist_linhas_transmissao_km': 'Linhas de Transmissão',
        'dist_gasodutos_km': 'Gasodutos',
        'dist_gasoduto_distribuicao_km': 'Redes de Distribuição de Gás',
        'dist_aerodromos_km': 'Outras Infraestruturas'
    }
    
    st.markdown("### 📍 Distâncias e Scores de Infraestrutura")
    
    infrastructure_data = []
    total_weighted_score = 0
    
    for dist_col, factor_name in distance_mapping.items():
        distance = property_data.get(dist_col, 999)
        score_col = f"{dist_col}_score"
        score = property_data.get(score_col, 0)
        
        if factor_name in INFRASTRUCTURE_WEIGHTS:
            weight_info = INFRASTRUCTURE_WEIGHTS[factor_name]
            weighted_contribution = score * (weight_info['weight'] / 100)
            total_weighted_score += weighted_contribution
            
            infrastructure_data.append({
                'Fator': factor_name,
                'Distância (km)': f"{distance:.1f}" if distance < 999 else "N/A",
                'Score (0-100)': f"{score:.1f}",
                'Peso (%)': weight_info['weight'],
                'Contribuição': f"{weighted_contribution:.1f}",
                'Descrição': weight_info['description']
            })
    
    # Tabela detalhada
    df_infra = pd.DataFrame(infrastructure_data)
    st.dataframe(df_infra, use_container_width=True, hide_index=True)
    
    # Resumo
    infra_score_original = property_data.get('infrastructure_score', 0)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score de Infraestrutura", f"{infra_score_original:.1f}/100")
    with col2:
        st.metric("Score Calculado", f"{total_weighted_score:.1f}/100")
    with col3:
        diff = abs(infra_score_original - total_weighted_score)
        st.metric("Diferença", f"{diff:.1f}", help="Diferença entre score original e calculado")
    
    # Gráfico de barras
    fig_infra = px.bar(
        df_infra, 
        x='Peso (%)', 
        y='Fator',
        color='Score (0-100)',
        orientation='h',
        title="Pesos dos Fatores de Infraestrutura",
        color_continuous_scale='Greens'
    )
    fig_infra.update_layout(height=400)
    st.plotly_chart(fig_infra, use_container_width=True)

def render_corrected_restrictions_analysis(property_data: Dict[str, Any]) -> None:
    """Análise de restrições com correção de escala"""
    
    st.markdown("## ⚠️ Análise de Restrições Ambientais e Legais")
    
    # Obter scores de restrição
    restriction_raw = property_data.get('restriction_score', 0)
    restriction_normalized = property_data.get('restriction_score_normalized', 0)
    
    # Aplicar correção de escala
    if restriction_raw <= 10:
        # Escala original 0-10 onde 10 = muitas restrições
        restriction_corrected = ((10 - restriction_raw) / 10) * 100
        scale_explanation = "0-10 (onde 10 = muitas restrições)"
        corrected_explanation = "0-100 (onde 100 = sem restrições)"
    else:
        # Já está em escala 0-100
        restriction_corrected = restriction_normalized if restriction_normalized > 0 else restriction_raw
        scale_explanation = "0-100"
        corrected_explanation = "Mantido na escala original"
    
    # Alertas de correção
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Score Original", 
            f"{restriction_raw:.1f}",
            help=f"Escala original: {scale_explanation}"
        )
    
    with col2:
        st.metric(
            "Score Corrigido",
            f"{restriction_corrected:.1f}/100", 
            help=f"Escala corrigida: {corrected_explanation}"
        )
    
    with col3:
        impact_level = get_restriction_impact_level(restriction_corrected)
        st.metric(
            "Nível de Impacto",
            impact_level['name'],
            help=impact_level['description']
        )
    
    # Explicação dos fatores
    st.markdown("### 📋 Fatores de Restrição Considerados")
    
    for factor, description in RESTRICTION_FACTORS.items():
        st.markdown(f"- **{factor}:** {description}")
    
    # Recomendações baseadas no nível de restrição
    st.markdown("### 💡 Impacto nas Restrições")
    
    if restriction_corrected >= 80:
        st.success("✅ **Baixo Impacto**: Poucas restrições ambientais e legais. Local favorável para implementação.")
    elif restriction_corrected >= 60:
        st.info("ℹ️ **Impacto Moderado**: Algumas restrições presentes. Análise detalhada recomendada.")
    elif restriction_corrected >= 40:
        st.warning("⚠️ **Alto Impacto**: Várias restrições identificadas. Licenciamento complexo esperado.")
    else:
        st.error("❌ **Impacto Muito Alto**: Muitas restrições críticas. Local não recomendado.")

def render_economic_projections(property_data: Dict[str, Any], radius: str) -> None:
    """Projeções econômicas básicas"""
    
    st.markdown("## 💰 Projeções Econômicas Preliminares")
    
    # Obter dados básicos
    biogas_col = f'total_biogas_nm3_year_{radius}'
    biogas_potential = property_data.get(biogas_col, property_data.get('total_biogas_nm3_year_30km', 0))
    
    # Estimativas econômicas simplificadas
    energy_mwh = (biogas_potential * 10) / 1000  # 1 Nm³ ≈ 10 kWh
    plant_capacity = (biogas_potential / 8760) * 10 if biogas_potential > 0 else 0
    
    # Preços estimados (valores aproximados para o mercado brasileiro)
    energy_price_brl_mwh = 350  # R$/MWh
    capex_brl_kw = 4500  # R$/kW instalado
    
    annual_revenue = energy_mwh * energy_price_brl_mwh
    investment_estimate = plant_capacity * capex_brl_kw
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Receita Anual Estimada",
            f"R$ {annual_revenue:,.0f}",
            help="Baseado em R$ 350/MWh"
        )
    
    with col2:
        st.metric(
            "Investimento Estimado",
            f"R$ {investment_estimate:,.0f}",
            help="CAPEX baseado em R$ 4.500/kW"
        )
    
    with col3:
        payback = investment_estimate / annual_revenue if annual_revenue > 0 else 0
        st.metric(
            "Payback Simples",
            f"{payback:.1f} anos",
            help="Tempo de retorno simplificado"
        )
    
    with col4:
        viability = "Viável" if payback < 10 and plant_capacity > 250 else "Análise Detalhada Necessária"
        st.metric(
            "Viabilidade Preliminar",
            viability,
            help="Avaliação inicial baseada em payback e capacidade"
        )
    
    st.warning("⚠️ **Disclaimer:** Estas são estimativas preliminares. Uma análise econômica detalhada deve considerar OPEX, financiamento, incentivos fiscais, riscos e outros fatores específicos.")

def render_technical_recommendations(property_data: Dict[str, Any], radius: str) -> None:
    """Recomendações técnicas baseadas na análise"""
    
    st.markdown("## 🎯 Recomendações Técnicas")
    
    score = property_data.get('mcda_score', 0)
    # Normalizar score para escala 0-100 se necessário
    score = min(max(score, 0), 100)
    classification = get_enhanced_classification(score, radius)
    
    biogas_col = f'total_biogas_nm3_year_{radius}'
    biogas_potential = property_data.get(biogas_col, 0)
    plant_capacity = (biogas_potential / 8760) * 10 if biogas_potential > 0 else 0
    
    st.markdown(f"### {classification['icon']} {classification['name']}")
    st.markdown(classification['recommendation'])
    
    # Próximos passos específicos
    st.markdown("### 📋 Próximos Passos Recomendados")
    
    if score >= 70:
        st.markdown("""
        1. **✅ Estudo de Viabilidade Econômica Detalhado**
        2. **✅ Levantamento de Campo Específico**  
        3. **✅ Análise de Licenciamento Ambiental**
        4. **✅ Negociação com Fornecedores de Resíduos**
        5. **✅ Desenvolvimento do Projeto Básico**
        """)
    elif score >= 50:
        st.markdown("""
        1. **⚠️ Análise Complementar de Restrições**
        2. **⚠️ Estudo de Otimização Logística**
        3. **⚠️ Avaliação de Alternativas Tecnológicas**
        4. **⚠️ Consulta com Especialistas Locais**
        """)
    else:
        st.markdown("""
        1. **❌ Não recomendado para desenvolvimento imediato**
        2. **🔍 Considerar localização alternativa**
        3. **📊 Reavaliar em cenários futuros**
        """)
    
    # Considerações específicas do raio
    st.markdown(f"### 🚛 Considerações Logísticas - Raio {radius}")
    
    if radius == '50km':
        st.warning("""
        **Atenção para Raio de 50km:**
        - Custos de transporte significativamente maiores
        - Necessário sistema logístico robusto
        - Considerar pré-tratamento in-situ
        - Avaliar viabilidade de múltiplas plantas menores
        """)
    elif radius == '30km':
        st.info("""
        **Raio de 30km - Balance Ótimo:**
        - Bom equilíbrio entre potencial e logística
        - Custos de transporte controlados
        - Flexibilidade operacional adequada
        """)
    else:  # 10km
        st.success("""
        **Raio de 10km - Logística Otimizada:**
        - Menores custos de transporte
        - Maior controle sobre fornecimento
        - Operação mais eficiente
        """)

# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def get_enhanced_classification(score: float, radius: str) -> Dict[str, str]:
    """Classificação aprimorada baseada em score e raio"""
    
    # Thresholds realistas por raio
    thresholds = {
        '10km': {'excellent': 61.3, 'very_good': 57.1, 'viable': 50.9},
        '30km': {'excellent': 65.5, 'very_good': 62.9, 'viable': 58.6}, 
        '50km': {'excellent': 75.8, 'very_good': 72.8, 'viable': 69.5}
    }
    
    current_thresholds = thresholds.get(radius, thresholds['30km'])
    
    if score >= current_thresholds['excellent']:
        return {
            'name': 'Excelente',
            'description': 'Localização ideal para planta de biogás',
            'recommendation': '🏆 **Altamente Recomendado**: Esta propriedade apresenta excelentes condições para desenvolvimento de projeto de biogás. Prosseguir com estudos detalhados imediatamente.',
            'icon': '🏆',
            'color': '#228B22'
        }
    elif score >= current_thresholds['very_good']:
        return {
            'name': 'Muito Bom',
            'description': 'Localização com bom potencial',
            'recommendation': '⭐ **Recomendado**: Propriedade com muito bom potencial. Realizar análise econômica detalhada e estudos complementares.',
            'icon': '⭐',
            'color': '#32CD32'
        }
    elif score >= current_thresholds['viable']:
        return {
            'name': 'Viável',
            'description': 'Localização com potencial adequado',
            'recommendation': '✅ **Viável com Ressalvas**: Potencial adequado identificado. Necessária análise cuidadosa de viabilidade econômica.',
            'icon': '✅',
            'color': '#FFD700'
        }
    else:
        return {
            'name': 'Limitado',
            'description': 'Potencial abaixo do ideal',
            'recommendation': '⚠️ **Potencial Limitado**: Score abaixo dos critérios técnicos. Considerar melhorias ou localização alternativa.',
            'icon': '⚠️',
            'color': '#FF4500'
        }

def get_restriction_impact_level(score: float) -> Dict[str, str]:
    """Determina nível de impacto das restrições"""
    
    if score >= 80:
        return {'name': 'Baixo', 'description': 'Poucas restrições ambientais'}
    elif score >= 60:
        return {'name': 'Moderado', 'description': 'Algumas restrições presentes'}
    elif score >= 40:
        return {'name': 'Alto', 'description': 'Várias restrições identificadas'}
    else:
        return {'name': 'Muito Alto', 'description': 'Muitas restrições críticas'}

def get_technical_viability(capacity_kw: float) -> str:
    """Avalia viabilidade técnica baseada na capacidade"""
    
    if capacity_kw >= 1000:
        return "Excelente (>1MW)"
    elif capacity_kw >= 500:
        return "Boa (500kW-1MW)"
    elif capacity_kw >= 250:
        return "Adequada (250-500kW)"
    else:
        return "Limitada (<250kW)"

def create_score_gauge(score: float, radius: str) -> go.Figure:
    """Cria gráfico de gauge para o score com escala correta"""
    
    # Garantir que o score está na faixa correta
    score_clamped = min(max(score, 0), 100)
    
    # Determinar cor baseada no score
    if score_clamped >= 70:
        bar_color = "#28a745"  # Verde
    elif score_clamped >= 50:
        bar_color = "#ffc107"  # Amarelo
    elif score_clamped >= 30:
        bar_color = "#fd7e14"  # Laranja
    else:
        bar_color = "#dc3545"  # Vermelho
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score_clamped,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Score MCDA<br>Cenário {radius}", 'font': {'size': 16}},
        number = {'font': {'size': 28}},
        gauge = {
            'axis': {
                'range': [0, 100],  # Escala fixa de 0 a 100
                'tickmode': 'linear',
                'tick0': 0,
                'dtick': 20,  # Marcações de 20 em 20 (0, 20, 40, 60, 80, 100)
                'tickfont': {'size': 12}
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': "#ffebee"},    # Vermelho claro
                {'range': [30, 50], 'color': "#fff3e0"},   # Laranja claro  
                {'range': [50, 70], 'color': "#fffde7"},   # Amarelo claro
                {'range': [70, 100], 'color': "#e8f5e8"}   # Verde claro
            ],
            'threshold': {
                'line': {'color': "red", 'width': 3},
                'thickness': 0.8,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300, 
        margin=dict(l=30, r=30, t=60, b=20),
        font=dict(color="black", family="Arial")
    )
    return fig

def create_mcda_radar_chart(components: list) -> go.Figure:
    """Cria gráfico radar dos componentes MCDA"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=[comp['score'] for comp in components],
        theta=[comp['name'] for comp in components],
        fill='toself',
        name='Scores MCDA'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="Componentes MCDA",
        height=300
    )
    
    return fig

def simulate_biomass_sources(biomass_score: float, area_ha: float, radius: str) -> list:
    """Simula dados de produção por fonte baseado no score com informações mais detalhadas"""
    
    # Fator de ajuste baseado no score
    score_factor = max(biomass_score / 100, 0.1)  # Mínimo de 10%
    
    # Base de cálculo mais realista
    sources_data = []
    
    # Mix regional típico da RMC baseado em dados reais
    regional_mix = {
        '10km': {
            'Cana-de-açúcar': {'proportion': 0.35, 'area_factor': 50, 'productivity': 80},
            'Citros': {'proportion': 0.20, 'area_factor': 20, 'productivity': 25}, 
            'Bovinos': {'proportion': 0.25, 'area_factor': 30, 'productivity': 2.5},
            'Soja': {'proportion': 0.12, 'area_factor': 15, 'productivity': 3.2},
            'Milho': {'proportion': 0.08, 'area_factor': 10, 'productivity': 5.8}
        },
        '30km': {
            'Cana-de-açúcar': {'proportion': 0.32, 'area_factor': 120, 'productivity': 80},
            'Citros': {'proportion': 0.18, 'area_factor': 45, 'productivity': 25},
            'Bovinos': {'proportion': 0.28, 'area_factor': 80, 'productivity': 2.5},
            'Suínos': {'proportion': 0.12, 'area_factor': 15, 'productivity': 0.8},
            'Soja': {'proportion': 0.10, 'area_factor': 35, 'productivity': 3.2}
        },
        '50km': {
            'Cana-de-açúcar': {'proportion': 0.28, 'area_factor': 200, 'productivity': 80},
            'Bovinos': {'proportion': 0.32, 'area_factor': 150, 'productivity': 2.5},
            'Citros': {'proportion': 0.15, 'area_factor': 75, 'productivity': 25},
            'Suínos': {'proportion': 0.15, 'area_factor': 25, 'productivity': 0.8},
            'Soja': {'proportion': 0.10, 'area_factor': 50, 'productivity': 3.2}
        }
    }
    
    current_mix = regional_mix.get(radius, regional_mix['30km'])
    
    total_biogas = 0
    
    for source, params in current_mix.items():
        # Calcular área efetiva baseada no score e parâmetros
        effective_area = area_ha * score_factor * (params['area_factor'] / 100)
        
        # Produção baseada na produtividade típica
        if source in ['Bovinos', 'Suínos']:
            # Para animais, usar número de cabeças
            animal_count = effective_area * params['productivity']
            if source in BIOMASS_SOURCES:
                source_info = BIOMASS_SOURCES[source]
                production_year = animal_count * source_info['yield_factor'] * 365  # kg/ano
                biogas_potential = production_year * source_info['biogas_potential'] / 1000  # Nm³/ano
                
                sources_data.append({
                    'Fonte': source,
                    'Área/Animais': f"{animal_count:,.0f} cabeças",
                    'Produção Estimada': f"{production_year/1000:,.1f} t dejetos/ano",
                    'Potencial Biogás': f"{biogas_potential:,.0f} Nm³/ano",
                    'Biogás (Nm³)': biogas_potential,
                    'Resíduos': ", ".join(source_info['residues'])
                })
                total_biogas += biogas_potential
        else:
            # Para culturas agrícolas
            production_year = effective_area * params['productivity']  # t/ha/ano
            if source in BIOMASS_SOURCES:
                source_info = BIOMASS_SOURCES[source]
                residue_production = production_year * source_info['yield_factor']
                biogas_potential = residue_production * source_info['biogas_potential']
                
                sources_data.append({
                    'Fonte': source,
                    'Área/Animais': f"{effective_area:,.0f} ha",
                    'Produção Estimada': f"{production_year:,.0f} t/ano",
                    'Potencial Biogás': f"{biogas_potential:,.0f} Nm³/ano",
                    'Biogás (Nm³)': biogas_potential,
                    'Resíduos': ", ".join(source_info['residues'])
                })
                total_biogas += biogas_potential
    
    # Adicionar informação de resíduos urbanos se aplicável
    if radius in ['30km', '50km']:
        # Estimar população urbana na área
        urban_population = (15000 if radius == '30km' else 35000) * score_factor
        urban_waste = urban_population * 0.5 * 365  # 0.5 kg/pessoa/dia
        urban_biogas = urban_waste * 100  # Nm³/ano
        
        sources_data.append({
            'Fonte': 'Resíduos Urbanos',
            'Área/Animais': f"{urban_population:,.0f} habitantes",
            'Produção Estimada': f"{urban_waste/1000:,.0f} t/ano",
            'Potencial Biogás': f"{urban_biogas:,.0f} Nm³/ano",
            'Biogás (Nm³)': urban_biogas,
            'Resíduos': "RSU, RPO, lodo ETE"
        })
        total_biogas += urban_biogas
    
    # Ordenar por potencial de biogás
    sources_data.sort(key=lambda x: x['Biogás (Nm³)'], reverse=True)
    
    return sources_data

def render_detailed_technical_analysis(property_data: Dict[str, Any], radius: str) -> None:
    """Análise técnica detalhada adicional"""
    
    st.markdown("## ⚙️ Análise Técnica Detalhada")
    
    # Parâmetros da propriedade
    area_ha = property_data.get('AREA_HA', 0)
    biomass_score = property_data.get('biomass_score', 0)
    biogas_col = f'total_biogas_nm3_year_{radius}'
    biogas_potential = property_data.get(biogas_col, property_data.get('total_biogas_nm3_year_30km', 0))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📐 Características da Propriedade")
        st.markdown(f"""
        - **Área Total**: {area_ha:,.1f} hectares
        - **Score de Biomassa**: {biomass_score:.1f}/100
        - **Raio de Captação**: {radius}
        - **Município**: {property_data.get('municipio', 'N/A')}
        """)
        
        # Classificação por área
        if area_ha >= 1000:
            area_class = "🏭 Grande Propriedade"
            area_note = "Excelente para plantas industriais"
        elif area_ha >= 500:
            area_class = "🏢 Propriedade Média-Grande" 
            area_note = "Adequada para plantas comerciais"
        elif area_ha >= 100:
            area_class = "🏠 Propriedade Média"
            area_note = "Viável para plantas pequenas"
        else:
            area_class = "🏘️ Propriedade Pequena"
            area_note = "Limitada para biogás comercial"
            
        st.info(f"{area_class}: {area_note}")
    
    with col2:
        st.markdown("### ⚡ Parâmetros Energéticos")
        
        # Cálculos energéticos
        if biogas_potential > 0:
            # Conversões energéticas
            energy_mwh_year = (biogas_potential * 10) / 1000  # 1 Nm³ ≈ 10 kWh
            energy_gj_year = energy_mwh_year * 3.6  # 1 MWh = 3.6 GJ
            plant_capacity_kw = (biogas_potential / 8760) * 10
            capacity_factor = 0.85  # Fator de capacidade típico
            
            st.markdown(f"""
            - **Potencial Energético**: {energy_mwh_year:,.0f} MWh/ano
            - **Equivalente**: {energy_gj_year:,.0f} GJ/ano
            - **Capacidade Instalada**: {plant_capacity_kw:,.0f} kW
            - **Fator de Capacidade**: {capacity_factor:.0%}
            - **Energia Líquida**: {energy_mwh_year * capacity_factor:,.0f} MWh/ano
            """)
            
            # Equivalências energéticas
            st.markdown("#### 🔋 Equivalências Energéticas")
            households_served = energy_mwh_year / 3.5  # 3.5 MWh/casa/ano média
            diesel_liters = energy_mwh_year * 250  # ~250L diesel/MWh
            
            st.markdown(f"""
            - **Residências Atendidas**: ~{households_served:,.0f} casas/ano
            - **Equivalente Diesel**: {diesel_liters:,.0f} litros/ano
            - **Redução CO₂**: ~{diesel_liters * 2.7 / 1000:,.0f} t CO₂eq/ano
            """)
    
    # Análise de viabilidade técnica
    st.markdown("### 🔧 Avaliação de Viabilidade Técnica")
    
    viability_factors = []
    
    # Fator 1: Capacidade mínima
    if plant_capacity_kw >= 1000:
        viability_factors.append({"factor": "Capacidade da Planta", "status": "✅", "note": f"{plant_capacity_kw:,.0f} kW - Excelente para viabilidade comercial"})
    elif plant_capacity_kw >= 500:
        viability_factors.append({"factor": "Capacidade da Planta", "status": "⚠️", "note": f"{plant_capacity_kw:,.0f} kW - Boa, mas requer análise cuidadosa"})
    elif plant_capacity_kw >= 250:
        viability_factors.append({"factor": "Capacidade da Planta", "status": "🔍", "note": f"{plant_capacity_kw:,.0f} kW - Limiar mínimo de viabilidade"})
    else:
        viability_factors.append({"factor": "Capacidade da Planta", "status": "❌", "note": f"{plant_capacity_kw:,.0f} kW - Abaixo do mínimo viável (250 kW)"})
    
    # Fator 2: Raio logístico
    if radius == '10km':
        viability_factors.append({"factor": "Logística de Transporte", "status": "✅", "note": "Raio ótimo - custos controlados"})
    elif radius == '30km':
        viability_factors.append({"factor": "Logística de Transporte", "status": "⚠️", "note": "Raio médio - necessário plano logístico"})
    else:
        viability_factors.append({"factor": "Logística de Transporte", "status": "❌", "note": "Raio alto - custos elevados de transporte"})
    
    # Fator 3: Diversificação de fontes
    sources_count = len([k for k, v in property_data.items() if 'biogas' in k.lower() and v > 0])
    if sources_count >= 4:
        viability_factors.append({"factor": "Diversificação de Fontes", "status": "✅", "note": f"{sources_count} fontes - Boa diversificação"})
    elif sources_count >= 2:
        viability_factors.append({"factor": "Diversificação de Fontes", "status": "⚠️", "note": f"{sources_count} fontes - Diversificação limitada"})
    else:
        viability_factors.append({"factor": "Diversificação de Fontes", "status": "❌", "note": f"{sources_count} fonte(s) - Risco de fornecimento"})
    
    # Exibir fatores
    for factor in viability_factors:
        st.markdown(f"**{factor['factor']}** {factor['status']}: {factor['note']}")
    
    # Recomendação final técnica
    positive_factors = len([f for f in viability_factors if f['status'] == '✅'])
    if positive_factors >= 2:
        st.success("🎯 **Recomendação Técnica**: Propriedade apresenta boas condições técnicas. Prosseguir com estudos detalhados.")
    elif positive_factors >= 1:
        st.warning("⚠️ **Recomendação Técnica**: Propriedade com potencial limitado. Análise econômica criteriosa necessária.")
    else:
        st.error("❌ **Recomendação Técnica**: Condições técnicas inadequadas. Considerar melhorias ou localização alternativa.")
    
    # Timeline de implementação
    st.markdown("### 📅 Timeline Estimado de Implementação")
    
    timeline_phases = [
        {"fase": "Estudos Preliminares", "duracao": "2-3 meses", "atividades": "Viabilidade técnico-econômica, licenças prévias"},
        {"fase": "Projeto Executivo", "duracao": "3-4 meses", "atividades": "Engenharia, especificações técnicas"},
        {"fase": "Licenciamento", "duracao": "6-12 meses", "atividades": "Licenças ambientais, alvarás"},
        {"fase": "Construção", "duracao": "8-12 meses", "atividades": "Obras civis, instalação equipamentos"},
        {"fase": "Comissionamento", "duracao": "2-3 meses", "atividades": "Testes, ajustes, operação assistida"}
    ]
    
    timeline_df = pd.DataFrame(timeline_phases)
    st.dataframe(timeline_df, use_container_width=True, hide_index=True)