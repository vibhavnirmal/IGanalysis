import streamlit as st

def group_values_and_update_df(df, col1, col2):
    
    # check if col2 is [[]]
    if col2 == [[]] or col2 == [[], []] or len(col2) != 2:
        st.warning('Please select the values for grouping.')
        return df
    
    if col1 and col2 is not None:

        df['PaxSPorPE'] = df[col1].apply(lambda x: 1 if x in col2[0] else 2 if x in col2[1] else 3)

        # check if 3 exists, if yes, give error
        if 3 in df['PaxSPorPE'].unique():
            st.error('Error: 3 is present in the column. Please check the values and try again.')
            return df

        return df

