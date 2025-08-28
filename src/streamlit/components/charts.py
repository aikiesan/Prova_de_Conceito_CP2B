import pandas as pd
import plotly.express as px
import streamlit as st


def top_municipios_bar(df: pd.DataFrame, top_n: int = 20) -> None:
    if df.empty:
        st.info("Sem dados para gráficos.")
        return
    dft = df.sort_values("total_final_nm_ano", ascending=False).head(top_n)
    fig = px.bar(dft, x="nm_mun", y="total_final_nm_ano", title=f"Top {top_n} municípios por potencial (Nm³/ano)")
    fig.update_layout(xaxis_title="Município", yaxis_title="Potencial (Nm³/ano)", height=400)
    st.plotly_chart(fig, use_container_width=True)


