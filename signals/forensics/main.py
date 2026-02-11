from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import os
import json

# --- MLOPS CONFIG ---
CONFIG_PATH = "../../forensics_model_artifact/filter_ensemble_weights.json"
weights = {}
try:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            weights = json.load(f)
except Exception as e:
    print(f"Failed to load S4 weights: {e}")

app = FastAPI(title="TrustLens Signal: Media Forensics")

class AnalyzeRequest(BaseModel):
    content_hash: str
    text_content: Optional[str] = None
    media_urls: List[str] = []
    timestamp: str
    source_url: str

class SignalResponse(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "media_forensics"
    risk_score: float
    confidence_score: float
    evidence_metadata: Dict[str, Any]
    explanation: str
    calibrated_uncertainty: float

@app.post("/analyze", response_model=SignalResponse)
async def analyze_forensics(request: AnalyzeRequest):
    if not request.media_urls:
         return SignalResponse(
            risk_score=0.0,
            confidence_score=1.0,
            evidence_metadata={"status": "skipped_no_media"},
            explanation="No media to analyze.",
            calibrated_uncertainty=0.0
        )
        
    # Simulated Feature Extraction
    # In live, this would run OpenCV/FFmpeg filters
    # Here we mock based on URL keywords for the Demo
    
    url = request.media_urls[0].lower()
    
    ela_score = 0.1
    noise_score = 0.1
    compression_score = 0.1
    
    if "deepfake" in url:
        noise_score = 0.9
        compression_score = 0.8
    elif "compressed" in url:
        compression_score = 0.9
    elif "tampered" in url:
        ela_score = 0.8
        
    # Weighted Ensemble
    w_ela = weights.get("ela_weight", 0.33)
    w_noise = weights.get("noise_weight", 0.33)
    w_comp = weights.get("compression_weight", 0.33)
    
    ensemble_risk = (ela_score * w_ela) + (noise_score * w_noise) + (compression_score * w_comp)
    
    # Heuristic: High compression reduces confidence in other signals
    uncertainty = 0.2
    if compression_score > 0.8:
        uncertainty = 0.7 # High uncertainty if compressed
        explanation = "High compression detected; forensic reliability reduced."
        # Cap risk if uncertain
        ensemble_risk = min(ensemble_risk, 0.4)
    else:
        explanation = "Forensic traces analyze."
        if ensemble_risk > 0.6:
            explanation = "Inconsistent noise/ELA patterns detected."
            
    return SignalResponse(
        risk_score=ensemble_risk,
        confidence_score=1.0 - uncertainty,
        evidence_metadata={"raw_scores": [ela_score, noise_score, compression_score]},
        explanation=explanation,
        calibrated_uncertainty=uncertainty
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "media_forensics"}
