from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import random
import os

app = FastAPI(title="NAVAM ML Serving (Demo)")

class ScoreRequest(BaseModel):
    habitation_id: str
    features: Dict[str, Any]

class ConfidenceInterval(BaseModel):
    point_estimate: float
    ci_lower_90: float
    ci_upper_90: float
    coverage_target: float = 0.90

class ShapValue(BaseModel):
    feature: str
    shap_value: float
    feature_value: float

class ScoreResponse(BaseModel):
    point_estimate: float
    ci_lower_90: float
    ci_upper_90: float
    shap_values: List[ShapValue]
    joint_hazard_probability: float | None = None

@app.get("/health")
async def health_check():
    return {"status": "ok", "mode": "demo" if os.getenv("DEMO_MODE") == "true" else "production"}

@app.post("/score", response_model=ScoreResponse)
async def get_score(request: ScoreRequest):
    # In DEMO_MODE, we generate realistic synthetic predictions based on input features
    base_score = 65.0
    if "elevation_m" in request.features:
        base_score += (2500 - float(request.features["elevation_m"])) * 0.01
        
    point = max(0.0, min(100.0, base_score + random.uniform(-5, 5)))
    ci_width = random.uniform(8.0, 15.0)
    
    return ScoreResponse(
        point_estimate=round(point, 2),
        ci_lower_90=round(max(0.0, point - ci_width), 2),
        ci_upper_90=round(min(100.0, point + ci_width), 2),
        shap_values=[
            ShapValue(feature="elevation_m", shap_value=12.4, feature_value=request.features.get("elevation_m", 1800)),
            ShapValue(feature="elderly_pct", shap_value=8.2, feature_value=request.features.get("elderly_pct", 15)),
            ShapValue(feature="housing_pucca_pct", shap_value=-5.1, feature_value=request.features.get("housing_pucca_pct", 40)),
        ],
        joint_hazard_probability=round(random.uniform(0.1, 0.4), 3)
    )
