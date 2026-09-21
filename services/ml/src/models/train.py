import os
import pickle
import pandas as pd
from xgboost import XGBRegressor
from mapie.regression import MapieQuantileRegressor
import mlflow
import mlflow.sklearn

def train_model():
    # Setup MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("hazard_susceptibility")

    # Load Data
    df = pd.read_csv('data/raw/data.csv')
    
    features = ['elevation', 'slope', 'rainfall', 'soil_type_idx']
    X = df[features]
    y = df['hazard_severity']

    with mlflow.start_run():
        # Base XGBoost model
        xgb_params = {
            'objective': 'reg:quantileerror',
            'quantile_alpha': np.array([0.05, 0.5, 0.95]), # Need to use specific quantile objective or standard MSE for base
            'max_depth': 5,
            'learning_rate': 0.1,
            'n_estimators': 100
        }
        
        # Note: XGBoost natively supports quantile regression in recent versions,
        # but MAPIE works by wrapping a standard regressor and applying conformal prediction.
        # We'll use standard XGBRegressor as base estimator for MAPIE CQR.
        base_estimator = XGBRegressor(max_depth=5, learning_rate=0.1, n_estimators=100, random_state=42)
        
        # Wrap with MAPIE for Conformalized Quantile Regression (CQR)
        # Using 90% coverage interval (alpha = 0.1)
        mapie_model = MapieQuantileRegressor(base_estimator, cv="prefit", alpha=0.1)
        
        # For prefit, we need to split data to train base estimator, then fit mapie on calibration set.
        # For simplicity, we just use cv='split'
        mapie_model = MapieQuantileRegressor(base_estimator, cv="split", alpha=0.1)
        
        print("Training MAPIE CQR model...")
        mapie_model.fit(X, y)
        
        # Log params
        mlflow.log_param("model_type", "XGBRegressor + MapieQuantileRegressor")
        mlflow.log_param("alpha", 0.1)
        
        # Save model locally for DVC
        os.makedirs('models', exist_ok=True)
        model_path = 'models/xgb_mapie_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(mapie_model, f)
            
        # Log model to MLflow
        mlflow.sklearn.log_model(mapie_model, "model")
        print(f"Model saved to {model_path} and logged to MLflow.")

if __name__ == "__main__":
    # Ensure working directory is services/ml
    import numpy as np # imported here for completeness
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    train_model()
