import pandas as pd
import numpy as np
import joblib
import os
from app.ml.data.features import skater_data_to_features, goalie_data_to_features

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


def prepare_skater_features_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare skater features for prediction (same as training but without cap_hit/log_cap_hit)
    Input DataFrame should have the same columns as build_skater_advanced_dataset returns
    """
    df = df.copy()
    
    # Filter by minimum icetime (same as training)
    if 'icetime' in df.columns:
        df = df[df['icetime'] > 300 * 60].copy()
    
    # Feature engineering (same as skater_data_to_features but without log_cap_hit)
    df['minutes_played'] = df['icetime'] / 60.0
    df['goals_per_60'] = df['i_f_goals'] / df['minutes_played']
    df['primary_assists_per_60'] = df['i_f_primary_assists'] / df['minutes_played']
    df['secondary_assists_per_60'] = df['i_f_secondary_assists'] / df['minutes_played']
    df['points_per_60'] = df['i_f_points'] / df['minutes_played']
    df['goals_above_expected'] = df['i_f_goals'] - df['i_f_x_goals']
    df['shots_per_60'] = df['i_f_unblocked_shot_attempts'] / df['minutes_played']
    df['xGoals_percentage'] = df['on_ice_x_goals_percentage']
    df['net_penalties_per_60'] = (df['penalties_drawn'] - df['i_f_penalties']) / df['minutes_played']
    df['blocks_per_60'] = df['shots_blocked_by_player'] / df['minutes_played']
    df['takeaways_per_60'] = df['i_f_takeaways'] / df['minutes_played']
    df['giveaways_per_60'] = df['i_f_giveaways'] / df['minutes_played']
    
    total_starts = (df['i_f_o_zone_shift_starts'] + 
                    df['i_f_d_zone_shift_starts'] + 
                    df['i_f_neutral_zone_shift_starts'])
    df['o_zone_start_pct'] = df['i_f_o_zone_shift_starts'] / total_starts.replace(0, np.nan)
    
    # Drop the same columns as in training
    drop_cols = [
        'i_f_goals', 'i_f_primary_assists', 'i_f_secondary_assists', 'i_f_points',
        'i_f_x_goals', 'i_f_shots_on_goal', 'i_f_unblocked_shot_attempts',
        'i_f_penalties', 'penalties_drawn', 
        'i_f_takeaways', 'i_f_giveaways', 'shots_blocked_by_player',
        'icetime', 'minutes_played', 'cap_hit',
        'i_f_o_zone_shift_starts', 'i_f_d_zone_shift_starts', 'i_f_neutral_zone_shift_starts',
        'player_id', 'season', 'contract_id', 'id'
    ]
    df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    df = df.fillna(0)
    
    return df


def prepare_goalie_features_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare goalie features for prediction (same as training but without cap_hit/log_cap_hit)
    Input DataFrame should have the same columns as goalie_advanced_dataset returns
    """
    df = df.copy()
    
    # Filter by minimum icetime (same as training)
    if 'icetime' in df.columns:
        df = df[df['icetime'] > 300 * 60].copy()
    
    # Feature engineering (same as goalie_data_to_features but without log_cap_hit)
    df['minutes_played'] = df['icetime'] / 60.0
    df['GSAx_total'] = df['x_goals'] - df['goals']
    df['GSAx_per_60'] = df['GSAx_total'] / df['minutes_played']
    df['save_pct'] = 1 - (df['goals'] / df['on_goal'])
    df['hd_save_pct'] = 1 - (df['high_danger_goals'] / df['high_danger_shots'].replace(0, np.nan))
    df['rebound_excess_per_60'] = (df['rebounds'] - df['x_rebounds']) / df['minutes_played']
    df['freeze_performance_ratio'] = df['act_freeze'] / df['x_freeze'].replace(0, np.nan)
    df['shots_faced_per_60'] = df['unblocked_shot_attempts'] / df['minutes_played']
    df['avg_shot_difficulty'] = df['x_goals'] / df['unblocked_shot_attempts'].replace(0, np.nan)
    
    # Drop the same columns as in training
    cols_to_drop = [
        'id', 'season', 'team', 'playoff', 
        'goals', 'x_goals', 'cap_hit', 
        'rebounds', 'x_rebounds', 
        'act_freeze', 'x_freeze',
        'icetime', 'minutes_played',
        'player_id', 'contract_id'
    ]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')
    df = df.fillna(0)
    
    return df


def predict(df: pd.DataFrame, model_name: str = 'forward_model') -> pd.DataFrame:
    """
    Make predictions on new player data
    
    Args:
        df: DataFrame with advanced stats (same format as dataset_builder returns)
            For skaters: must have columns from build_skater_advanced_dataset
            For goalies: must have columns from goalie_advanced_dataset
        model_name: Name of the model to use ('forward_model', 'defenseman_model', or 'goalie_model')
    
    Returns:
        DataFrame with predictions added as 'predicted_log_cap_hit' and 'predicted_cap_hit' columns
    """
    model, expected_features = load_model(model_name)
    
    # Prepare features based on model type
    if 'goalie' in model_name:
        df_features = prepare_goalie_features_for_prediction(df)
    else:
        df_features = prepare_skater_features_for_prediction(df)
    
    # Check for missing features
    missing_features = set(expected_features) - set(df_features.columns)
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}. "
                        f"Have: {list(df_features.columns)}, Need: {expected_features}")
    
    # Select features in the correct order
    df_features = df_features[expected_features]
    
    # Make predictions (returns log_cap_hit)
    predicted_log_cap_hit = model.predict(df_features)
    
    # Convert back to cap_hit (inverse of log1p)
    predicted_cap_hit = np.expm1(predicted_log_cap_hit)
    
    # Add predictions to result
    df_result = df.copy()
    df_result['predicted_log_cap_hit'] = predicted_log_cap_hit
    df_result['predicted_cap_hit'] = predicted_cap_hit
    
    return df_result


def predict_single_player(player_stats: dict, model_name: str = 'forward_model') -> dict:
    """
    Make a prediction for a single player
    
    Args:
        player_stats: Dictionary with player advanced stats
            For skaters: columns from build_skater_advanced_dataset
            For goalies: columns from goalie_advanced_dataset
        model_name: Name of the model to use
    
    Returns:
        Dictionary with 'predicted_log_cap_hit' and 'predicted_cap_hit'
    """
    df = pd.DataFrame([player_stats])
    result = predict(df, model_name)
    return {
        'predicted_log_cap_hit': result['predicted_log_cap_hit'].iloc[0],
        'predicted_cap_hit': result['predicted_cap_hit'].iloc[0]
    }