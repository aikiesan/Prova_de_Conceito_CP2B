import streamlit as st


def inject_simple_css() -> None:
    """CSS básico para testar se está funcionando"""
    st.markdown(
        """
        <style>
        /* TESTE - CSS BÁSICO */
        .main > div {
            background-color: #f0f8ff !important;
            padding: 20px !important;
        }
        
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        
        /* Header de teste */
        .test-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .test-header h1 {
            margin: 0;
            font-size: 2rem;
        }
        
        /* Botões de teste */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
        }
        
        /* Cards de teste */
        .test-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def create_test_header(title: str) -> None:
    """Header de teste"""
    st.markdown(
        f"""
        <div class="test-header">
            <h1>🚀 {title}</h1>
            <p>Se você vê este header com gradiente azul-roxo, o CSS está funcionando!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_test_card(title: str, content: str) -> None:
    """Card de teste"""
    st.markdown(
        f"""
        <div class="test-card">
            <h3 style="margin: 0 0 10px 0; color: #667eea;">{title}</h3>
            <p style="margin: 0; color: #333;">{content}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
