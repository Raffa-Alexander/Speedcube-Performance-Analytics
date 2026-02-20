import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(page_title="Cube Performance Dashboard", layout="wide")
st.title("Speedcube Performance Dashboard")


def parse_time_mmss(s):
    """Converte strings mm:ss.xx para pd.Timedelta"""
    if pd.isna(s):
        return pd.Timedelta(0)
    # separa minutos e segundos
    try:
        min_part, sec_part = s.split(":")
        total_seconds = int(min_part) * 60 + float(sec_part)
        return pd.Timedelta(seconds=total_seconds)
    except:
        return pd.Timedelta(0)

# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    # ler CSV com separador correto
    df = pd.read_csv("data.csv", sep=";", engine="python", encoding="utf-8-sig")
    
    # padronizar nomes
    df.columns = df.columns.str.strip().str.lower()
    
    # conversão de Date
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    
    # conversão de Time
    df["time"] = df["time"].astype(str).apply(parse_time_mmss)
    df["time_sec"] = df["time"].dt.total_seconds()
    
    df = df.sort_values("date")
    
    # features derivadas
    df["year"] = df["date"].dt.year
    df["hour"] = df["date"].dt.hour
    df["weekday"] = df["date"].dt.day_name()
    
    return df

df = load_data()

# ----------------------------
# SIDEBAR FILTER
# ----------------------------
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

# ----------------------------
# METRICS
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Solves", len(df))
col2.metric("Mean Time", f"{df['time_sec'].mean():.2f} s")
col3.metric("Best Time", f"{df['time_sec'].min():.2f} s")
col4.metric("Standard Deviation", f"{df['time_sec'].std():.2f}")

st.divider()


# ----------------------------
# MOVING AVERAGE
# ----------------------------
window = st.sidebar.slider("Moving Average Window", 1, 200, 100)

df["ma"] = df["time_sec"].rolling(window).mean()

# gráfico base com pontos para os tempos originais
fig1 = px.scatter(
    df,
    x="date",
    y="time_sec",
    title="Solve Times Over Time",
    labels={"time_sec": "Time (s)", "date": "Date"},
    render_mode="webgl"
)

# adicionar MA como linha
fig1.add_scattergl(
    x=df["date"],
    y=df["ma"],
    mode="lines",
    name=f"MA{window}",
    line=dict(color="#fc8d62", width=3)
)

# opcional: mudar cor dos pontos originais
fig1.update_traces(marker=dict(color='blue', size=2, opacity=0.5), selector=dict(mode='markers'))

st.plotly_chart(fig1, use_container_width=True)

# ----------------------------
# PERFORMANCE BY HOUR
# ----------------------------
st.subheader("Performance by Hour")

hour_stats = df.groupby("hour")["time_sec"].mean().reset_index()
sub_x = df.groupby

fig2 = px.bar(hour_stats, x="hour", y="time_sec", title="Average Time by Hour")
st.plotly_chart(fig2, use_container_width=True)

# ----------------------------
# DISTRIBUTION
# ----------------------------
st.subheader("Time Distribution")

fig3 = px.histogram(df, x="time_sec", nbins=50, title="Histogram of Solve Times")
st.plotly_chart(fig3, use_container_width=True)

# ---------------------------- 
# SUB X
# ----------------------------
st.subheader("Sub-X Times")

# valores de referência (6s a 15s, você pode mudar)
sub_x_values = range(6, 16)  

# contar quantos solves ficaram abaixo de cada valor
sub_x_counts = [ (df["time_sec"] < x).sum() for x in sub_x_values ]

# criar labels tipo "Sub 6s", "Sub 7s", ...
sub_x_labels = [f"Sub {x}s" for x in sub_x_values]

sub_x_df = pd.DataFrame({
    "sub_x": sub_x_labels,  # usar labels como eixo X
    "amount": sub_x_counts
})

# gráfico de barras com texto em cima da barra
fig4 = px.bar(
    sub_x_df,
    x="sub_x",
    y="amount",
    text="amount",  # mostra valor acima de cada barra
    title="Sub-X Solves",
    labels={"sub_x": "", "amount": "Number of Solves"}  # remove label do eixo X
)

# opcional: melhorar estética do texto
fig4.update_traces(textposition="outside", marker_color="skyblue")

st.plotly_chart(fig4, use_container_width=True)