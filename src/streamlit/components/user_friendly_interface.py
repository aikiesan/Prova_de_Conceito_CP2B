"""
User-Friendly Interface Components for CP2B Dashboard
Enhanced UI components for better user experience and intuitive data exploration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import time
from datetime import datetime

class UserFriendlyInterface:
    """Enhanced user interface components for better usability"""
    
    def __init__(self):
        """Initialize the user-friendly interface"""
        self.help_messages = {
            'search': "💡 **Dica:** Use palavras-chave como 'São', 'Santos', 'Ribeirão' para encontrar municípios rapidamente",
            'filters': "💡 **Dica:** Combine múltiplos filtros para análises mais específicas",
            'visualization': "💡 **Dica:** Clique nos elementos dos gráficos para interagir",
            'export': "💡 **Dica:** Exporte os dados filtrados para análises externas"
        }

    def render_welcome_guide(self) -> None:
        """Render welcome guide for new users"""
        
        if st.session_state.get('show_welcome', True):
            st.info("👋 **Bem-vindo ao CP2B!** Sistema de Análise de Potencial de Biogás em São Paulo")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **🔍 Como usar:**
                1. Use os filtros na barra lateral
                2. Explore o mapa interativo
                3. Analise os gráficos e dados
                """)
            
            with col2:
                st.markdown("""
                **📊 Funcionalidades:**
                - Busca inteligente de municípios
                - Filtros por região e potencial
                - Visualizações interativas
                """)
            
            with col3:
                if st.button("❌ Não mostrar novamente"):
                    st.session_state.show_welcome = False
                    st.rerun()
            
            st.markdown("---")

    def render_quick_stats_cards(self, df: pd.DataFrame) -> None:
        """Render quick statistics cards"""
        
        if df.empty:
            st.warning("📊 Nenhum dado disponível para estatísticas")
            return
        
        # Calculate statistics
        total_municipalities = len(df)
        total_potential = df['total_final_nm_ano'].sum() if 'total_final_nm_ano' in df.columns else 0
        avg_potential = df['total_final_nm_ano'].mean() if 'total_final_nm_ano' in df.columns else 0
        max_potential = df['total_final_nm_ano'].max() if 'total_final_nm_ano' in df.columns else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🏛️ Municípios",
                f"{total_municipalities:,}",
                help="Total de municípios na análise atual"
            )
        
        with col2:
            potential_millions = total_potential / 1_000_000 if total_potential > 0 else 0
            st.metric(
                "⚡ Potencial Total",
                f"{potential_millions:.1f}M Nm³/ano",
                help="Somatória do potencial de biogás"
            )
        
        with col3:
            avg_thousands = avg_potential / 1_000 if avg_potential > 0 else 0
            st.metric(
                "📊 Média Municipal",
                f"{avg_thousands:.0f}k Nm³/ano",
                help="Potencial médio por município"
            )
        
        with col4:
            max_millions = max_potential / 1_000_000 if max_potential > 0 else 0
            st.metric(
                "🥇 Maior Potencial",
                f"{max_millions:.1f}M Nm³/ano",
                help="Maior potencial individual"
            )

    def render_data_quality_indicator(self, df: pd.DataFrame) -> None:
        """Render data quality indicators"""
        
        if df.empty:
            return
        
        # Calculate data quality metrics
        total_rows = len(df)
        complete_rows = len(df.dropna())
        completeness = (complete_rows / total_rows) * 100 if total_rows > 0 else 0
        
        # Check for zero values
        zero_potential = len(df[df['total_final_nm_ano'] == 0]) if 'total_final_nm_ano' in df.columns else 0
        non_zero_percentage = ((total_rows - zero_potential) / total_rows) * 100 if total_rows > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            color = "🟢" if completeness >= 90 else "🟡" if completeness >= 70 else "🔴"
            st.metric(
                f"{color} Completude dos Dados",
                f"{completeness:.1f}%",
                help="Percentual de dados completos (sem valores nulos)"
            )
        
        with col2:
            color = "🟢" if non_zero_percentage >= 80 else "🟡" if non_zero_percentage >= 60 else "🔴"
            st.metric(
                f"{color} Municípios c/ Potencial",
                f"{non_zero_percentage:.1f}%",
                help="Percentual de municípios com potencial > 0"
            )
        
        with col3:
            # Calculate data freshness (if timestamp available)
            st.metric(
                "📅 Dados Atualizados",
                "2024",
                help="Ano de referência dos dados"
            )

    def render_smart_insights(self, df: pd.DataFrame) -> None:
        """Render automatically generated insights"""
        
        if df.empty:
            return
        
        st.markdown("### 🧠 **Insights Automáticos**")
        
        insights = []
        
        # Top municipality insight
        if 'total_final_nm_ano' in df.columns and not df.empty:
            top_municipality = df.loc[df['total_final_nm_ano'].idxmax()]
            top_name = top_municipality.get('nm_mun', 'N/A')
            top_potential = top_municipality.get('total_final_nm_ano', 0)
            
            insights.append({
                'icon': '🏆',
                'title': 'Maior Potencial',
                'message': f"**{top_name}** tem o maior potencial: {top_potential/1000:.0f}k Nm³/ano",
                'type': 'success'
            })
        
        # Concentration insight
        if len(df) > 10:
            top_10_potential = df.nlargest(10, 'total_final_nm_ano')['total_final_nm_ano'].sum()
            total_potential = df['total_final_nm_ano'].sum()
            concentration = (top_10_potential / total_potential) * 100 if total_potential > 0 else 0
            
            insights.append({
                'icon': '📊',
                'title': 'Concentração',
                'message': f"Top 10 municípios concentram **{concentration:.1f}%** do potencial total",
                'type': 'info'
            })
        
        # Regional distribution
        agricultural_total = df.get('total_agricola_nm_ano', pd.Series([0])).sum()
        livestock_total = df.get('total_pecuaria_nm_ano', pd.Series([0])).sum()
        
        if agricultural_total > livestock_total:
            dominant_sector = "agrícola"
            dominance = (agricultural_total / (agricultural_total + livestock_total)) * 100
        elif livestock_total > agricultural_total:
            dominant_sector = "pecuário"  
            dominance = (livestock_total / (agricultural_total + livestock_total)) * 100
        else:
            dominant_sector = None
            dominance = 50
        
        if dominant_sector and dominance > 60:
            insights.append({
                'icon': '🌾' if dominant_sector == 'agrícola' else '🐄',
                'title': 'Setor Dominante',
                'message': f"O setor **{dominant_sector}** representa {dominance:.1f}% do potencial",
                'type': 'info'
            })
        
        # Render insights
        for insight in insights:
            if insight['type'] == 'success':
                st.success(f"{insight['icon']} **{insight['title']}:** {insight['message']}")
            elif insight['type'] == 'info':
                st.info(f"{insight['icon']} **{insight['title']}:** {insight['message']}")
            elif insight['type'] == 'warning':
                st.warning(f"{insight['icon']} **{insight['title']}:** {insight['message']}")

    def render_progress_indicators(self, current_step: str, total_steps: List[str]) -> None:
        """Render progress indicators for multi-step processes"""
        
        if not total_steps:
            return
        
        current_index = total_steps.index(current_step) if current_step in total_steps else 0
        progress = (current_index + 1) / len(total_steps)
        
        st.progress(progress)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"📍 **Etapa Atual:** {current_step}")
        with col2:
            st.caption(f"**{current_index + 1}/{len(total_steps)}**")

    def render_interactive_tutorial(self) -> None:
        """Render interactive tutorial/onboarding"""
        
        if st.session_state.get('show_tutorial', False):
            
            tutorial_step = st.session_state.get('tutorial_step', 0)
            
            tutorial_steps = [
                {
                    'title': 'Bem-vindo ao CP2B! 👋',
                    'content': 'Este sistema analisa o potencial de biogás nos 645 municípios de São Paulo.',
                    'action': 'Vamos começar!'
                },
                {
                    'title': 'Filtros na Barra Lateral 🔍',
                    'content': 'Use os filtros à esquerda para explorar dados específicos por município, região ou tipo de resíduo.',
                    'action': 'Próximo'
                },
                {
                    'title': 'Mapa Interativo 🗺️',
                    'content': 'Clique nos pontos do mapa para ver detalhes de cada município.',
                    'action': 'Próximo'
                },
                {
                    'title': 'Análises e Gráficos 📊',
                    'content': 'Explore as diferentes abas para análises detalhadas e comparações.',
                    'action': 'Próximo'
                },
                {
                    'title': 'Pronto para Explorar! 🚀',
                    'content': 'Agora você pode usar todas as funcionalidades do sistema.',
                    'action': 'Finalizar'
                }
            ]
            
            if tutorial_step < len(tutorial_steps):
                step_data = tutorial_steps[tutorial_step]
                
                st.info(f"**{step_data['title']}**\n\n{step_data['content']}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if tutorial_step > 0:
                        if st.button("⬅️ Anterior"):
                            st.session_state.tutorial_step = max(0, tutorial_step - 1)
                            st.rerun()
                
                with col2:
                    if st.button(f"➡️ {step_data['action']}"):
                        if tutorial_step < len(tutorial_steps) - 1:
                            st.session_state.tutorial_step = tutorial_step + 1
                        else:
                            st.session_state.show_tutorial = False
                            st.session_state.tutorial_step = 0
                        st.rerun()
                
                with col3:
                    if st.button("❌ Pular Tutorial"):
                        st.session_state.show_tutorial = False
                        st.session_state.tutorial_step = 0
                        st.rerun()

    def render_feedback_widget(self) -> None:
        """Render user feedback widget"""
        
        with st.expander("💬 Feedback do Usuário", expanded=False):
            feedback_type = st.selectbox(
                "Tipo de feedback:",
                ["Sugestão", "Bug Report", "Pergunta", "Elogio"],
                key="feedback_type"
            )
            
            feedback_text = st.text_area(
                "Sua mensagem:",
                placeholder="Conte-nos sua experiência ou sugestão...",
                key="feedback_text"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                user_email = st.text_input(
                    "Email (opcional):",
                    placeholder="seu.email@exemplo.com",
                    key="feedback_email"
                )
            
            with col2:
                rating = st.slider(
                    "Avaliação geral:",
                    min_value=1,
                    max_value=5,
                    value=5,
                    key="feedback_rating"
                )
            
            if st.button("📤 Enviar Feedback"):
                if feedback_text.strip():
                    # Here you would typically save the feedback to a database or file
                    # For now, we'll just show a success message
                    st.success("✅ Obrigado pelo seu feedback! Sua opinião é muito importante.")
                    
                    # Clear the form
                    st.session_state.feedback_text = ""
                    st.session_state.feedback_email = ""
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("⚠️ Por favor, escreva sua mensagem antes de enviar.")

    def render_shortcuts_help(self) -> None:
        """Render keyboard shortcuts and help"""
        
        with st.expander("⌨️ Atalhos e Ajuda", expanded=False):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🔍 Busca Rápida:**
                - Digite o nome do município na barra lateral
                - Use filtros rápidos para cenários comuns
                - Combine múltiplos filtros para análises específicas
                """)
            
            with col2:
                st.markdown("""
                **📊 Visualização:**
                - Clique nos gráficos para interagir
                - Use o zoom do mapa para focar em regiões
                - Exporte dados para análises externas
                """)
            
            st.markdown("""
            **💡 Dicas Úteis:**
            - 🏆 Use "Top 50" para ver os maiores potenciais rapidamente
            - 🌾 Filtre por setor (Agrícola/Pecuária/Urbano) para análises específicas
            - 🗺️ Explore diferentes regiões usando os filtros regionais
            - 📈 Use os sliders de potencial para encontrar faixas específicas
            """)

    def render_data_export_options(self, df: pd.DataFrame) -> None:
        """Render enhanced data export options"""
        
        if df.empty:
            return
        
        st.markdown("### 📤 **Opções de Exportação**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # CSV Export
            csv_data = df.to_csv(index=False)
            st.download_button(
                "📊 Exportar CSV",
                csv_data,
                file_name=f"cp2b_dados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Exportar dados filtrados em formato CSV"
            )
        
        with col2:
            # Excel Export (simplified - would need openpyxl)
            st.button(
                "📈 Exportar Excel",
                help="Exportar dados em formato Excel com múltiplas planilhas",
                disabled=True  # Would need implementation
            )
        
        with col3:
            # Summary Report
            if st.button("📋 Relatório Resumo", help="Gerar relatório resumido"):
                summary_data = self._generate_summary_report(df)
                st.download_button(
                    "⬇️ Download Resumo",
                    summary_data,
                    file_name=f"cp2b_resumo_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
        
        with col4:
            # GeoJSON Export (if coordinates available)
            st.button(
                "🗺️ Exportar GeoJSON",
                help="Exportar dados geoespaciais",
                disabled=True  # Would need implementation with coordinates
            )

    def render_comparison_tool(self, df: pd.DataFrame) -> None:
        """Render municipality comparison tool"""
        
        if df.empty or len(df) < 2:
            return
        
        st.markdown("### ⚖️ **Ferramenta de Comparação**")
        
        # Select municipalities to compare
        municipality_options = [f"{row['nm_mun']} ({row['cd_mun']})" 
                               for _, row in df.iterrows()]
        
        selected_municipalities = st.multiselect(
            "Selecione municípios para comparar (até 5):",
            options=municipality_options[:100],  # Limit options for performance
            max_selections=5,
            key="comparison_municipalities"
        )
        
        if len(selected_municipalities) >= 2:
            # Extract selected data
            selected_codes = [mun.split("(")[1].split(")")[0] for mun in selected_municipalities]
            comparison_df = df[df['cd_mun'].astype(str).isin(selected_codes)]
            
            # Render comparison chart
            self._render_comparison_chart(comparison_df)
            
            # Render comparison table
            self._render_comparison_table(comparison_df)

    # Helper methods
    def _generate_summary_report(self, df: pd.DataFrame) -> str:
        """Generate a text summary report"""
        
        if df.empty:
            return "Nenhum dado disponível para relatório."
        
        total_municipalities = len(df)
        total_potential = df['total_final_nm_ano'].sum() if 'total_final_nm_ano' in df.columns else 0
        avg_potential = df['total_final_nm_ano'].mean() if 'total_final_nm_ano' in df.columns else 0
        
        top_5 = df.nlargest(5, 'total_final_nm_ano')[['nm_mun', 'total_final_nm_ano']]
        
        report = f"""
RELATÓRIO RESUMIDO - CP2B SISTEMA DE BIOGÁS
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
============================================

ESTATÍSTICAS GERAIS:
- Total de Municípios: {total_municipalities:,}
- Potencial Total: {total_potential:,.0f} Nm³/ano
- Potencial Médio: {avg_potential:,.0f} Nm³/ano

TOP 5 MUNICÍPIOS:
"""
        for i, (_, row) in enumerate(top_5.iterrows(), 1):
            report += f"{i}. {row['nm_mun']}: {row['total_final_nm_ano']:,.0f} Nm³/ano\n"
        
        if 'total_agricola_nm_ano' in df.columns and 'total_pecuaria_nm_ano' in df.columns:
            agri_total = df['total_agricola_nm_ano'].sum()
            livestock_total = df['total_pecuaria_nm_ano'].sum()
            
            report += f"""
DISTRIBUIÇÃO POR SETOR:
- Agrícola: {agri_total:,.0f} Nm³/ano ({agri_total/total_potential*100:.1f}%)
- Pecuária: {livestock_total:,.0f} Nm³/ano ({livestock_total/total_potential*100:.1f}%)
"""
        
        return report

    def _render_comparison_chart(self, comparison_df: pd.DataFrame) -> None:
        """Render comparison chart"""
        
        # Prepare data for comparison
        chart_data = comparison_df[['nm_mun', 'total_final_nm_ano', 'total_agricola_nm_ano', 'total_pecuaria_nm_ano']].copy()
        
        fig = px.bar(
            chart_data,
            x='nm_mun',
            y=['total_final_nm_ano', 'total_agricola_nm_ano', 'total_pecuaria_nm_ano'],
            title="Comparação de Potencial de Biogás",
            labels={'value': 'Potencial (Nm³/ano)', 'nm_mun': 'Município'},
            barmode='group'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    def _render_comparison_table(self, comparison_df: pd.DataFrame) -> None:
        """Render comparison table"""
        
        st.markdown("**Tabela Comparativa:**")
        
        # Select key columns for comparison
        comparison_columns = ['nm_mun', 'total_final_nm_ano', 'total_agricola_nm_ano', 'total_pecuaria_nm_ano']
        display_df = comparison_df[comparison_columns].copy()
        
        # Format numbers
        numeric_columns = ['total_final_nm_ano', 'total_agricola_nm_ano', 'total_pecuaria_nm_ano']
        for col in numeric_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True)


def render_user_friendly_dashboard(df: pd.DataFrame) -> Dict[str, Any]:
    """Main function to render user-friendly dashboard components"""
    
    ui = UserFriendlyInterface()
    
    # Welcome guide for new users
    ui.render_welcome_guide()
    
    # Interactive tutorial
    if st.sidebar.checkbox("📚 Mostrar Tutorial", key="show_tutorial_toggle"):
        st.session_state.show_tutorial = True
    
    ui.render_interactive_tutorial()
    
    # Quick stats cards
    ui.render_quick_stats_cards(df)
    
    # Data quality indicators
    with st.expander("📊 Qualidade dos Dados", expanded=False):
        ui.render_data_quality_indicator(df)
    
    # Smart insights
    ui.render_smart_insights(df)
    
    # Comparison tool
    with st.expander("⚖️ Comparar Municípios", expanded=False):
        ui.render_comparison_tool(df)
    
    # Export options
    with st.expander("📤 Exportar Dados", expanded=False):
        ui.render_data_export_options(df)
    
    # Help and shortcuts
    ui.render_shortcuts_help()
    
    # Feedback widget
    ui.render_feedback_widget()
    
    return {
        'interface_loaded': True,
        'tutorial_active': st.session_state.get('show_tutorial', False),
        'welcome_shown': st.session_state.get('show_welcome', True)
    }