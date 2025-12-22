from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import joblib
import os
from app.ml.data.dataset_builder import build_forward_dataset, build_defenseman_dataset
from app.ml.data.features import skater_data_to_features
from sklearn.model_selection import train_test_split

ARTIFACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'artifacts')


# Test using cd /Users/evancillie/Documents/GitHub/TradeValue/backend
# python3 -m app.ml.training.evaluate

def evaluate_model(model_name='forward_model'):
    """Evaluate a trained model on test data"""
    
    model_path = os.path.join(ARTIFACTS_DIR, f'{model_name}.pkl')
    model = joblib.load(model_path)
    
    if 'forward' in model_name:
        df = build_forward_dataset()
    else:
        df = build_defenseman_dataset()
    
    df_features = skater_data_to_features(df)
    
    X = df_features.drop(columns=['pv'])
    y = df_features['pv']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2}
