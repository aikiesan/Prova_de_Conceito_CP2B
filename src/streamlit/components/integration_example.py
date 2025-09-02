"""
Integration Example - How to Use Enhanced Filters in Your App
This shows how to integrate the new user-friendly components with your existing app.py
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

# Import the new enhanced components
try:
    from .enhanced_filters import render_enhanced_filters_sidebar, EnhancedFilters
    from .user_friendly_interface import render_user_friendly_dashboard, UserFriendlyInterface
except ImportError:
    # Fallback for testing
    from enhanced_filters import render_enhanced_filters_sidebar, EnhancedFilters
    from user_friendly_interface import render_user_friendly_dashboard, UserFriendlyInterface

def enhanced_dashboard_page(df: pd.DataFrame, page_config: dict) -> None:
    """
    Enhanced version of your dashboard page with new user-friendly features
    Replace or enhance your existing render_dashboard_page with this
    """
    
    # Render enhanced filters in sidebar and get filtered data
    filter_results = render_enhanced_filters_sidebar(df)
    filtered_df = filter_results['filtered_data']
    applied_filters = filter_results['applied_filters']
    
    # Show filter summary if filters are applied
    if len(filtered_df) < len(df):
        reduction = filter_results['filter_summary']['reduction_percent']
        st.info(f"🎯 **{len(filtered_df)} municípios selecionados** (redução: {reduction:.1f}%)")
    
    # Render user-friendly interface components
    ui_results = render_user_friendly_dashboard(filtered_df)
    
    # Your existing dashboard content with enhanced data
    st.markdown("---")
    
    # Enhanced residue selection (improved version of your existing selector)
    residue_options = {
        "⚡ Potencial Total": "total_final_nm_ano",
        "🌾 Total Agrícola": "total_agricola_nm_ano", 
        "🐄 Total Pecuária": "total_pecuaria_nm_ano",
        "🗑️ Resíduos Urbanos": "urban_combined",
        "🌾 Cana-de-açúcar": "biogas_cana_nm_ano",
        "🌱 Soja": "biogas_soja_nm_ano",
        "🌽 Milho": "biogas_milho_nm_ano",
        "☕ Café": "biogas_cafe_nm_ano",
        "🍊 Citros": "biogas_citros_nm_ano",
        "🐄 Bovinos": "biogas_bovinos_nm_ano",
        "🐷 Suínos": "biogas_suino_nm_ano",
        "🐔 Aves": "biogas_aves_nm_ano",
        "🐟 Piscicultura": "biogas_piscicultura_nm_ano"
    }
    
    # Enhanced header with better UX
    st.markdown("## 🗺️ **Visualização Interativa**")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_residue_display = st.selectbox(
            "Tipo de resíduo para visualização:",
            options=list(residue_options.keys()),
            key="enhanced_residue_selector",
            help="Selecione o tipo de resíduo para colorir o mapa"
        )
        selected_residue = residue_options[selected_residue_display]
    
    with col2:
        show_zero_values = st.checkbox(
            "Incluir potencial zero",
            value=True,
            key="enhanced_show_zeros",
            help="Mostrar municípios sem potencial"
        )
    
    with col3:
        fullscreen_mode = st.checkbox(
            "🖥️ Tela Cheia",
            key="enhanced_fullscreen",
            help="Maximizar visualização do mapa"
        )
    
    # Apply residue-specific filtering to the already filtered data
    final_df = apply_residue_visualization_filters(
        filtered_df, 
        selected_residue, 
        show_zero_values
    )
    
    if final_df.empty:
        st.warning("🔍 Nenhum dado encontrado com os filtros aplicados.")
        return
    
    # Apply fullscreen CSS if needed
    if fullscreen_mode:
        st.markdown("""
        <style>
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        .stSidebar {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Your existing map rendering (enhanced with filtered data)
    try:
        from .maps import render_map
        
        render_map(
            final_df,
            selected_municipios=applied_filters.get('search', {}).get('selected_municipalities', []),
            filters={
                'pre_filtered': True,
                'selected_residue': selected_residue,
                'enhanced_filters_applied': True,
                'filter_summary': filter_results['filter_summary']
            }
        )
        
        if not fullscreen_mode:
            st.caption("💡 Use os filtros da barra lateral para análises mais específicas")
        
    except ImportError:
        st.error("❌ Componente de mapa não encontrado")
    
    # Additional analysis sections (only show if not in fullscreen)
    if not fullscreen_mode:
        render_enhanced_analysis_sections(final_df, selected_residue)

def render_enhanced_analysis_sections(df: pd.DataFrame, selected_residue: str) -> None:
    """Render enhanced analysis sections with better UX"""
    
    st.markdown("---")
    
    # Tabbed interface for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 **Análise Rápida**",
        "🏆 **Rankings**", 
        "📈 **Gráficos**",
        "📋 **Dados Detalhados**"
    ])
    
    with tab1:
        render_quick_analysis(df, selected_residue)
    
    with tab2:
        render_enhanced_rankings(df, selected_residue)
    
    with tab3:
        render_enhanced_charts(df, selected_residue)
    
    with tab4:
        render_enhanced_data_table(df, selected_residue)

def render_quick_analysis(df: pd.DataFrame, selected_residue: str) -> None:
    """Render quick analysis with key insights"""
    
    if df.empty:
        st.info("Nenhum dado disponível")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 **Resumo da Seleção**")
        
        total_potential = df[selected_residue].sum() if selected_residue in df.columns else 0
        non_zero_count = len(df[df[selected_residue] > 0]) if selected_residue in df.columns else 0
        avg_potential = df[df[selected_residue] > 0][selected_residue].mean() if selected_residue in df.columns and non_zero_count > 0 else 0
        
        st.metric("Total do Resíduo", f"{total_potential/1_000_000:.1f}M Nm³/ano")
        st.metric("Municípios Produtores", f"{non_zero_count:,}")
        st.metric("Média dos Produtores", f"{avg_potential/1_000:.0f}k Nm³/ano")
    
    with col2:
        st.markdown("### 📊 **Distribuição**")
        
        # Simple distribution chart
        if selected_residue in df.columns and not df[selected_residue].isna().all():
            
            # Create bins for distribution
            non_zero_data = df[df[selected_residue] > 0][selected_residue]
            
            if len(non_zero_data) > 0:
                import plotly.express as px
                
                fig = px.histogram(
                    x=non_zero_data,
                    nbins=20,
                    title="Distribuição do Potencial",
                    labels={'x': 'Potencial (Nm³/ano)', 'y': 'Número de Municípios'}
                )
                
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sem dados de potencial para este resíduo")

def render_enhanced_rankings(df: pd.DataFrame, selected_residue: str) -> None:
    """Render enhanced rankings with better visualization"""
    
    if df.empty:
        st.info("Nenhum dado disponível")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 **Top 10 - Resíduo Selecionado**")
        
        if selected_residue in df.columns:
            top_10 = df.nlargest(10, selected_residue)
            
            for i, (_, row) in enumerate(top_10.iterrows(), 1):
                potential = row[selected_residue]
                municipality = row.get('nm_mun', 'N/A')
                
                # Create progress bar effect
                max_potential = top_10[selected_residue].max()
                progress = potential / max_potential if max_potential > 0 else 0
                
                st.markdown(f"""
                **#{i} {municipality}**  
                `{potential/1_000:.0f}k Nm³/ano`
                """)
                st.progress(progress)
        else:
            st.warning("Coluna não encontrada nos dados")
    
    with col2:
        st.markdown("### ⚡ **Top 10 - Total Geral**")
        
        if 'total_final_nm_ano' in df.columns:
            top_10_total = df.nlargest(10, 'total_final_nm_ano')
            
            for i, (_, row) in enumerate(top_10_total.iterrows(), 1):
                total_potential = row['total_final_nm_ano']
                municipality = row.get('nm_mun', 'N/A')
                
                # Create progress bar effect
                max_potential = top_10_total['total_final_nm_ano'].max()
                progress = total_potential / max_potential if max_potential > 0 else 0
                
                st.markdown(f"""
                **#{i} {municipality}**  
                `{total_potential/1_000:.0f}k Nm³/ano`
                """)
                st.progress(progress)

def render_enhanced_charts(df: pd.DataFrame, selected_residue: str) -> None:
    """Render enhanced charts with better interactivity"""
    
    if df.empty:
        st.info("Nenhum dados disponível")
        return
    
    chart_type = st.selectbox(
        "Tipo de gráfico:",
        ["Barras", "Dispersão", "Mapa de Calor", "Comparativo"],
        key="enhanced_chart_type"
    )
    
    if chart_type == "Barras":
        render_enhanced_bar_chart(df, selected_residue)
    elif chart_type == "Dispersão":
        render_scatter_plot(df, selected_residue)
    elif chart_type == "Mapa de Calor":
        render_heatmap(df, selected_residue)
    elif chart_type == "Comparativo":
        render_comparative_chart(df)

def render_enhanced_bar_chart(df: pd.DataFrame, selected_residue: str) -> None:
    """Enhanced bar chart with more options"""
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        top_n = st.slider("Top N municípios:", 5, 50, 20, key="bar_top_n")
        show_values = st.checkbox("Mostrar valores", value=True, key="bar_show_values")
    
    with col1:
        if selected_residue in df.columns:
            import plotly.express as px
            
            chart_data = df.nlargest(top_n, selected_residue)
            
            fig = px.bar(
                chart_data,
                x='nm_mun',
                y=selected_residue,
                title=f"Top {top_n} Municípios - {selected_residue}",
                labels={selected_residue: 'Potencial (Nm³/ano)', 'nm_mun': 'Município'},
                color=selected_residue,
                color_continuous_scale='Viridis'
            )
            
            if show_values:
                fig.update_traces(texttemplate='%{y:,.0f}', textposition='outside')
            
            fig.update_layout(
                height=500,
                xaxis_tickangle=-45,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)

def render_scatter_plot(df: pd.DataFrame, selected_residue: str) -> None:
    """Render scatter plot for correlation analysis"""
    
    if 'total_final_nm_ano' in df.columns and selected_residue in df.columns:
        import plotly.express as px
        
        fig = px.scatter(
            df,
            x=selected_residue,
            y='total_final_nm_ano',
            hover_data=['nm_mun'],
            title=f"Correlação: {selected_residue} vs Total",
            labels={
                selected_residue: f'{selected_residue} (Nm³/ano)',
                'total_final_nm_ano': 'Total Geral (Nm³/ano)'
            },
            trendline="ols"
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate and show correlation
        correlation = df[selected_residue].corr(df['total_final_nm_ano'])
        st.metric("Correlação", f"{correlation:.3f}")

def render_heatmap(df: pd.DataFrame, selected_residue: str) -> None:
    """Render correlation heatmap"""
    
    # Select numeric columns for heatmap
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    biogas_cols = [col for col in numeric_cols if 'biogas_' in col or 'total_' in col or 'potencial' in col]
    
    if len(biogas_cols) >= 2:
        import plotly.express as px
        
        correlation_matrix = df[biogas_cols].corr()
        
        fig = px.imshow(
            correlation_matrix,
            title="Matriz de Correlação - Tipos de Resíduos",
            color_continuous_scale='RdBu_r',
            aspect="auto"
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

def render_comparative_chart(df: pd.DataFrame) -> None:
    """Render comparative analysis chart"""
    
    # Compare main categories
    categories = {
        'Agrícola': 'total_agricola_nm_ano',
        'Pecuária': 'total_pecuaria_nm_ano'
    }
    
    available_categories = {k: v for k, v in categories.items() if v in df.columns}
    
    if available_categories:
        import plotly.express as px
        
        # Prepare data for comparison
        comparison_data = []
        for category, column in available_categories.items():
            total = df[column].sum()
            comparison_data.append({'Categoria': category, 'Total': total})
        
        import pandas as pd
        comparison_df = pd.DataFrame(comparison_data)
        
        fig = px.pie(
            comparison_df,
            values='Total',
            names='Categoria',
            title="Distribuição por Categoria"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_enhanced_data_table(df: pd.DataFrame, selected_residue: str) -> None:
    """Render enhanced data table with better formatting"""
    
    if df.empty:
        st.info("Nenhum dado disponível")
        return
    
    # Column selection
    col1, col2 = st.columns(2)
    
    with col1:
        show_all_columns = st.checkbox("Mostrar todas as colunas", key="table_all_cols")
    
    with col2:
        max_rows = st.selectbox("Máximo de linhas:", [25, 50, 100, "Todas"], index=1, key="table_max_rows")
    
    # Prepare display dataframe
    if show_all_columns:
        display_df = df.copy()
    else:
        # Show key columns
        key_columns = ['nm_mun', 'cd_mun', selected_residue, 'total_final_nm_ano']
        display_df = df[[col for col in key_columns if col in df.columns]].copy()
    
    # Apply row limit
    if max_rows != "Todas":
        display_df = display_df.head(max_rows)
    
    # Format numeric columns
    numeric_columns = display_df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "0")
    
    st.dataframe(display_df, use_container_width=True)
    
    # Table summary
    st.caption(f"📊 Mostrando {len(display_df)} de {len(df)} municípios")

def apply_residue_visualization_filters(df: pd.DataFrame, selected_residue: str, show_zero_values: bool) -> pd.DataFrame:
    """Apply filters specific to residue visualization"""
    
    filtered_df = df.copy()
    
    # Filter zero values if needed
    if not show_zero_values and selected_residue in filtered_df.columns:
        filtered_df = filtered_df[filtered_df[selected_residue] > 0]
    
    # Set display_value for map visualization
    if selected_residue in filtered_df.columns:
        filtered_df['display_value'] = filtered_df[selected_residue]
    else:
        filtered_df['display_value'] = filtered_df.get('total_final_nm_ano', 0)
    
    return filtered_df


# Example of how to integrate with your existing app.py:
"""
# In your app.py, replace the render_dashboard_page method with:

def render_dashboard_page(self, df: pd.DataFrame, page_config: dict) -> None:
    # Use the enhanced dashboard page
    enhanced_dashboard_page(df, page_config)

# Or add it as a new page:
elif current_page == "enhanced_dashboard":
    enhanced_dashboard_page(df, page_config)
"""