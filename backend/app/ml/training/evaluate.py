import os
import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit

from app.ml.data.dataset_builder import build_forward_dataset, build_defenseman_dataset, build_goalie_dataset
from app.ml.data.features import skater_data_to_features, goalie_data_to_features

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

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# DB_HOST=localhost python3 -m app.ml.training.evaluate


def evaluate_model(model_name="forward_model"):
    """Evaluate trained model with grouped hold-out; reports log and dollar MAE."""
    model_path = os.path.join(ARTIFACTS_DIR, f"{model_name}.pkl")
    model = joblib.load(model_path)

    feature_names_path = os.path.join(ARTIFACTS_DIR, f"{model_name}_feature_names.pkl")

    if "forward" in model_name:
        df = build_forward_dataset()
        df_features = skater_data_to_features(df)
    elif "defenseman" in model_name:
        df = build_defenseman_dataset()
        df_features = skater_data_to_features(df)
    elif "goalie" in model_name:
        df = build_goalie_dataset()
        df_features = goalie_data_to_features(df)
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    if df_features.empty or TARGET_COL not in df_features.columns:
        return {"error": "empty dataset or missing target"}

    if os.path.exists(feature_names_path):
        saved_feature_cols = joblib.load(feature_names_path)
        feature_cols = [col for col in saved_feature_cols if col in df_features.columns]
        if len(feature_cols) != len(saved_feature_cols):
            missing = set(saved_feature_cols) - set(feature_cols)
            pass
    else:
        feature_cols = [c for c in df_features.columns if c not in FEATURES_EXCLUDE]

    X = df_features[feature_cols]
    y = df_features[TARGET_COL]
    groups = df_features["player_id"].values

    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))
    X_test = X.iloc[test_idx]
    y_test = y.iloc[test_idx]

    y_pred = model.predict(X_test)

    mae_log = mean_absolute_error(y_test, y_pred)
    rmse_log = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    mae_dollars = mean_absolute_error(np.expm1(y_test), np.expm1(y_pred))
    rmse_dollars = np.sqrt(mean_squared_error(np.expm1(y_test), np.expm1(y_pred)))

    return {
        "mae_log": mae_log,
        "rmse_log": rmse_log,
        "r2": r2,
        "mae_cap_hit_usd": mae_dollars,
        "rmse_cap_hit_usd": rmse_dollars,
    }


if __name__ == "__main__":
    evaluate_model(model_name="forward_model")
    evaluate_model(model_name="defenseman_model")
    evaluate_model(model_name="goalie_model")
