# TrustLens Architecture Specification

## Global Architecture Diagram

```mermaid
graph TD
    User(User Browser) --> Extension[Browser Extension (Lite Signal Extraction)];
    Extension --> Gateway[API Gateway (Orchestrator)];
    
    subgraph "Strictly Isolated Signal Services"
        Gateway --> S1[Signal 1: Crypto Provenance];
        Gateway --> S2[Signal 2: Observable Diffusion];
        Gateway --> S3[Signal 3: Intent-Aware Semantic Drift];
        Gateway --> S4[Signal 4: Selective Media Forensics];
        Gateway --> S5[Signal 5: Source Behavior];
    end
    
    S1 --> TIG[Trust Inference Graph Engine];
    S2 --> TIG;
    S3 --> TIG;
    S4 --> TIG;
    S5 --> TIG;
    
    TIG --> Gateway;
    Gateway --> Extension;
    
    Sentinel[Sentinel Oversight Agent] -.-> Gateway;
    Sentinel -.-> S1;
    Sentinel -.-> S2;
    Sentinel -.-> S3;
    Sentinel -.-> S4;
    Sentinel -.-> S5;
    Sentinel -.-> TIG;
    
    style Sentinel fill:#f9f,stroke:#333,stroke-width:4px
```

## Component Responsibilities

### 1. Browser Extension (Client)
- **Role**: Lightweight signal extraction + UI rendering.
- **Constraints**: NO heavy ML inference. No external script injection.
- **Tech**: React + Vite, Manifest v3.
- **Key Tasks**: 
    - Extract text, image metadata.
    - Compute SHA-256 content hash.
    - Render Trust Badge (Neutral -> Signal).

### 2. API Gateway
- **Role**: Routing + Orchestration.
- **Constraints**: Stateless. No ML logic.
- **Key Tasks**: 
    - Rate limiting.
    - Dispatch to signals.
    - Forward aggregated results to TIG.

### 3. Signal Services (The "Organs")

| Signal | Type | Input | Output | Model/Logic |
| :--- | :--- | :--- | :--- | :--- |
| **S1: Crypto Provenance** | Deterministic | C2PA Metadata | Provenance Present (Y/N) | Signature Validation |

| **S2: Observable Diffusion** | ML | Content Hash/Text | Diffusion Risk Band | Burst Detection, Similarity |
| **S3: Semantic Drift** | ML Pipeline | Text | Drift Risk, Claims | Intent Class -> Claim Extract -> Embed |
| **S4: Media Forensics** | ML (Conditional) | Image/Video | Manipulation Risk | Noise Residual, Compression Artifacts |
| **S5: Source Behavior** | Historic | Domain/Author | Behavior Trend | Time-decayed scoring |

> **Explicit Limitation (S2)**
> Signal 2 does not attempt to reconstruct full propagation graphs or infer private network behavior. Diffusion risk is inferred solely from publicly observable reuse patterns, indexed sources, and temporal similarity signals. Private messaging platforms and closed networks are explicitly out of scope.

> **Failure-Safe Rule (S3)**
> If intent classification confidence does not exceed the minimum threshold for factual content, the semantic drift pipeline MUST terminate early and return “Insufficient Signal” rather than a risk assessment.

> **Fairness Constraint (S5)**
> Source behavior modeling is trend-based, time-decayed, and reversible. Past errors do not permanently penalize sources, and transparent corrections actively increase confidence. No static reputation scores are stored or exposed.


### 4. Trust Inference Graph (TIG) (The "Brain")
- **Role**: Evidence Fusion.
- **Logic**: Probabilistic combination of signals. Resolves contradictions.
- **Output**: 
    - Context Risk
    - Provenance Confidence
    - Manipulation Risk
    - Diffusion Risk
    - **Overall Trust Posture** (with uncertainty)

> **Signal Combination Strategy**
> The Trust Inference Graph combines signals using calibrated likelihood contributions rather than absolute scores. Each signal contributes confidence-weighted evidence, and contradictions are resolved through attenuation rather than override. No single signal can dominate the Trust Posture unless its confidence exceeds a predefined threshold. Unknown or low-confidence signals reduce certainty rather than increasing risk.

### 5. Sentinel Oversight Agent (The "Immune System")
- **Role**: Infrastructure Guardian.
- **Constraints**: Cannot modify ML models or inference logic.
- **Key Tasks**:
    - Health monitoring.
    - Model hash verification.
    - Auto-restarts/Rollbacks.

## Data Flow
1. **Extension** captures content -> Hash + Metadata.
2. **Gateway** receives payload -> Fans out to S1-S5.
3. **Signals** process in parallel (S4 conditional) -> Return intermediate evidence.
4. **TIG** receives all evidence -> Computes final Trust Posture.
5. **Gateway** returns Trust Posture to Extension.
6. **Extension** updates Badge/Panel.

## Hard Failure Conditions
- Binary truth output.
- Fake ML/Placeholders.
- Overconfident claims.
- Hidden uncertainty.
