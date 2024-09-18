import streamlit as st
import pandas as pd
from utils import managecolumns, loaddata, peakrolling

def set_session_state():
    if 'new_column_names' not in st.session_state:
        st.session_state.new_column_names = None
    
    if 'now_show' not in st.session_state:
        st.session_state.now_show = False

    if "updated_column_names" not in st.session_state:
        st.session_state.updated_column_names = None

    if "selected_file" not in st.session_state:
        st.session_state.selected_file = None

def main():
    set_session_state()


    # wide mode
    st.set_page_config(layout="wide")

    # Title of the app
    st.title('Data Analysis Tool :bar_chart:')

    expanderCol1, expanderCol2 = st.columns(2)

  
    with expanderCol1:
        expander = st.expander("Choose Single or Multiple csv files to start analysis", expanded=True)
        with expander:
            # File uploader widget in the sidebar
            uploaded_files = st.file_uploader('Upload a CSV file', type='csv', accept_multiple_files=True, 
                                            key='file_uploader', help='Upload a CSV file to start the analysis.')
            # set expander state to expanded=False
            expander.expanded = False
    with expanderCol2:
        with st.expander("Know what you can do with this tool"):
            st.markdown('''
                    <p style="text-align: justify">
                        This is a simple tool to perform Peak Rolling on CSV files generated from Simio Input Generator. 
                        You can upload a CSV file, set column names, and perform operations (such as summing two columns 
                        to create a new column), sort by a column and get rolling peak with or without grouping on the 
                        other columns.
                    </p>''', 
                    unsafe_allow_html=True)       

    if len(uploaded_files) > 1:
        # create radio buttons for multiple files
        selected_file = st.sidebar.radio('Select a file:', uploaded_files, format_func=lambda x: x.name)
        st.session_state.selected_file = selected_file
    else:
        st.session_state.selected_file = uploaded_files[0] if uploaded_files else None


    if st.session_state.selected_file is not None:
        # Delimiter selection option
        delimiter = st.sidebar.radio('Select delimiter:', ['Comma (`,`)', 'Semicolon (`;`)', 'Tab (`\\t`)'], horizontal=True)

        # Map delimiter choice to actual delimiter
        delimiter_map = {
            'Comma (`,`)': ',',
            'Semicolon (`;`)': ';',
            'Tab (`\\t`)': '\t'
        }
        delimiter = delimiter_map[delimiter]

        header_option = st.sidebar.radio('Does the CSV file have Column Names?', ["No", "Yes"], horizontal=True)
       
        df = loaddata.load_data(st.session_state.selected_file, header_option, delimiter)
        
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
        st.write(f'Number of columns: ', df.shape[1], 'Number of rows: ', df.shape[0])
        if st.checkbox('Show Summary (contains count, mean, std, min, max, etc. over each column)'):
            st.write(df.describe())
            
        st.write('### Data Preview')
        tableElement = st.empty()
        tableElement.write(df)

        # Initialize session state for column names if it doesn't exist
        if "new_column_names" not in st.session_state:
            st.session_state.new_column_names = None
        
        if "updated_column_names" not in st.session_state:
            st.session_state.updated_column_names = None

        # Handle scenario when user selects "No" for header option
        if header_option == "No":
            
            # Check if new column names are not set or mismatch the DataFrame's columns
            if st.session_state.new_column_names != None and len(df.columns) != len(st.session_state.new_column_names):
                # Reset new_column_names session state if mismatch
                st.session_state.new_column_names = None
            
            # If new column names have not been set, prompt the user to enter them
            if 'new_column_names' not in st.session_state or st.session_state.new_column_names is None:
                st.write("No column names present. Please enter new column names.")
                
                c1, c2 = st.columns(2, gap="medium")
                
                # Button to trigger column name entry
                with c1:
                    if st.button("Enter Column Names"):
                        managecolumns.manage_columns(df, mode='create')
                
                # Show current status of column names
                with c2:
                    st.write("No column names entered yet.")
            
            # If column names are already set, give options to view or change
            else:
                c1, c2 = st.columns(2, gap="medium")
                
                # Option to view the entered column names
                with c1:
                    viewCols = st.checkbox("View Column Names")
                    if viewCols:
                        if 'new_column_names' in st.session_state and st.session_state.new_column_names:
                            st.write("Current Column Names:", st.session_state.new_column_names)
                        else:
                            st.write("No column names available.")
                
                # Button to change the column names
                with c2:
                    if st.button("Change Column Names"):
                        managecolumns.manage_columns(df, mode='change')



        # Use either the session state column names or original column names
        if st.session_state.new_column_names:
            df.columns = st.session_state.new_column_names

        tableElement.dataframe(df)

        if st.session_state.now_show:
            available_operations_between_2_cols_map = {'add': '+', 'subtract': '-', 'multiply': '*', 'divide': '/'}
            available_operations_for_single_col_map = {'mean': 'mean', 'sum': 'sum', 'max': 'max', 'min': 'min'}

            # perform new operations? 
            st.write('### Perform Operations on Columns ? :1234:')

            with st.expander("See explanation"):
                st.markdown("""
                    <span style='color:orange'><b>Note:</b></span> 
                    The following mathematical operations are permitted:
                    <ul>
                        <li><b>On two separate columns:</b> Addition, subtraction, multiplication, and division</li>
                        <li><b>On a single column:</b> Calculation of the mean, sum, maximum value (max), or minimum value (min)</li>
                    </ul>
                    """, unsafe_allow_html=True)


            performOperations = st.toggle(key='perform_ops', value=False, label='Perform Operations on Columns ?')

            if performOperations:
                # Choose whether to perform operations between two columns or not
                operation_between_2_cols = st.radio('Perform operation between two columns?', [True, False])

                if operation_between_2_cols:
                    # Ensure the dataframe has the updated column names

                    # try:
                    #     # assert len(df.columns) == len(st.session_state.new_column_names), "Number of columns in the dataframe does not match the number of column names."
                    #     df.columns = st.session_state.new_column_names

                    # except Exception as e:
                    #     st.error(f"Error: {e}")
                    
                    # Layout for selecting columns and operation
                    col1_col, col2_col, operation_col = st.columns(3)
                    
                    # Select first and second columns
                    with col1_col:
                        col1 = st.selectbox('Select column 1:', 
                                            st.session_state.new_column_names, 
                                            index=None,
                                            placeholder="Select first column...")

                    with col2_col:
                        col2 = st.selectbox('Select column 2:', st.session_state.new_column_names, 
                                            index=None,
                                            placeholder="Select second column...")

                    # Select operation to perform between columns
                    with operation_col:
                        operation_name = st.selectbox('Select operation:', list(available_operations_between_2_cols_map.keys()), 
                                            index=None,
                                            placeholder="Select operation [ + - / * ]")

                    

                    # Perform the operation
                    if operation_name in available_operations_between_2_cols_map:
                        operation = available_operations_between_2_cols_map[operation_name]
                        new_col_name = 'TempColumn'

                        try:
                            df[new_col_name] = df[col1].combine(df[col2], eval(f'lambda x, y: x {operation} y'))
                            
                            st.caption(f"New column with name '`{new_col_name}`' is created at the end of the DataFrame.")
                            st.write(df)
                            st.session_state.updated_column_names = df.columns.tolist()
                        except Exception as e:
                            st.error(f"Error performing operation '{operation_name}' between columns '{col1}' and '{col2}': {e}")

                else:
                    # Single-column operation layout
                    operation_for_single_col_col, col_col = st.columns(2)

                    # Select operation and column for a single-column operation
                    with operation_for_single_col_col:
                        operation_for_single_col = st.selectbox('Select operation for single column:', list(available_operations_for_single_col_map.keys()))

                    with col_col:
                        col = st.selectbox('Select column:', st.session_state.new_column_names)

                    # Perform the operation
                    if operation_for_single_col in available_operations_for_single_col_map:
                        operation = available_operations_for_single_col_map[operation_for_single_col]

                        try:
                            # Execute the operation and display the result
                            result = getattr(df[col], operation)()
                            st.write(f'Result of {operation_for_single_col} on column {col}:', result)

                        except Exception as e:
                            st.error(f"Error performing operation '{operation_for_single_col}' on column '{col}': {e}")
                    else:
                        st.error(f"Invalid operation: {operation_for_single_col}")
            else:
                # check length of columns
                if st.session_state.new_column_names != None and len(df.columns) != len(st.session_state.new_column_names):
                    # if last column name is TempColumn, remove it
                    if df.columns[-1] == 'TempColumn':
                        df = df.drop(columns=['TempColumn'])
                    st.session_state.new_column_names = df.columns.tolist()
                    st.session_state.updated_column_names = df.columns.tolist()

                    
            # select, sort by column
            st.write('### Select and Sort by Column :arrow_up_down:')

            performSorting = st.toggle(key='perform_sorting', value=True, label='Perform Sorting ?')

            if performSorting:
                sort_by_col_select, sort_order_select, yes_sort_button = st.columns([2, 2, 1], gap="medium")

                with sort_by_col_select:
                    sort_by_column = st.selectbox('Select sorting column:', st.session_state.updated_column_names, 
                                            index=None,
                                            placeholder="Select Sorting column...", label_visibility='collapsed')

                with sort_order_select:
                    sort_order = st.radio('Order:', ['Ascending', 'Descending'], horizontal=True, label_visibility='collapsed')

                with yes_sort_button:
                    if st.button('Sort Now'):
                        # Sort the dataframe by the selected column and order
                        ascending = True if sort_order == 'Ascending' else False
                        df = df.sort_values(by=sort_by_column, ascending=ascending)
                
                st.dataframe(df)

            st.write('### Rolling Max Calculation')
            performRollingMaxCalc = st.toggle(key='perform_rolling', value=False, label='Perform Peak Rolling ?')

            if performRollingMaxCalc:
                # Select a Time column for rolling sum calculation
                st.write('Select the Time Column (in minutes 0-1440) and the Entities Columns to get the rolling sum')

                times_col, entities_col, time_window_col = st.columns(3)

                with times_col:
                    colT1 = st.selectbox('Select Times column:', st.session_state.updated_column_names, 
                                            index=None,
                                            placeholder="Select Times column...", label_visibility='collapsed')

                with entities_col:
                    colE2 = st.selectbox('Select Entities column:', st.session_state.updated_column_names, 
                                            index=None,
                                            placeholder="Select Entities column...", label_visibility='collapsed')

                with time_window_col:
                    # select values from (60, 30, 20, 15, 10, 5)
                    window_selection_vals = [5, 10, 15, 20, 30, 60]
                    colTimeWin3 = st.select_slider('Select Time Window:', window_selection_vals, value=window_selection_vals[-1] )
            
                # group by column
                st.write('#### Group by Column')
                performGroupBy = st.toggle(key='perform_group_by', value=False, label='Perform Group by Column ?')

                if performGroupBy:
                    group_by_column = st.selectbox('Select group by column:', st.session_state.updated_column_names, 
                                            index=None,
                                            placeholder="Select group by column...", label_visibility='collapsed')
                    if group_by_column and colT1 and colE2:
                        # check length of columns
                        if len(df.columns) != len(st.session_state.new_column_names):
                            st.session_state.new_column_names = df.columns.tolist()
                        rollingMax = peakrolling.rolling_bin_max_sum_grouped(df, colT1, colE2, window=colTimeWin3, groupBy=group_by_column, show_in_hhmm_format=True)
                    else:
                        st.warning('Please select the column names first to perform operations.', icon='⚠️')
                else:
                    if colT1 and colE2:
                        rollingMax, rollingMaxTime = peakrolling.rolling_bin_max_sum(df, colT1, colE2,window=colTimeWin3, show_in_hhmm_format=True)
                        
                        st.write(pd.DataFrame({'RollingMax': [rollingMax], 'RollingMaxTime': [rollingMaxTime]}))
                    else:
                        st.write('Please select the column names first to perform operations.')
                    
        else:
            st.warning('Please set column names first to perform operations.', icon='⚠️')            
    else:
        # Message for no file upload
        st.write('Please upload a CSV file to start the analysis.')


if __name__ == "__main__":
    main()
