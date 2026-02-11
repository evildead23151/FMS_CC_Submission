from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import os
import json

# --- MLOPS CONFIG ---
CONFIG_PATH = "../../source_model_artifact/behavior_decay_params.json"
params = {}
try:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            params = json.load(f)
except Exception as e:
    print(f"Failed to load S5 params: {e}")

app = FastAPI(title="TrustLens Signal: Source Behavior")

class AnalyzeRequest(BaseModel):
    content_hash: str
    text_content: Optional[str] = None
    media_urls: List[str] = []
    timestamp: str
    source_url: str

class SignalResponse(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: str = "source_behavior"
    risk_score: float
    confidence_score: float
    evidence_metadata: Dict[str, Any]
    explanation: str
    calibrated_uncertainty: float

@app.post("/analyze", response_model=SignalResponse)
async def analyze_source(request: AnalyzeRequest):
    # Simulated Historical Database
    # In prod, this hits Redis/Postgres
    
    domain = request.source_url.replace("https://", "").replace("http://", "").split("/")[0]
    
    # Demo Mock DB
    mock_db = {
        "verified-news.com": {"risk": 0.1, "history": 1000, "corrections": 5},
        "sketchy-blog.net": {"risk": 0.8, "history": 20, "corrections": 0},
        "reformed-outlet.org": {"risk": 0.4, "history": 500, "corrections": 12}
    }
    
    data = mock_db.get(domain)
    
    if not data:
        # COLD START RULE
        return SignalResponse(
            risk_score=0.3, # Neutral/Low Risk
            confidence_score=0.1, # Low Confidence
            evidence_metadata={"status": "cold_start"},
            explanation="New or unknown source. Converting to neutral risk.",
            calibrated_uncertainty=0.9
        )
        
    # Apply Decay/Dynamics (Simplified)
    risk = data["risk"]
    conf = 0.8 if data["history"] > 100 else 0.4
    
    # Check for Fairness/Redemption
    if data["corrections"] > 10 and risk > 0.3:
        explanation = "Source has history of transparent corrections. Risk attenuated."
        risk -= 0.1
    else:
        explanation = "Historical behavior analysis complete."

    return SignalResponse(
        risk_score=max(0.0, risk),
        confidence_score=conf,
        evidence_metadata=data,
        explanation=explanation,
        calibrated_uncertainty=1.0 - conf
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "source_behavior"}
