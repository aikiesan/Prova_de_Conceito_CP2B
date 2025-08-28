import streamlit as st


def create_gradient_header(title: str, subtitle: str = "", icon: str = "🌱") -> None:
    """Cria header com gradiente moderno"""
    st.markdown(
        f"""
        <div class="gradient-header fade-in">
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


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        /* ==== SISTEMA DE CORES MODERNO ==== */
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-gradient: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            --warning-gradient: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
            --info-gradient: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            --danger-gradient: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
            
            --bg-primary: #ffffff;
            --bg-secondary: #f7fafc;
            --bg-tertiary: #edf2f7;
            --text-primary: #1a202c;
            --text-secondary: #4a5568;
            --text-muted: #718096;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 25px rgba(0,0,0,0.15), 0 4px 10px rgba(0,0,0,0.1);
            --radius: 12px;
            --radius-sm: 8px;
        }
        
        /* ==== LAYOUT E TIPOGRAFIA ==== */
        .main > div {
            padding-top: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* ==== HEADERS COM GRADIENTE ==== */
        .gradient-header {
            background: var(--primary-gradient);
            color: white;
            padding: 1.5rem 2rem;
            border-radius: var(--radius);
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            text-align: center;
        }
        
        .gradient-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .gradient-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
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
        
        /* ==== SEÇÕES COM GRADIENTE ==== */
        .section-header {
            background: var(--success-gradient);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: var(--radius);
            margin: 2rem 0 1rem 0;
            box-shadow: var(--shadow-md);
        }
        
        .section-header h2 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .section-header-info {
            background: var(--info-gradient);
        }
        
        .section-header-warning {
            background: var(--warning-gradient);
        }
        
        .section-header-danger {
            background: var(--danger-gradient);
        }
        
        /* ==== SIDEBAR APRIMORADA ==== */
        .sidebar .sidebar-content {
            background: var(--bg-primary);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: var(--shadow-sm);
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
        }
        
        .stNumberInput > div > div {
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
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
            background: var(--bg-primary);
            border-radius: var(--radius) var(--radius) 0 0;
            border-bottom: 3px solid transparent;
        }
        
        .stTabs > div > div > div > div[aria-selected="true"] {
            border-bottom: 3px solid #667eea;
            background: var(--primary-gradient);
            color: white;
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
        """,
        unsafe_allow_html=True,
    )


