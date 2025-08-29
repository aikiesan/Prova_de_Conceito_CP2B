import streamlit as st


def create_gradient_header(title: str, subtitle: str = "", icon: str = "🌱") -> None:
    """Cria header limpo sem gradiente"""
    st.markdown(
        f"""
        <div class="clean-header fade-in">
            <h1>{icon} {title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_section_header(title: str, icon: str = "📊", style: str = "success") -> None:
    """Cria header de seção com gradiente"""
    style_class = f"section-header-{style}" if style != "success" else ""
    st.markdown(
        f"""
        <div class="section-header {style_class}">
            <h2>{icon} {title}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_metric_card(icon: str, value: str, label: str, delta: str = "") -> None:
    """Cria card de métrica estilizado"""
    st.markdown(
        f"""
        <div class="metric-card fade-in">
            <span class="metric-card-icon">{icon}</span>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-delta">{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_loading_spinner() -> None:
    """Exibe spinner de carregamento"""
    st.markdown(
        '<div class="loading-spinner"></div>',
        unsafe_allow_html=True,
    )


def inject_global_css(dark_mode: bool = False) -> None:
    # Definir cores baseado no modo
    if dark_mode:
        colors = {
            "bg_primary": "#000000",
            "bg_secondary": "#1a1a1a", 
            "bg_tertiary": "#2d2d2d",
            "text_primary": "#ffffff",
            "text_secondary": "#b3b3b3",
            "text_muted": "#808080",
            "border_color": "#404040",
            "shadow_opacity": "0.3"
        }
    else:
        colors = {
            "bg_primary": "#ffffff",
            "bg_secondary": "#f7fafc",
            "bg_tertiary": "#edf2f7", 
            "text_primary": "#1a202c",
            "text_secondary": "#4a5568",
            "text_muted": "#718096",
            "border_color": "#e2e8f0",
            "shadow_opacity": "0.1"
        }

    # Build CSS string without f-string to avoid % conflicts
    css_styles = f"""
        <style>
        /* ==== SISTEMA DE CORES MODERNO ==== */
        :root {{
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-gradient: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            --warning-gradient: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
            --info-gradient: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            --danger-gradient: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
            
            /* Cores dinâmicas baseadas no modo */
            --bg-primary: {colors["bg_primary"]};
            --bg-secondary: {colors["bg_secondary"]};
            --bg-tertiary: {colors["bg_tertiary"]};
            --text-primary: {colors["text_primary"]};
            --text-secondary: {colors["text_secondary"]};
            --text-muted: {colors["text_muted"]};
            --border-color: {colors["border_color"]};
            --shadow-sm: 0 1px 3px rgba(0,0,0,{colors["shadow_opacity"]}), 0 1px 2px rgba(0,0,0,0.24);
            --shadow-md: 0 4px 6px rgba(0,0,0,{colors["shadow_opacity"]}), 0 1px 3px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 25px rgba(0,0,0,{colors["shadow_opacity"]}), 0 4px 10px rgba(0,0,0,0.1);
            --radius: 12px;
            --radius-sm: 8px;
        }}"""

    # Add the rest of CSS without f-string formatting
    css_styles += """
        
        /* ==== LAYOUT E TIPOGRAFIA ==== */
        .main > div {
            padding-top: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .stApp {
            background: var(--bg-primary) !important;
        }
        
        /* ==== HEADERS LIMPOS SEM GRADIENTE ==== */
        .clean-header {
            background: var(--bg-secondary);
            color: var(--text-primary);
            padding: 1.5rem 2rem;
            border-radius: var(--radius);
            margin-bottom: 2rem;
            box-shadow: var(--shadow-md);
            text-align: center;
            border: 1px solid var(--border-color);
        }
        
        .clean-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
        }
        
        .clean-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.8;
            font-size: 1.1rem;
            color: var(--text-secondary);
        }
        
        /* ==== CARDS DE MÉTRICAS APRIMORADOS ==== */
        .metric-card {
            background: var(--bg-primary);
            border-radius: var(--radius);
            padding: 1.5rem;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            color: var(--text-primary);
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
        }
        
        .metric-card-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0.5rem 0;
            line-height: 1.2;
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
        }
        
        .metric-delta {
            color: var(--text-muted);
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }
        
        /* ==== SEÇÕES LIMPAS SEM GRADIENTE ==== */
        .section-header {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            padding: 1rem 1.5rem;
            border-radius: var(--radius);
            margin: 2rem 0 1rem 0;
            box-shadow: var(--shadow-sm);
            border-left: 4px solid #48bb78;
        }
        
        .section-header h2 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-primary);
        }
        
        .section-header-info {
            border-left-color: #4299e1;
        }
        
        .section-header-warning {
            border-left-color: #ed8936;
        }
        
        .section-header-danger {
            border-left-color: #f56565;
        }
        
        /* ==== SIDEBAR APRIMORADA ==== */
        .sidebar .sidebar-content {
            background: var(--bg-primary);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-sm);
            color: var(--text-primary);
        }

        /* Streamlit sidebar styling */
        .css-1d391kg {
            background: var(--bg-primary) !important;
        }

        .css-1lcbmhc {
            background: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        /* ==== TABELAS E DATAFRAMES ==== */
        .stDataFrame > div {
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow-md);
        }
        
        /* ==== BOTÕES APRIMORADOS ==== */
        .stButton > button {
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: var(--radius-sm);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-sm);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        /* ==== SELECTBOX E INPUTS ==== */
        .stSelectbox > div > div {
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        .stNumberInput > div > div {
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }

        .stTextInput > div > div {
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        /* ==== PROGRESS BARS ==== */
        .stProgress > div > div > div {
            background: var(--primary-gradient);
            border-radius: var(--radius-sm);
        }
        
        /* ==== ALERTAS E NOTIFICAÇÕES ==== */
        .stAlert {
            border-radius: var(--radius);
            border: none;
            box-shadow: var(--shadow-sm);
        }
        
        /* ==== TABS MODERNAS ==== */
        .stTabs > div > div > div > div {
            background: var(--bg-secondary);
            border-radius: var(--radius) var(--radius) 0 0;
            border-bottom: 3px solid transparent;
            color: var(--text-primary);
        }
        
        .stTabs > div > div > div > div[aria-selected="true"] {
            border-bottom: 3px solid #667eea;
            background: var(--primary-gradient);
            color: white !important;
        }

        /* Métricas do Streamlit */
        [data-testid="metric-container"] {
            background: var(--bg-primary) !important;
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            color: var(--text-primary) !important;
        }

        [data-testid="metric-container"] > div {
            color: var(--text-primary) !important;
        }

        [data-testid="metric-container"] label {
            color: var(--text-secondary) !important;
        }
        
        /* ==== LOADING E SPINNERS ==== */
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        
        .loading-spinner::after {
            content: '';
            width: 40px;
            height: 40px;
            border: 4px solid var(--border-color);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* ==== RESPONSIVIDADE ==== */
        @media (max-width: 768px) {
            .main > div {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            .gradient-header h1 {
                font-size: 2rem;
            }
            
            .metric-value {
                font-size: 1.5rem;
            }
            
            .metric-card {
                padding: 1rem;
            }
        }
        
        /* ==== ACESSIBILIDADE ==== */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        
        /* ==== ANIMAÇÕES SUAVES ==== */
        * {
            transition: all 0.2s ease;
        }
        
        .fade-in {
            animation: fadeIn 0.6s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* ==== UTILITÁRIOS ==== */
        .text-center { text-align: center; }
        .text-muted { color: var(--text-muted); }
        .mb-0 { margin-bottom: 0 !important; }
        .mb-1 { margin-bottom: 0.5rem !important; }
        .mb-2 { margin-bottom: 1rem !important; }
        .mt-0 { margin-top: 0 !important; }
        .mt-1 { margin-top: 0.5rem !important; }
        .mt-2 { margin-top: 1rem !important; }
        </style>
        """

    st.markdown(
        css_styles,
        unsafe_allow_html=True,
    )
        
        /* ==== LAYOUT E TIPOGRAFIA ==== */
        .main > div {
            padding-top: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .stApp {
            background: var(--bg-primary) !important;
        }
        
        /* ==== HEADERS LIMPOS SEM GRADIENTE ==== */
        .clean-header {
            background: var(--bg-secondary);
            color: var(--text-primary);
            padding: 1.5rem 2rem;
            border-radius: var(--radius);
            margin-bottom: 2rem;
            box-shadow: var(--shadow-md);
            text-align: center;
            border: 1px solid var(--border-color);
        }
        
        .clean-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
        }
        
        .clean-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.8;
            font-size: 1.1rem;
            color: var(--text-secondary);
        }
        
        /* ==== CARDS DE MÉTRICAS APRIMORADOS ==== */
        .metric-card {
            background: var(--bg-primary);
            border-radius: var(--radius);
            padding: 1.5rem;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            color: var(--text-primary);
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
        }
        
        .metric-card-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            display: block;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0.5rem 0;
            line-height: 1.2;
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
        }
        
        .metric-delta {
            color: var(--text-muted);
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }
        
        /* ==== SEÇÕES LIMPAS SEM GRADIENTE ==== */
        .section-header {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            padding: 1rem 1.5rem;
            border-radius: var(--radius);
            margin: 2rem 0 1rem 0;
            box-shadow: var(--shadow-sm);
            border-left: 4px solid #48bb78;
        }
        
        .section-header h2 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-primary);
        }
        
        .section-header-info {
            border-left-color: #4299e1;
        }
        
        .section-header-warning {
            border-left-color: #ed8936;
        }
        
        .section-header-danger {
            border-left-color: #f56565;
        }
        
        /* ==== SIDEBAR APRIMORADA ==== */
        .sidebar .sidebar-content {
            background: var(--bg-primary);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-sm);
            color: var(--text-primary);
        }

        /* Streamlit sidebar styling */
        .css-1d391kg {
            background: var(--bg-primary) !important;
        }

        .css-1lcbmhc {
            background: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
        }
        
        /* ==== TABELAS E DATAFRAMES ==== */
        .stDataFrame > div {
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow-md);
        }
        
        /* ==== BOTÕES APRIMORADOS ==== */
        .stButton > button {
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: var(--radius-sm);
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-sm);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        /* ==== SELECTBOX E INPUTS ==== */
        .stSelectbox > div > div {
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        .stNumberInput > div > div {
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }

        .stTextInput > div > div {
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        
        /* ==== PROGRESS BARS ==== */
        .stProgress > div > div > div {
            background: var(--primary-gradient);
            border-radius: var(--radius-sm);
        }
        
        /* ==== ALERTAS E NOTIFICAÇÕES ==== */
        .stAlert {
            border-radius: var(--radius);
            border: none;
            box-shadow: var(--shadow-sm);
        }
        
        /* ==== TABS MODERNAS ==== */
        .stTabs > div > div > div > div {
            background: var(--bg-secondary);
            border-radius: var(--radius) var(--radius) 0 0;
            border-bottom: 3px solid transparent;
            color: var(--text-primary);
        }
        
        .stTabs > div > div > div > div[aria-selected="true"] {
            border-bottom: 3px solid #667eea;
            background: var(--primary-gradient);
            color: white !important;
        }

        /* Métricas do Streamlit */
        [data-testid="metric-container"] {
            background: var(--bg-primary) !important;
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 1rem;
            color: var(--text-primary) !important;
        }

        [data-testid="metric-container"] > div {
            color: var(--text-primary) !important;
        }

        [data-testid="metric-container"] label {
            color: var(--text-secondary) !important;
        }
        
        /* ==== LOADING E SPINNERS ==== */
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        
        .loading-spinner::after {
            content: '';
            width: 40px;
            height: 40px;
            border: 4px solid var(--border-color);
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0%% { transform: rotate(0deg); }
            100%% { transform: rotate(360deg); }
        }
        
        /* ==== RESPONSIVIDADE ==== */
        @media (max-width: 768px) {
            .main > div {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            .gradient-header h1 {
                font-size: 2rem;
            }
            
            .metric-value {
                font-size: 1.5rem;
            }
            
            .metric-card {
                padding: 1rem;
            }
        }
        
        /* ==== ACESSIBILIDADE ==== */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        
        /* ==== ANIMAÇÕES SUAVES ==== */
        * {
            transition: all 0.2s ease;
        }
        
        .fade-in {
            animation: fadeIn 0.6s ease-in;
        }
        
        @keyframes fadeIn {
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }
        
        /* ==== UTILITÁRIOS ==== */
        .text-center { text-align: center; }
        .text-muted { color: var(--text-muted); }
        .mb-0 { margin-bottom: 0 !important; }
        .mb-1 { margin-bottom: 0.5rem !important; }
        .mb-2 { margin-bottom: 1rem !important; }
        .mt-0 { margin-top: 0 !important; }
        .mt-1 { margin-top: 0.5rem !important; }
        .mt-2 { margin-top: 1rem !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_theme_toggle() -> bool:
    """Cria toggle para alternar entre dark/light mode"""
    
    # Inicializar estado se não existir
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        dark_mode = st.toggle(
            "🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode",
            value=st.session_state.dark_mode,
            help="Alternar entre tema claro e escuro"
        )
        
        # Atualizar estado se mudou
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
    
    return st.session_state.dark_mode


