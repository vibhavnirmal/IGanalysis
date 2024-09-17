import streamlit as st
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

def rolling_bin_max_sum_grouped(df, timeColumn, entityColumn, bin_interval=1, window=60, groupBy='', show_in_hhmm_format=False):
    # Create bins for the given time column (0 to 1440 minutes, at bin_interval granularity)
    bins = pd.cut(df[timeColumn], bins=range(0, 1441, bin_interval), right=False)

    # Dictionary to store results for each PaxType
    results = {'PaxType': [], 'RollingMax': [], 'RollingMaxTime': []}
    
    # Iterate through each unique PaxType (groupBy category)
    for pax_type in df[groupBy].unique():
        temp_pax_type = df[df[groupBy] == pax_type]

        # Group by the time bins and sum the entity column within each bin
        grpSizeSum = temp_pax_type.groupby(bins, observed=False)[entityColumn].sum()

        # Calculate rolling sum and rolling max over the window
        rolling_sum = grpSizeSum.rolling(window=min(window, len(grpSizeSum)), min_periods=1).sum()  # Ensure rolling doesn't fail on small windows
        rolling_max = rolling_sum.max()
        rolling_max_time = rolling_sum.idxmax()

        # Check if the rolling sum is not empty
        if pd.notna(rolling_max_time):
            rolling_max_time_value = rolling_max_time.left  # Extract the left side of the interval
        else:
            rolling_max_time_value = None

        # Convert rolling max time to HH:MM format if required
        if show_in_hhmm_format and rolling_max_time_value is not None:
            rolling_max_time_value = str(timedelta(minutes=int(rolling_max_time_value)))[:-3]

        # Append results for this PaxType
        results['PaxType'].append(pax_type)
        results['RollingMax'].append(int(rolling_max) if pd.notna(rolling_max) else 0)
        results['RollingMaxTime'].append(rolling_max_time_value if rolling_max_time_value is not None else 'N/A')

    fig, ax = plt.subplots()

    for pax_type in df[groupBy].unique():
        temp_pax_type = df[df[groupBy] == pax_type]
        grpSizeSum = temp_pax_type.groupby(bins, observed=False)[entityColumn].sum()
        rolling_sum_chart = grpSizeSum.rolling(window).sum()
        rolling_sum_chart.index = rolling_sum_chart.index.map(lambda x: x.left)
        rolling_sum_df = rolling_sum_chart.reset_index()
        rolling_sum_df.columns = ['Time', 'Rolling Sum']

        # show max values
        rolling_sum_df['Rolling Sum Max'] = rolling_sum_df['Rolling Sum'].max()
        rolling_sum_df['Rolling Sum Max Time'] = rolling_sum_df[rolling_sum_df['Rolling Sum'] == rolling_sum_df['Rolling Sum Max']]['Time']

        ax.plot(rolling_sum_df['Time'], rolling_sum_df['Rolling Sum'], label=pax_type)
        ax.scatter(rolling_sum_df['Rolling Sum Max Time'], rolling_sum_df['Rolling Sum Max'], label=f'{pax_type} Max', color='red')
        

    ax.set_xlabel('Time')
    ax.set_ylabel('Rolling Sum')
    ax.legend(title='PaxType')
    ax.set_title('Rolling Sum for Each PaxType')


    # show on left side of the screen
    colPlot1, colDataShow = st.columns(2)
    with colPlot1:
        st.pyplot(fig)

    with colDataShow:
        st.write(pd.DataFrame(results))


    # Return the final dataframe
    return pd.DataFrame(results, columns=['PaxType', 'RollingMax', 'RollingMaxTime'])

def rolling_bin_max_sum(df, timeColumn, entityColumn, bin_interval=1, window=60, show_in_hhmm_format=False):
    temp = df.copy()
    bins = pd.cut(temp[timeColumn], bins=range(0, 1441, bin_interval), right=False)
    
    grpSizeSum = temp.groupby(bins, observed=False)[entityColumn].sum()


    # Calculate rolling max of x-minute intervals
    rolling_sum = grpSizeSum.rolling(window).sum()
    rolling_max = rolling_sum.max()
    rolling_max_time = rolling_sum.idxmax()

    # plot
    rolling_sum_chart = rolling_sum.copy()
    rolling_sum_chart.index = rolling_sum.index.map(lambda x: x.left)
    rolling_sum_df = rolling_sum_chart.reset_index()    
    rolling_sum_df.columns = ['Time', 'Rolling Sum']
    st.line_chart(rolling_sum_df.set_index('Time')['Rolling Sum'])

    if show_in_hhmm_format:
        # convert to HH:MM format
        rolling_max_time_in_hhmm = str(timedelta(minutes=int(rolling_max_time.left)))[:-3]

        return int(rolling_max), rolling_max_time_in_hhmm
    else:
        return int(rolling_max), rolling_max_time

@st.cache_data
def load_data(uploaded_file, header_option, delimiter):
    # Use header=None if the user wants to provide column names manually
    if header_option == "No Header":
        return pd.read_csv(uploaded_file, header=None, delimiter=delimiter)
    else:
        return pd.read_csv(uploaded_file, delimiter=delimiter)

def main():
    # Set page layout to wide mode
    st.set_page_config(layout="wide")

    if 'new_column_names' not in st.session_state:
        st.session_state.new_column_names = []
    
    if 'now_show' not in st.session_state:
        st.session_state.now_show = False

    # Title of the app
    st.title('Data Analysis Tool')

    # Sidebar section for file upload and options
    st.sidebar.write('### Upload CSV File')

    # File uploader widget in the sidebar
    uploaded_file = st.sidebar.file_uploader('Upload a CSV file', type='csv')

    if uploaded_file is not None:
        # Delimiter selection option
        delimiter = st.sidebar.radio('Select delimiter:', ['Comma ( , )', 'Semicolon ( ; )', 'Tab ( \\t )'])

        # Map delimiter choice to actual delimiter
        delimiter_map = {
            'Comma ( , )': ',',
            'Semicolon ( ; )': ';',
            'Tab ( \\t )': '\t'
        }
        delimiter = delimiter_map[delimiter]

        # Header option for the CSV
        header_option = st.sidebar.radio('Does the CSV file have headers?', ["Yes, has Headers", "No Header"])

        df = load_data(uploaded_file, header_option, delimiter)

        summary_col1, fileName_col2 = st.columns([1, 1])
        
        with summary_col1:
            # column length
            st.write(f'Number of columns: ', df.shape[1], 'Number of rows: ', df.shape[0])
            if st.checkbox('Show Summary'):
                st.write(df.describe())

        with fileName_col2:
            # Display file name
            st.markdown(
                f"""
                <style>
                .file-name {{ text-align: right; font-size: 18px; color: gray; }}
                </style>
                <div class="file-name">Uploaded file: {uploaded_file.name}</div>
                """,
                unsafe_allow_html=True
            )

        tableElement = st.empty()
        tableElement.write(df)

        # Initialize session state for column names if it doesn't exist
        if "new_column_names" not in st.session_state:
            st.session_state.new_column_names = None
        
        if "updated_column_names" not in st.session_state:
            st.session_state.updated_column_names = None

        # If the user selected "No Header", provide an option to input column names
        if header_option == "No Header":
            st.sidebar.write('### Add column names')
            
            # Single text input for all column names separated by commas
            all_column_names = st.sidebar.text_input('Enter all column names separated by commas', placeholder='Column1, Column2, Column3, ...')
            
            # Create a button to update column names
            if st.sidebar.button('Set Column Names'):
                # Process the input to create the list of column names
                new_column_names = [name.strip().replace('"', '').replace("'", '') for name in all_column_names.split(',')]
                
                # Check if the number of column names matches the number of columns in the dataframe
                if len(new_column_names) != df.shape[1]:
                    st.sidebar.error(f"Number of column names provided ({len(new_column_names)}) does not match the number of columns in the DataFrame ({df.shape[1]}).")
                elif '' in new_column_names:
                    st.sidebar.error("Column names cannot be empty.")
                elif len(new_column_names) != len(set(new_column_names)):
                    st.sidebar.error("Duplicate column names are not allowed!")
                else:
                    # Store the new column names in session state
                    st.session_state.new_column_names = new_column_names
                    st.session_state.updated_column_names = new_column_names
                    st.sidebar.success("Column names set successfully!")
                    st.session_state.now_show = True
        
        # Use either the session state column names or original column names
        if st.session_state.new_column_names:
            df.columns = st.session_state.new_column_names

        tableElement.dataframe(df)

        if st.session_state.now_show:
            available_operations_between_2_cols_map = {'add': '+', 'subtract': '-', 'multiply': '*', 'divide': '/'}
            available_operations_for_single_col_map = {'mean': 'mean', 'sum': 'sum', 'max': 'max', 'min': 'min'}

            # perform new operations? 
            st.write('### Perform Operations on Columns ?')
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

                    try:
                        # assert len(df.columns) == len(st.session_state.new_column_names), "Number of columns in the dataframe does not match the number of column names."
                        df.columns = st.session_state.new_column_names

                    except Exception as e:
                        st.error(f"Error: {e}")
                    
                    # Layout for selecting columns and operation
                    col1_col, col2_col, operation_col = st.columns(3)
                    
                    # Select first and second columns
                    with col1_col:
                        col1 = st.selectbox('Select column 1:', st.session_state.new_column_names)

                    with col2_col:
                        col2 = st.selectbox('Select column 2:', st.session_state.new_column_names)

                    # Select operation to perform between columns
                    with operation_col:
                        operation_name = st.selectbox('Select operation:', list(available_operations_between_2_cols_map.keys()))

                    

                    # Perform the operation
                    if operation_name in available_operations_between_2_cols_map:
                        operation = available_operations_between_2_cols_map[operation_name]
                        new_col_name = 'TempColumn'

                        try:
                            df[new_col_name] = df[col1].combine(df[col2], eval(f'lambda x, y: x {operation} y'))
                            st.write(df)
                            st.session_state.updated_column_names = df.columns.tolist()
                        except Exception as e:
                            st.error(f"Error performing operation '{operation_name}' between columns '{col1}' and '{col2}': {e}")
                    else:
                        st.error(f"Invalid operation: {operation_name}")

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


                    
            # select, sort by column
            st.write('### Select and Sort by Column')

            performSorting = st.toggle(key='perform_sorting', value=False, label='Perform Sorting ?')

            if performSorting:
                sort_by_col_select, sort_order_select, yes_sort_button = st.columns([2, 1, 1])

                with sort_by_col_select:
                    sort_by_column = st.selectbox('Select sorting column:', st.session_state.updated_column_names)

                with sort_order_select:
                    sort_order = st.radio('Order:', ['Ascending', 'Descending'])

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
                    colT1 = st.selectbox('Select Times column:', st.session_state.updated_column_names)

                with entities_col:
                    colE2 = st.selectbox('Select Entities column:', st.session_state.updated_column_names)

                with time_window_col:
                    # select values from (60, 30, 20, 15, 10, 5)
                    window_selection_vals = [60, 30, 20, 15, 10, 5]
                    colTimeWin3 = st.selectbox('Select Time Window:', window_selection_vals)
            
                # group by column
                st.write('#### Group by Column')
                performGroupBy = st.toggle(key='perform_group_by', value=True, label='Perform Group by Column ?')

                if performGroupBy:
                    group_by_column = st.selectbox('Select group by column:', st.session_state.updated_column_names)
                    
                    rollingMax = rolling_bin_max_sum_grouped(df, colT1, colE2, window=colTimeWin3, groupBy=group_by_column, show_in_hhmm_format=True)
                else:
                    rollingMax, rollingMaxTime = rolling_bin_max_sum(df, colT1, colE2,window=colTimeWin3, show_in_hhmm_format=True)
                    
                    st.write(pd.DataFrame({'RollingMax': [rollingMax], 'RollingMaxTime': [rollingMaxTime]}))
        else:
            st.write('Please set column names first to perform operations.')            
    else:
        # Message for no file upload
        st.write('Please upload a CSV file to start the analysis.')


if __name__ == "__main__":
    main()
