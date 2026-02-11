from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import os
import pickle
import hashlib
import time

# --- MLOPS CONFIG ---
MODEL_PATH = "../../diffusion_model_artifact/diffusion_isolation_forest.pkl"
HASH_PATH = "../../diffusion_model_artifact/artifact_hash.sha256"

# Load Model
clf = None
model_hash = "unknown"

try:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            clf = pickle.load(f)
        
    if os.path.exists(HASH_PATH):
        with open(HASH_PATH, "r") as f:
            model_hash = f.read().strip()
            
except Exception as e:
    print(f"CRITICAL: Failed to load S2 Model: {e}")

app = FastAPI(title="TrustLens Signal: Diffusion Risk")

class AnalyzeRequest(BaseModel):
    content_hash: str
    text_content: Optional[str] = None
    media_urls: List[str] = []
    timestamp: str
    source_url: str
    # Simulated metadata for local demo if extraction is weak
    simulated_iat_sequence: Optional[List[float]] = None 

class SignalResponse(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "diffusion"
    risk_score: float
    confidence_score: float
    evidence_metadata: Dict[str, Any]
    explanation: str
    calibrated_uncertainty: float

@app.post("/analyze", response_model=SignalResponse)
async def analyze_diffusion(request: AnalyzeRequest):
    global clf
    
    # 1. Feature Extraction (Simulated for Extension MVP)
    # The extension sends hash/url. In a real crawler, we'd fetch share history.
    # For local proto, we accept "simulated_iat_sequence" or generate dummy features.
    
    if request.simulated_iat_sequence:
        features = [request.simulated_iat_sequence] # 10 IATs
    else:
        # Fallback: Hash-based procedural generation for deterministic demo
        h_val = int(hashlib.sha256(request.content_hash.encode()).hexdigest(), 16)
        if h_val % 3 == 0:
            # Simulate Coordinated (Low variance)
             features = [[0.2] * 10]
        elif h_val % 3 == 1:
            # Simulate Organic (High variance)
            features = [[5.0, 10.0, 2.0, 40.0, 5.0, 6.0, 12.0, 3.0, 8.0, 1.0]]
        else:
            # Unknown
            features = None

    if not clf:
        return SignalResponse(risk_score=0.5, confidence_score=0.0, explanation="Model not loaded", calibrated_uncertainty=1.0, evidence_metadata={})

    if features:
        # Score
        try:
             raw_score = -clf.decision_function(features)[0] # Inverted: Higher = Anomaly/Coordinated
             # Normalize roughly -0.2 to 0.2 range to 0-1
             risk = max(0.0, min(1.0, (raw_score + 0.2) * 2.5))
             
             # Organic usually has score < 0 (risk < 0.5)
             # Coordinated usually has score > 0 (risk > 0.5)
             
             explanation = "Patterns resemble coordinated amplification." if risk > 0.6 else "Diffusion pattern consistent with organic sharing."
             confidence = 0.8
             uncertainty = 0.2
        except:
             risk = 0.5
             explanation = "Feature extraction failed."
             confidence = 0.1
             uncertainty = 0.9
    else:
        risk = 0.3
        explanation = "Insufficient diffusion data."
        confidence = 0.2
        uncertainty = 0.8

    return SignalResponse(
        risk_score=risk,
        confidence_score=confidence,
        evidence_metadata={"model_version": model_hash[:8]},
        explanation=explanation,
        calibrated_uncertainty=uncertainty
    )

@app.get("/health")
def health_check():
    status = "healthy" if clf else "degraded"
    return {"status": status, "service": "diffusion", "model_hash": model_hash}
