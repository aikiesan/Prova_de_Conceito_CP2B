import streamlit as st


def create_gradient_header(title: str, subtitle: str = "", icon: str = "🌱") -> None:
    """Cria header simples"""
    st.markdown(f"# {icon} {title}")
    if subtitle:
        st.markdown(f"*{subtitle}*")


def create_section_header(title: str, icon: str = "📊", style: str = "success") -> None:
    """Cria header de seção simples"""
    st.markdown(f"## {icon} {title}")


def create_metric_card(icon: str, value: str, label: str, delta: str = "") -> None:
    """Cria card de métrica simples"""
    st.metric(label=f"{icon} {label}", value=value, delta=delta)


def show_loading_spinner() -> None:
    """Exibe spinner de carregamento"""
    st.info("Carregando...")


def inject_global_css(dark_mode: bool = False) -> None:
    """CSS básico sem problemas de sintaxe"""
    st.markdown("""
    <style>
    .stApp {
        font-family: 'Arial', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)


def create_theme_toggle() -> bool:
    """Toggle simples para tema"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    dark_mode = st.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_mode
    return dark_mode


def create_dashboard_header(residue_options: dict) -> tuple:
    """
    Cria header organizado para o dashboard com seleção múltipla de resíduos
    
    Args:
        residue_options: Dicionário com opções de resíduos
        
    Returns:
        tuple: (selected_residues, show_zero_values, max_municipalities, selection_mode)
    """
    
    # CSS melhorado para o header e funcionalidades fullscreen
    st.markdown("""
    <style>
    .dashboard-header {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .header-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    .control-section-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-bar {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 500;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    /* CSS para mapa fullscreen */
    .fullscreen-map {
        width: 100vw !important;
        height: 98vh !important;
        margin-left: calc(-50vw + 50%) !important;
        margin-top: -2rem !important;
        margin-bottom: -2rem !important;
        position: relative;
        z-index: 1;
    }
    
    /* Toggle button for sidebar */
    .sidebar-toggle {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 1000;
        background: #667eea;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 18px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    
    .sidebar-toggle:hover {
        background: #5a67d8;
        transform: scale(1.1);
    }
    
    /* Hide Streamlit sidebar when fullscreen mode */
    .fullscreen-mode .stSidebar {
        display: none !important;
    }
    
    /* Expand main content in fullscreen */
    .fullscreen-mode .main .block-container {
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container do header usando Streamlit nativo
    with st.container():
        st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
        st.markdown('<div class="header-title">🗺️ Mapa Interativo de Biogás - São Paulo</div>', unsafe_allow_html=True)
        
        # Layout em colunas com melhor organização
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.markdown('<div class="control-section-title">📊 Seleção de Resíduos</div>', unsafe_allow_html=True)
            
            # Modo de seleção
            selection_mode = st.radio(
                "Modo:",
                options=["🎯 Individual", "🔄 Múltiplos"],
                horizontal=True,
                key="dashboard_selection_mode",
                help="Individual: um resíduo por vez | Múltiplos: combine vários resíduos"
            )
            
            if selection_mode == "🎯 Individual":
                # Seleção individual (comportamento original)
                selected_residue_label = st.selectbox(
                    "Escolha um resíduo:",
                    options=list(residue_options.keys()),
                    index=0,
                    key="dashboard_single_residue_selector",
                    help="Visualize um tipo de resíduo por vez"
                )
                selected_residues = [residue_options[selected_residue_label]]
                selected_labels = [selected_residue_label]
            else:
                # Seleção múltipla
                selected_residue_labels = st.multiselect(
                    "Escolha vários resíduos:",
                    options=list(residue_options.keys()),
                    default=[list(residue_options.keys())[0]],  # Default primeiro item
                    key="dashboard_multi_residue_selector",
                    help="Selecione múltiplos resíduos para combinar seus potenciais"
                )
                
                if not selected_residue_labels:
                    selected_residue_labels = [list(residue_options.keys())[0]]  # Fallback
                
                selected_residues = [residue_options[label] for label in selected_residue_labels]
                selected_labels = selected_residue_labels
        
        with col2:
            st.markdown('<div class="control-section-title">⚙️ Opções</div>', unsafe_allow_html=True)
            show_zero_values = st.checkbox(
                "Incluir potencial zero",
                value=False,
                key="dashboard_show_zeros",
                help="Mostrar municípios mesmo com potencial de biogás zero"
            )
            
        with col3:
            st.markdown('<div class="control-section-title">🎯 Limite</div>', unsafe_allow_html=True)
            max_municipalities = st.slider(
                "Máximo de municípios:",
                min_value=25, 
                max_value=645, 
                value=200, 
                step=25,
                key="dashboard_max_municipalities",
                help="Limite o número de municípios exibidos no mapa"
            )
            
        with col4:
            st.markdown('<div class="control-section-title">🔄 Controles</div>', unsafe_allow_html=True)
            
            # Toggle para modo fullscreen
            fullscreen_mode = st.checkbox(
                "🖥️ Mapa Grande", 
                value=st.session_state.get('fullscreen_mode', False),
                key="dashboard_fullscreen_toggle",
                help="Expandir mapa para usar quase toda a tela"
            )
            st.session_state.fullscreen_mode = fullscreen_mode
            
            if st.button("🔄 Atualizar", use_container_width=True, type="primary"):
                st.cache_data.clear()
                # Limpar também o cache do banco de dados
                try:
                    import sys
                    import os
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    parent_dir = os.path.dirname(current_dir)
                    if parent_dir not in sys.path:
                        sys.path.append(parent_dir)
                    from database import clear_cache
                    clear_cache()
                except ImportError:
                    pass  # Se não conseguir importar, continua sem erro
                st.rerun()
        
        # Barra de status expandida para mostrar breakdown de múltiplos resíduos
        if 'filtered_count' in st.session_state:
            filtered_count = st.session_state.filtered_count
            potential_count = st.session_state.get('potential_count', filtered_count)
            
            if selection_mode == "🔄 Múltiplos" and len(selected_residues) > 1:
                # Status detalhado para múltiplos resíduos
                residue_names = [label.replace("⚡", "").replace("🌾", "").replace("🐄", "").replace("🗑️", "").replace("🐔", "").replace("🌱", "").replace("🌽", "").replace("☕", "").replace("🍊", "").replace("🐷", "").replace("🐟", "").replace("🌲", "").replace("🍃", "").strip() for label in selected_labels]
                residue_summary = " + ".join(residue_names[:3])  # Mostrar até 3 nomes
                if len(residue_names) > 3:
                    residue_summary += f" (+{len(residue_names)-3} mais)"
                
                status_text = f"🔄 Combinando: {residue_summary} | 📊 {filtered_count} municípios ({potential_count} com potencial)"
            else:
                # Status simples para seleção individual
                status_text = f"📊 Exibindo: {filtered_count} municípios ({potential_count} com potencial)"
            
            st.markdown(f'<div class="status-bar">{status_text}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    return selected_residues, show_zero_values, max_municipalities, selection_mode, fullscreen_mode


def create_map_section(title: str = "Visualização do Mapa"):
    """
    Cria uma seção estilizada para o mapa de forma simples
    
    Args:
        title: Título da seção do mapa
    """
    
    # CSS básico para melhorar a aparência 
    st.markdown("""
    <style>
    .map-section {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .map-section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        text-align: center;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Título da seção
    st.markdown(f'<div class="map-section-title">{title}</div>', unsafe_allow_html=True)