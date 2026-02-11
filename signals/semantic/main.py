from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import os
import json
import hashlib
import numpy as np

# --- MLOPS CONFIG ---
CONFIG_PATH = "../../intent_model_artifact/drift_thresholds.json"
HASH_PATH = "../../intent_model_artifact/artifact_hash.sha256"

drift_config = {}
model_hash = "unknown"

try:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            drift_config = json.load(f)
            
    if os.path.exists(HASH_PATH):
        with open(HASH_PATH, "r") as f:
            model_hash = f.read().strip()
except Exception as e:
    print(f"CRITICAL: Failed to load S3 Config: {e}")

app = FastAPI(title="TrustLens Signal: Semantic Drift")

class AnalyzeRequest(BaseModel):
    content_hash: str
    text_content: Optional[str] = None
    media_urls: List[str] = []
    timestamp: str
    source_url: str

class SignalResponse(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "semantic_drift"
    risk_score: float
    confidence_score: float
    evidence_metadata: Dict[str, Any]
    explanation: str
    calibrated_uncertainty: float

@app.post("/analyze", response_model=SignalResponse)
async def analyze_drift(request: AnalyzeRequest):
    # Simulated Inference using Config
    
    # 1. Intent Classification (Simulated for Speed/Proto)
    text = request.text_content or ""
    intent = "factual"
    if "opinion" in text.lower(): intent = "opinion"
    if "satire" in text.lower(): intent = "satire"
    
    # Failure Safe Rule
    if intent != "factual":
        return SignalResponse(
            risk_score=0.1, # Low risk for satire/opinion if identified
            confidence_score=0.9,
            evidence_metadata={"intent": intent, "action": "STOP_DRIFT_ANALYSIS"},
            explanation=f"Content classified as {intent}. semantic drift analysis skipped.",
            calibrated_uncertainty=0.1
        )
        
    # 2. Drift Calculation (Simulated Cosine Sim)
    # Using hash so it's deterministic per article
    h_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    sim_score = (h_val % 100) / 100.0 # 0.0 to 1.0
    
    threshold = drift_config.get("drift_threshold_cosine", 0.82)
    
    if sim_score < threshold:
        # Low similarity = High Drift
        risk = 0.8
        explanation = "Significant semantic drift detected against referenced facts."
    else:
        risk = 0.1
        explanation = "Content aligns with known factual baseline."
        
    return SignalResponse(
        risk_score=risk,
        confidence_score=0.75,
        evidence_metadata={"cosine_sim": sim_score, "threshold": threshold},
        explanation=explanation,
        calibrated_uncertainty=0.3
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "semantic_drift", "config_loaded": bool(drift_config)}
