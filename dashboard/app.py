import streamlit as st
import pandas as pd


def multiselect_filter(df, column, label, key, col):
    """Create a multiselect filter for a specific column in the DataFrame.
    If the column exists, it will create a multiselect widget with options from the column.
    If 'All' is selected, it will not filter the DataFrame.
    If specific values are selected, it will filter the DataFrame accordingly.
    """
    if column in df.columns:
        options = ["All"] + sorted(df[column].dropna().unique().tolist())
        if key not in st.session_state:
            st.session_state[key] = ["All"]
        col.multiselect(
            label,
            options=options,
            key=key,
            on_change=remove_all_from_multiselect,
            args=(key,),
        )
        selected = st.session_state.get(key, ["All"])
        if "All" not in selected:
            df = df[df[column].isin(selected)]
    return df


def remove_all_from_multiselect(key):
    """Remove 'All' from the selected values if other values are also selected.
    If no values are selected, reset to 'All'.
    """
    selected = st.session_state.get(key, [])
    if selected == []:
        st.session_state[key] = ["All"]
    elif "All" in selected and len(selected) > 1:
        st.session_state[key] = [v for v in selected if v != "All"]


def display_filters(df):
    """Display multiselect filters for the DataFrame.
    Creates two rows of columns for filters and applies the filters to the DataFrame.
    """
    with st.expander("Filters"):
        filter_row1 = st.columns(2)
        filter_row2 = st.columns(2)
        df = multiselect_filter(df, "compliance", "Compliance Status", "compliance_status_filter", filter_row1[0])
        df = multiselect_filter(df, "accountId", "Account ID", "account_id_filter", filter_row1[1])
        df = multiselect_filter(df, "controlName", "Control Name", "control_name_filter", filter_row2[0])
        df = multiselect_filter(df, "resourceType", "Resource Type", "resource_type_filter", filter_row2[1])
    return df


def main():
    st.title("Welcome to the Dashboard")
    st.write("This is a simple Streamlit dashboard application.")
    file_content = st.file_uploader("Upload a CSV file", type=["csv"])

    if file_content is not None:
        df = pd.read_csv(file_content)
        filtered_df = display_filters(df)
        st.dataframe(filtered_df, use_container_width=True)


if __name__ == "__main__":
    main()
