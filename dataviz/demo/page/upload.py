import pandas as pd
import streamlit as st
from config import LICENSE_KEY, SAMPLE_COLUMNS, SAMPLE_DTYPE
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(layout="wide")

# Initialize session state for dataframes
session_state_keys = [
    "_uploaded_file",
    "_sample_df",
    "_sample_aggrid",
]
for key in session_state_keys:
    if key not in st.session_state:
        st.session_state[key] = None


# Callback for saving filter state
onFilterChanged = JsCode(
    """
function onFilterChanged(params) {
    console.log('onFilterChanged start');
    const filterState = params.api.getFilterModel();
    const filterStateStr = JSON.stringify(filterState);
    console.log('filterState captured in JS:', filterState);
    console.log('filterStateStr captured in JS:', filterStateStr);
    localStorage.setItem('filterStateStr', filterStateStr);  // Save filter state to localStorage
    console.log('onFilterChanged end');
}
"""
)


onFirstDataRendered = JsCode(
    """
function onFirstDataRendered(params) {
  console.log('onFirstDataRendered start');
  var filterStateStr = localStorage.getItem('filterStateStr');
  console.log('filterStateStr loaded:', filterStateStr);
  console.log('JSON parsed filterStateStr:', JSON.parse(filterStateStr));
  params.api.setFilterModel(JSON.parse(filterStateStr));

  console.log('onFirstDataRendered end');
}
"""
)

options = {
    "onFirstDataRendered": onFirstDataRendered,
    "onFilterChanged": onFilterChanged,
}


def _load_sample_sheet(file, sheet_name="sample"):
    df = pd.read_excel(file, sheet_name=sheet_name, dtype=SAMPLE_DTYPE)
    df = df.loc[:, SAMPLE_COLUMNS]
    return df


# Function to set up AG Grid
def _set_sample_aggrid(df: pd.DataFrame):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination()
    gb.configure_selection(selection_mode="disable")
    gb.configure_default_column(filterable=True, editable=False)
    gb.configure_side_bar(filters_panel=True, columns_panel=True)
    gb.configure_first_column_as_index(headerText="sample_name")
    gb.configure_columns(
        column_names=[
            "age",
            "age_float",
            "hospital",
            "receive_time",
            "clinical_diagnosis",
        ],
        hide=True,
    )
    gb.configure_columns(
        column_names=["age_group"],
        rowGroup=True,
    )

    gb.configure_grid_options(**options)

    go = gb.build()

    return AgGrid(
        df,
        update_on=["cellValueChanged"],
        gridOptions=go,
        theme="streamlit",
        height=800,
        allow_unsafe_jscode=True,
        license_key=LICENSE_KEY,
        enable_enterprise_modules=True,
    )


@st.experimental_fragment()
def upload_data():
    uploaded_file = st.file_uploader(
        label="Please choose an Excel file to upload", type=["xlsx"]
    )
    if uploaded_file is not None:
        st.session_state._uploaded_file = uploaded_file

    if st.session_state.get("_uploaded_file") is not None:
        uploaded_file = st.session_state._uploaded_file
        try:
            df_sample = _load_sample_sheet(file=uploaded_file)
            st.session_state._sample_df = df_sample
        except Exception as e:
            st.error(f"Error reading the uploaded file: {e}")
        else:
            process_data(df_sample)


@st.experimental_fragment()
def process_data(df_sample: pd.DataFrame):
    if st.session_state.get("_sample_df") is not None:
        df_sample = st.session_state._sample_df

        tab1, tab2 = st.tabs(["AgGrid", "Data"])
        with tab1:
            sample_grid_table = _set_sample_aggrid(df=df_sample)
            st.session_state._sample_aggrid = sample_grid_table

        with tab2:
            st.write(st.session_state._sample_aggrid.data)

    else:
        st.write("Please upload a file to proceed.")


upload_data()
