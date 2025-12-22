import pandas as pd
import numpy as np
import joblib
import os

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# python3 -m app.ml.inference.predictor

# Path to artifacts directory
ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')


def load_model(model_name: str = 'forward_model'):
    """Load a trained model and its feature names"""
    model_path = os.path.join(ARTIFACTS_DIR, f'{model_name}.pkl')
    feature_names_path = os.path.join(ARTIFACTS_DIR, f'{model_name}_feature_names.pkl')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Train the model first.")
    
    if not os.path.exists(feature_names_path):
        raise FileNotFoundError(f"Feature names not found at {feature_names_path}.")
    
    model = joblib.load(model_path)
    feature_names = joblib.load(feature_names_path)
    
    return model, feature_names


def prepare_features_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare features for prediction (same as training but without creating pv)
    Note: For prediction, you don't need cap_hit since that's what you're trying to predict
    """
    df = df.copy()
    
    df = df[df['gp'] > 0]
    
    df['points_per_game'] = df['points'] / df['gp']
    df['goals_per_game'] = df['goals'] / df['gp']
    df['assists_per_game'] = df['assists'] / df['gp']
    
    drop_columns = ['firstname', 'lastname', 'position', 'id', 'season', 'goals', 'assists', 
                    'points', 'cap_hit', 'gp', 'points_per_game']
    
    df = df.drop(columns=[col for col in drop_columns if col in df.columns])
    
    return df


def predict(df: pd.DataFrame, model_name: str = 'forward_model') -> pd.DataFrame:
    """
    Make predictions on new player data
    
    Args:
        df: DataFrame with player stats (must have: gp, goals, assists, points, plus_minus, pim, shots, shootpct)
        model_name: Name of the model to use ('forward_model' or 'defenseman_model')
    
    Returns:
        DataFrame with predictions added as 'predicted_pv' column
    """
    model, expected_features = load_model(model_name)
    
    df_features = prepare_features_for_prediction(df)
    
    missing_features = set(expected_features) - set(df_features.columns)
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}. "
                        f"Have: {list(df_features.columns)}, Need: {expected_features}")
    
    df_features = df_features[expected_features]
    
    predictions = model.predict(df_features)
    
    
    df_result = df.copy()
    df_result['predicted_pv'] = predictions
    
    return df_result


def predict_single_player(player_stats: dict, model_name: str = 'forward_model') -> float:
    """
    Make a prediction for a single player
    
    Args:
        player_stats: Dictionary with player stats
            Required: gp, goals, assists, points, plus_minus, pim, shots, shootpct
            Optional: firstname, lastname, position, id, season (for reference)
        model_name: Name of the model to use
    
    Returns:
        Predicted pv value
    """
    df = pd.DataFrame([player_stats])
    result = predict(df, model_name)
    return result['predicted_pv'].iloc[0]

