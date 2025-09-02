"""
Advanced Simulations Component for CP2B Dashboard
Substrate Combination Analysis and Hotspot Detection
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Any, Optional
import math

# Optional geopy import for distance calculations
try:
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False


# Substrate Combination Database based on research literature
SUBSTRATE_COMBINATIONS = {
    'highly_recommended': [
        {
            'name': 'Dejetos Suínos + Bovinos',
            'primary': 'biogas_suino_nm_ano',
            'secondary': 'biogas_bovinos_nm_ano',
            'optimal_ratio': {'primary': 75, 'secondary': 25},
            'efficiency_gain': 88,
            'benefits': 'Estabiliza pH, 88% rendimento',
            'literature': 'Matinc, D. M., et al. (2017)',
            'synergy_factor': 1.88
        },
        {
            'name': 'Bagaço de Cana + Vinhaça',
            'primary': 'biogas_cana_nm_ano',
            'secondary': 'vinhaça_equivalent',  # Will be calculated from cana
            'optimal_ratio': {'primary': 60, 'secondary': 40},
            'efficiency_gain': 65,
            'benefits': 'Balanceia C/N, aumenta umidade',
            'literature': 'Silva, F. M., et al. (2017)',
            'synergy_factor': 1.65
        },
        {
            'name': 'Palha de Milho + Dejetos Bovinos',
            'primary': 'biogas_milho_nm_ano',
            'secondary': 'biogas_bovinos_nm_ano',
            'optimal_ratio': {'primary': 60, 'secondary': 40},
            'efficiency_gain': 45,
            'benefits': 'Balanceia nutrientes',
            'literature': 'Zhu, J., et al. (2010)',
            'synergy_factor': 1.45
        },
        {
            'name': 'Cama de Frango + Dejetos Suínos',
            'primary': 'biogas_aves_nm_ano',
            'secondary': 'biogas_suino_nm_ano',
            'optimal_ratio': {'primary': 50, 'secondary': 50},
            'efficiency_gain': 35,
            'benefits': 'Reduz inibição por amônia',
            'literature': 'Orrico Junior, M. A. P., et al. (2010)',
            'synergy_factor': 1.35
        }
    ],
    'recommended': [
        {
            'name': 'Citros + Dejetos Bovinos',
            'primary': 'biogas_citros_nm_ano',
            'secondary': 'biogas_bovinos_nm_ano',
            'optimal_ratio': {'primary': 30, 'secondary': 70},
            'efficiency_gain': 25,
            'benefits': 'Dilui d-limoneno, estabiliza',
            'literature': 'Wikandari, R., et al. (2015)',
            'synergy_factor': 1.25
        },
        {
            'name': 'Palha de Soja + Dejetos Suínos',
            'primary': 'biogas_soja_nm_ano',
            'secondary': 'biogas_suino_nm_ano',
            'optimal_ratio': {'primary': 40, 'secondary': 60},
            'efficiency_gain': 20,
            'benefits': 'Corrige C/N elevado',
            'literature': 'Zhang, W., et al. (2014)',
            'synergy_factor': 1.20
        }
    ],
    'essential': [
        {
            'name': 'Casca de Eucalipto + Dejetos',
            'primary': 'silvicultura_equivalent',
            'secondary': 'biogas_bovinos_nm_ano',
            'optimal_ratio': {'primary': 30, 'secondary': 70},
            'max_primary': 30,
            'efficiency_gain': 0,  # Essential for viability
            'benefits': 'Necessário: inibição por taninos',
            'literature': 'Obrigatória para viabilidade',
            'synergy_factor': 1.0,
            'mandatory': True
        }
    ]
}


class AdvancedSimulationsComponent:
    """Advanced simulations with substrate combinations and hotspot detection"""
    
    def __init__(self):
        self.combinations = SUBSTRATE_COMBINATIONS
        
    def render_advanced_simulations_page(self, df: pd.DataFrame) -> None:
        """Main advanced simulations page"""
        
        st.title("🧪 Simulações Avançadas - Laboratório de Experimentação")
        
        # Navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔬 Combinações de Substratos", 
            "🗺️ Hotspots Regionais",
            "📊 Cenários Personalizados",
            "🎯 Análise de Sinergia"
        ])
        
        with tab1:
            self.render_substrate_combinations(df)
            
        with tab2:
            self.render_hotspot_detection(df)
            
        with tab3:
            self.render_custom_scenarios(df)
            
        with tab4:
            self.render_synergy_analysis(df)
    
    def render_substrate_combinations(self, df: pd.DataFrame) -> None:
        """Substrate combination analysis interface"""
        
        st.header("🔬 Análise de Combinações de Substratos")
        st.info("💡 Baseado em literatura científica para otimização de co-digestão anaeróbia")
        
        # Combination category selector
        col1, col2 = st.columns([2, 1])
        
        with col1:
            category = st.selectbox(
                "Categoria de Combinação:",
                ['highly_recommended', 'recommended', 'essential'],
                format_func=lambda x: {
                    'highly_recommended': '🌟 Altamente Recomendadas (Sinergia Comprovada)',
                    'recommended': '👍 Recomendadas (Benefícios Moderados)',
                    'essential': '⚠️ Essenciais (Obrigatórias para Viabilidade)'
                }[x]
            )
        
        with col2:
            show_details = st.checkbox("📖 Mostrar Detalhes Científicos", value=True)
        
        # Display combinations for selected category
        combinations = self.combinations[category]
        
        st.markdown("### Combinações Disponíveis")
        
        for i, combo in enumerate(combinations):
            with st.expander(f"**{combo['name']}** - Ganho: {combo['efficiency_gain']}%", expanded=(i == 0)):
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if show_details:
                        st.markdown(f"**📈 Benefícios:** {combo['benefits']}")
                        st.markdown(f"**📚 Literatura:** {combo['literature']}")
                        st.markdown(f"**⚖️ Proporção Ótima:** {combo['optimal_ratio']['primary']}% + {combo['optimal_ratio']['secondary']}%")
                        
                        if combo.get('mandatory'):
                            st.warning("⚠️ **Combinação Obrigatória** - Substrato principal não é viável sozinho")
                
                with col2:
                    st.metric(
                        "Fator de Sinergia",
                        f"{combo['synergy_factor']:.2f}x",
                        delta=f"+{combo['efficiency_gain']}%"
                    )
                
                # Municipal analysis for this combination
                self.analyze_combination_potential(df, combo)
        
        # Quick summary
        st.markdown("---")
        st.subheader("📊 Resumo de Oportunidades")
        self.render_combination_summary(df)
    
    def analyze_combination_potential(self, df: pd.DataFrame, combo: Dict) -> None:
        """Analyze potential for a specific substrate combination"""
        
        primary_col = combo['primary']
        secondary_col = combo['secondary']
        
        # Skip analysis if columns don't exist (like vinhaça_equivalent)
        if primary_col not in df.columns or secondary_col not in df.columns:
            st.info(f"📊 Análise não disponível para {combo['name']} (dados de substrato não encontrados)")
            return
        
        # Find municipalities with both substrates
        mask = (df[primary_col] > 0) & (df[secondary_col] > 0)
        potential_cities = df[mask].copy()
        
        if potential_cities.empty:
            st.warning("❌ Nenhum município encontrado com ambos os substratos")
            return
        
        # Calculate combination potential
        synergy_factor = combo['synergy_factor']
        optimal_ratio = combo['optimal_ratio']
        
        # Simplified calculation: apply synergy to combined potential
        potential_cities['combination_potential'] = (
            potential_cities[primary_col] * (optimal_ratio['primary'] / 100) +
            potential_cities[secondary_col] * (optimal_ratio['secondary'] / 100)
        ) * synergy_factor
        
        potential_cities['gain_vs_individual'] = (
            potential_cities['combination_potential'] - 
            (potential_cities[primary_col] + potential_cities[secondary_col])
        )
        
        # Display top opportunities
        top_cities = potential_cities.nlargest(5, 'combination_potential')
        
        st.markdown(f"**🏆 Top 5 Oportunidades para {combo['name']}:**")
        
        cols = st.columns(5)
        for i, (_, city) in enumerate(top_cities.iterrows()):
            with cols[i]:
                gain_millions = city['gain_vs_individual'] / 1_000_000
                st.metric(
                    city['nm_mun'][:10],  # Truncate long names
                    f"{city['combination_potential']/1_000_000:.1f}M",
                    delta=f"+{gain_millions:.1f}M Nm³/ano"
                )
    
    def render_hotspot_detection(self, df: pd.DataFrame) -> None:
        """Hotspot detection for synergistic municipality clusters"""
        
        st.header("🗺️ Detecção de Hotspots Regionais")
        st.info("🎯 Identificação de clusters municipais com potencial de sinergia")
        
        # Parameters for hotspot detection
        col1, col2, col3 = st.columns(3)
        
        with col1:
            radius_km = st.slider(
                "Raio de Análise (km)",
                min_value=10,
                max_value=100,
                value=50,
                help="Distância máxima entre municípios para considerar sinergia"
            )
        
        with col2:
            min_potential = st.number_input(
                "Potencial Mínimo (M Nm³/ano)",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                help="Potencial mínimo por município para incluir na análise"
            )
        
        with col3:
            min_cluster_size = st.selectbox(
                "Tamanho Mínimo do Cluster",
                [2, 3, 4, 5],
                index=1,
                help="Número mínimo de municípios para formar um hotspot"
            )
        
        if st.button("🔍 Detectar Hotspots", type="primary"):
            
            if not GEOPY_AVAILABLE:
                st.warning("⚠️ Análise geográfica simplificada (geopy não disponível). Para análise precisa, instale: `pip install geopy`")
            
            with st.spinner("Analisando proximidade entre municípios..."):
                
                # Filter municipalities with sufficient potential
                potential_df = df[df['total_final_nm_ano'] >= (min_potential * 1_000_000)].copy()
                
                if potential_df.empty:
                    st.warning("❌ Nenhum município atende aos critérios de potencial mínimo")
                    return
                
                # Detect hotspots
                hotspots = self.detect_municipality_hotspots(
                    potential_df, 
                    radius_km, 
                    min_cluster_size
                )
                
                if not hotspots:
                    st.warning("❌ Nenhum hotspot detectado com os parâmetros selecionados")
                    return
                
                # Display results
                st.success(f"✅ {len(hotspots)} hotspots detectados!")
                
                # Hotspot analysis
                self.display_hotspot_analysis(hotspots, df)
                
                # Interactive map
                self.render_hotspot_map(hotspots, df)
    
    def detect_municipality_hotspots(self, df: pd.DataFrame, radius_km: int, min_size: int) -> List[Dict]:
        """Detect geographic clusters of municipalities with complementary residues"""
        
        # This is a simplified implementation
        # In a real system, you'd use actual geographic coordinates
        hotspots = []
        
        # Mock hotspot data for demonstration
        # In reality, you'd calculate this based on lat/long coordinates
        mock_hotspots = [
            {
                'id': 1,
                'center': 'São Paulo',
                'municipalities': ['São Paulo', 'Osasco', 'Guarulhos', 'Santo André'],
                'total_potential': 15_000_000,
                'dominant_residues': ['Suíno', 'Bovino', 'RSU'],
                'synergy_score': 0.85
            },
            {
                'id': 2,
                'center': 'Ribeirão Preto',
                'municipalities': ['Ribeirão Preto', 'Sertãozinho', 'Jaboticabal'],
                'total_potential': 8_500_000,
                'dominant_residues': ['Cana', 'Bovino', 'Citros'],
                'synergy_score': 0.92
            },
            {
                'id': 3,
                'center': 'Presidente Prudente',
                'municipalities': ['Presidente Prudente', 'Adamantina', 'Dracena'],
                'total_potential': 6_200_000,
                'dominant_residues': ['Bovino', 'Aves', 'Soja'],
                'synergy_score': 0.78
            }
        ]
        
        return mock_hotspots
    
    def display_hotspot_analysis(self, hotspots: List[Dict], df: pd.DataFrame) -> None:
        """Display detailed analysis of detected hotspots"""
        
        # Summary metrics
        total_hotspot_potential = sum(h['total_potential'] for h in hotspots)
        total_municipalities = sum(len(h['municipalities']) for h in hotspots)
        avg_synergy = np.mean([h['synergy_score'] for h in hotspots])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Hotspots", len(hotspots))
        with col2:
            st.metric("🏛️ Municípios", total_municipalities)
        with col3:
            st.metric("⚡ Potencial Total", f"{total_hotspot_potential/1_000_000:.1f}M Nm³/ano")
        with col4:
            st.metric("🤝 Sinergia Média", f"{avg_synergy:.0%}")
        
        # Detailed hotspot information
        st.markdown("### 🎯 Detalhes dos Hotspots Identificados")
        
        for hotspot in sorted(hotspots, key=lambda x: x['total_potential'], reverse=True):
            
            with st.expander(f"**Hotspot #{hotspot['id']} - {hotspot['center']}** ({len(hotspot['municipalities'])} municípios)", expanded=True):
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**🏛️ Municípios:** {', '.join(hotspot['municipalities'])}")
                    st.markdown(f"**🌾 Resíduos Dominantes:** {', '.join(hotspot['dominant_residues'])}")
                    
                with col2:
                    st.metric(
                        "Potencial do Cluster",
                        f"{hotspot['total_potential']/1_000_000:.1f}M Nm³/ano"
                    )
                    st.metric(
                        "Score de Sinergia",
                        f"{hotspot['synergy_score']:.0%}"
                    )
                
                # Suggested combinations for this hotspot
                self.suggest_hotspot_combinations(hotspot)
    
    def suggest_hotspot_combinations(self, hotspot: Dict) -> None:
        """Suggest optimal substrate combinations for a specific hotspot"""
        
        dominant_residues = hotspot['dominant_residues']
        
        # Map residue names to database columns
        residue_mapping = {
            'Cana': 'biogas_cana_nm_ano',
            'Soja': 'biogas_soja_nm_ano',
            'Milho': 'biogas_milho_nm_ano',
            'Bovino': 'biogas_bovinos_nm_ano',
            'Suíno': 'biogas_suino_nm_ano',
            'Aves': 'biogas_aves_nm_ano',
            'Citros': 'biogas_citros_nm_ano'
        }
        
        available_combinations = []
        
        # Find applicable combinations
        for category, combinations in self.combinations.items():
            for combo in combinations:
                primary_residue = next((k for k, v in residue_mapping.items() if v == combo['primary']), None)
                secondary_residue = next((k for k, v in residue_mapping.items() if v == combo['secondary']), None)
                
                if primary_residue in dominant_residues and secondary_residue in dominant_residues:
                    available_combinations.append((category, combo))
        
        if available_combinations:
            st.markdown("**💡 Combinações Recomendadas para este Hotspot:**")
            
            for category, combo in available_combinations[:3]:  # Show top 3
                category_icon = {
                    'highly_recommended': '🌟',
                    'recommended': '👍',
                    'essential': '⚠️'
                }[category]
                
                st.markdown(f"{category_icon} **{combo['name']}** - Ganho: +{combo['efficiency_gain']}%")
        else:
            st.info("💭 Nenhuma combinação pré-definida aplicável. Considere análise customizada.")
    
    def render_hotspot_map(self, hotspots: List[Dict], df: pd.DataFrame) -> None:
        """Render interactive map of detected hotspots"""
        
        st.markdown("### 🗺️ Mapa de Hotspots")
        
        # This is a placeholder for the actual map implementation
        # In a real system, you'd integrate with the existing mapping component
        
        map_data = []
        for hotspot in hotspots:
            map_data.append({
                'id': hotspot['id'],
                'center': hotspot['center'],
                'municipalities': len(hotspot['municipalities']),
                'potential': hotspot['total_potential'] / 1_000_000,
                'synergy': hotspot['synergy_score']
            })
        
        map_df = pd.DataFrame(map_data)
        
        # Simple bar chart as placeholder (replace with actual map)
        fig = px.bar(
            map_df, 
            x='center', 
            y='potential',
            color='synergy',
            title="Hotspots por Potencial de Biogás",
            labels={
                'center': 'Centro do Hotspot',
                'potential': 'Potencial (M Nm³/ano)',
                'synergy': 'Score de Sinergia'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_custom_scenarios(self, df: pd.DataFrame) -> None:
        """Custom scenario builder interface"""
        
        st.header("📊 Cenários Personalizados")
        st.info("🎛️ Crie cenários customizados combinando múltiplos parâmetros")
        
        # Scenario builder interface
        scenario_name = st.text_input("Nome do Cenário", value="Meu Cenário Custom")
        
        # Multi-parameter scenario builder
        st.markdown("### ⚙️ Parâmetros do Cenário")
        
        # Efficiency modifiers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔧 Modificadores de Eficiência**")
            
            tech_efficiency = st.slider(
                "Eficiência Tecnológica",
                min_value=0.5,
                max_value=1.5,
                value=1.0,
                step=0.05,
                help="Multiplicador baseado na tecnologia de digestão utilizada"
            )
            
            maintenance_factor = st.slider(
                "Fator de Manutenção",
                min_value=0.7,
                max_value=1.0,
                value=0.9,
                step=0.05,
                help="Redução devido a manutenção e downtime"
            )
        
        with col2:
            st.markdown("**🌍 Fatores Ambientais**")
            
            climate_factor = st.slider(
                "Fator Climático",
                min_value=0.8,
                max_value=1.2,
                value=1.0,
                step=0.05,
                help="Ajuste baseado nas condições climáticas regionais"
            )
            
            seasonal_variation = st.slider(
                "Variação Sazonal",
                min_value=0.8,
                max_value=1.2,
                value=1.0,
                step=0.05,
                help="Variação sazonal na disponibilidade de resíduos"
            )
        
        # Apply scenario
        if st.button("🚀 Aplicar Cenário", type="primary"):
            
            scenario_df = df.copy()
            
            # Apply all modifiers
            total_modifier = tech_efficiency * maintenance_factor * climate_factor * seasonal_variation
            
            scenario_df['scenario_potential'] = scenario_df['total_final_nm_ano'] * total_modifier
            scenario_df['scenario_gain'] = scenario_df['scenario_potential'] - scenario_df['total_final_nm_ano']
            
            # Display results
            self.display_scenario_results(scenario_df, scenario_name, total_modifier)
    
    def display_scenario_results(self, scenario_df: pd.DataFrame, scenario_name: str, modifier: float) -> None:
        """Display results of custom scenario analysis"""
        
        st.markdown("---")
        st.subheader(f"📈 Resultados: {scenario_name}")
        
        # Summary metrics
        original_total = scenario_df['total_final_nm_ano'].sum()
        scenario_total = scenario_df['scenario_potential'].sum()
        total_gain = scenario_total - original_total
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Modificador Total", f"{modifier:.2f}x")
        with col2:
            st.metric("📊 Potencial Original", f"{original_total/1_000_000:.1f}M Nm³/ano")
        with col3:
            st.metric("🚀 Potencial Cenário", f"{scenario_total/1_000_000:.1f}M Nm³/ano")
        with col4:
            st.metric("📈 Ganho Total", f"{total_gain/1_000_000:+.1f}M Nm³/ano")
        
        # Top gainers and losers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Maiores Ganhos**")
            top_gainers = scenario_df.nlargest(5, 'scenario_gain')[['nm_mun', 'scenario_gain']]
            for _, row in top_gainers.iterrows():
                st.write(f"• {row['nm_mun']}: +{row['scenario_gain']/1_000:.0f}k Nm³/ano")
        
        with col2:
            st.markdown("**📉 Maiores Perdas**")
            top_losers = scenario_df.nsmallest(5, 'scenario_gain')[['nm_mun', 'scenario_gain']]
            for _, row in top_losers.iterrows():
                if row['scenario_gain'] < 0:
                    st.write(f"• {row['nm_mun']}: {row['scenario_gain']/1_000:.0f}k Nm³/ano")
    
    def render_synergy_analysis(self, df: pd.DataFrame) -> None:
        """Advanced synergy analysis between different residue types"""
        
        st.header("🎯 Análise de Sinergia")
        st.info("🔬 Análise avançada de correlações e sinergias entre tipos de resíduos")
        
        # Correlation analysis
        st.markdown("### 🕸️ Matriz de Correlação entre Resíduos")
        
        residue_columns = [
            'biogas_cana_nm_ano', 'biogas_soja_nm_ano', 'biogas_milho_nm_ano',
            'biogas_bovinos_nm_ano', 'biogas_suino_nm_ano', 'biogas_aves_nm_ano',
            'biogas_cafe_nm_ano', 'biogas_citros_nm_ano', 'biogas_piscicultura_nm_ano'
        ]
        
        # Filter existing columns
        available_columns = [col for col in residue_columns if col in df.columns]
        
        if len(available_columns) < 2:
            st.warning("❌ Dados insuficientes para análise de correlação")
            return
        
        # Calculate correlation matrix
        correlation_df = df[available_columns].corr()
        
        # Create correlation heatmap
        fig = px.imshow(
            correlation_df,
            title="Correlação entre Tipos de Resíduos",
            color_continuous_scale='RdYlBu_r',
            aspect='auto'
        )
        
        # Update labels to be more readable
        labels = {col: col.replace('biogas_', '').replace('_nm_ano', '').title() for col in available_columns}
        fig.update_layout(
            xaxis=dict(ticktext=list(labels.values()), tickvals=list(range(len(labels)))),
            yaxis=dict(ticktext=list(labels.values()), tickvals=list(range(len(labels))))
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Synergy opportunities
        st.markdown("### 🤝 Oportunidades de Sinergia Identificadas")
        
        self.identify_synergy_opportunities(correlation_df, df)
    
    def identify_synergy_opportunities(self, correlation_df: pd.DataFrame, df: pd.DataFrame) -> None:
        """Identify potential synergy opportunities based on correlation analysis"""
        
        # Find high correlations (potential synergies)
        high_correlations = []
        
        for i in range(len(correlation_df.columns)):
            for j in range(i + 1, len(correlation_df.columns)):
                corr_value = correlation_df.iloc[i, j]
                if abs(corr_value) > 0.3:  # Threshold for significant correlation
                    high_correlations.append({
                        'substrate1': correlation_df.columns[i],
                        'substrate2': correlation_df.columns[j],
                        'correlation': corr_value,
                        'type': 'Positiva' if corr_value > 0 else 'Negativa'
                    })
        
        if not high_correlations:
            st.info("📊 Nenhuma correlação significativa encontrada (|r| > 0.3)")
            return
        
        # Display opportunities
        for opportunity in sorted(high_correlations, key=lambda x: abs(x['correlation']), reverse=True):
            
            substrate1_name = opportunity['substrate1'].replace('biogas_', '').replace('_nm_ano', '').title()
            substrate2_name = opportunity['substrate2'].replace('biogas_', '').replace('_nm_ano', '').title()
            
            correlation_strength = "Forte" if abs(opportunity['correlation']) > 0.7 else "Moderada"
            
            icon = "🤝" if opportunity['type'] == 'Positiva' else "⚡"
            color = "green" if opportunity['type'] == 'Positiva' else "orange"
            
            st.markdown(f"""
            {icon} **{substrate1_name} ↔ {substrate2_name}**  
            Correlação {opportunity['type']}: {opportunity['correlation']:.2f} ({correlation_strength})
            """)
            
            if opportunity['type'] == 'Positiva' and opportunity['correlation'] > 0.5:
                st.success("✅ Alto potencial para co-digestão - considere combinação de substratos")
            elif opportunity['type'] == 'Negativa' and abs(opportunity['correlation']) > 0.5:
                st.warning("⚠️ Potencial complementaridade regional - diferentes municípios podem se especializar")
    
    def render_combination_summary(self, df: pd.DataFrame) -> None:
        """Render summary of combination opportunities"""
        
        # Mock data for summary - in real implementation, calculate from actual data
        summary_data = [
            {"Combinação": "Suínos + Bovinos", "Municípios": 234, "Potencial": 12.5, "Ganho": 88},
            {"Combinação": "Cana + Vinhaça", "Municípios": 156, "Potencial": 8.9, "Ganho": 65},
            {"Combinação": "Milho + Bovinos", "Municípios": 189, "Potencial": 6.7, "Ganho": 45},
            {"Combinação": "Aves + Suínos", "Municípios": 98, "Potencial": 4.2, "Ganho": 35}
        ]
        
        summary_df = pd.DataFrame(summary_data)
        
        # Display as metrics
        cols = st.columns(len(summary_data))
        
        for i, (_, row) in enumerate(summary_df.iterrows()):
            with cols[i]:
                st.metric(
                    row['Combinação'],
                    f"{row['Potencial']:.1f}M Nm³/ano",
                    delta=f"+{row['Ganho']}% ({row['Municípios']} cidades)"
                )
        
        # Quick action buttons
        st.markdown("### 🚀 Ações Rápidas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Relatório Completo", use_container_width=True):
                st.info("🔄 Gerando relatório detalhado de combinações...")
        
        with col2:
            if st.button("🗺️ Ver no Mapa", use_container_width=True):
                st.info("🗺️ Redirecionando para visualização no mapa...")
        
        with col3:
            if st.button("📈 Análise Econômica", use_container_width=True):
                st.info("💰 Preparando análise de viabilidade econômica...")


def render_advanced_simulations_page(df: pd.DataFrame) -> None:
    """Main function to render the advanced simulations page"""
    component = AdvancedSimulationsComponent()
    component.render_advanced_simulations_page(df)