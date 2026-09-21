from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
import shap
import os

app = FastAPI(title="NAVAM ML Serving API", version="1.0")

MODEL = None
EXPLAINER = None

class PredictionRequest(BaseModel):
    habitation_id: str
    elevation: float
    slope: float
    rainfall: float
    soil_type_idx: int

class PredictionResponse(BaseModel):
    habitation_id: str
    prediction: float
    lower_bound_90: float
    upper_bound_90: float
    top_5_features: dict

@app.on_event("startup")
def load_artifacts():
    global MODEL, EXPLAINER
    # We navigate up from src/api/main.py to services/ml/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    model_path = os.path.join(base_dir, 'models', 'xgb_mapie_model.pkl')
    try:
        with open(model_path, 'rb') as f:
            MODEL = pickle.load(f)
        base_model = MODEL.single_estimator_
        EXPLAINER = shap.TreeExplainer(base_model)
        print("Model and explainer loaded successfully.")
    except Exception as e:
        print(f"Warning: Could not load model artifacts. Ensure training is run first. {e}")

@app.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    if MODEL is None or EXPLAINER is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    X_df = pd.DataFrame([{
        'elevation': req.elevation,
        'slope': req.slope,
        'rainfall': req.rainfall,
        'soil_type_idx': req.soil_type_idx
    }])
    
    pred, pis = MODEL.predict(X_df)
    
    shap_vals = EXPLAINER.shap_values(X_df)[0]
    feature_names = X_df.columns.tolist()
    
    feature_importances = {name: float(val) for name, val in zip(feature_names, shap_vals)}
    top_features = dict(sorted(feature_importances.items(), key=lambda item: abs(item[1]), reverse=True)[:5])
    
    return PredictionResponse(
        habitation_id=req.habitation_id,
        prediction=float(pred[0]),
        lower_bound_90=float(pis[0, 0, 0]),
        upper_bound_90=float(pis[0, 1, 0]),
        top_5_features=top_features
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
