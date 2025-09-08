import streamlit as st

def inject_custom_css():
    """Injects custom CSS for enhanced styling."""
    st.markdown("""
    <style>
    /* Main panel styling */
    .floating-panel {
        position: fixed;
        top: 80px;
        right: 20px;
        width: 350px;
        max-height: 80vh;
        overflow-y: auto;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        padding: 15px;
        z-index: 1000;
        transition: all 0.3s ease;
    }
    
    .floating-panel.hidden {
        transform: translateX(400px);
        opacity: 0;
    }
    
    .floating-panel-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
    }
    
    /* Panel tabs */
    .panel-tabs {
        display: flex;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
    }
    
    .tab {
        padding: 8px 15px;
        cursor: pointer;
        margin-right: 5px;
        border-radius: 5px 5px 0 0;
    }
    
    .tab.active {
        background-color: #f0f2f6;
        font-weight: 600;
    }
    
    .tab:hover {
        background-color: #e6e6e6;
    }
    
    /* Toggle button */
    .panel-toggle-button {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1001;
    }
    
    .panel-toggle-button button {
        border-radius: 50%;
        width: 40px;
        height: 40px;
        background-color: white;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
    }
    
    /* Metric cards */
    .stMetric {
        background-color: #f9f9f9;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #ff4b4b;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 6px;
        transition: all 0.2s;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Enhanced selectbox accessibility styling */
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e1e5e9;
        transition: all 0.2s ease;
        font-size: 1rem;
        padding: 0.5rem 0.75rem;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #ff4b4b;
        box-shadow: 0 0 0 3px rgba(255, 75, 75, 0.1);
        outline: none;
    }
    
    .stSelectbox > div > div > select:hover {
        border-color: #cbd5e0;
    }
    
    /* Radio button accessibility improvements */
    .stRadio > div {
        gap: 1rem;
        padding: 0.5rem 0;
    }
    
    .stRadio > div > label {
        font-weight: 500;
        cursor: pointer;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > label:hover {
        background-color: rgba(255, 75, 75, 0.05);
    }
    
    /* Enhanced multiselect for accessibility */
    .stMultiSelect > div > div > div {
        border-radius: 8px;
        border: 2px solid #e1e5e9;
        transition: all 0.2s ease;
        min-height: 3rem;
    }
    
    .stMultiSelect > div > div > div:focus-within {
        border-color: #ff4b4b;
        box-shadow: 0 0 0 3px rgba(255, 75, 75, 0.1);
    }
    
    /* Help text styling for better readability */
    .stHelp {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.4;
    }
    
    /* Map container */
    .stLeafletMap {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)