# TrustLens Local Production Deployment

> **Status**: LIVE (Localhost)
> **Mode**: Full End-to-End Logic
> **Artifacts**: Hash-Locked from `mlops/`

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn requests httpx scikit-learn pandas numpy matplotlib transformers torch
   ```

2. **Generate ML Artifacts** (If not already done):
   ```bash
   python mlops/colab_notebooks/s2_diffusion_train.py
   python mlops/colab_notebooks/s3_intent_classification_train.py
   # ... etc
   ```

3. **Launch System**:
   Double-click `start_system.bat` or run:
   ```cmd
   .\start_system.bat
   ```

## 🏗️ Architecture (Local Port Mapping)

| Component | Port | Description |
| :--- | :--- | :--- |
| **Gateway** | `8000` | Main Entry Point (`/scan`) |
| **S1 Provenance** | `8001` | C2PA Validation |
| **S2 Diffusion** | `8002` | Isolation Forest (`diffusion_isolation_forest.pkl`) |
| **S3 Semantic** | `8003` | Intent Guardrails (`drift_thresholds.json`) |
| **S4 Forensics** | `8004` | Ensemble Logic (`filter_ensemble_weights.json`) |
| **S5 Source** | `8005` | Decay Dynamics (`behavior_decay_params.json`) |
| **Trust Graph** | `8006` | Probabilistic Fusion Engine |
| **Sentinel** | N/A | Background Process (Logs to `sentinel.log`) |
| **Extension** | `5173` | Vite Dev Server |

## 🧪 Validation Scenarios

1. **Viral Misinformation (Burst)**:
   - Input: Hash ending in `% 3 == 0` (Simulated in S2).
   - Result: Badge RED/YELLOW, S2 Risk High.

2. **Satire**:
   - Input: Text containing "Satire".
   - Result: Badge GREEN (Neutral), S3 returns specific "STOP" metadata.

3. **Unknown Source**:
   - Input: Source not in `mock_db`.
   - Result: Badge NEUTRAL, Uncertainty High (Cold Start Rule).

## 🛡️ Sentinel Oversight

Check `sentinel.log` for heartbeat entries.
Sentinel will alert if any service on ports 8000-8006 goes down.
