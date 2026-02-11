
# Start Services in specific windows/tabs or background

echo "Starting TrustLens Local Deployment..."

# 1. Start Signal Services
start "S1 Provenance" cmd /k "uvicorn signals.provenance.main:app --port 8001"
start "S2 Diffusion" cmd /k "uvicorn signals.diffusion.main:app --port 8002"
start "S3 Semantic" cmd /k "uvicorn signals.semantic.main:app --port 8003"
start "S4 Forensics" cmd /k "uvicorn signals.forensics.main:app --port 8004"
start "S5 Source" cmd /k "uvicorn signals.source.main:app --port 8005"

# 2. Start Trust Inference Graph
start "Trust Graph" cmd /k "uvicorn trust_graph.main:app --port 8006"

# 3. Start API Gateway
start "API Gateway" cmd /k "uvicorn gateway.main:app --port 8000"

# 4. Start Sentinel
start "Sentinel" cmd /k "python sentinel/main.py"

# 5. Start Frontend
cd browser_extension
start "Extension Dev" cmd /k "npm run dev"

echo "All services launched. Check Sentinel window for status."
