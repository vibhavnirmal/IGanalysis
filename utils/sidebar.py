import streamlit as st
from . import loaddata

def sidebar(newKey):
    # Delimiter selection option
    delimiter = st.sidebar.radio('Select delimiter:', ['Comma (`,`)', 'Semicolon (`;`)', 'Tab (`\\t`)'], horizontal=True, key=newKey+"delim")

    # Map delimiter choice to actual delimiter
    delimiter_map = {
        'Comma (`,`)': ',',
        'Semicolon (`;`)': ';',
        'Tab (`\\t`)': '\t'
    }
    delimiter = delimiter_map[delimiter]

    header_option = st.sidebar.radio('Does the CSV file have Column Names?', ["No", "Yes"], horizontal=True, key=newKey+"header")
    
    df = loaddata.load_data(st.session_state.selected_file, header_option, delimiter)
    
    if header_option == "Yes":
        st.session_state.now_show = True
        st.session_state.new_column_names = df.columns.tolist()
        st.session_state.updated_column_names = df.columns.tolist()
    
    # Display file name
    st.markdown(
        f"""
        <style>
        .file-name {{ text-align: right; font-size: 18px; color: gray; }}
        </style>
        <div class="file-name">Uploaded file: {st.session_state.selected_file.name}</div>
        """,
        unsafe_allow_html=True
    )

    # column length
    st.write('Number of columns: ', df.shape[1], 'Number of rows: ', df.shape[0])
    if st.checkbox('Show Summary (contains count, mean, std, min, max, etc. over each column)', key=newKey+"checkbox"):
        st.write(df.describe())
        
    st.write('### Data Preview')
    tableElement = st.empty()
    tableElement.write(df)

    # Initialize session state for column names if it doesn't exist
    if "new_column_names" not in st.session_state:
        st.session_state.new_column_names = None
    
    if "updated_column_names" not in st.session_state:
        st.session_state.updated_column_names = None

    return df, header_option, tableElement