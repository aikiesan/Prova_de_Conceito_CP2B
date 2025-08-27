import pandas as pd
import streamlit as st


def render_table(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Sem registros para exibir.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True)


