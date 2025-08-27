from typing import Dict, Any
import pandas as pd
import streamlit as st


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
        "biogas_cana",
        "biogas_soja",
        "biogas_milho",
        "biogas_bovino",
        "biogas_cafe",
        "biogas_citros",
        "biogas_suinos",
        "biogas_aves",
        "biogas_piscicultura",
    ]
    total = 0.0
    for s in sources:
        if enabled_sources.get(s, True):
            total += float(m_row.get(s, 0) or 0)
    return total


# Fatores de conversão padrão para diferentes cenários
DEFAULT_CONVERSION_FACTORS = {
    'conservador': {
        'biogas_cana': 50.0,      # m³/ton (bagaço + palha)
        'biogas_soja': 35.0,      # m³/ton (restos culturais)
        'biogas_milho': 40.0,     # m³/ton (sabugo + palha)
        'biogas_cafe': 45.0,      # m³/ton (polpa + casca)
        'biogas_citros': 30.0,    # m³/ton (bagaço)
        'biogas_bovino': 25.0,    # m³/ton (esterco fresco)
        'biogas_suinos': 60.0,    # m³/ton (dejetos)
        'biogas_aves': 80.0,      # m³/ton (cama de frango)
        'biogas_piscicultura': 20.0,  # m³/ton (resíduos)
        'total_ch4_rsu_rpo': 100.0    # m³/ton (RSU)
    },
    'realista': {
        'biogas_cana': 75.0,
        'biogas_soja': 50.0,
        'biogas_milho': 60.0,
        'biogas_cafe': 65.0,
        'biogas_citros': 45.0,
        'biogas_bovino': 35.0,
        'biogas_suinos': 80.0,
        'biogas_aves': 100.0,
        'biogas_piscicultura': 30.0,
        'total_ch4_rsu_rpo': 150.0
    },
    'otimista': {
        'biogas_cana': 100.0,
        'biogas_soja': 70.0,
        'biogas_milho': 85.0,
        'biogas_cafe': 90.0,
        'biogas_citros': 65.0,
        'biogas_bovino': 50.0,
        'biogas_suinos': 120.0,
        'biogas_aves': 140.0,
        'biogas_piscicultura': 45.0,
        'total_ch4_rsu_rpo': 200.0
    }
}

BIOGAS_SOURCE_LABELS = {
    'biogas_cana': '🌾 Cana-de-açúcar',
    'biogas_soja': '🌱 Soja',
    'biogas_milho': '🌽 Milho',
    'biogas_cafe': '☕ Café',
    'biogas_citros': '🍊 Citros',
    'biogas_bovino': '🐄 Bovinos',
    'biogas_suinos': '🐷 Suínos',
    'biogas_aves': '🐔 Aves',
    'biogas_piscicultura': '🐟 Piscicultura',
    'total_ch4_rsu_rpo': '🗑️ RSU + RPO'
}


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
        '🌾 Fontes Agrícolas': ['biogas_cana', 'biogas_soja', 'biogas_milho', 'biogas_cafe', 'biogas_citros'],
        '🐄 Fontes Pecuárias': ['biogas_bovino', 'biogas_suinos', 'biogas_aves', 'biogas_piscicultura'],
        '🗑️ Resíduos Urbanos': ['total_ch4_rsu_rpo']
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
    agricola_sources = ['biogas_cana', 'biogas_soja', 'biogas_milho', 'biogas_cafe', 'biogas_citros']
    pecuaria_sources = ['biogas_bovino', 'biogas_suinos', 'biogas_aves', 'biogas_piscicultura']
    
    df_scenario['total_agricola_scenario'] = df_scenario[[col for col in agricola_sources if col in df_scenario.columns]].sum(axis=1)
    df_scenario['total_pecuaria_scenario'] = df_scenario[[col for col in pecuaria_sources if col in df_scenario.columns]].sum(axis=1)
    
    return df_scenario


