"""
Teste do CSS limpo - fundo branco e design elegante
"""
import streamlit as st
import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from streamlit.utils.styling_clean import (
    inject_clean_css, 
    create_clean_header, 
    create_section_header,
    create_clean_card,
    create_info_box
)

# Configurar página
st.set_page_config(
    page_title="CP2B - Teste CSS Limpo",
    page_icon="🌱",
    layout="wide"
)

# Aplicar CSS limpo
inject_clean_css()

# Header principal
create_clean_header(
    "CP2B - Dashboard de Biogás", 
    "Design limpo com fundo branco e elementos elegantes",
    "🌱"
)

# Seção de teste
create_section_header("Teste de Componentes", "🧪")

# Cards de teste
col1, col2 = st.columns(2)

with col1:
    create_clean_card(
        "✅ CSS Funcionando", 
        "Este card tem fundo branco, borda sutil e sombra suave. Passe o mouse para ver o efeito hover."
    )
    
    create_clean_card(
        "🎨 Design Limpo", 
        "Fundo branco, cores suaves e elementos bem definidos para melhor legibilidade."
    )

with col2:
    create_clean_card(
        "📊 Métricas", 
        "As métricas abaixo devem ter bordas e efeitos hover elegantes."
    )
    
    create_clean_card(
        "🔘 Botões", 
        "Os botões têm cor verde e efeito hover suave."
    )

# Caixas de informação
create_info_box("💡 <strong>Info:</strong> Esta é uma caixa de informação azul.", "info")
create_info_box("✅ <strong>Sucesso:</strong> CSS aplicado com sucesso!", "success")
create_info_box("⚠️ <strong>Aviso:</strong> Teste de caixa de aviso.", "warning")

# Métricas de teste
st.markdown("### 📊 Métricas de Teste")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Municípios", "645", "100%")

with col2:
    st.metric("Potencial Total", "1.2M Nm³/ano", "15%")

with col3:
    st.metric("Fontes Ativas", "10", "2")

with col4:
    st.metric("Viabilidade", "Alto", "Positivo")

# Botões de teste
st.markdown("### 🔘 Botões de Teste")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Processar Dados"):
        st.success("Dados processados com sucesso!")

with col2:
    if st.button("📊 Gerar Relatório"):
        st.info("Relatório gerado!")

with col3:
    if st.button("🗺️ Atualizar Mapa"):
        st.balloons()

# Controles de interface
st.markdown("### 🎛️ Controles")
col1, col2 = st.columns(2)

with col1:
    st.selectbox("Selecione um município:", ["São Paulo", "Campinas", "Santos"])
    st.slider("Potencial mínimo:", 0, 100000, 10000)

with col2:
    st.number_input("Valor customizado:", 0, 1000000, 50000)
    st.text_input("Buscar município:", placeholder="Digite o nome...")

# Tabs de teste
st.markdown("### 📋 Tabs de Teste")
tab1, tab2, tab3 = st.tabs(["🗺️ Mapa", "📊 Dashboard", "📋 Dados"])

with tab1:
    st.write("Conteúdo do mapa - design limpo e elegante")
    
with tab2:
    st.write("Dashboard executivo com métricas")
    
with tab3:
    st.write("Tabela de dados dos municípios")

# Verificação final
st.markdown("---")
st.markdown("### 🔍 Checklist de Design:")
st.write("- ✅ Fundo branco limpo?")
st.write("- ✅ Header verde com texto branco?") 
st.write("- ✅ Cards com bordas sutis e sombras?")
st.write("- ✅ Botões verdes com hover?")
st.write("- ✅ Métricas com bordas e hover?")
st.write("- ✅ Tabs com indicador ativo?")

if st.button("🎉 Design Aprovado!"):
    st.success("🎊 CSS limpo funcionando perfeitamente!")
    st.balloons()
