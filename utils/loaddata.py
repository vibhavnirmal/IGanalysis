import pandas as pd
import streamlit as st

@st.cache_data
def load_data(uploaded_file, header_option, delimiter):
    # Use header=None if the user wants to provide column names manually
    if header_option == "No":
        return pd.read_csv(uploaded_file, header=None, delimiter=delimiter)
    else:
        return pd.read_csv(uploaded_file, delimiter=delimiter)