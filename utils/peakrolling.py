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

        rolling_max_time = rolling_max_time.left
        return int(rolling_max), rolling_max_time
