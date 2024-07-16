import pandas as pd
import streamlit as st
from page.sample import _load_sample_sheet
from st_aggrid import GridOptionsBuilder, JsCode
from utils.config import AgGridConfig, GridOptionsBuilderConfig
from utils.constants import DRUGRESIS_COLUMNS, DRUGRESIS_DTYPE, LICENSE_KEY

# Initialize session state for dataframes
session_state_keys = [
    "_uploaded_file",
    "_drugresis_df",
    "_drugresis_aggrid",
]
for key in session_state_keys:
    if key not in st.session_state:
        st.session_state[key] = None

# Set filter state
onFirstDataRendered = JsCode(
    """
function onFirstDataRendered(params) {
  console.log('onFirstDataRendered start');
  var drugresisFilterStateStr = localStorage.getItem('drugresisFilterStateStr');
  console.log('filterStateStr loaded:', drugresisFilterStateStr);
  console.log('JSON parsed filterStateStr:', JSON.parse(drugresisFilterStateStr));
  params.api.setFilterModel(JSON.parse(drugresisFilterStateStr));

  console.log('onFirstDataRendered end');
}
"""
)


onFilterChanged = JsCode(
    """
function onFilterChanged(params) {
    console.log('onFilterChanged start');
    const drugresisFilterState = params.api.getFilterModel();
    const drugresisFilterStateStr = JSON.stringify(drugresisFilterState);
    console.log('filterState captured in JS:', drugresisFilterState);
    console.log('filterStateStr captured in JS:', drugresisFilterStateStr);
    localStorage.setItem('drugresisFilterStateStr', drugresisFilterStateStr);  // Save filter state to localStorage
    console.log('onFilterChanged end');
}
"""
)


RETAIN_FILTER_STATE_OPTIONS = {
    "onFirstDataRendered": onFirstDataRendered,
    "onFilterChanged": onFilterChanged,
}


def _load_drugresis_sheet(file, sheet_name="drugresis"):
    df = pd.read_excel(file, sheet_name=sheet_name, dtype=DRUGRESIS_DTYPE)
    df = df.loc[:, DRUGRESIS_COLUMNS]
    return df


def _merge_sample_df(df_drugresis: pd.DataFrame, df_sample: pd.DataFrame):
    df_merge = df_sample.merge(
        df_drugresis, left_on="sample_name", right_on="sample_name", how="left"
    )
    return df_merge


@st.experimental_fragment()
def upload_data():
    # Check if data is loaded
    if st.session_state.get("_uploaded_file") is None:
        st.warning("Please Upload a excel in the Home page first.")
        st.stop()

    uploaded_file = st.session_state._uploaded_file
    try:
        df_drugresis = _load_drugresis_sheet(file=uploaded_file)
        df_sample = _load_sample_sheet(uploaded_file)
        df_merge = _merge_sample_df(df_drugresis=df_drugresis, df_sample=df_sample)
        st.session_state._drugresis_df = df_merge
    except Exception as e:
        st.error(f"Error reading the uploaded file: {e}")
    else:
        process_data(df_drugresis)


@st.experimental_fragment()
def process_data(df_drugresis: pd.DataFrame):
    if st.session_state.get("_drugresis_df") is not None:
        df_drugresis = st.session_state._drugresis_df
        gb = GridOptionsBuilder.from_dataframe(df_drugresis)
        ag_grid_config = AgGridConfig(
            grid_options_builder_config=GridOptionsBuilderConfig(
                configure_pagination=[{"enabled": True}],
                configure_selection=[{"selection_mode": "disable"}],
                configure_default_column=[{"filter": True, "editable": False}],
                configure_side_bar=[{"filters_panel": True, "columns_panel": True}],
                configure_first_column_as_index=[{"headerText": "sample_name"}],
                configure_columns=[
                    {"column_names": [], "hide": True},
                    {"column_names": [], "rowGroup": True},
                ],
                configure_grid_options=[RETAIN_FILTER_STATE_OPTIONS],
            ),
            kwargs={
                "theme": "streamlit",
                "height": 800,
                "allow_unsafe_jscode": True,
                "license_key": LICENSE_KEY,
                "enable_enterprise_modules": True,
            },
        )

        tab1, tab2 = st.tabs(["AgGrid", "Data"])
        with tab1:
            sample_grid_table = ag_grid_config.get_aggrid(gb, df_drugresis)
            st.session_state._drugresis_aggrid = sample_grid_table

        with tab2:
            st.write(st.session_state._drugresis_aggrid.data)

    else:
        st.write("Please upload a file to proceed.")


upload_data()
