# Simple CP2B Property Report Component
# Relatório simples e funcional com foco em objetividade e UX

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def render_simple_property_report(property_data: Dict[str, Any], radius: str = '30km') -> None:
    """Relatório completo e bem estruturado da propriedade"""
    try:
        if not property_data:
            st.error("❌ Dados da propriedade não encontrados")
            return

        # Header com estilo
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2c5530 0%, #4a7c59 100%); 
                    color: white; padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='margin: 0; color: white;'>📊 Relatório de Viabilidade - Planta de Biogás</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Info básica em cards
        cod_imovel = property_data.get('cod_imovel', 'N/A')
        area_ha = property_data.get('AREA_HA', 0)
        municipio = property_data.get('municipio', 'N/A')
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📍 Código", cod_imovel)
        with col2:
            st.metric("🏘️ Município", municipio)
        with col3:
            st.metric("📐 Área", f"{area_ha:.1f} ha")
        with col4:
            st.metric("🎯 Cenário", radius)
        
        st.markdown("---")
        
        # Scores principais com gráficos
        st.markdown("## 🎯 Análise MCDA Completa")
        
        # Obter e processar scores
        mcda_score = min(max(property_data.get('mcda_score', 0), 0), 100)
        biomass_score = min(max(property_data.get('biomass_score', 0), 0), 100)
        infra_score = property_data.get('infrastructure_score', 0)
        restriction_score = property_data.get('restriction_score', 0)
        
        # Recalcular score de infraestrutura se necessário (processo silencioso)
        if infra_score == 0:
            distances = {
                "rodovias_federais": property_data.get('dist_rodovias_federais_km', 999),
                "rodovias_estaduais": property_data.get('dist_rodovias_estaduais_km', 999),
                "subestacoes": property_data.get('dist_subestacoes_km', 999),
                "gasodutos": property_data.get('dist_gasodutos_km', 999),
                "linhas_transmissao": property_data.get('dist_linhas_transmissao_km', 999)
            }
            
            weights = {
                "rodovias_federais": 0.25,
                "rodovias_estaduais": 0.20,
                "subestacoes": 0.20,
                "gasodutos": 0.20,
                "linhas_transmissao": 0.15
            }
            
            total_score = 0
            valid_items = 0
            
            for infra_type, distance in distances.items():
                if distance > 0 and distance < 200:
                    individual_score = max(0, min(100, 100 * (1 - distance / 50)))
                    weighted_score = individual_score * weights[infra_type]
                    total_score += weighted_score
                    valid_items += 1
            
            if valid_items > 0:
                infra_score = total_score
        
        infra_score = min(max(infra_score, 0), 100)
        
        # Corrigir restriction score
        if restriction_score <= 10:
            restriction_final = ((10 - restriction_score) / 10) * 100
        else:
            restriction_final = min(max(100 - restriction_score, 0), 100)
        
        # Gráfico de radar dos scores
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Dados para o gráfico radar
            categories = ['Biomassa', 'Infraestrutura', 'Restrições<br>(Invertidas)', 'Score MCDA']
            values = [biomass_score, infra_score, restriction_final, mcda_score]
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Scores',
                line_color='rgb(46, 139, 87)',
                fillcolor='rgba(46, 139, 87, 0.3)'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], dtick=20)
                ),
                showlegend=False,
                title="Análise Radar dos Componentes MCDA",
                height=400
            )
            
            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            # Métricas principais
            st.metric("🎯 Score MCDA", f"{mcda_score:.1f}/100", delta=None)
            st.metric("🌱 Biomassa", f"{biomass_score:.1f}/100", delta=None)
            st.metric("🏗️ Infraestrutura", f"{infra_score:.1f}/100", delta=None)
            st.metric("🛡️ Restrições", f"{restriction_final:.1f}/100", delta=None)
        
        # Classificação com gauge
        st.markdown("## 📈 Classificação de Viabilidade")
        
        if mcda_score >= 70:
            classification = "🟢 **EXCELENTE**"
            description = "Altamente recomendado para implementação"
            color = "#28a745"
        elif mcda_score >= 60:
            classification = "🟡 **BOA**"
            description = "Recomendado com algumas ressalvas técnicas"
            color = "#ffc107"
        elif mcda_score >= 50:
            classification = "🟠 **MODERADA**"
            description = "Viável com investimentos em infraestrutura"
            color = "#fd7e14"
        else:
            classification = "🔴 **BAIXA**"
            description = "Não recomendado nas condições atuais"
            color = "#dc3545"
            
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Gauge do score
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = mcda_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"Score MCDA<br>({radius})"},
                gauge = {
                    'axis': {'range': [0, 100], 'dtick': 20},
                    'bar': {'color': color, 'thickness': 0.3},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 50], 'color': "#ffe6e6"},
                        {'range': [50, 70], 'color': "#fff3cd"},
                        {'range': [70, 100], 'color': "#d4edda"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
            
        with col2:
            st.markdown(f"### {classification}")
            st.markdown(f"**{description}**")
            
            # Progress bars para componentes
            st.markdown("**Contribuições por Componente:**")
            components = [
                ("Biomassa (40%)", biomass_score, "#2E8B57"),
                ("Infraestrutura (35%)", infra_score, "#4169E1"),
                ("Restrições (25%)", restriction_final, "#DC143C")
            ]
            
            for name, score, color in components:
                st.markdown(f"**{name}:** {score:.1f}/100")
                progress_val = min(max(score/100, 0.0), 1.0)
                st.progress(progress_val)
        
        st.markdown("---")
        
        # Disponibilidade de resíduos
        st.markdown("## 🌾 Disponibilidade de Resíduos")
        
        # Estimativas de resíduos baseadas na área da propriedade
        # Valores médios para região de Campinas
        residues_data = {
            "🌽 Cana-de-açúcar": {
                "area_pct": 0.40,  # 40% da propriedade
                "yield_ton_ha": 85,  # toneladas/ha
                "residue_pct": 0.28  # 28% de resíduos
            },
            "🍊 Citros": {
                "area_pct": 0.15,
                "yield_ton_ha": 25,
                "residue_pct": 0.15
            },
            "🐄 Bovinos": {
                "area_pct": 0.25,  # área de pastagem
                "animals_per_ha": 1.5,
                "residue_ton_animal": 15
            },
            "🌽 Milho/Soja": {
                "area_pct": 0.20,
                "yield_ton_ha": 8,
                "residue_pct": 0.22
            }
        }
        
        # Calcular resíduos primeiro (para uso global)
        residue_summary = []
        total_residues = 0
        
        for source, params in residues_data.items():
            source_area = area_ha * params['area_pct']
            
            if "animals_per_ha" in params:  # Pecuária
                animals = source_area * params['animals_per_ha']
                residue_ton = animals * params['residue_ton_animal']
            else:  # Agricultura
                production = source_area * params['yield_ton_ha']
                residue_ton = production * params['residue_pct']
            
            total_residues += residue_ton
            
            residue_summary.append({
                "Fonte": source,
                "Área (ha)": f"{source_area:.1f}",
                "Resíduos (t/ano)": f"{residue_ton:.0f}"
            })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Estimativa de Resíduos por Fonte")
            df_residues = pd.DataFrame(residue_summary)
            st.dataframe(df_residues, use_container_width=True, hide_index=True)
            
        with col2:
            st.markdown("### 📈 Totais Estimados")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("🏞️ Área Total", f"{area_ha:.1f} ha")
                st.metric("📦 Total de Resíduos", f"{total_residues:.0f} t/ano")
                
            with col_b:
                residue_per_ha = total_residues / area_ha if area_ha > 0 else 0
                st.metric("📊 Densidade", f"{residue_per_ha:.1f} t/ha/ano")
                
                # Classificação do potencial
                if residue_per_ha > 20:
                    potential_class = "🟢 Alto"
                elif residue_per_ha > 10:
                    potential_class = "🟡 Moderado"
                else:
                    potential_class = "🟠 Baixo"
                    
                st.metric("⭐ Potencial", potential_class)
            
            # Composição dos resíduos
            st.markdown("**Composição dos Resíduos:**")
            for source, params in residues_data.items():
                pct = (area_ha * params['area_pct'] / area_ha * 100) if area_ha > 0 else 0
                st.write(f"• {source}: {pct:.0f}% da área")
            
        st.markdown("---")
        
        # Análise detalhada de infraestrutura
        st.markdown("## 🛣️ Análise de Infraestrutura")
        
        infra_items = [
            ("🛣️ Rodovias Federais", property_data.get('dist_rodovias_federais_km', 0), property_data.get('dist_rodovias_federais_km_score', 0)),
            ("🛤️ Rodovias Estaduais", property_data.get('dist_rodovias_estaduais_km', 0), property_data.get('dist_rodovias_estaduais_km_score', 0)),
            ("⚡ Subestações", property_data.get('dist_subestacoes_km', 0), property_data.get('dist_subestacoes_km_score', 0)),
            ("🔥 Gasodutos", property_data.get('dist_gasodutos_km', 0), property_data.get('dist_gasodutos_km_score', 0)),
            ("📡 Linhas Transmissão", property_data.get('dist_linhas_transmissao_km', 0), property_data.get('dist_linhas_transmissao_km_score', 0))
        ]
        
        # Tabela de infraestrutura (foco em distâncias)
        infra_data = []
        for name, distance, score in infra_items:
            if distance > 0 and distance < 200:  # Distâncias válidas
                # Status mais detalhado com explicações
                if distance <= 2:
                    status = "🟢 **EXCELENTE** (<2km)"
                    description = "Muito próximo - custos baixos"
                elif distance <= 5:
                    status = "🟢 **BOM** (2-5km)"
                    description = "Próximo - viável economicamente"
                elif distance <= 10:
                    status = "🟡 **MODERADO** (5-10km)"
                    description = "Razoável - custos moderados"
                elif distance <= 20:
                    status = "🟠 **DISTANTE** (10-20km)"
                    description = "Longe - custos elevados"
                else:
                    status = "🔴 **MUITO DISTANTE** (>20km)"
                    description = "Muito longe - custos proibitivos"
                    
                infra_data.append({
                    "🏗️ Infraestrutura": name,
                    "📏 Distância": f"{distance:.1f} km",
                    "📊 Avaliação": status,
                    "💭 Impacto": description
                })
        
        if infra_data:
            df_infra = pd.DataFrame(infra_data)
            st.dataframe(df_infra, use_container_width=True, hide_index=True)
            
# Gráfico de distâncias removido - tabela é suficiente
        else:
            st.warning("⚠️ Dados de infraestrutura não disponíveis ou inválidos")
            
        st.markdown("---")
        
        # Análise de restrições ambientais
        st.markdown("## 🛡️ Análise de Restrições Ambientais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("📊 Score de Restrição", f"{restriction_final:.1f}/100")
            st.caption("100 = sem restrições, 0 = muitas restrições")
            
            # Interpretação das restrições
            if restriction_final >= 80:
                rest_status = "🟢 **BAIXO RISCO**"
                rest_desc = "Poucas restrições ambientais"
            elif restriction_final >= 60:
                rest_status = "🟡 **RISCO MODERADO**" 
                rest_desc = "Algumas restrições manejáveis"
            elif restriction_final >= 40:
                rest_status = "🟠 **RISCO ALTO**"
                rest_desc = "Várias restrições importantes"
            else:
                rest_status = "🔴 **RISCO MUITO ALTO**"
                rest_desc = "Muitas restrições críticas"
                
            st.markdown(f"{rest_status}")
            st.caption(rest_desc)
            
        with col2:
            st.markdown("### 🌍 Fatores de Restrição Avaliados")
            
            restriction_factors = [
                "🌳 **Unidades de Conservação**",
                "🏛️ **Terras Indígenas**", 
                "🏙️ **Áreas Urbanas**",
                "✈️ **Aeroportos (segurança)**",
                "💧 **Corpos d'água**",
                "⛰️ **Declividade do terreno**",
                "🦅 **Áreas de proteção ambiental**"
            ]
            
            for factor in restriction_factors:
                st.markdown(f"• {factor}")
                
        # Explicação técnica
        with st.expander("ℹ️ Como são calculadas as restrições"):
            st.markdown("""
            **Metodologia de Cálculo:**
            
            O score de restrições considera a proximidade e sobreposição com:
            
            - **Zonas de amortecimento** de unidades de conservação (buffer de 1-5km)
            - **Distância mínima** de áreas urbanas (>2km recomendado)
            - **Restrições aeroportuárias** (zonas de segurança da aviação)
            - **Corpos d'água** e áreas de preservação permanente
            - **Declividade** superior a 15% (limitação técnica)
            - **Sobreposição** com terras indígenas ou quilombolas
            
            **Score final:** Combina todos os fatores em uma escala de 0-100, onde valores mais altos indicam menor restrição ambiental.
            """)
        
        # Recomendações básicas
        st.markdown("---")
        
        st.markdown("## 💡 Recomendações Técnicas")
        
        recommendations = []
        
        if mcda_score >= 70:
            recommendations.append("✅ **Proceder com estudos de viabilidade detalhados**")
            recommendations.append("📋 Elaborar projeto executivo da planta de biogás")
        elif mcda_score >= 50:
            recommendations.append("🔍 **Realizar estudos complementares de infraestrutura**")
            if infra_score < 30:
                recommendations.append("⚡ Avaliar custos de conexão elétrica e logística")
        else:
            recommendations.append("❌ **Não recomendado** nas condições atuais")
            recommendations.append("🔄 Considerar outras propriedades com melhor score MCDA")
            
        # Recomendações baseadas nos resíduos disponíveis
        if total_residues > 5000:
            recommendations.append("🏭 Alto volume de resíduos - Potencial para planta de grande porte")
        elif total_residues > 1000:
            recommendations.append("🏢 Volume moderado - Adequado para planta de médio porte")
        elif total_residues > 200:
            recommendations.append("🏠 Volume baixo - Viável para micro planta")
            
        for rec in recommendations:
            st.markdown(rec)
        
        # Botão voltar
        if st.button("⬅️ Voltar ao Mapa", type="primary", use_container_width=True):
            st.session_state.current_page = "mcda"
            st.session_state.current_view = "map"
            st.session_state.cp2b_selected_property = None
            st.rerun()
            
        logger.info(f"✅ Relatório simples renderizado para {cod_imovel}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao renderizar relatório simples: {str(e)}")
        st.error(f"Erro: {str(e)}")
        
        # Fallback básico
        st.markdown("## ⚠️ Erro no Relatório")
        st.write("Não foi possível carregar os dados completos da propriedade.")
        
        if st.button("⬅️ Voltar", type="primary"):
            st.session_state.current_page = "mcda"
            st.rerun()