import pandas as pd
import plotly.express as px
import numpy as np

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
    


def prepare_base_dataframe(df, SESSION_MAX_GAP_SEC):
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df["time"] = df["time"].astype(str).apply(parse_time_mmss)
    df["time_sec"] = df["time"].dt.total_seconds()
    
    df = df.sort_values("date")
    
    df["year"] = df["date"].dt.year
    df["hour"] = df["date"].dt.hour
    df["weekday"] = df["date"].dt.day_name()

    df["time_diff"] = df["date"].diff().dt.total_seconds()
    df["new_session"] = df["time_diff"] > SESSION_MAX_GAP_SEC
    df["session_id"] = df["new_session"].cumsum()
    return df



def add_session_ids(df, max_gap_minutes):
    ...

def add_week_column(df):
    ...

def add_recency_weights(df, decay_factor):
    ...

def week_column(df):
    '''
    Creates a week column 
    '''
    df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)

    weekly = df.groupby("week").agg(weekly_volume=("time_sec", "count"), weekly_median=("time_sec", "median"),)

    sessions_per_week = (
        df.groupby(["week", "session_id"])
        .size()
        .reset_index(name="session_size")
        .groupby("week")
        .size()
    )
    weekly["n_sessions"] = sessions_per_week
    weekly = weekly.fillna(0)
    weekly["prev_week_median"] = weekly["weekly_median"].shift(1)
    weekly_valid = weekly.dropna(subset=["prev_week_median"]).copy() 
    weekly_valid["delta_pct_current_week"] = (
        (weekly_valid["prev_week_median"] - weekly_valid["weekly_median"])
        / weekly_valid["prev_week_median"]
    ) * 100
    return df, weekly, weekly_valid

def add_weekly_structure_bins(weekly_valid: pd.DataFrame, volume_q: int=4, session_q: int=3) -> pd.DataFrame:
    
    weekly_valid = weekly_valid.copy()

    # ----- Volume Quantiles -----
    _, volume_bins = pd.qcut(
        weekly_valid["weekly_volume"],
        q=volume_q,
        retbins=True,
        duplicates="drop"
    )

    volume_labels = []
    for i in range(len(volume_bins) - 1):
        low = int(np.floor(volume_bins[i]))
        high = int(np.ceil(volume_bins[i + 1]))
        volume_labels.append(f"Q{i+1}\n{low}–{high}")

    weekly_valid["volume_bin"] = pd.qcut(
        weekly_valid["weekly_volume"],
        q=volume_q,
        labels=volume_labels,
        duplicates="drop"
    )

    # ----- Session Fragmentation Quantiles -----
    _, session_bins = pd.qcut(
        weekly_valid["n_sessions"],
        q=session_q,
        retbins=True,
        duplicates="drop"
    )

    frag_names = ["Low Frag", "Mid Frag", "High Frag"]
    session_labels = []

    for i in range(len(session_bins) - 1):
        low = int(np.floor(session_bins[i]))
        high = int(np.ceil(session_bins[i + 1]))
        session_labels.append(f"{frag_names[i]}\n{low}–{high}")

    weekly_valid["session_bin"] = pd.qcut(
        weekly_valid["n_sessions"],
        q=session_q,
        labels=session_labels,
        duplicates="drop"
    )

    weekly_valid["volume_bin"] = pd.Categorical(
        weekly_valid["volume_bin"],
        categories=volume_labels,
        ordered=True
    )

    weekly_valid["session_bin"] = pd.Categorical(
        weekly_valid["session_bin"],
        categories=session_labels,
        ordered=True
    )

    return weekly_valid

def weighted_linear_regression(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    time_col: str,
    decay_factor: float,
    n_points: int = 100
) -> tuple[np.ndarray, np.ndarray] | tuple[None, None]:
    """
    Computes weighted linear regression using exponential time decay.

    Returns:
        x_line, y_line for plotting
        or (None, None) if not enough data
    """

    if len(df) <= 1:
        return None, None

    x = df[x_col].values
    y = df[y_col].values
    w = np.exp(-decay_factor * df[time_col].values)

    coef = np.polyfit(x, y, 1, w=w)

    x_line = np.linspace(x.min(), x.max(), n_points)
    y_line = coef[0] * x_line + coef[1]

    return x_line, y_line



    

def compute_session_stats(df):
    ...

def compute_subx_probability(df, threshold):
    ...