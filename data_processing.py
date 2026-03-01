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
    

def compute_session_stats(df):
    ...

def compute_subx_probability(df, threshold):
    ...