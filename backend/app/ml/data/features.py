import pandas as pd
import numpy as np

# Target: log1p(cap_hit) in dollars; inference uses expm1 to recover cap_hit.

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# DB_HOST=localhost python3 -m app.ml.data.features


def skater_data_to_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering for skaters (forwards + defensemen); adds log_cap_hit target."""
    if df is None or df.empty:
        return df
    df = df[df["icetime"] > 300 * 60].copy()
    df = df.dropna(subset=["cap_hit"]).copy()
    df = df[df["cap_hit"] > 0].copy()
    df["log_cap_hit"] = np.log1p(df["cap_hit"].astype(float))

    df["minutes_played"] = df["icetime"] / 60.0
    df["goals_per_60"] = df["i_f_goals"] / df["minutes_played"]
    df["primary_assists_per_60"] = df["i_f_primary_assists"] / df["minutes_played"]
    df["secondary_assists_per_60"] = df["i_f_secondary_assists"] / df["minutes_played"]
    df["points_per_60"] = df["i_f_points"] / df["minutes_played"]
    df["goals_above_expected"] = df["i_f_goals"] - df["i_f_x_goals"]
    df["shots_per_60"] = df["i_f_unblocked_shot_attempts"] / df["minutes_played"]
    df["xGoals_percentage"] = df["on_ice_x_goals_percentage"]
    df["net_penalties_per_60"] = (df["penalties_drawn"] - df["i_f_penalties"]) / df["minutes_played"]
    df["blocks_per_60"] = df["shots_blocked_by_player"] / df["minutes_played"]
    df["takeaways_per_60"] = df["i_f_takeaways"] / df["minutes_played"]
    df["giveaways_per_60"] = df["i_f_giveaways"] / df["minutes_played"]
    total_starts = (
        df["i_f_o_zone_shift_starts"]
        + df["i_f_d_zone_shift_starts"]
        + df["i_f_neutral_zone_shift_starts"]
    )
    df["o_zone_start_pct"] = df["i_f_o_zone_shift_starts"] / total_starts.replace(0, np.nan)

    # Workload + market context (keep for model; raw icetime dropped below)
    df["log_icetime"] = np.log1p(df["icetime"].astype(float).clip(lower=0))
    df["rfa_flag"] = df["rfa"].fillna(False).astype(int)
    df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(0)
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0)

    drop_cols = [
        "i_f_goals",
        "i_f_primary_assists",
        "i_f_secondary_assists",
        "i_f_points",
        "i_f_x_goals",
        "i_f_shots_on_goal",
        "i_f_unblocked_shot_attempts",
        "i_f_penalties",
        "penalties_drawn",
        "i_f_takeaways",
        "i_f_giveaways",
        "shots_blocked_by_player",
        "icetime",
        "minutes_played",
        "cap_hit",
        "cap_pct",
        "rfa",
        "on_ice_x_goals_percentage",
        "i_f_o_zone_shift_starts",
        "i_f_d_zone_shift_starts",
        "i_f_neutral_zone_shift_starts",
    ]
    df = df.drop(columns=drop_cols, errors="ignore").fillna(0)
    return df


def goalie_data_to_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering for goalies; adds log_cap_hit target."""
    if df is None or df.empty:
        return df
    df = df[df["icetime"] > 300 * 60].copy()
    df = df.dropna(subset=["cap_hit"]).copy()
    df = df[df["cap_hit"] > 0].copy()
    df["log_cap_hit"] = np.log1p(df["cap_hit"].astype(float))
    df["minutes_played"] = df["icetime"] / 60.0
    df["GSAx_total"] = df["x_goals"] - df["goals"]
    df["GSAx_per_60"] = df["GSAx_total"] / df["minutes_played"]
    df["save_pct"] = 1 - (df["goals"] / df["on_goal"])
    df["hd_save_pct"] = 1 - (df["high_danger_goals"] / df["high_danger_shots"].replace(0, np.nan))
    df["rebound_excess_per_60"] = (df["rebounds"] - df["x_rebounds"]) / df["minutes_played"]
    df["freeze_performance_ratio"] = df["act_freeze"] / df["x_freeze"].replace(0, np.nan)
    df["shots_faced_per_60"] = df["unblocked_shot_attempts"] / df["minutes_played"]
    df["avg_shot_difficulty"] = df["x_goals"] / df["unblocked_shot_attempts"].replace(0, np.nan)

    df["log_icetime"] = np.log1p(df["icetime"].astype(float).clip(lower=0))
    df["rfa_flag"] = df["rfa"].fillna(False).astype(int)
    df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(0)
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0)

    cols_to_drop = [
        "id",
        "season",
        "team",
        "playoff",
        "goals",
        "x_goals",
        "cap_hit",
        "cap_pct",
        "rfa",
        "rebounds",
        "x_rebounds",
        "act_freeze",
        "x_freeze",
        "icetime",
        "minutes_played",
    ]
    df = df.drop(columns=cols_to_drop, errors="ignore")
    df = df.fillna(0)
    return df
