import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, RandomizedSearchCV
from sklearn.ensemble import HistGradientBoostingRegressor

from app.ml.data.dataset_builder import build_forward_dataset, build_defenseman_dataset, build_goalie_dataset
from app.ml.data.features import skater_data_to_features, goalie_data_to_features
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error


# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# DB_HOST=localhost python3 -m app.ml.training.train_player_model

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")

TARGET_COL = "log_cap_hit"
FEATURES_EXCLUDE = {
    "player_id",
    "contract_id",
    "cap_hit",
    "cap_pct",
    TARGET_COL,
    "id",
    "season",
    "rfa",
}


def train_player_model(df: pd.DataFrame, model_name: str = "player_model"):
    """
    Train HistGradientBoosting on log1p(cap_hit); CV grouped by player_id to reduce leakage.
    """
    if df is None or df.empty or TARGET_COL not in df.columns:
        raise ValueError(f"No training data or missing {TARGET_COL} column.")

    feature_cols = [c for c in df.columns if c not in FEATURES_EXCLUDE]
    X = df[feature_cols]
    y = df[TARGET_COL]
    groups = df["player_id"].values

    n_groups = df["player_id"].nunique()
    if n_groups < 2:
        raise ValueError("Need at least 2 distinct players to train with group splits.")

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    groups_train = groups[train_idx]

    n_groups_train = len(np.unique(groups_train))
    if n_groups_train < 2:
        raise ValueError("Training split has fewer than 2 players; cannot use grouped CV.")
    n_splits_cv = min(5, n_groups_train)
    cv = GroupKFold(n_splits=n_splits_cv)

    gbm = HistGradientBoostingRegressor(random_state=42, loss="squared_error")
    param_distributions = {
        "learning_rate": [0.01, 0.05, 0.1, 0.2],
        "max_iter": [100, 300, 500, 1000],
        "max_depth": [3, 5, 10, None],
        "min_samples_leaf": [10, 20, 50],
        "l2_regularization": [0.0, 0.1, 1.0],
    }
    
    print(f"Tuning {model_name} hyperparameters... (This may take a minute)")
    search = RandomizedSearchCV(
        gbm,
        param_distributions,
        n_iter=20,
        scoring="neg_mean_absolute_error",
        cv=cv,
        n_jobs=-1,
        verbose=0,
        random_state=42,
    )
    search.fit(X_train, y_train, groups=groups_train)
    best_model = search.best_estimator_
    print(f"Best Params for {model_name}: {search.best_params_}")
    if not os.path.exists(ARTIFACTS_DIR):
        os.makedirs(ARTIFACTS_DIR)
    model_path = os.path.join(ARTIFACTS_DIR, f"{model_name}.pkl")
    joblib.dump(best_model, model_path)
    feature_names_path = os.path.join(ARTIFACTS_DIR, f"{model_name}_feature_names.pkl")
    joblib.dump(feature_cols, feature_names_path)
    meta = {
        "target": "log1p(cap_hit_usd)",
        "inverse": "expm1",
    }
    joblib.dump(meta, os.path.join(ARTIFACTS_DIR, f"{model_name}_meta.pkl"))
    return best_model


def train_models():
    """Train forward, defenseman, and goalie models."""
    forward_df = build_forward_dataset()
    defenseman_df = build_defenseman_dataset()
    forward_df = skater_data_to_features(forward_df)
    defenseman_df = skater_data_to_features(defenseman_df)
    goalie_df = build_goalie_dataset()
    goalie_df = goalie_data_to_features(goalie_df)

    if not forward_df.empty:
        train_player_model(forward_df, model_name="forward_model")
    else:
        pass

    if not defenseman_df.empty:
        train_player_model(defenseman_df, model_name="defenseman_model")
    else:
        pass

    if not goalie_df.empty:
        train_player_model(goalie_df, model_name="goalie_model")
    else:
        pass


if __name__ == "__main__":
    train_models()
