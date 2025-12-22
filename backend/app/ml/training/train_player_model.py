import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from app.ml.data.dataset_builder import build_forward_dataset, build_defenseman_dataset
from app.ml.data.features import skater_data_to_features

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# python3 -m app.ml.training.train_player_model

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')

def train_player_model(df: pd.DataFrame, model_name: str = 'player_model'):
    """Trains a player model and saves it to artifacts folder"""
    X = df.drop(columns=['pv'])
    y = df['pv']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    model_path = os.path.join(ARTIFACTS_DIR, f'{model_name}.pkl')
    joblib.dump(model, model_path)
    
    feature_names_path = os.path.join(ARTIFACTS_DIR, f'{model_name}_feature_names.pkl')
    joblib.dump(list(X.columns), feature_names_path)
    return model

def train_moodels():
    """Trains all models"""
    forward_df = build_forward_dataset()
    defenseman_df = build_defenseman_dataset()
    forward_df = skater_data_to_features(forward_df)
    defenseman_df = skater_data_to_features(defenseman_df)
    train_player_model(forward_df, model_name='forward_model')
    train_player_model(defenseman_df, model_name='defenseman_model')
    
    
if __name__ == "__main__":
    train_moodels()
