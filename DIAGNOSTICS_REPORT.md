# TrustLens Local Deployment Diagnostics Report

> **Status**: WARNING ⚠️
> **Timestamp**: 2026-02-11
> **Environment**: Windows Localhost

## 🔍 Root Cause Analysis of Failures

The system has experienced intermittent failures ("Scanning Failed") due to a combination of **Resource Contention**, **Process Management**, and **Configuration Gaps** inherent to running a distributed microservice architecture on a single Windows machine.

### 1. The "Zombie Process" Issue (Critical)
*   **Observation**: The Gateway (Port 8000) frequently becomes unreachable even after restarting scripts.
*   **Technical Reason**: Windows does not always cleanly kill child processes spawned by batch scripts or Python sub-shells. When we run `taskkill /F /IM python.exe`, it kills the *interpreter*, but sometimes leaves the `uvicorn` socket bound in a `TIME_WAIT` state or a detached process holding the port.
*   **Impact**: When you try to restart, the new Gateway process crashes silently because `Address already in use`, leading to "Scanning Failed" in the extension.

### 2. CORS & Network Security
*   **Observation**: Browser Extension blocked from accessing `localhost:8000`.
*   **Technical Reason**: Browser extensions operate in a unique security context (`chrome-extension://`). The locally hosted API Gateway did not originally have `CORSMiddleware` configured to explicitly allow this origin.
*   **Resolution**: Added `allow_origins=["*"]` to `gateway/main.py`. This is fixed, but required a restart which triggered Issue #1.

### 3. "Mock" vs. "Real" Logic Disconnect
*   **Observation**: Different links produced the exact same output.
*   **Technical Reason**: To deliver the prototype quickly, the Frontend `App.jsx` was hardcoded to send a static dummy string ("This is a sample test article...") because building a real-time web scraper is complex.
*   **Impact**: The system looked "broken" because it ignored user input.
*   **Resolution**: Upgraded Gateway to perform real-time `httpx.get()` calls to fetch live HTML from `steelersnow.com`.

### 4. Cold Start Latency
*   **Observation**: First request often fails or times out.
*   **Technical Reason**: We are spinning up 5 ML models (Isolation Forest, Transformers, etc.) simultaneously. On a local machine, this spikes CPU usage, causing the API Gateway to timeout (default 5s) before the signals (S2-S5) are ready to accept connections.

## 🛠️ Corrective Actions Taken

1.  **Orchestration**: Created `start_quick.bat` to manage processes better, though Windows limitations remain.
2.  **Code Hardening**:
    *   Added **CORS** to Gateway.
    *   Added **Real Fetching** to Gateway.
    *   Added **Dynamic Hashing** to Frontend.
3.  **Resilience**: Manually force-killed processes to clear `TIME_WAIT` sockets.

## 📋 Current System State

| Component | Status | Port | Notes |
| :--- | :--- | :--- | :--- |
| **Gateway** | **LIVE** | 8000 | Now fetches real URL content. |
| **Frontend** | **LIVE** | 5173 | Connected, Dynamic Inputs enabled. |
| **Signals** | **LIVE** | 8001-8005 | Running, processing real text. |
| **Sentinel** | **OFF** | N/A | Disabled to save resources for Signals. |

**Recommendation**: If "Scanning Failed" recurs, wait 30 seconds for ports to clear, then run `start_quick.bat` exactly once. Do not spam the start command.
