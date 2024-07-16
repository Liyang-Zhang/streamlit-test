import pandas as pd
import streamlit as st
from page.sample import _load_sample_sheet
from st_aggrid import GridOptionsBuilder, JsCode
from utils.config import AgGridConfig, GridOptionsBuilderConfig
from utils.constants import ETIOLOGY_COLUMNS, ETIOLOGY_DTYPE, LICENSE_KEY
from utils.plot import sample_etiology_heatmap

# Initialize session state for dataframes
session_state_keys = [
    "_uploaded_file",
    "_etiology_df",
    "_etiology_aggrid",
]
for key in session_state_keys:
    if key not in st.session_state:
        st.session_state[key] = None

# Set filter state
onFirstDataRendered = JsCode(
    """
function onFirstDataRendered(params) {
  console.log('onFirstDataRendered start');
  var etiologyFilterStateStr = localStorage.getItem('etiologyFilterStateStr');
  console.log('filterStateStr loaded:', etiologyFilterStateStr);
  console.log('JSON parsed filterStateStr:', JSON.parse(etiologyFilterStateStr));
  params.api.setFilterModel(JSON.parse(etiologyFilterStateStr));

  console.log('onFirstDataRendered end');
}
"""
)


onFilterChanged = JsCode(
    """
function onFilterChanged(params) {
    console.log('onFilterChanged start');
    const etiologyFilterState = params.api.getFilterModel();
    const etiologyFilterStateStr = JSON.stringify(etiologyFilterState);
    console.log('filterState captured in JS:', etiologyFilterState);
    console.log('filterStateStr captured in JS:', etiologyFilterStateStr);
    localStorage.setItem('etiologyFilterStateStr', etiologyFilterStateStr);  // Save filter state to localStorage
    console.log('onFilterChanged end');
}
"""
)


RETAIN_FILTER_STATE_OPTIONS = {
    "onFirstDataRendered": onFirstDataRendered,
    "onFilterChanged": onFilterChanged,
}


def _load_etiology_sheet(file, sheet_name="etiology"):
    df = pd.read_excel(file, sheet_name=sheet_name, dtype=ETIOLOGY_DTYPE)
    df = df.loc[:, ETIOLOGY_COLUMNS]
    return df


def _merge_sample_df(df_etiology: pd.DataFrame, df_sample: pd.DataFrame):
    df_merge = df_sample.merge(
        df_etiology, left_on="sample_name", right_on="sample_name", how="left"
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
        df_etiology = _load_etiology_sheet(file=uploaded_file)
        df_sample = _load_sample_sheet(uploaded_file)
        df_merge = _merge_sample_df(df_etiology=df_etiology, df_sample=df_sample)
        st.session_state._etiology_df = df_merge
    except Exception as e:
        st.error(f"Error reading the uploaded file: {e}")
    else:
        process_data(df_etiology)


def process_data(df_etiology: pd.DataFrame):
    if st.session_state.get("_etiology_df") is not None:
        df_etiology = st.session_state._etiology_df
        gb = GridOptionsBuilder.from_dataframe(df_etiology)
        ag_grid_config = AgGridConfig(
            grid_options_builder_config=GridOptionsBuilderConfig(
                configure_pagination=[{"enabled": True}],
                configure_selection=[{"selection_mode": "disable"}],
                configure_default_column=[{"filter": True, "editable": False}],
                configure_side_bar=[{"filters_panel": True, "columns_panel": True}],
                configure_first_column_as_index=[{"headerText": "sample_name"}],
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
            sample_grid_table = ag_grid_config.get_aggrid(gb, df_etiology)
            st.session_state._etiology_aggrid = sample_grid_table

        with tab2:
            st.write(st.session_state._etiology_aggrid.data)

    else:
        st.write("Please upload a file to proceed.")


@st.experimental_fragment()
def etiology_plot():
    print("Running plot")
    df_toplot = st.session_state._etiology_aggrid.data
    # Get total unique pathos count
    total_patho_num = df_toplot["patho_name"].nunique()

    # Step 1: Slider to select the number of pathos to display
    selected_patho_num = st.slider(
        "Please selcet the number of pathos to plot:",
        min_value=1,
        max_value=total_patho_num,
        value=total_patho_num,
    )
    st.write(selected_patho_num)

    # Step 2: Get the top N pathos based on selected patho count
    top_pathos = (
        df_toplot["patho_name"]
        .value_counts()
        .nlargest(selected_patho_num)
        .index.tolist()
    )

    # Step 3: Multiselect widget for user to select specific pathos of interest
    selected_pathos = st.multiselect(
        "Select the pathos you are interested in:",
        options=top_pathos,
        default=top_pathos,
    )

    # Step 4: Filter the dataframe based on final selected pathos
    filtered_df = df_toplot.loc[df_toplot["patho_name"].isin(selected_pathos)]

    if st.button("Update plot"):
        tab1, tab2 = st.tabs(["Count", "Frequency"])
        with tab1:
            fig_count = sample_etiology_heatmap(filtered_df)
            st.plotly_chart(fig_count, use_container_width=True)
        with tab2:
            fig_freq = sample_etiology_heatmap(filtered_df, mode="frequency")
            st.plotly_chart(fig_freq, use_container_width=True)


upload_data()
etiology_plot()
