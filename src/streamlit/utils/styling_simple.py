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