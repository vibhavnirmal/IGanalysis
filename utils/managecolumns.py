from streamlit_tags import st_tags
import streamlit as st

COLUMN_SUGGESTIONS = [
    "ReplicationNum", "AirlineIdx", "FlightDepTime", "DepMarket", "SSCPType", "GrpSize", 
    "PaxArrTime", "PaxSpeed", "SSCPDelay", "Visitors", "LobbyDelay", "DepFlightNumber", 
    "PaxType", "PaxIDNum", "PaxSSCPTime", "PaxSPorPE"
]

@st.dialog("Manage Column Names")
def manage_columns(df, mode='create'):
    """
    Function to either create or change column names in a DataFrame.
    
    Parameters:
    - df: DataFrame whose columns will be renamed.
    - mode: 'create' for creating new column names, 'change' for editing existing ones.
    """
    if mode == 'create':
        st.write('#### Add')
    else:
        st.write('#### Update')

    # Display possible column suggestions
    st.write('''<p style="color: orange">Possible Column Names:</p>
                <p>{}</p>
                '''.format(", ".join(COLUMN_SUGGESTIONS)),
             unsafe_allow_html=True)

    # Toggle for user to choose between tag input or manual input
    use_tags = st.checkbox('Use tags to enter column names', value=True)

    if use_tags:
        all_column_names = st_tags(
            label=f'Enter `{df.shape[1]}` column names:',
            text='Press enter to add more',
            value=[],
            suggestions=COLUMN_SUGGESTIONS,
            maxtags=df.shape[1]
        )
    else:
        all_column_names = st.text_area(
            f'Enter `{df.shape[1]}` column names separated by commas (,)', 
            height=150
        ).split(',')
        all_column_names = [name.strip() for name in all_column_names if name.strip()]

    if len(all_column_names) > 0:
        showColumnsNames = st.checkbox('Show Column Names', value=False)
        if showColumnsNames:
            st.write(all_column_names)

    # Validate input
    if len(all_column_names) != df.shape[1]:
        st.error(f"Number of column names ({len(all_column_names)}) does not match the number of columns in the DataFrame ({df.shape[1]}).")
    elif len(all_column_names) != len(set(all_column_names)):
        st.error("Duplicate column names are not allowed!")
    elif '' in all_column_names:
        st.error("Column names cannot be empty.")
    else:
        st.write('Total column names entered: ', len(all_column_names))

    # Button to set column names
    if st.button('Set Column Names'):
        # If validation passed, store the new column names
        st.session_state.new_column_names = all_column_names
        st.session_state.updated_column_names = all_column_names
        st.session_state.now_show = True

        df.columns = all_column_names
        st.success("Column names set successfully!")
        st.rerun()
