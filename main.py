import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import data_processing as dp

##### CONSTANTS #####

COLOR_BARS = "#3691E0"
COLOR_SCATTERS = "#3691E0"
COLOR_LINES = "#E17070"
HEATMAP_COLOR_PATTERN = "Viridis_r"

SESSION_MAX_GAP_SEC = 600 # Max time gap between two solves for them to be considered in the same session. 600s = 10min

##### CONFIG #####

st.set_page_config(page_title="Cube Performance Analysis", layout="wide")
st.title("Speedcube Performance Analysis")

##### LOAD DATA #####

@st.cache_data
def load_data():
    '''
    Loads data from "data.csv" to variable "df". 
    '''
    df = pd.read_csv("data.csv", sep=";", engine="python", encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()
df = dp.prepare_base_dataframe(df, SESSION_MAX_GAP_SEC)

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
best_ao5 = dp.compute_best_ao5_wca(df)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Solves", len(df))
col2.metric("Mean Time", f"{df['time_sec'].mean():.2f} s")
col3.metric("Best Time", f"{df['time_sec'].min():.2f} s")
col4.metric("Best Average of 5", f"{best_ao5:.2f} s" if best_ao5 is not None else "—")
col5.metric("Standard Deviation", f"{df['time_sec'].std():.2f}")

st.divider()

######################
##### DASHBOARDS #####
######################

window = st.sidebar.slider("Moving Mean Window", 1, 1000, 500)
df["ma"] = df["time_sec"].rolling(window).mean()
df["std_movel"] = df["time_sec"].rolling(window=window, min_periods=100).std() #calculate std variation
df["z_score"] = (df["time_sec"] - df["ma"]) / df["std_movel"]

sessions_df = df.groupby("session_id").agg({"z_score": "mean", "time_sec": "count", "days_from_latest": "min"}).rename(columns={"time_sec": "session_size"}).dropna()

st.subheader("Solves distribution plots")

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
    line=dict(color=COLOR_LINES, width=3)
) # Plots MA filtered times as line

fig1.update_traces(marker=dict(color=COLOR_SCATTERS, size=3, opacity=0.5), selector=dict(mode='markers'))
st.plotly_chart(fig1, use_container_width=True)


##### LINE: HISTOGRAM + SUB X (MESMA LINHA) #####

col_dist, col_subx = st.columns(2)

##### HISTOGRAM OF TIME WINDOWS (9.00-9.99, 10.00-10.99, 11.00-11.99, ...) #####

with col_dist:
    fig3 = px.histogram(
        df, 
        x="time_sec", 
        nbins=50, 
        title="Histogram of Solve Times"
    )
    fig3.update_xaxes(dtick=1)   
    fig3.update_traces(marker=dict(color=COLOR_BARS))

    st.plotly_chart(fig3, use_container_width=True) 

##### SUB X #####
with col_subx:
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
    fig4.update_traces(marker=dict(color=COLOR_BARS))

    fig4.update_traces(textposition="outside")
    st.plotly_chart(fig4, use_container_width=True)


st.markdown(r"""
### Statistical Methodology & Machine Learning

To ensure a fair analysis across different years and skill levels, the data undergoes a transformation process to neutralize the "historical improvement bias."

#### 1. Moving Z-Score Normalization
Since performance naturally evolves over time, comparing absolute times from 2019 to 2026 would be statistically invalid. Instead, we calculate a **Z-Score** based on a **Moving Average (MA)**:

$$Z = \frac{x - \mu_\text{moving}}{\sigma_\text{moving}}$$

Where:
*   **$x$**: Current solve time.
*   **$\mu_\text{moving}$**: Mean of the last $N$ solves (set by the "Moving Mean Window" slider). 
*   **$\sigma_\text{moving}$**: Standard Deviation of the last $N$ solves.

**Interpretation:** A $Z = 0$ indicates a performance exactly at your current average. A $Z = -1.5$ indicates a "peak" solve, 1.5 standard deviations faster than your current baseline.
Mean is prefered over average for this analysis to reduce the noise of outliers. $Z>0$ indicates a worse than average solve.
""")


##### LINE: IMPACT OF TIME #####

st.subheader("Impact of time of the week, solves amount, sessions size and distribution on perfomance")


col_heatmap, col_years = st.columns(2)

##### HEATMAP #####
with col_heatmap:

    heatmap_data = (df.groupby(["weekday", "hour"])["z_score"].mean().reset_index() ) # creates data frame

    heatmap_data["weekday"] = pd.Categorical(
        heatmap_data["weekday"],
        categories= ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 
        ordered=True
    ) #reinforce week order instead of alphabetical

    pivot_table = heatmap_data.pivot(
        index="weekday",
        columns="hour",
        values="z_score"
    ) #transforms data frame into matrix

    fig_heat = px.imshow(
        pivot_table,
        color_continuous_scale=HEATMAP_COLOR_PATTERN,
        labels=dict(color="z_score"),
        aspect="auto",
        title="Heatmap",
    )

    fig_heat.update_xaxes(dtick=2)   
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("""
    Best performance was noticed between 14:00 and 19:00. 
    It might suggest better concentration at these times.
    No correlation between week day and performance.
    """)


##### SOLVES AND PERFORMANCE PER YEAR #####
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
    fig_year.update_traces(marker=dict(color=COLOR_BARS), textposition="outside")

    # adicionar linha da mediana
    fig_year.add_scatter(
        x=yearly_stats["year"],
        y=yearly_stats["median_time"],
        mode="lines+markers",
        name="Median Time (s)",
        yaxis="y2",
        line=dict(color=COLOR_LINES, width=3)
    )

    fig_year.update_layout(
        yaxis2=dict(
            title="Median Time (s)",
            overlaying="y",
            side="right"
        )
    )

    st.plotly_chart(fig_year, use_container_width=True)

    st.markdown("""
    Years with more practice clearly result to better performance.
    """)












df, weekly, weekly_valid = dp.week_column(df)
weekly_valid = dp.add_weekly_structure_bins(weekly_valid)

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


### Clusters 1


k_clusters = st.sidebar.slider("Training Structure Clusters",2, 10, 4)

st.header("Clustering")

session_features = (df.groupby("session_id").agg(session_size=("time_sec", "count"), z_score_mean=("z_score", "mean"), week=("week", "first")).reset_index())

weekly_session_count = (session_features.groupby("week").size().rename("weekly_n_sessions"))
session_features = session_features.merge(weekly_session_count, on="week")

X = session_features[["session_size", "weekly_n_sessions"]]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = KMeans(n_clusters=k_clusters, random_state=1, n_init=10)
session_features["cluster"] = model.fit_predict(X_scaled)

cluster_order = (session_features.groupby("cluster")["z_score_mean"].mean().sort_values().index)
cluster_color_map = {cluster: i for i, cluster in enumerate(cluster_order)}

session_features["cluster_rank"] = session_features["cluster"].map(cluster_color_map)

colors = px.colors.sample_colorscale( "RdYlGn_r", [i / (k_clusters - 1) for i in range(k_clusters)])
color_map = {i: colors[i] for i in range(k_clusters)}

fig_clusters = px.scatter(
    session_features,
    x="session_size",
    y="weekly_n_sessions",
    color="cluster_rank",
    color_continuous_scale="RdYlGn_r",
    title="Training Structure Clusters",
    labels={
        "session_size": "Session Size",
        "weekly_n_sessions": "Weekly Session Frequency",
        "cluster_rank": "Cluster (sorted by performance)"
    }
)

fig_clusters.update_traces(
    marker=dict(size=8)
)

st.markdown("""
This plot groups training sessions using **K-Means clustering** based on:
- session size (number of solves per session)
- weekly training frequency (number of sessions per week)
Clusters are then **sorted by mean performance (z-score)**, allowing interpretation from worst to best training structure.
Each color represents a distinct training behavior pattern, and the gradient reflects performance ranking across clusters.
""")

st.plotly_chart(fig_clusters, use_container_width=True)

st.markdown("""
Hihger weekly sessions frequency and longer sessions show better perfromance, which is expected. 
When having to choose between session frequency and session size the result suggests to choose less sessions, but longer.
""")











min_solves_k_means = st.sidebar.slider("Min solves per session (K-Means)", 1, 50, 10) # Slider para controle
sessions_df = sessions_df[sessions_df["session_size"] >= min_solves_k_means] #filter analysis to include only sessions greater than min_solves_k_means
scaler = StandardScaler()
X_scaled = scaler.fit_transform(sessions_df[["z_score", "session_size"]])

k_clusters = st.sidebar.slider("Clusters k amount", 1, 10, 3)
model = KMeans(n_clusters=k_clusters, random_state=42, n_init=10)
sessions_df["cluster"] = model.fit_predict(X_scaled)

st.markdown("""     
The Y-axis (Z-Score) is inverted in the plot. Therefore, "better" performances (negative Z-Scores) appear at the top of the chart.

""")

fig_clusters = px.scatter(
    sessions_df,
    x="session_size",
    y="z_score",
    color=sessions_df["cluster"].astype(str),
    title="Session Clusters: Volume vs. Performance",
    labels={"session_size": "Solves amount", "z-score": "Average z-score"},
    color_discrete_sequence=px.colors.qualitative.Safe
)

# Inverter o eixo Y porque no Cubo Mágico tempos menores (e Z-scores negativos) são melhores
fig_clusters.update_yaxes(autorange="reversed") # Zoom nos Z-Scores principais
st.plotly_chart(fig_clusters, use_container_width=True)

st.markdown("""
The graph shows all sessions recorded with a z-score attatched to them instead. 
When divided into three clusters it shows one group of longer sessions with small variation,
and two group with less sessions but more variation, one with better and the other one with worse z-scores.
REV
In larger sessions typically the first solves are not very good, the middle ones are the best and the last ones are worse. 
That happens because there is always a performance peak, which after reached gets worse until a point is reached where motivation is lost.
""")

































min_session_size = 40

st.header("Fatigue Analysis")

session_sizes = df.groupby("session_id")["z_score"].transform("count")

fatigue_df = df[session_sizes >= min_session_size].copy()
fatigue_df["solve_index"] = fatigue_df.groupby("session_id").cumcount()
fatigue_df["session_size"] = fatigue_df.groupby("session_id")["z_score"].transform("count")
fatigue_df["relative_position"] = fatigue_df["solve_index"] / (fatigue_df["session_size"] - 1)
fatigue_df["fatigue_bin"] = pd.cut(
    fatigue_df["relative_position"],
    bins=np.linspace(0, 1, 21),
    labels=[
        "0-5%", "5-10%", "10-15%", "15-20%",
        "20-25%", "25-30%", "30-35%", "35-40%",
        "40-45%", "45-50%", "50-55%", "55-60%",
        "60-65%", "65-70%", "70-75%", "75-80%",
        "80-85%", "85-90%", "90-95%", "95-100%"
    ],
    include_lowest=True
)

fatigue_curve = (
    fatigue_df.groupby("fatigue_bin")
    .agg(
        mean_z_score=("z_score", "mean"),
        n_solves=("z_score", "count")
    )
    .reset_index()
)

fig_fatigue = px.line(
    fatigue_curve,
    x="fatigue_bin",
    y="mean_z_score",
    markers=True,
    title="Average Performance During Sessions",
    labels={
        "fatigue_bin": "Session Phase",
        "mean_z_score": "Mean Z-Score"
    }
)

fig_fatigue.update_yaxes(autorange="reversed")

st.plotly_chart(fig_fatigue, use_container_width=True)
st.markdown("""
            The plot shows the following trend of the sessions:
            - The fisrst couple solves serve as warm-up and are worse than average
            - The peak is reached between $40\%$ and $90\%$ of the session solves
            - The final stage represents the collapse, where performance significantly worse and motivation shrinks, resulting in stopping the practice.
            """)


fatigue_smooth = (fatigue_df.groupby("solve_index").agg(mean_z=("z_score", "mean")).rolling(5).mean().reset_index()
)

fig_smooth = px.line(
    fatigue_smooth,
    x="solve_index",
    y="mean_z",
    title="Fatigue Curve During Sessions",
    labels={
        "solve_index": "Solve Number",
        "mean_z": "Mean Z-Score"
    }
)

fig_smooth.update_yaxes(autorange="reversed")
st.plotly_chart(fig_smooth, use_container_width=True)







weekly.to_csv("generated dataframes/weekly.csv")
weekly_valid.to_csv("generated dataframes/weekly_valid.csv")
df.to_csv("generated dataframes/df.csv")
df.to_csv("generated dataframes/fatigue_df.csv")