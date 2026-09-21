import os
import pickle
import pandas as pd
import shap
import mlflow
import numpy as np

def evaluate_model():
    # Setup MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("hazard_susceptibility")

    # Load Data and Model
    df = pd.read_csv('data/raw/data.csv')
    features = ['elevation', 'slope', 'rainfall', 'soil_type_idx']
    X = df[features]
    y_true = df['hazard_severity']
    
    with open('models/xgb_mapie_model.pkl', 'rb') as f:
        mapie_model = pickle.load(f)
        
    with mlflow.start_run():
        # Predict with 90% confidence interval
        y_pred, y_pis = mapie_model.predict(X)
        
        # y_pis shape is (n_samples, 2, n_alphas) where n_alphas=1 for alpha=0.1
        # Extract lower and upper bounds
        y_lower = y_pis[:, 0, 0]
        y_upper = y_pis[:, 1, 0]
        
        # Calculate coverage (should be ~90%)
        coverage = np.mean((y_true >= y_lower) & (y_true <= y_upper))
        print(f"Empirical Coverage: {coverage*100:.2f}%")
        mlflow.log_metric("empirical_coverage", coverage)
        
        # SHAP Explainability
        # MAPIE wraps the base estimator. We extract the base XGBoost model to compute SHAP values.
        base_model = mapie_model.single_estimator_
        
        explainer = shap.TreeExplainer(base_model)
        shap_values = explainer.shap_values(X)
        
        print("SHAP values computed successfully.")
        
        # Save a summary plot artifact
        import matplotlib.pyplot as plt
        shap.summary_plot(shap_values, X, show=False)
        plt.savefig("models/shap_summary.png", bbox_inches='tight')
        mlflow.log_artifact("models/shap_summary.png")
        print("Evaluation complete. Results logged to MLflow.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    evaluate_model()
