import streamlit as st


def inject_improved_css() -> None:
    """CSS melhorado com fundo mais legível"""
    st.markdown(
        """
        <style>
        /* ==== SISTEMA DE CORES MELHORADO ==== */
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-gradient: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            --warning-gradient: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
            --info-gradient: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            
            /* Cores de fundo mais suaves */
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #edf2f7;
            --bg-accent: #f0f4f8;
            
            --text-primary: #1a202c;
            --text-secondary: #4a5568;
            --text-muted: #718096;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 25px rgba(0,0,0,0.15), 0 4px 10px rgba(0,0,0,0.1);
            --radius: 12px;
        }
        
        /* ==== FUNDO PRINCIPAL MELHORADO ==== */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
            min-height: 100vh;
        }
        
        .main > div {
            background: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(10px);
            border-radius: var(--radius);
            padding: 2rem !important;
            margin: 1rem !important;
            box-shadow: var(--shadow-sm);
        }
        
        /* ==== HEADERS MODERNOS ==== */
        .gradient-header {
            background: var(--primary-gradient);
            color: white;
            padding: 2rem;
            border-radius: var(--radius);
            margin-bottom: 2rem;
            box-shadow: var(--shadow-lg);
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .gradient-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
            pointer-events: none;
        }
        
        .gradient-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
        }
        
        .gradient-header p {
            margin: 1rem 0 0 0;
            opacity: 0.95;
            font-size: 1.1rem;
            position: relative;
            z-index: 1;
        }
        
        /* ==== CARDS APRIMORADOS ==== */
        .enhanced-card {
            background: var(--bg-primary);
            border-radius: var(--radius);
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .enhanced-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-left-color: #764ba2;
        }
        
        .enhanced-card h3 {
            margin: 0 0 0.5rem 0;
            color: var(--text-primary);
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .enhanced-card p {
            margin: 0;
            color: var(--text-secondary);
            line-height: 1.6;
        }
        
        /* ==== BOTÕES MELHORADOS ==== */
        .stButton > button {
            background: var(--primary-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius) !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: var(--shadow-sm) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0) !important;
        }
        
        /* ==== MÉTRICAS ESTILIZADAS ==== */
        [data-testid="metric-container"] {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            padding: 1rem;
            border-radius: var(--radius);
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }
        
        /* ==== SIDEBAR MELHORADA ==== */
        .css-1d391kg {
            background: var(--bg-primary) !important;
        }
        
        .css-1lcbmhc {
            background: var(--bg-secondary) !important;
            border-radius: var(--radius);
            margin: 0.5rem;
            padding: 1rem;
            box-shadow: var(--shadow-sm);
        }
        
        /* ==== TABS MODERNAS ==== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background: var(--bg-secondary);
            padding: 0.5rem;
            border-radius: var(--radius);
            margin-bottom: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: var(--radius);
            padding: 0.75rem 1.5rem;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: var(--primary-gradient);
            color: white;
            box-shadow: var(--shadow-sm);
        }
        
        /* ==== INPUTS E SELECTBOX ==== */
        .stSelectbox > div > div,
        .stNumberInput > div > div,
        .stTextInput > div > div {
            border-radius: var(--radius) !important;
            border: 1px solid var(--border-color) !important;
            background: var(--bg-primary) !important;
        }
        
        /* ==== ALERTAS E NOTIFICAÇÕES ==== */
        .stAlert {
            border-radius: var(--radius) !important;
            border: none !important;
            box-shadow: var(--shadow-sm) !important;
        }
        
        /* ==== DATAFRAMES ==== */
        .stDataFrame > div {
            border-radius: var(--radius) !important;
            overflow: hidden !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        /* ==== ANIMAÇÕES SUAVES ==== */
        .fade-in {
            animation: fadeIn 0.6s ease-in;
        }
        
        @keyframes fadeIn {
            from { 
                opacity: 0; 
                transform: translateY(20px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }
        
        /* ==== RESPONSIVIDADE ==== */
        @media (max-width: 768px) {
            .main > div {
                margin: 0.5rem !important;
                padding: 1rem !important;
            }
            
            .gradient-header h1 {
                font-size: 2rem;
            }
            
            .enhanced-card {
                padding: 1rem;
            }
        }
        
        /* ==== SCROLLBAR PERSONALIZADA ==== */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary-gradient);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6b5b95 100%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_improved_header(title: str, subtitle: str = "") -> None:
    """Header melhorado com gradiente e legibilidade"""
    st.markdown(
        f"""
        <div class="gradient-header fade-in">
            <h1>🌱 {title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_improved_card(title: str, content: str, icon: str = "📊") -> None:
    """Card melhorado com melhor legibilidade"""
    st.markdown(
        f"""
        <div class="enhanced-card fade-in">
            <h3>{icon} {title}</h3>
            <p>{content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_section_divider(text: str = "") -> None:
    """Divisor de seção elegante"""
    if text:
        st.markdown(
            f"""
            <div style="text-align: center; margin: 2rem 0;">
                <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #667eea, transparent); margin-bottom: 1rem;">
                <span style="background: var(--bg-primary); padding: 0 1rem; color: var(--text-muted); font-weight: 500;">{text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #667eea, transparent); margin: 2rem 0;">
            """,
            unsafe_allow_html=True,
        )
