import plotly.express as px
import streamlit as st
from config import SAMPLE_DTYPE

st.set_page_config(layout="wide")

# Check if data is saved
if st.session_state.get("_sample_aggrid") is None:
    st.warning("Please Upload a excel in the Upload page first.")
    st.stop()


df_toplot = st.session_state._sample_aggrid["data"]
for column, dtype in SAMPLE_DTYPE.items():
    if column in df_toplot.columns:
        df_toplot[column] = df_toplot[column].astype(dtype)


st.dataframe(data=df_toplot, height=600, use_container_width=True)

st.markdown("## Sample info in daily scale")
tab1, tab2 = st.tabs(["Age group", "Gender group"])
with tab1:
    df_age_group = (
        df_toplot.groupby([df_toplot["collect_time"].dt.date, "age_group"])
        .size()
        .reset_index(name="count")
    )

    fig_age_group = px.line(
        df_age_group,
        x="collect_time",
        y="count",
        color="age_group",
        title="按年龄段分组的送样量折线图",
        labels={"collect_time": "时间", "count": "送样量", "age_group": "年龄组"},
    )
    st.plotly_chart(fig_age_group, use_container_width=True)

with tab2:
    df_gender = (
        df_toplot.groupby([df_toplot["collect_time"].dt.date, "gender"])
        .size()
        .reset_index(name="count")
    )

    fig_gender = px.line(
        df_gender,
        x="collect_time",
        y="count",
        color="gender",
        title="按性别分组的送样量折线图",
        labels={"collect_time": "时间", "count": "送样量", "性别": "性别"},
    )
    st.plotly_chart(fig_gender, use_container_width=True)


df_toplot["month"] = df_toplot["collect_time"].dt.to_period("M").astype(str)

st.markdown("## Sample info in monthly scale")
tab1, tab2 = st.tabs(["Age group", "Gender group"])
with tab1:
    df_age_group_month = (
        df_toplot.groupby(["month", "age_group"]).size().reset_index(name="count")
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
