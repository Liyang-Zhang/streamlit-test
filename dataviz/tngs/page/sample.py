import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import GridOptionsBuilder, JsCode

from dataviz.tngs.utils.config import AgGridConfig, GridOptionsBuilderConfig
from dataviz.tngs.utils.constants import LICENSE_KEY, SAMPLE_COLUMNS, SAMPLE_DTYPE
from dataviz.tngs.utils.plot import plot_histogram, plot_pie_chart, plot_wordcloud

# Initialize session state for dataframes
session_state_keys = [
    "_uploaded_file",
    "_sample_df",
    "_sample_aggrid",
]
for key in session_state_keys:
    if key not in st.session_state:
        st.session_state[key] = None

# Set filter state
onFirstDataRendered = JsCode(
    """
function onFirstDataRendered(params) {
  console.log('onFirstDataRendered start');
  var sampleFilterStateStr = localStorage.getItem('sampleFilterStateStr');
  console.log('filterStateStr loaded:', sampleFilterStateStr);
  console.log('JSON parsed filterStateStr:', JSON.parse(sampleFilterStateStr));
  params.api.setFilterModel(JSON.parse(sampleFilterStateStr));

  console.log('onFirstDataRendered end');
}
"""
)


onFilterChanged = JsCode(
    """
function onFilterChanged(params) {
    console.log('onFilterChanged start');
    const sampleFilterState = params.api.getFilterModel();
    const sampleFilterStateStr = JSON.stringify(sampleFilterState);
    console.log('filterState captured in JS:', sampleFilterState);
    console.log('filterStateStr captured in JS:', sampleFilterStateStr);
    localStorage.setItem('sampleFilterStateStr', sampleFilterStateStr);  // Save filter state to localStorage
    console.log('onFilterChanged end');
}
"""
)


RETAIN_FILTER_STATE_OPTIONS = {
    "onFirstDataRendered": onFirstDataRendered,
    "onFilterChanged": onFilterChanged,
}


def _load_sample_sheet(file, sheet_name="sample"):
    df = pd.read_excel(file, sheet_name=sheet_name, dtype=SAMPLE_DTYPE)
    df = df.loc[:, SAMPLE_COLUMNS]
    return df


@st.experimental_fragment()
def load_data():
    # Check if data is loaded
    if st.session_state.get("_uploaded_file") is None:
        st.warning("Please Upload a excel in the Home page first.")
        st.stop()

    uploaded_file = st.session_state._uploaded_file
    try:
        df_sample = _load_sample_sheet(file=uploaded_file)
        st.session_state._sample_df = df_sample
    except Exception as e:
        st.error(f"Error reading the uploaded file: {e}")
    else:
        process_data(df_sample)


def process_data(df_sample: pd.DataFrame):
    if st.session_state.get("_sample_df") is not None:
        df_sample = st.session_state._sample_df
        gb = GridOptionsBuilder.from_dataframe(df_sample)
        ag_grid_config = AgGridConfig(
            grid_options_builder_config=GridOptionsBuilderConfig(
                configure_pagination=[{"enabled": True}],
                configure_selection=[{"selection_mode": "disable"}],
                configure_default_column=[{"filter": True, "editable": False}],
                configure_side_bar=[{"filters_panel": True, "columns_panel": True}],
                configure_first_column_as_index=[{"headerText": "sample_name"}],
                configure_columns=[
                    {
                        "column_names": [
                            "age",
                            "age_float",
                            "hospital",
                            "receive_time",
                            "clinical_diagnosis",
                        ],
                        "hide": True,
                    }
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
            sample_grid_table = ag_grid_config.get_aggrid(gb, df_sample)
            st.session_state._sample_aggrid = sample_grid_table

        with tab2:
            st.write(st.session_state._sample_aggrid.data)

    else:
        st.write("Please upload a file to proceed.")

    print("Processed data:", st.session_state._sample_aggrid.data.shape)


@st.experimental_fragment()
def sample_plot():
    """
    Make plot based on the filtered sample df
    """
    if st.button("Update plot"):
        df_toplot = st.session_state._sample_aggrid.data
        print("Plot data:", df_toplot.shape)

        for column, dtype in SAMPLE_DTYPE.items():
            if column in df_toplot.columns:
                df_toplot[column] = df_toplot[column].astype(dtype)

        st.markdown("## Sample overview")
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
            [
                "Sample type",
                "Gender",
                "Age",
                "Department",
                "Patho",
                "Drugresis",
                "出具结果",
                "clinical_diagnosis",
            ]
        )
        with tab1:
            fig_sampletype = plot_pie_chart(df_toplot, "sample_type")
            st.plotly_chart(fig_sampletype, use_container_width=True)
        with tab2:
            fig_gender = plot_pie_chart(df_toplot, "gender")
            st.plotly_chart(fig_gender, use_container_width=True)
        with tab3:
            fig_agegroup = plot_pie_chart(df_toplot, "age_group")
            st.plotly_chart(fig_agegroup, use_container_width=True)
        with tab4:
            fig_department = plot_pie_chart(df_toplot, "department")
            st.plotly_chart(fig_department, use_container_width=True)
        with tab5:
            fig_patho = plot_histogram(df_toplot, "number_of_detected_pathos")
            st.plotly_chart(fig_patho, use_container_width=True)
        with tab6:
            fig_drugresis = plot_histogram(df_toplot, "number_of_detected_drugresis")
            st.plotly_chart(fig_drugresis, use_container_width=True)
        with tab7:
            fig_result = plot_wordcloud(df_toplot, "出具结果")
            st.pyplot(fig_result, use_container_width=True)
        with tab8:
            fig_clinicaldiagnosis = plot_wordcloud(df_toplot, "clinical_diagnosis")
            st.pyplot(fig_clinicaldiagnosis, use_container_width=True)

        st.markdown("## Sample info in month scale")
        df_toplot["month"] = df_toplot["collect_time"].dt.to_period("M").astype(str)
        tab1, tab2 = st.tabs(["Age group", "Gender group"])
        with tab1:
            df_age_group_month = (
                df_toplot.groupby(["month", "age_group"])
                .size()
                .reset_index(name="count")
            )

            fig_age_group_month = px.line(
                df_age_group_month,
                x="month",
                y="count",
                color="age_group",
                title="按年龄段分组的送样量折线图",
                labels={"month": "月份", "count": "送样量", "age_group": "年龄组"},
            )
            fig_age_group_month.update_layout(xaxis=dict(tickformat="%Y-%m"))
            st.plotly_chart(fig_age_group_month, use_container_width=True)

        with tab2:
            df_gender_month = (
                df_toplot.groupby(["month", "gender"]).size().reset_index(name="count")
            )

            # 使用 plotly.express 创建按性别分组的送样量折线图
            fig_gender_month = px.line(
                df_gender_month,
                x="month",
                y="count",
                color="gender",
                title="按性别分组的送样量折线图",
                labels={"month": "月份", "count": "送样量", "性别": "性别"},
            )
            fig_gender_month.update_layout(xaxis=dict(tickformat="%Y-%m"))
            st.plotly_chart(fig_gender_month, use_container_width=True)


# Main commands to run
print("1111111111111111111111")
load_data()
print("2222222222222222222222")
sample_plot()
print("3333333333333333333333")
