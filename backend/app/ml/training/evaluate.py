from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import joblib
import os
from app.ml.data.dataset_builder import build_forward_dataset, build_defenseman_dataset, build_goalie_dataset
from app.ml.data.features import skater_data_to_features, goalie_data_to_features
from sklearn.model_selection import train_test_split

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')


# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# DB_HOST=localhost python3 -m app.ml.training.evaluate

def evaluate_model(model_name='forward_model'):
    """Evaluate a trained model on test data"""
    
    model_path = os.path.join(ARTIFACTS_DIR, f'{model_name}.pkl')
    model = joblib.load(model_path)
    
    # Load the feature names that were used during training
    feature_names_path = os.path.join(ARTIFACTS_DIR, f'{model_name}_feature_names.pkl')
    
    if 'forward' in model_name:
        df = build_forward_dataset()
        df_features = skater_data_to_features(df)
    elif 'defenseman' in model_name:
        df = build_defenseman_dataset()
        df_features = skater_data_to_features(df)
    elif 'goalie' in model_name:
        df = build_goalie_dataset()
        df_features = goalie_data_to_features(df)
    else:
        raise ValueError(f"Unknown model name: {model_name}")
    
    # Load saved feature names and ensure correct order
    if os.path.exists(feature_names_path):
        saved_feature_cols = joblib.load(feature_names_path)
        # Filter to only features that exist and maintain the order from training
        feature_cols = [col for col in saved_feature_cols if col in df_features.columns]
        
        if len(feature_cols) != len(saved_feature_cols):
            missing = set(saved_feature_cols) - set(feature_cols)
            print(f"Warning: {len(missing)} features from training not found in data: {missing}")
            print(f"Using {len(feature_cols)} features for evaluation")
    else:
        # Fallback if no saved features
        features_to_exclude = ['player_id', 'season', 'contract_id', 'cap_pct', 'log_cap_pct', 'id']
        feature_cols = [c for c in df_features.columns if c not in features_to_exclude]
    
    # Extract features in the correct order (only those used during training)
    X = df_features[feature_cols]
    y = df_features['log_cap_pct']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Predict (HistGradientBoostingRegressor can handle DataFrames directly)
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2}

if __name__ == "__main__":
    print("Forward Model Evaluation:", evaluate_model(model_name='forward_model'))
    print("Defenseman Model Evaluation:", evaluate_model(model_name='defenseman_model'))
    print("Goalie Model Evaluation:", evaluate_model(model_name='goalie_model'))