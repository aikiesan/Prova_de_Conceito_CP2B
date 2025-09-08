"""
Scientific References Display Component for CP2B Dashboard
Simple component to display scientific references with interactive buttons
"""

import streamlit as st
import sys
import os

def render_scientific_references_section():
    """Render the scientific references section with buttons for each residue type"""
    
    try:
        # Try both import paths
        try:
            from utils.scientific_references import show_complete_bibliography, show_biogas_references
        except ImportError:
            from ..utils.scientific_references import show_complete_bibliography, show_biogas_references
        
        st.markdown("---")
        st.markdown("### 📚 Referências Científicas")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("""
            **Fatores de Conversão Baseados em Literatura Científica:**
            
            Os valores de conversão (m³/ton) utilizados neste sistema são fundamentados em mais de 35 estudos peer-reviewed, 
            incluindo pesquisas específicas para condições brasileiras e internacionais.
            """)
        
        with col2:
            if st.button("📖 Ver Bibliografia Completa", key="show_bibliography_main"):
                st.session_state.show_scientific_refs = True
        
        # Show complete bibliography if requested
        if st.session_state.get('show_scientific_refs', False):
            with st.expander("📚 Bibliografia Científica Completa", expanded=True):
                try:
                    show_complete_bibliography()
                except Exception as e:
                    st.error(f"Erro ao carregar bibliografia: {e}")
                
                if st.button("🔺 Fechar Bibliografia", key="close_bibliography"):
                    st.session_state.show_scientific_refs = False
                    st.rerun()
        
        # Scientific reference buttons for specific residues
        st.markdown("**📖 Referências por Tipo de Resíduo:**")
        
        ref_col1, ref_col2, ref_col3 = st.columns(3)
        
        # Define residue sources and their labels
        agricultural_sources = {
            'biogas_cana_nm_ano': '🌾 Cana-de-açúcar',
            'biogas_soja_nm_ano': '🌱 Soja', 
            'biogas_milho_nm_ano': '🌽 Milho',
            'biogas_cafe_nm_ano': '☕ Café'
        }
        
        livestock_sources = {
            'biogas_bovinos_nm_ano': '🐄 Bovinos',
            'biogas_suino_nm_ano': '🐷 Suínos',
            'biogas_aves_nm_ano': '🐔 Aves',
            'biogas_piscicultura_nm_ano': '🐟 Piscicultura'
        }
        
        other_sources = {
            'biogas_citros_nm_ano': '🍊 Citros'
        }
        
        with ref_col1:
            st.markdown("**🌾 Fontes Agrícolas:**")
            for source, label in agricultural_sources.items():
                if st.button(f"📚 {label.split(' ', 1)[1]}", key=f"ref_{source}"):
                    try:
                        show_biogas_references(source)
                    except Exception as e:
                        st.error(f"Erro ao carregar referências: {e}")
        
        with ref_col2:
            st.markdown("**🐄 Fontes Pecuárias:**")
            for source, label in livestock_sources.items():
                if st.button(f"📚 {label.split(' ', 1)[1]}", key=f"ref_{source}"):
                    try:
                        show_biogas_references(source)
                    except Exception as e:
                        st.error(f"Erro ao carregar referências: {e}")
        
        with ref_col3:
            st.markdown("**🍊 Outros:**")
            for source, label in other_sources.items():
                if st.button(f"📚 {label.split(' ', 1)[1]}", key=f"ref_{source}"):
                    try:
                        show_biogas_references(source)
                    except Exception as e:
                        st.error(f"Erro ao carregar referências: {e}")
        
        # Add conversion factors info
        st.markdown("---")
        with st.expander("ℹ️ Informações sobre Fatores de Conversão"):
            st.markdown("""
            **Metodologia dos Fatores de Conversão:**
            
            - **Cenário Conservador**: Valores mínimos baseados em condições sub-ótimas
            - **Cenário Moderado**: Valores médios para condições típicas brasileiras  
            - **Cenário Otimista**: Valores máximos com tecnologia avançada e condições ideais
            
            **Fontes Científicas Incluem:**
            - Estudos brasileiros específicos para clima tropical
            - Pesquisas internacionais adaptadas para condições locais
            - Normas técnicas IEA Bioenergy Task 37
            - Dissertações e teses de universidades nacionais
            
            **Nota**: Os fatores podem variar regionalmente devido a diferenças climáticas, 
            tecnológicas e de composição dos resíduos.
            """)
        
    except Exception as e:
        st.error(f"Erro ao carregar sistema de referências científicas: {e}")
        st.info("As referências científicas estão temporariamente indisponíveis.")


def render_conversion_factors_with_references():
    """Render conversion factors with scientific reference buttons"""
    
    conversion_factors = {
        'Conservador': {
            'biogas_cana_nm_ano': 50.0,      
            'biogas_soja_nm_ano': 35.0,      
            'biogas_milho_nm_ano': 40.0,     
            'biogas_cafe_nm_ano': 45.0,      
            'biogas_citros_nm_ano': 30.0,    
            'biogas_bovinos_nm_ano': 25.0,   
            'biogas_suino_nm_ano': 60.0,     
            'biogas_aves_nm_ano': 25.0,      
            'biogas_piscicultura_nm_ano': 20.0,
        }
    }
    
    labels = {
        'biogas_cana_nm_ano': '🌾 Cana-de-açúcar',
        'biogas_soja_nm_ano': '🌱 Soja',
        'biogas_milho_nm_ano': '🌽 Milho',
        'biogas_cafe_nm_ano': '☕ Café',
        'biogas_citros_nm_ano': '🍊 Citros',
        'biogas_bovinos_nm_ano': '🐄 Bovinos',
        'biogas_suino_nm_ano': '🐷 Suínos',
        'biogas_aves_nm_ano': '🐔 Aves',
        'biogas_piscicultura_nm_ano': '🐟 Piscicultura',
    }
    
    st.markdown("### 📊 Fatores de Conversão (Cenário Conservador)")
    
    col1, col2, col3 = st.columns(3)
    
    sources = list(conversion_factors['Conservador'].keys())
    
    for i, source in enumerate(sources):
        col = [col1, col2, col3][i % 3]
        
        with col:
            factor = conversion_factors['Conservador'][source]
            label = labels[source]
            
            # Create metric with reference button
            st.metric(label, f"{factor} m³/ton")
            
            # Add small reference button
            if st.button(f"📚", key=f"factor_ref_{source}", help=f"Ver referências científicas para {label}"):
                try:
                    from utils.scientific_references import show_biogas_references
                    show_biogas_references(source)
                except ImportError:
                    from ..utils.scientific_references import show_biogas_references
                    show_biogas_references(source)
                except Exception as e:
                    st.error(f"Erro ao carregar referências: {e}")