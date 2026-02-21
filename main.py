import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

##### Utilities #####

def linear_regression(session_stats, x, y):
    '''
    Generates a line showing tendency with a slope according to density of points
    '''
    slope, intercept = np.polyfit(x, y, 1)
    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = slope * x_line + intercept
    return x_line, y_line

##### CONFIG #####

st.set_page_config(page_title="Cube Performance Dashboard", layout="wide")
st.title("Speedcube Performance Dashboard")


def parse_time_mmss(s):
    """Converts strings mm:ss.xx to pd.Timedelta"""
    if pd.isna(s):
        return pd.Timedelta(0)

    try:
        min_part, sec_part = s.split(":")
        total_seconds = int(min_part) * 60 + float(sec_part)
        return pd.Timedelta(seconds=total_seconds)
    except:
        return pd.Timedelta(0)

##### LOAD DATA #####

@st.cache_data
def load_data():
    '''
    Loads data from "data.csv" to variable "df". 
    '''
    df = pd.read_csv("data.csv", sep=";", engine="python", encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()

    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df["time"] = df["time"].astype(str).apply(parse_time_mmss)
    df["time_sec"] = df["time"].dt.total_seconds()
    
    df = df.sort_values("date")
    
    df["year"] = df["date"].dt.year
    df["hour"] = df["date"].dt.hour
    df["weekday"] = df["date"].dt.day_name()

    df["time_diff"] = df["date"].diff().dt.total_seconds()
    df["new_session"] = df["time_diff"] > 300
    df["session_id"] = df["new_session"].cumsum()
    
    return df

df = load_data()

##### SIDEBAR FILTER #####

st.sidebar.header("Filters")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date]
)

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    df = df.loc[mask]

##### METRICS #####

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Solves", len(df))
col2.metric("Mean Time", f"{df['time_sec'].mean():.2f} s")
col3.metric("Best Time", f"{df['time_sec'].min():.2f} s")
col4.metric("Standard Deviation", f"{df['time_sec'].std():.2f}")

st.divider()

######################
##### DASHBOARDS #####
#####################

##### MOVING AVERAGE #####
window = st.sidebar.slider("Moving Average Window", 1, 200, 150)

df["ma"] = df["time_sec"].rolling(window).mean()


fig1 = px.scatter(
    df,
    x="date",
    y="time_sec",
    title="Solve Times Over Time",
    labels={"time_sec": "Time (s)", "date": "Date"},
    render_mode="webgl"
) # Plot all times as points

fig1.add_scattergl(
    x=df["date"],
    y=df["ma"],
    mode="lines",
    name=f"MA{window}",
    line=dict(color="#fc8d62", width=3)
) # Plots MA filtered times as line

fig1.update_traces(marker=dict(color='blue', size=2, opacity=0.5), selector=dict(mode='markers'))
st.plotly_chart(fig1, use_container_width=True)


##### LINE: HISTOGRAM + SUB X (MESMA LINHA) #####

col_dist, col_subx = st.columns(2)

##### HISTOGRAM OF TIME WINDOWS (9.00-9.99, 10.00-10.99, 11.00-11.99, ...) #####

with col_dist:
    st.subheader("Time Distribution")

    fig3 = px.histogram(
        df, 
        x="time_sec", 
        nbins=50, 
        title="Histogram of Solve Times"
    )
    fig3.update_xaxes(dtick=1)   
    st.plotly_chart(fig3, use_container_width=True) 

##### SUB X #####
with col_subx:
    st.subheader("Sub-X Times")

    sub_x_values = range(6, 16)
    total_solves = len(df) 
    sub_x_counts = [(df["time_sec"] < x).sum() for x in sub_x_values]
    sub_x_probs = [ (count / total_solves) if total_solves > 0 else 0 for count in sub_x_counts] 
    sub_x_labels = [f"Sub {x}s" for x in sub_x_values]
    sub_x_df = pd.DataFrame({
        "sub_x": sub_x_labels,
        "amount": sub_x_counts,
        "prob": sub_x_probs
    })

    fig4 = px.bar(
        sub_x_df,
        x="sub_x",
        y="amount",
        text=sub_x_df["prob"].apply(lambda x: f"{x:.1%}"),
        title="Sub-X Solves",
        labels={"sub_x": "", "amount": "Number of Solves"}
    )

    fig4.update_traces(textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)


# LINE: SUB-X PROBABILITY OVER TIME

st.subheader("Rolling Probability of Sub-X")

sub_x_value = st.sidebar.slider("Select X (seconds)", 5.0, 15.0, 8.0, step=0.1)
df["is_sub_x"] = df["time_sec"] < sub_x_value
prob_window = st.sidebar.slider("Probability Window", 50, 2000, 500) # rolling probability
df["sub_x_prob"] = df["is_sub_x"].rolling(prob_window).mean()

fig_prob = px.line(
    df,
    x="date",
    y="sub_x_prob",
    title=f"Rolling Probability of Sub-{sub_x_value}s",
    labels={"sub_x_prob": "Probability", "date": "Date"}
)
fig_prob.update_traces(line=dict(color="#2a9d8f", width=3))
fig_prob.update_layout(yaxis=dict(range=[0, 1]))
st.plotly_chart(fig_prob, use_container_width=True)


# LINE: IMPACT OF TIME

st.subheader("Impact of time and frequency on performance")

col_heatmap, col_years = st.columns(2)

##### HEATMAP #####
with col_heatmap:

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    heatmap_data = (
        df.groupby(["weekday", "hour"])["time_sec"]
        .mean() 
        .reset_index()
    )

    heatmap_data["weekday"] = pd.Categorical(
        heatmap_data["weekday"],
        categories=weekday_order,
        ordered=True
    )

    pivot_table = heatmap_data.pivot(
        index="weekday",
        columns="hour",
        values="time_sec"
    )

    fig_heat = px.imshow(
        pivot_table,
        color_continuous_scale="RdYlGn_r",
        labels=dict(color="Average Time (s)"),
        aspect="auto",
        title="Heatmap",
    )

    fig_heat.update_xaxes(dtick=2)   
    st.plotly_chart(fig_heat, use_container_width=True)


##### SOLVES & PERFORMANCE PER YEAR #####
with col_years:

    yearly_stats = (
        df.groupby("year")
        .agg(
            solves=("time_sec", "count"),
            median_time=("time_sec", "median")
        )
        .reset_index()
        .sort_values("year")
    )

    yearly_stats["improvement_pct"] = (
        yearly_stats["median_time"].pct_change() * -100
    ) # Compare percentual improvament againts last year

    fig_year = px.bar(
        yearly_stats,
        x="year",
        y="solves",
        #text="solves",
        title="Annual Solves and Median Performance",
        labels={"year": "Year", "solves": "Number of Solves"}
    )

    fig_year.update_traces(textposition="outside")

    # adicionar linha da mediana
    fig_year.add_scatter(
        x=yearly_stats["year"],
        y=yearly_stats["median_time"],
        mode="lines+markers",
        name="Median Time (s)",
        yaxis="y2"
    )

    fig_year.update_layout(
        yaxis2=dict(
            title="Median Time (s)",
            overlaying="y",
            side="right"
        )
    )

    st.plotly_chart(fig_year, use_container_width=True)


##### LINE: SESSION SIZE IMPACT #####

st.subheader("Impact of Session Size on Performance")

col_ses_mean, col_ses_prob = st.columns(2)

with col_ses_mean:
    ##### SESSION SIZE PLOTS #####

    analysis_sub_x = st.sidebar.slider(
        "Session Analysis Sub-X (seconds)",
        5.0, 15.0, 8.0, step=0.1,
        key="session_analysis_subx"
    )

    session_stats = (
        df.groupby("session_id")
        .agg(
            session_size=("time_sec", "count"),
            session_mean=("time_sec", "mean"),
        )
        .reset_index()
    )

    subx_per_session = (
        df.assign(is_sub=lambda x: x["time_sec"] < analysis_sub_x)
        .groupby("session_id")["is_sub"]
        .mean()
        .reset_index(name="session_subx_prob")
    )
    session_stats = session_stats.merge(subx_per_session, on="session_id")
    min_session_size = st.sidebar.slider("Minimum Session Size", 5, 100, 15)
    session_stats = session_stats[session_stats["session_size"] >= min_session_size]

    fig_session_mean = px.scatter(
        session_stats,
        x="session_size",
        y="session_mean",
        title="Session Size vs Mean Time",
        labels={
            "session_size": "Session Size",
            "session_mean": "Mean Time (s)"
        }
    )

    if len(session_stats) > 1:
        x_line, y_line = linear_regression(session_stats, session_stats["session_size"], session_stats["session_mean"])
        fig_session_mean.add_scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name="Linear Trend",
            line=dict(color="red", width=3)
        )
    st.plotly_chart(fig_session_mean, use_container_width=True)


with col_ses_prob:
    ##### SESSION SIZE PROBABILITY PLOTS #####

    fig_session_subx = px.scatter(
        session_stats,
        x="session_size",
        y="session_subx_prob",
        title=f"Session Size vs Sub-{analysis_sub_x}s Probability",
        labels={
            "session_size": "Session Size",
            "session_subx_prob": "Probability"
        }
    )

    fig_session_subx.update_layout(
        yaxis=dict(range=[0, 1])
    )

    if len(session_stats) > 1:
        x_line, y_line = linear_regression(session_stats, session_stats["session_size"], session_stats["session_subx_prob"])
        fig_session_subx.add_scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name="Linear Trend",
            line=dict(color="red", width=3)
        )
    st.plotly_chart(fig_session_subx, use_container_width=True)