import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from app.ml.data.dataset_builder import build_forward_dataset, build_defenseman_dataset, build_goalie_dataset
from app.ml.data.features import skater_data_to_features, goalie_data_to_features
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error


# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# DB_HOST=localhost python3 -m app.ml.training.train_player_model

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import HistGradientBoostingRegressor

def train_player_model(df: pd.DataFrame, model_name: str = 'player_model'):
    """
    Trains a high-accuracy Gradient Boosting model with hyperparameter tuning.
    Saves the best model and feature names to the artifacts folder.
    """
    features_to_exclude = ['player_id', 'season', 'contract_id', 'cap_pct', 'log_cap_pct', 'id']
    feature_cols = [c for c in df.columns if c not in features_to_exclude]
    
    X = df[feature_cols]
    y = df['log_cap_pct']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    gbm = HistGradientBoostingRegressor(random_state=42, loss='squared_error')
    
    param_distributions = {
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'max_iter': [100, 300, 500, 1000],
        'max_depth': [3, 5, 10, None],
        'min_samples_leaf': [10, 20, 50],
        'l2_regularization': [0.0, 0.1, 1.0]
    }
    
    print(f"Tuning {model_name} hyperparameters... (This may take a minute)")
    search = RandomizedSearchCV(
        gbm, 
        param_distributions, 
        n_iter=20,
        scoring='neg_mean_absolute_error', 
        cv=5, 
        n_jobs=-1,
        verbose=1,
        random_state=42
    )
    search.fit(X_train, y_train)
    best_model = search.best_estimator_
    print(f"Best Params for {model_name}: {search.best_params_}")
    if not os.path.exists(ARTIFACTS_DIR):
        os.makedirs(ARTIFACTS_DIR)
    model_path = os.path.join(ARTIFACTS_DIR, f'{model_name}.pkl')
    joblib.dump(best_model, model_path)
    feature_names_path = os.path.join(ARTIFACTS_DIR, f'{model_name}_feature_names.pkl')
    joblib.dump(feature_cols, feature_names_path)
    return best_model

def train_moodels():
    """Trains all models"""
    forward_df = build_forward_dataset()
    defenseman_df = build_defenseman_dataset()
    forward_df = skater_data_to_features(forward_df)
    defenseman_df = skater_data_to_features(defenseman_df)
    goalie_df = build_goalie_dataset()
    goalie_df = goalie_data_to_features(goalie_df)
    train_player_model(forward_df, model_name='forward_model')
    train_player_model(defenseman_df, model_name='defenseman_model')
    train_player_model(goalie_df, model_name='goalie_model')
    
if __name__ == "__main__":
    train_moodels()
