import streamlit as st
import pandas as pd
import re
from utils import sidebar, columnnames

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

    # Title of the app
    st.title('Hour by Hour Data Analysis Tool :bar_chart:')

    with st.expander("Know what you can do with this tool"):
        st.markdown('''
                <p style="text-align: justify">
                    This is a simple tool to perform data analysis based on hour by hour data. Some of the operations you can perform are:
                    <ul>
                    <li>Upload a csv/txt file and set column names.</li>
                    <li>Select column to groupby and perform operations like Mean, Sum, Max, Min.</li>
                    <li>Select column(s) to perform operations.</li>
                    <li>Filter the data based on the range of hours selected.</li>
                    <li>Plot the graph based on the operations performed.</li>
                </p>
                <p style="text-align: justify">
                Use this if some of the columns in your data are:
                    
                    Date, Time, Precheck Flow In, Standard Flow In

                </p>''', 
                unsafe_allow_html=True) 

    # expander = st.expander("Choose Single or Multiple csv files to start analysis", expanded=True)
    # with expander:
        # File uploader widget in the sidebar
    uploaded_files = st.sidebar.file_uploader('Upload a CSV file', type=['csv', 'txt'], 
                                    accept_multiple_files=True, 
                                    key='uploaded_files', 
                                    help='Upload a CSV file to start the analysis.')
        # set expander state to expanded=False
        # expander.expanded = False
    
    # with col2:


    if len(uploaded_files) > 1:
        # create radio buttons for multiple files
        selected_file = st.sidebar.radio('Select a file:', uploaded_files, format_func=lambda x: x.name)
        st.session_state.selected_file = selected_file
    else:
        st.session_state.selected_file = uploaded_files[0] if uploaded_files else None


    if st.session_state.selected_file is not None:
        df, header_option, tableElement = sidebar.sidebar("input_gen")

        columnnames.column_names(df, header_option, "input_gen")

        # Use either the session state column names or original column names
        if st.session_state.new_column_names:
            df.columns = st.session_state.new_column_names


        # Define the pattern to match 'checkpoint' followed by an optional space and a letter
        pattern = r"checkpoint\s*([A-Z])"

        # Search for the pattern in the filename (case-insensitive)
        match = re.search(pattern, st.session_state.selected_file.name, re.IGNORECASE)

        if match:
            # Extract the letter (A, B, C, etc.)
            letter = match.group(1).upper()  # Use .upper() to ensure consistency
            checkpoint = f'Checkpoint {letter}'
        else:
            print("No 'checkpoint' pattern found.")
            checkpoint = st.radio('Select a checkpoint:', [
                'Checkpoint A', 'Checkpoint B'
            ], index=None, key='checkpoint')

        # convert df['Time'] to datetime object
        df['Time'] = pd.to_datetime(df['Time'], format='%m/%d/%Y %H:%M')

        df['Hour'] = df['Time'].dt.hour
        df['Month'] = df['Time'].dt.month
        df['Day'] = df['Time'].dt.day
        df['Year'] = df['Time'].dt.year
        df['Quarter'] = df['Time'].dt.quarter

        tableElement.dataframe(df, use_container_width=True)

        st.write('## Select the columns to perform operations...')

        tempcol1, tempcol2 = st.columns(2)

        tempcol3, tempcol4 = st.columns(2)

        with tempcol1:
            # groupby 
            groupby = st.selectbox('Select columns to groupby:', df.columns, index=None)

        with tempcol2:
            # which kind of operation to perform
            operation = st.selectbox('Select operation:', ['Mean', 'Sum', 'Max', 'Min'], index=None)

        with tempcol3:
            # select columns to perform operations
            columnsToPerformOps = st.multiselect('Select columns to perform operations:', df.columns, default=[])

        if groupby is not None and len(groupby) > 0:
            if 'Hour' in groupby:
                with tempcol4:
                    # range slider for selecting the time window
                    values = st.slider('Select a range of hours', 1, 24, (4, 11))
            if 'Month' in groupby:
                with tempcol4:
                    # range slider for selecting the time window
                    values = st.slider('Select a range of months', 1, 12, (1, 6))

        if groupby is not None and operation is not None and len(columnsToPerformOps) > 0:
            # if groupby hour? then
            if 'Hour' in groupby:
                # filter the dataframe based on the range of hours selected
                df = df[(df['Hour'] >= values[0]) & (df['Hour'] <= values[1])].copy()

            # perform operations on the selected columns
            filtered_df = df.groupby(groupby)[columnsToPerformOps].agg(operation.lower()).round(0)

            st.write('Plotting graph...')
            st.bar_chart(filtered_df.iloc[:, :3], use_container_width=True, stack=False)

            if 'Precheck Sum In Flow' in filtered_df.columns and f'{checkpoint} Sum In Flow' in filtered_df.columns:
                # get % of the total sum
                filtered_df['Precheck %'] = (filtered_df['Precheck Sum In Flow'] / (filtered_df['Precheck Sum In Flow'] + filtered_df[f'{checkpoint} Sum In Flow'])) * 100
                filtered_df[f'{checkpoint} %'] = (filtered_df[f'{checkpoint} Sum In Flow'] / (filtered_df['Precheck Sum In Flow'] + filtered_df[f'{checkpoint} Sum In Flow'])) * 100

            st.dataframe(filtered_df, use_container_width=True)


        else:
            st.warning(':warning: Please select the columns to perform operations... ')
            






if __name__ == "__main__":
    main()
