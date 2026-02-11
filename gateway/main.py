from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import asyncio
import os

app = FastAPI(title="TrustLens API Gateway")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow Extension/Dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration (Env vars in prod)
SIGNAL_URLS = {
    "provenance": "http://localhost:8001/analyze",
    "diffusion": "http://localhost:8002/analyze",
    "semantic": "http://localhost:8003/analyze",
    "forensics": "http://localhost:8004/analyze",
    "source": "http://localhost:8005/analyze",
}
TIG_URL = "http://localhost:8006/inference"

class ScanRequest(BaseModel):
    url: str
    content_hash: str
    text_content: Optional[str] = None
    media_urls: List[str] = []
    timestamp: str

class TrustResponse(BaseModel):
    request_id: str
    trust_posture: str # "neutral", "caution", "high_risk"
    signals: Dict[str, Any]
    tig_result: Dict[str, Any]

async def query_signal(client: httpx.AsyncClient, name: str, url: str, payload: dict) -> dict:
    try:
        resp = await client.post(url, json=payload, timeout=5.0)
        resp.raise_for_status()
        return {name: resp.json()}
    except Exception as e:
        print(f"Error querying {name}: {e}")
        # Fail-safe: Return default unknown/neutral for this signal
        return {name: {"risk_level": "unknown", "confidence": 0.0, "error": str(e)}}

@app.post("/scan", response_model=TrustResponse)
async def scan_content(request: ScanRequest):
    # 1. Validation & Content Fetching
    # REAL PRODUCT UPGRADE: Actually fetch the URL content
    if not request.text_content or len(request.text_content) < 50:
        try:
            print(f"Fetching real content from: {request.url}")
            async with httpx.AsyncClient(follow_redirects=True) as client:
                resp = await client.get(request.url, timeout=10.0)
                # Simple HTML to Text (Production would use BeautifulSoup)
                # Just taking the first 5000 chars of raw HTML body for now
                # to enable semantic analysis
                raw_text = resp.text[:5000] 
                request.text_content = raw_text
                print(f"Fetched {len(raw_text)} chars.")
        except Exception as e:
            print(f"Fetch failed: {e}")
            request.text_content = "Content fetch failed."

    # 2. Fan-out to Signals
    payload = request.model_dump()
    
    async with httpx.AsyncClient() as client:
        # Launch all signal requests in parallel
        tasks = [
            query_signal(client, name, url, payload) 
            for name, url in SIGNAL_URLS.items()
        ]
        
        # S4 (Forensics) is conditional: only if media_urls present
        
        results_list = await asyncio.gather(*tasks)
    
    # 3. Aggregate Results
    aggregated_signals = {}
    for res in results_list:
        aggregated_signals.update(res)
        
    # 4. Forward to Trust Inference Graph (TIG)
    # The TIG adds the "Trust Posture" and "Conflict Resolution"
    try:
        async with httpx.AsyncClient() as client:
             tig_resp = await client.post(TIG_URL, json={"signals": aggregated_signals}, timeout=2.0)
             tig_result = tig_resp.json()
    except Exception as e:
        # Fallback if TIG fails
        tig_result = {
            "overall_trust_posture": "unknown",
            "confidence": 0.0,
            "explanation": "Trust Engine unavailable."
        }
            
    # 5. Return Final Response
    return TrustResponse(
        request_id=request.content_hash, # Simplified
        trust_posture=tig_result.get("overall_trust_posture", "unknown"),
        signals=aggregated_signals,
        tig_result=tig_result
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "layer": "gateway"}
