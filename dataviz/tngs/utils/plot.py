import os

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Figure
from plotly.subplots import make_subplots
from wordcloud import WordCloud


def sample_etiology_heatmap(df: pd.DataFrame, mode: str = "count") -> Figure:
    """
    Make heatmap to show the detected patho in a period of time.
    Input:
        1. df: etiology and sample merged dataframe with necessary cols:
            1. sample_name (string)
            2. collect_time (datetime64)
            3. patho_name (string)
        2. mode: str, either "count" for number of detections or "frequency" for detection frequency.
    Return:
        1. plotly Figure
    """

    COLUMN_DTYPE = {
        "sample_name": "string",
        "patho_name": "string",
        "collect_time": "datetime64[ns]",
    }

    # Check necessary columns
    missing_columns = [col for col in COLUMN_DTYPE.keys() if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in DataFrame: {missing_columns}")

    # Convert data type
    for col, dtype in COLUMN_DTYPE.items():
        try:
            df.loc[:, col] = df[col].astype(dtype)
        except Exception as e:
            raise ValueError(f"Cannot convert column '{col}' to type '{dtype}': {e}")

    # Extract cols
    df_sub = df[list(COLUMN_DTYPE.keys())].copy()

    df_sub["month"] = (
        df_sub["collect_time"].astype("datetime64[ns]").dt.to_period("M").astype(str)
    )
    # Aggregate data to get counts
    heatmap_data = (
        df_sub.groupby(["month", "patho_name"]).size().reset_index(name="count")
    )

    # Get monthly sample count
    monthly_samples = df_sub.groupby("month")["sample_name"].nunique()
    monthly_samples.name = "total_samples"
    print(monthly_samples)
    # monthly_samples = df_sub.groupby("month")["sample_name"].nunique().reset_index(name="total_samples")

    # Always store a heatmap_data_count for bar plot
    heatmap_data_count = heatmap_data
    heatmap_data_count["value"] = heatmap_data_count["count"]

    if mode == "frequency":
        # Merge heatmap data with monthly sample counts to calculate frequencies
        heatmap_data = pd.merge(heatmap_data, monthly_samples, on="month")
        print(heatmap_data)
        heatmap_data["value"] = heatmap_data["count"] / heatmap_data["total_samples"]
        colorbar_title = "Frequency"
        # Pivot the data for heatmap
        heatmap_data_pivot = heatmap_data.pivot(
            index="patho_name", columns="month", values="value"
        ).fillna(0)
        heatmap_data_pivot = heatmap_data_pivot.loc[
            heatmap_data_pivot.sum(axis=1).sort_values(ascending=True).index
        ]
        heatmap_data_count_pivot = heatmap_data_count.pivot(
            index="patho_name", columns="month", values="value"
        ).fillna(0)
        heatmap_data_count_pivot = heatmap_data_count_pivot.loc[
            heatmap_data_pivot.sum(axis=1).sort_values(ascending=True).index
        ]
        total_counts = heatmap_data_count_pivot.sum(axis=1)
        monthly_totals = heatmap_data_count_pivot.sum(axis=0)
    elif mode == "count":
        heatmap_data["value"] = heatmap_data["count"]
        colorbar_title = "Count"
        # Pivot the data for heatmap
        heatmap_data_pivot = heatmap_data.pivot(
            index="patho_name", columns="month", values="value"
        ).fillna(0)
        heatmap_data_pivot = heatmap_data_pivot.loc[
            heatmap_data_pivot.sum(axis=1).sort_values(ascending=True).index
        ]
        total_counts = heatmap_data_pivot.sum(axis=1)
        monthly_totals = heatmap_data_pivot.sum(axis=0)
    else:
        raise ValueError("Invalid mode. Choose either 'count' or 'frequency'.")

    # Plot
    dynamic_height = 20 * len(heatmap_data_pivot.index)

    fig = make_subplots(
        rows=2,
        cols=2,
        row_heights=[0.1, 0.9],
        column_widths=[0.8, 0.2],
        specs=[[{"type": "bar"}, None], [{"type": "heatmap"}, {"type": "bar"}]],
        horizontal_spacing=0.05,
        vertical_spacing=0.005,
        shared_xaxes=True,
        shared_yaxes=True,
    )
    # 添加月份总检出的柱状图
    monthly_bar = go.Bar(
        x=monthly_totals.index.astype(str),
        y=monthly_totals.values,
        name="Total Pathos",
        orientation="v",
    )
    fig.add_trace(monthly_bar, row=1, col=1)
    # 添加每个月的总样本数柱状图
    sample_bar = go.Bar(
        x=monthly_samples.index.astype(str),
        y=monthly_samples.values,
        name="Total Samples",
        orientation="v",
        marker_color="rgba(255, 0, 0, 0.5)",  # 使用不同颜色
    )
    fig.add_trace(sample_bar, row=1, col=1)

    # 添加热图
    heatmap = go.Heatmap(
        z=heatmap_data_pivot.values,
        x=heatmap_data_pivot.columns.astype(str),
        y=heatmap_data_pivot.index,
        colorscale="Blues",
        colorbar=dict(title="Count"),
        name=f"Detected {colorbar_title}",
    )
    fig.add_trace(heatmap, row=2, col=1)

    # 添加柱状图
    bar = go.Bar(
        x=total_counts.values, y=total_counts.index, orientation="h", name="Total patho"
    )
    fig.add_trace(bar, row=2, col=2)

    # 更新布局
    fig.update_layout(
        title="Pathogen Detection Frequency Heatmap with Total Counts",
        height=dynamic_height + 500,
        width=1200,
        yaxis=dict(tickfont=dict(size=10)),
        showlegend=False,
        barmode="overlay",
    )

    return fig


def plot_pie_chart(df, column_name):
    """
    Function to plot a pie chart for a specific column in the DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    column_name (str): The name of the column to plot.

    Returns:
    A Plotly pie chart.
    """
    fig = px.pie(df, names=column_name, title=f"Distribution of {column_name}")
    return fig


def plot_histogram(df, column_name, bins=None):
    """
    Function to plot a histogram for a specific column in the DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    column_name (str): The name of the column to plot.
    bins (int): The number of bins for the histogram. Default is None.

    Returns:
    A Plotly histogram.
    """
    fig = px.histogram(
        df, x=column_name, nbins=bins, title=f"Histogram of {column_name}"
    )
    return fig


def plot_wordcloud(df, column_name, font_path="./dataviz/tngs/utils/simhei.ttf"):
    """
    Function to plot a word cloud for a specific column in the DataFrame.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing the data.
    column_name (str): The name of the column to plot.

    Returns:
    A matplotlib plot of the word cloud.
    """
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    # Concatenate all text in the column into a single string
    text = " ".join(df[column_name].astype(str).values)

    # Generate the word cloud
    wordcloud = WordCloud(
        width=800, height=400, background_color="white", font_path=font_path
    ).generate(text)

    # Plot the word cloud
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    return fig
