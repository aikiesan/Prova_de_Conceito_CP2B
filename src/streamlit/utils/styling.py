import streamlit as st


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        .metric-card { padding: 12px; border-radius: 8px; background: #F8FAFF; border: 1px solid #E5ECF6; }
        .metric-value { font-size: 1.4rem; font-weight: 700; }
        .metric-label { color: #6B7280; font-size: 0.85rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


