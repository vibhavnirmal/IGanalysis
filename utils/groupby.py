import streamlit as st
import pandas as pd

# Sample Data
data = {
    'Category': ['A', 'A', 'B', 'B', 'C', 'C'],
    'Subcategory': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
    'Values': [100, 150, 200, 250, 300, 350],
    'Counts': [20, 10, 10, 20, 30, 30]
}
df = pd.DataFrame(data)

st.title('Group Data by Multiple Columns')

# Display the DataFrame
st.write("Original Data:")
st.dataframe(df)

# Allow user to select multiple columns to group by
group_by_columns = st.multiselect(
    'Select columns to group by:',
    options=df.columns.tolist(),
    default=[]
)

# Check if the user has selected any columns
if group_by_columns:
    # Group by the selected columns and aggregate by sum (or any other aggregation)
    grouped_df = df.groupby(group_by_columns).sum().reset_index()
    
    # Display the grouped DataFrame
    st.write(f"Data grouped by {', '.join(group_by_columns)}:")
    st.dataframe(grouped_df)
else:
    st.write("Please select at least one column to group by.")
