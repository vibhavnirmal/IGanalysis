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

    st.set_page_config(
        page_title="Hour By Hour TS Tool"
    )

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

        tempColNeg1, tempColNeg2 = st.columns(2)

        with tempColNeg1:
            removeNegativeValues = st.checkbox('Remove negative values', value=False)
        
        with tempColNeg2:
            if removeNegativeValues:
                # turn negative values to 0 from f'{checkpoint} Sum In Flow' and 'Precheck Sum In Flow' and count the number of negative values
                negative_values = df[(df[f'{checkpoint} Sum In Flow'] < 0) | (df['Precheck Sum In Flow'] < 0)].shape[0]
                df[f'{checkpoint} Sum In Flow'] = df[f'{checkpoint} Sum In Flow'].apply(lambda x: 0 if x < 0 else x)
                df['Precheck Sum In Flow'] = df['Precheck Sum In Flow'].apply(lambda x: 0 if x < 0 else x)
                st.write(f'Number of negative values removed: `{negative_values}`')

        # convert df['Time'] to datetime object
        df['Time'] = pd.to_datetime(df['Time'], format='%m/%d/%Y %H:%M')

        tableElement.dataframe(df, use_container_width=True)

        df['Hour'] = df['Time'].dt.hour
        df['Month'] = df['Time'].dt.month
        df['Day'] = df['Time'].dt.day
        df['Year'] = df['Time'].dt.year
        df['Quarter'] = df['Time'].dt.quarter
        df['Date'] = df['Time'].dt.date


        st.write('## Select the columns to perform operations...')

        tempcol1, tempcol2 = st.columns(2)

        tempcol5, tempcol6 = st.columns(2)

        tempcol3, tempcol4 = st.columns(2)

        with tempcol1:
            # groupby 
            groupby = st.selectbox('Select column to groupby:', df.columns, index=None)
            if groupby is not None and 'Date' in groupby:
                st.warning(':warning: Selection includes first month and excludes the last month selected for example [inclusive Nov-23, exclusive Dec-23) will have 1 Nov to 30 Nov')

        with tempcol3:
            # which kind of operation to perform
            operation = st.selectbox('Select operation:', ['Mean', 'Max', 'Quantile'], index=None)

        with tempcol5:
            if groupby is not None and 'Date' in groupby:
                with tempcol2:
                    # radio to select month (year)
                    df['Date'] = pd.to_datetime(df['Date'])
                    month_year = df['Date'].dt.strftime('%b-%y').unique()
                    selected_month_year_range = st.select_slider(
                        'Select a range of month-year:',
                        options=month_year,
                        value=(month_year[2], month_year[5]),
                        key='selected_month_year_range'
                    )
                        
        with tempcol4:
            if operation is not None and 'quantile' in operation.lower():
                # quantile value
                quantileQ = st.slider('Select quantile value:', 0.0, 1.0, 0.75, 0.05)      

        if groupby is not None and len(groupby) > 0:
            if 'Hour' in groupby:
                with tempcol2:
                    # range slider for selecting the time window
                    hoursvalues = st.slider('Select a range of hours', 1, 24, (4, 11))

            if 'Month' in groupby:
                with tempcol2:
                    # range slider for selecting the time window
                    monthvalues = st.slider('Select a range of months', 1, 12, (4, 9))

            if 'Date' in groupby:
                with tempcol2:
                    # range slider for selecting the time window
                    datevalues = st.slider('Select a range of dates', 1, 31, (1, 15))
        
        # select columns to perform operations
        columnsToPerformOps = st.multiselect('Select column(s) to perform operations:', df.columns, default=[])


        if groupby is not None and operation is not None and len(columnsToPerformOps) > 0:
            # if groupby hour? then
            if 'Hour' in groupby:
                # filter the dataframe based on the range of hours selected
                df = df[(df['Hour'] >= hoursvalues[0]) & (df['Hour'] <= hoursvalues[1])].copy()

            if 'Month' in groupby:
                # filter the dataframe based on the range of months selected
                df = df[(df['Month'] >= monthvalues[0]) & (df['Month'] <= monthvalues[1])].copy()

            if 'Date' in groupby:
                # filter the dataframe based on the range of dates selected
                # filter over months and dates
                print(len(df))
                selected_month_year_range = pd.to_datetime(selected_month_year_range, format='%b-%y')
                df = df[(df['Date'] >= selected_month_year_range[0]) & (df['Date'] <= selected_month_year_range[1])].copy()
                print(len(df))
                df = df[(df['Day'] >= datevalues[0]) & (df['Day'] <= datevalues[1])].copy()
                print(len(df))

            # perform operations on the selected columns
            if operation.lower() == 'quantile':
                filtered_df = df.groupby(groupby)[columnsToPerformOps].quantile(quantileQ).round(0)
            else:
                filtered_df = df.groupby(groupby)[columnsToPerformOps].agg(operation.lower()).round(0)

            showTable1, showGraph1 = st.columns(2)

            with showTable1:
                showTable1Checkbox = st.checkbox('Show data for each hour as table', value=True, key='showTable1Checkbox')

            with showGraph1:
                showGraph1Checkbox = st.checkbox('Show Graph', value=False, key='showGraph1Checkbox')

            if showGraph1Checkbox:
                st.write('Plotting graph...')
                st.bar_chart(filtered_df.iloc[:, :3], use_container_width=True, stack=False)

            if showTable1Checkbox:
                if 'Precheck Sum In Flow' in filtered_df.columns and f'{checkpoint} Sum In Flow' in filtered_df.columns:
                    # get % of the total sum
                    filtered_df['Precheck %'] = (filtered_df['Precheck Sum In Flow'] / (filtered_df['Precheck Sum In Flow'] + filtered_df[f'{checkpoint} Sum In Flow'])) * 100
                    filtered_df[f'{checkpoint} %'] = (filtered_df[f'{checkpoint} Sum In Flow'] / (filtered_df['Precheck Sum In Flow'] + filtered_df[f'{checkpoint} Sum In Flow'])) * 100
                # if filtered_df has 2 different dates in last 2 rows, remove last row
                if len(filtered_df) > 1 and filtered_df.iloc[-1, 0] != filtered_df.iloc[-2, 0]:
                    filtered_df.drop(filtered_df.tail(1).index, inplace=True)

                st.dataframe(filtered_df, use_container_width=True)

            print("month selected is: ", selected_month_year_range)
            print("date selected is: ", datevalues)

            st.write('## :airplane_departure: Calculate the number of lanes required based on throughput...')

            tempColNew1, tempColNew2 = st.columns(2)
            tempColNew3, tempColNew4 = st.columns(2)

            with tempColNew1:
                precheck_throughput = st.selectbox('Select Precheck Column:', df.columns, index=None)

            with tempColNew2:
                precheck_throughput_slider = st.slider('Select Precheck Throughput (PAX/Hour):', 100, 300, 250, 5)

            with tempColNew3:
                standard_throughput = st.selectbox('Select Standard Column:', df.columns, index=None)

            with tempColNew4:
                standard_throughput_slider = st.slider('Select Standard Throughput (PAX/Hour):', 100, 300, 150, 5)

            if precheck_throughput is not None and standard_throughput is not None:

                st.write(f'Selected throughput values for `precheck` is `{precheck_throughput_slider} Pax/Hour` and for `standard` is `{standard_throughput_slider} Pax/Hour`')

                if precheck_throughput is not None and precheck_throughput_slider is not None:
                    filtered_df['Precheck Lanes Needed'] = (filtered_df[precheck_throughput] / precheck_throughput_slider).round(0).apply(lambda x: 1 if x == 0 else x)
                    # st.dataframe(filtered_df, use_container_width=True)

                if standard_throughput is not None and standard_throughput_slider is not None:
                    filtered_df['Standard Lanes Needed'] = (filtered_df[standard_throughput] / standard_throughput_slider).round(0).apply(lambda x: 1 if x == 0 else x)
                
                # drop Precheck % and Checkpoint % columns
                if 'Precheck %' in filtered_df.columns:
                    filtered_df.drop(columns=['Precheck %', f'{checkpoint} %'], inplace=True)

                # rearrange the columns in the dataframe 1 Checkpoint A Sum In Flow, 2 Standard Lanes Needed, 3 Precheck Sum In Flow, 4 Precheck Lanes Needed
                filtered_df = filtered_df[[f'{checkpoint} Sum In Flow', 'Standard Lanes Needed', 'Precheck Sum In Flow', 'Precheck Lanes Needed']]

                # find max lanes needed out of Precheck Lanes Needed and Standard Lanes Needed
                max_standard = filtered_df['Standard Lanes Needed'].max()
                max_precheck = filtered_df['Precheck Lanes Needed'].max()

                if operation.lower() == 'mean':
                    myOperation = 'Average'
                elif operation.lower() == 'max':
                    myOperation = 'Maximum'
                elif operation.lower() == 'quantile':
                    myOperation = str(quantileQ) + ' Quantile'

                if standard_throughput_slider > 0 and precheck_throughput_slider > 0 and max_standard > 0 and max_precheck > 0:
                    st.markdown(f"""
                        - If we perform operations to get `{myOperation}` values over the data:
                            - With **Standard throughput**: `{standard_throughput_slider} Pax/Hour` Max lanes required: `{int(max_standard)}`
                            - With **Precheck throughput**: `{precheck_throughput_slider} Pax/Hour` Max lanes required: `{int(max_precheck)}`
                        """, unsafe_allow_html=True)
                else:
                    st.warning(':warning: Please modify the search parameters to calculate the number of lanes')


                showTable2, showGraph2 = st.columns(2)

                with showTable2:
                    showTable2Checkbox = st.checkbox('Show data for each hour as table', value=False, key='showTable2Checkbox')

                with showGraph2:
                    showGraph2Checkbox = st.checkbox('Show Graph', value=False, key='showGraph2Checkbox')

                if showTable2Checkbox:
                    st.dataframe(filtered_df, use_container_width=True)

                if showGraph2Checkbox:
                    st.bar_chart(filtered_df.iloc[:, 1::2], use_container_width=True, stack=False)
            else:
                st.warning(':warning: Please select the throughput columns to calculate the number of lanes')


                                
        else:
            st.warning(':warning: Please select the columns to perform operations... ')

        








if __name__ == "__main__":
    main()
