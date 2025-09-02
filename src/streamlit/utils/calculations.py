from typing import Dict, Any
import pandas as pd
import streamlit as st

# Import scientific references system
try:
    from utils.scientific_references import get_reference_manager, show_reference_button
    REFERENCES_AVAILABLE = True
except ImportError:
    REFERENCES_AVAILABLE = False


def calculate_biogas_potential(residuos: float, fator: float) -> float:
    """
    Calcula potencial de biogás baseado em resíduos e fator de conversão.

    Args:
        residuos (float): Quantidade de resíduos em toneladas/ano
        fator (float): Fator de conversão m³/ton

    Returns:
        float: Potencial de biogás em m³/ano
    """
    return float(residuos or 0) * float(fator or 0)


def recompute_total_by_sources(m_row: Dict[str, float], enabled_sources: Dict[str, bool]) -> float:
    sources = [
        "biogas_cana_nm_ano",
        "biogas_soja_nm_ano",
        "biogas_milho_nm_ano",
        "biogas_bovinos_nm_ano",
        "biogas_cafe_nm_ano",
        "biogas_citros_nm_ano",
        "biogas_suino_nm_ano",
        "biogas_aves_nm_ano",
        "biogas_piscicultura_nm_ano",
    ]
    total = 0.0
    for s in sources:
        if enabled_sources.get(s, True):
            total += float(m_row.get(s, 0) or 0)
    return total


# Scientific reference mapping for conversion factors
CONVERSION_FACTOR_REFERENCES = {
    'biogas_cana_nm_ano': ['darwin_2017', 'silva_2017', 'moraes_2015', 'melo_2024'],  # Sugarcane bagasse and vinasse
    'biogas_soja_nm_ano': ['zhu_2017', 'murphy_2011'],  # Soybean straw  
    'biogas_milho_nm_ano': ['stachowiak_2019', 'ona_2019', 'zhang_2022', 'khan_2024', 'zhu_2010', 'murphy_2011'],  # Corn residues
    'biogas_cafe_nm_ano': ['paes_2023', 'passos_2018', 'czekala_2023', 'braojos_2024', 'murphy_2011'],  # Coffee residues
    'biogas_citros_nm_ano': ['serrano_2014', 'szaja_2020', 'jiang_2020', 'diniso_2024', 'murphy_2011'],  # Citrus residues
    'biogas_bovinos_nm_ano': ['darwin_2017', 'paes_2023', 'ona_2019', 'matinc_2017_detailed'],  # Cattle manure
    'biogas_suino_nm_ano': ['matinc_2017', 'matinc_2017_detailed', 'souza_2008'],  # Swine manure
    'biogas_aves_nm_ano': ['ona_2019'],  # Poultry manure
    'biogas_piscicultura_nm_ano': ['estevez_2019', 'braganca_2023', 'ingabire_2023', 'kafle_2012'],  # Fish farming residues
    'silvicultura_nm_ano': ['musa_2021', 'morales_2021', 'zhang_2015', 'xu_2019'],  # Forestry residues
    'rsu_potencial_nm_habitante_ano': ['prabhu_2016', 'jiang_2020'],  # Municipal solid waste
    'rpo_potencial_nm_habitante_ano': ['bella_2022', 'prabhu_2016']  # Organic waste
}

# Fatores de conversão padrão para diferentes cenários
DEFAULT_CONVERSION_FACTORS = {
    'conservador': {
        'biogas_cana_nm_ano': 50.0,      # m³/ton (bagaço + palha)
        'biogas_soja_nm_ano': 35.0,      # m³/ton (restos culturais)
        'biogas_milho_nm_ano': 40.0,     # m³/ton (sabugo + palha)
        'biogas_cafe_nm_ano': 45.0,      # m³/ton (polpa + casca)
        'biogas_citros_nm_ano': 30.0,    # m³/ton (bagaço)
        'biogas_bovinos_nm_ano': 25.0,    # m³/ton (esterco fresco)
        'biogas_suino_nm_ano': 60.0,    # m³/ton (dejetos)
        'biogas_aves_nm_ano': 25.0,      # m³/ton (cama de frango) - CORRECTED
        'biogas_piscicultura_nm_ano': 20.0,  # m³/ton (resíduos)
        'rsu_potencial_nm_habitante_ano': 100.0,    # m³/habitante/ano (RSU)
        'rpo_potencial_nm_habitante_ano': 50.0      # m³/habitante/ano (RPO)
    },
    'realista': {
        'biogas_cana_nm_ano': 75.0,
        'biogas_soja_nm_ano': 50.0,
        'biogas_milho_nm_ano': 60.0,
        'biogas_cafe_nm_ano': 65.0,
        'biogas_citros_nm_ano': 45.0,
        'biogas_bovinos_nm_ano': 35.0,
        'biogas_suino_nm_ano': 80.0,
        'biogas_aves_nm_ano': 35.0,      # m³/ton (cama de frango) - CORRECTED
        'biogas_piscicultura_nm_ano': 30.0,
        'rsu_potencial_nm_habitante_ano': 150.0,
        'rpo_potencial_nm_habitante_ano': 75.0
    },
    'otimista': {
        'biogas_cana_nm_ano': 100.0,
        'biogas_soja_nm_ano': 70.0,
        'biogas_milho_nm_ano': 85.0,
        'biogas_cafe_nm_ano': 90.0,
        'biogas_citros_nm_ano': 65.0,
        'biogas_bovinos_nm_ano': 50.0,
        'biogas_suino_nm_ano': 120.0,
        'biogas_aves_nm_ano': 45.0,      # m³/ton (cama de frango) - CORRECTED
        'biogas_piscicultura_nm_ano': 45.0,
        'rsu_potencial_nm_habitante_ano': 200.0,
        'rpo_potencial_nm_habitante_ano': 100.0
    }
}

BIOGAS_SOURCE_LABELS = {
    'biogas_cana_nm_ano': '🌾 Cana-de-açúcar',
    'biogas_soja_nm_ano': '🌱 Soja',
    'biogas_milho_nm_ano': '🌽 Milho',
    'biogas_cafe_nm_ano': '☕ Café',
    'biogas_citros_nm_ano': '🍊 Citros',
    'biogas_bovinos_nm_ano': '🐄 Bovinos',
    'biogas_suino_nm_ano': '🐷 Suínos',
    'biogas_aves_nm_ano': '🐔 Aves',
    'biogas_piscicultura_nm_ano': '🐟 Piscicultura',
    'silvicultura_nm_ano': '🌲 Silvicultura',
    'rsu_potencial_nm_habitante_ano': '🗑️ RSU (por hab.)',
    'rpo_potencial_nm_habitante_ano': '🌳 RPO (por hab.)'
}


def render_conversion_factor_with_references(source: str, factor: float, scenario: str = "realista") -> None:
    """Render a conversion factor with its scientific references"""
    
    if not REFERENCES_AVAILABLE:
        st.metric(BIOGAS_SOURCE_LABELS.get(source, source), f"{factor} m³/ton")
        return
    
    # Get references for this source
    references = CONVERSION_FACTOR_REFERENCES.get(source, [])
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.metric(BIOGAS_SOURCE_LABELS.get(source, source), f"{factor} m³/ton")
    
    with col2:
        if references:
            # Show primary reference button
            primary_ref = references[0]
            show_reference_button(
                primary_ref, 
                "📖 Source", 
                key=f"factor_{source}_{scenario}"
            )
            
            # Show additional references if available
            if len(references) > 1:
                with st.expander("More References", expanded=False):
                    for i, ref_id in enumerate(references[1:], 1):
                        show_reference_button(
                            ref_id,
                            f"📖 Ref {i+1}",
                            key=f"factor_{source}_{scenario}_{i}"
                        )
        else:
            st.caption("📚 Ref. pending")


def show_all_references_for_source(source: str) -> None:
    """Show all scientific references for a specific biogas source"""
    
    if not REFERENCES_AVAILABLE:
        st.info("Scientific references system not available")
        return
    
    references = CONVERSION_FACTOR_REFERENCES.get(source, [])
    source_label = BIOGAS_SOURCE_LABELS.get(source, source)
    
    st.markdown(f"### 📚 Scientific References for {source_label}")
    
    if not references:
        st.info("No specific references available for this source yet")
        return
    
    ref_manager = get_reference_manager()
    
    for ref_id in references:
        ref = ref_manager.get_reference(ref_id)
        if ref:
            with st.expander(f"{ref.authors.split(',')[0]} et al. ({ref.year})", expanded=False):
                ref_manager.show_reference_modal(ref)
        else:
            st.error(f"Reference not found: {ref_id}")


def render_scientific_references_summary() -> None:
    """Render a summary of all scientific references used in the system"""
    
    if not REFERENCES_AVAILABLE:
        st.error("Scientific references system not available")
        return
    
    ref_manager = get_reference_manager()
    
    st.title("📚 Scientific References - CP2B Biogas System")
    st.markdown("Complete scientific bibliography supporting biogas conversion factors and substrate combinations")
    
    # Render the complete references page
    ref_manager.render_references_page()


def render_scenario_simulator() -> Dict[str, Any]:
    """
    Renderiza simulador de cenários com fatores de conversão personalizáveis
    
    Returns:
        Dict contendo cenário selecionado e fatores customizados
    """
    st.subheader("🎯 Simulador de Cenários")
    
    # Seleção de cenário base
    col1, col2 = st.columns([2, 1])
    
    with col1:
        scenario_type = st.selectbox(
            "Cenário Base:",
            ['conservador', 'realista', 'otimista', 'customizado'],
            index=1,  # Default: realista
            help="Selecione um cenário pré-definido ou customize os fatores"
        )
    
    with col2:
        if st.button("🔄 Reset Fatores"):
            # Limpar fatores customizados do session_state
            for key in list(st.session_state.keys()):
                if key.startswith('custom_factor_'):
                    del st.session_state[key]
            st.rerun()
    
    # Obter fatores base
    if scenario_type == 'customizado':
        base_factors = DEFAULT_CONVERSION_FACTORS['realista']
        st.info("💡 Ajuste os fatores abaixo para criar seu cenário customizado")
    else:
        base_factors = DEFAULT_CONVERSION_FACTORS[scenario_type]
        st.info(f"📊 Cenário **{scenario_type.title()}** selecionado")
    
    # Interface para ajuste de fatores
    st.markdown("### ⚙️ Fatores de Conversão (m³/ton)")
    
    conversion_factors = {}
    
    # Organizar por categoria
    categories = {
        '🌾 Fontes Agrícolas': ['biogas_cana_nm_ano', 'biogas_soja_nm_ano', 'biogas_milho_nm_ano', 'biogas_cafe_nm_ano', 'biogas_citros_nm_ano'],
        '🐄 Fontes Pecuárias': ['biogas_bovinos_nm_ano', 'biogas_suino_nm_ano', 'biogas_aves_nm_ano', 'biogas_piscicultura_nm_ano'],
        '🗑️ Resíduos Urbanos': ['rsu_potencial_nm_habitante_ano', 'rpo_potencial_nm_habitante_ano']
    }
    
    for category, sources in categories.items():
        with st.expander(f"{category} ({len(sources)} fontes)", expanded=(scenario_type == 'customizado')):
            
            cols = st.columns(2)
            
            for i, source in enumerate(sources):
                col = cols[i % 2]
                
                with col:
                    # Valor padrão do cenário
                    default_value = base_factors.get(source, 50.0)
                    
                    # Chave para session_state
                    factor_key = f"custom_factor_{source}"
                    
                    # Slider para ajuste
                    if scenario_type == 'customizado':
                        # Permitir edição completa
                        factor_value = st.slider(
                            BIOGAS_SOURCE_LABELS.get(source, source),
                            min_value=0.0,
                            max_value=300.0,
                            value=st.session_state.get(factor_key, default_value),
                            step=5.0,
                            key=factor_key,
                            help=f"Fator de conversão para {source}"
                        )
                    else:
                        # Mostrar valor fixo do cenário
                        st.metric(
                            BIOGAS_SOURCE_LABELS.get(source, source),
                            f"{default_value:.1f} m³/ton",
                            help=f"Fator padrão do cenário {scenario_type}"
                        )
                        factor_value = default_value
                    
                    conversion_factors[source] = factor_value
    
    # Comparação entre cenários
    if scenario_type == 'customizado':
        st.markdown("### 📊 Comparação com Cenários Padrão")
        
        comparison_data = []
        for scenario_name, scenario_factors in DEFAULT_CONVERSION_FACTORS.items():
            total_factor = sum(scenario_factors.values())
            comparison_data.append({
                'Cenário': scenario_name.title(),
                'Total Fatores': f"{total_factor:.1f}",
                'Média': f"{total_factor/len(scenario_factors):.1f}"
            })
        
        # Adicionar cenário customizado
        custom_total = sum(conversion_factors.values())
        comparison_data.append({
            'Cenário': 'Customizado',
            'Total Fatores': f"{custom_total:.1f}",
            'Média': f"{custom_total/len(conversion_factors):.1f}"
        })
        
        st.dataframe(pd.DataFrame(comparison_data), hide_index=True)
    
    return {
        'scenario_type': scenario_type,
        'conversion_factors': conversion_factors,
        'is_custom': scenario_type == 'customizado'
    }


def apply_scenario_to_data(df: pd.DataFrame, scenario_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplica cenário de conversão aos dados dos municípios
    
    Args:
        df: DataFrame com dados dos municípios
        scenario_config: Configuração do cenário (do render_scenario_simulator)
    
    Returns:
        DataFrame com potenciais recalculados
    """
    if df.empty:
        return df
    
    df_scenario = df.copy()
    conversion_factors = scenario_config.get('conversion_factors', {})
    
    # Recalcular potenciais baseado nos novos fatores
    for source, factor in conversion_factors.items():
        if source in df_scenario.columns:
            # Assumindo que temos dados de resíduos base (toneladas)
            # Para este exemplo, vamos aplicar o fator diretamente aos valores existentes
            # Em implementação real, você teria dados de resíduos separados
            
            # Fator de ajuste baseado na diferença do cenário realista (base)
            base_factor = DEFAULT_CONVERSION_FACTORS['realista'].get(source, 1.0)
            adjustment_ratio = factor / base_factor if base_factor > 0 else 1.0
            
            df_scenario[source] = df_scenario[source] * adjustment_ratio
    
    # Recalcular totais
    biogas_sources = [col for col in conversion_factors.keys() if col in df_scenario.columns]
    df_scenario['total_final_scenario'] = df_scenario[biogas_sources].sum(axis=1)
    
    # Recalcular totais por categoria
    agricola_sources = ['biogas_cana_nm_ano', 'biogas_soja_nm_ano', 'biogas_milho_nm_ano', 'biogas_cafe_nm_ano', 'biogas_citros_nm_ano']
    pecuaria_sources = ['biogas_bovinos_nm_ano', 'biogas_suino_nm_ano', 'biogas_aves_nm_ano', 'biogas_piscicultura_nm_ano']
    
    df_scenario['total_agricola_scenario'] = df_scenario[[col for col in agricola_sources if col in df_scenario.columns]].sum(axis=1)
    df_scenario['total_pecuaria_scenario'] = df_scenario[[col for col in pecuaria_sources if col in df_scenario.columns]].sum(axis=1)
    
    return df_scenario


