import streamlit as st
from . import managecolumns
import pandas as pd

def column_names(df, header_option, newKey):
    # Handle scenario when user selects "No" for header option
    if header_option == "No":
        
        # Check if new column names are not set or mismatch the DataFrame's columns
        if st.session_state.new_column_names is not None and len(df.columns) != len(st.session_state.new_column_names):
            # Reset new_column_names session state if mismatch
            st.session_state.new_column_names = None
        
        # If new column names have not been set, prompt the user to enter them
        if 'new_column_names' not in st.session_state or st.session_state.new_column_names is None:
            st.write("No column names present. Please enter new column names.")
            
            c1, c2 = st.columns(2, gap="medium")
            
            # Button to trigger column name entry
            with c1:
                if st.button("Enter Column Names", key=newKey+"entercols"):
                    managecolumns.manage_columns(df, mode='create')
            
            # Show current status of column names
            with c2:
                st.write("No column names entered yet.")
        
        # If column names are already set, give options to view or change
        else:
            viewCols = st.checkbox("View/Edit Column Names", key=newKey+"viewcols")

            if viewCols:
                columnsDF = pd.DataFrame([st.session_state.new_column_names], columns=list(range(1, len(st.session_state.new_column_names) + 1)))
                columnsDF = st.data_editor(columnsDF)
                st.session_state.new_column_names = columnsDF.iloc[0].tolist()
                st.session_state.updated_column_names = columnsDF.iloc[0].tolist()