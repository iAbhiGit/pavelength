# scripts/ui_styles.py

import streamlit as st

def inject_custom_styles():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            background-color: #0e1117;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 16px;
            padding: 1rem 2rem;
            color: #ffffff;
        }
        .stButton > button {
            background-color: #2E86AB;
            color: white;
            font-weight: 600;
            border-radius: 10px;
            padding: 0.6rem 1.4rem;
        }
        .stTextInput input, .stSelectbox select {
            border-radius: 8px;
            height: 2.5rem;
            background-color: #1e222a;
            color: #ffffff;
            border: 1px solid #444;
        }
        h1 {
            text-align: center;
            color: #ffffff;
            font-size: 2.5rem;
            font-weight: 700;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
        }
        </style>
    """, unsafe_allow_html=True)
