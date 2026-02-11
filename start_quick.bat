
@echo off
echo Starting TrustLens (Lite Mode)...

start "Gateway & Graph" cmd /k "uvicorn gateway.main:app --port 8000 & uvicorn trust_graph.main:app --port 8006"
start "Signals" cmd /k "uvicorn signals.diffusion.main:app --port 8002 & uvicorn signals.semantic.main:app --port 8003 & uvicorn signals.forensics.main:app --port 8004 & uvicorn signals.source.main:app --port 8005"
start "Frontend" cmd /k "cd browser_extension && npm run dev"

echo TrustLens is LIVE. Open Chrome and load 'browser_extension' folder.
