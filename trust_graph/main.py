from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from .engine import TrustEngine

app = FastAPI(title="TrustLens Inference Graph (TIG)")
engine = TrustEngine()

class InferenceRequest(BaseModel):
    signals: Dict[str, Any]

@app.post("/inference")
async def run_inference(request: InferenceRequest):
    try:
        result = engine.fuse_evidence(request.signals)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "trust_graph"}
