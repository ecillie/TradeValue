import pandas as pd
import numpy as np
from app.ml.data.dataset_builder import build_forward_dataset, build_defenseman_dataset

# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# python3 -m app.ml.data.features

def skater_data_to_features(df: pd.DataFrame) -> pd.DataFrame:
    """Adds features to the dataset"""
    drop_columns = ['firstname', 'lastname', 'position', 'id', 'season',  'goals', 'assists', 'points', 'cap_hit', 'gp', 'points_per_game']
    df['points_per_game'] = df['points'] / df['gp']
    df['goals_per_game'] = df['goals'] / df['gp']
    df['assists_per_game'] = df['assists'] / df['gp']
    df['pv'] = df['cap_hit'] / df['points_per_game'].replace(0, np.nan).fillna(1.0)
    df['pv'] = df['pv'].apply(lambda x: x if x > 0 else 1.0)
    
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['pv'])
    df = df.drop(columns=drop_columns, errors='ignore')
    return df