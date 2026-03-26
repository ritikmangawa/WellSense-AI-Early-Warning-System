from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import numpy as np
from tensorflow.keras.models import load_model

# Create a modular APIRouter so this entire AI system can be plugged into another project!
mental_health_router = APIRouter()

# 1. Load the GRU brain we just trained!
import os
_BASE = os.path.dirname(os.path.abspath(__file__))
model = load_model(os.path.join(_BASE, "..", "model", "gru_model.h5"))

# 2. Define what data the frontend should send us
class RiskRequest(BaseModel):
    user_id: Optional[str] = "user_123"
    # We need 7 days of data, with 5 features each 
    # Example format: [[5.9, 2.7, 7.4, 1, 1], ... ] x 7
    sequence: list

@mental_health_router.get("/")
def home():
    return {"message": "Early Warning Mental Health API is Running!"}

# --- EXPLAINABILITY AI ---
def generate_explanation(sequence: list) -> str:
    # sequence is 7 days, each day is [sleep, screen, study, activity, stress]
    recent_days = sequence[-3:] # Look at the last 3 days
    reasons = []
    
    # Check Sleep < 6 hours (index 0)
    if sum(1 for day in recent_days if day[0] < 6) >= 2:
        reasons.append("you have been sleeping less than 6 hours frequently")
        
    # Check Stress >= 1 [Medium/High] (index 4)
    if sum(1 for day in recent_days if day[4] >= 1) >= 2:
        reasons.append("your stress levels have been elevated")
        
    # Check Activity == 0 [No exercise] (index 3)
    if sum(1 for day in recent_days if day[3] == 0) >= 2:
        reasons.append("you haven't exercised much lately")
        
    if not reasons:
        return "Our AI noticed subtle patterns in your routine indicating stress risk."
        
    return f"Your risk is elevated because {' and '.join(reasons)}."
# -------------------------

# 3. Create the Prediction Endpoint
@mental_health_router.post("/predict")
def predict_risk(data: RiskRequest):
    # Convert incoming data list to a numpy array expected by the GRU: (1 sample, 7 days, 5 features)
    input_seq = np.array(data.sequence).reshape(1, 7, 5)
    
    # Make the prediction
    # model.predict returns something like [[0.82]], so we grab [0][0] to just get 0.82
    prediction = model.predict(input_seq)[0][0]
    
    explanation = None
    if prediction > 0.7:
        risk_message = "⚠️ High stress risk in next 3 days. Take a break!"
        explanation = generate_explanation(data.sequence)
    elif prediction > 0.4:
        risk_message = "⚠️ Moderate risk. Keep an eye on your rest."
        explanation = generate_explanation(data.sequence)
    else:
        risk_message = "✅ Low risk. You are doing great!"
        
    return {
        "risk_score": float(prediction),
        "message": risk_message,
        "explanation": explanation
    }

# Standalone execution app setup
app = FastAPI()

# Allow the React frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Plug in the modular AI router!
app.include_router(mental_health_router)

